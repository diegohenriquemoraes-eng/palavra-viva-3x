"""Carrega passagens bíblicas por idioma a partir dos JSONs de domínio público.

Referências canônicas usam o nome do livro em inglês (formato scrollmapper):
    "Psalms 91"        -> capítulo inteiro
    "Psalms 91:1-4"    -> faixa de versículos
    "John 3:16"        -> um versículo
"""

from __future__ import annotations

import json
import re
from functools import lru_cache

from . import idiomas

REF_RE = re.compile(r"^(.+?)\s+(\d+)(?::(\d+)(?:-(\d+))?)?(?:/(\d+)(?:-(\d+))?)?$")

# Ref POR FRASE (16/09/2026): "Meditaciones 6:75/1" = só a 1ª frase do
# parágrafo 75 do livro 6; "/2-3" = frases 2 a 3. Existe porque o corpus
# estoico é fatiado por PARÁGRAFO (a "verse" do JSON), e a tradução Díaz de
# Miranda (1785) tem parágrafos de 50 a 120 palavras: 308 parágrafos nunca
# usados em Short estavam trancados pelo teto de 20 s, e dentro deles há mais
# de 800 frases de 12 a 40 palavras. A frase é a unidade natural da máxima —
# foi assim que os poços do Poder Crudo e do Astucia Fría já vinham fatiados.
# Só vale para UM parágrafo (v1 == v2). A exibição ("Meditaciones 6:75") e a
# descrição omitem a parte da frase: a fonte é o parágrafo, e é ele que o
# espectador vai procurar.
FRASE_RE = re.compile(r"(?<=[.;!?])\s+(?=[¿¡\"“'(A-ZÁÉÍÓÚÑÜ])")

# Inscrições de Salmos que não fazem sentido narradas ("Al Músico principal...",
# "To the chief Musician...", "Salmo de Davi:"). Removidas só do versículo 1.
INSCRICAO = {
    "es": re.compile(
        # "Sigaión" entrou em 25/08/2026: sem ele o Salmo 7 era o ÚNICO dos 150
        # cuja inscrição escapava e ia para a narração ("Sigaión de David, que
        # cantó a Jehová sobre las palabras de Cus..."), como se fosse o
        # versículo 1. O EN já cobria o equivalente ("Shiggaion").
        r"^(?:(?:Al Músico principal|Salmo|Cántico|Canción|Oración|Masquil|"
        r"Michtam|Mictam|Sigaión)[^.]*\.\s*)+",
        re.IGNORECASE,
    ),
    "en": re.compile(
        r"^(?:(?:To the chief Musician|A Psalm|A Song|A Prayer|Maschil|"
        r"Michtam|Shiggaion|The song|A song)[^.]*\.\s*)+",
        re.IGNORECASE,
    ),
    "pt": re.compile(
        r"^(?:(?:Para o regente|Salmo|Cântico|Canção|Oração|Instrução|Hino|"
        r"Masquil|Mictão|Poema)[^:.]*[:.]\s*)+",
        re.IGNORECASE,
    ),
}

# Anotação litúrgica, não é fala do versículo. ES/EN: "Selah." PT (BLivre): "(Selá)"
SELAH = re.compile(r"\s*\(?\s*(?:Selah|Selá)\.?\s*\)?\s*", re.IGNORECASE)

# A RV1909 é anterior à reforma ortográfica ("á", "fué", "vió"). Corrigir a
# GRAFIA não troca a tradução — o texto segue sendo RV1909, domínio público.
ARCAISMOS_ES = [
    (re.compile(r"\bá\b"), "a"), (re.compile(r"\bÁ\b"), "A"),
    (re.compile(r"\bé\b"), "e"), (re.compile(r"\bÉ\b"), "E"),
    (re.compile(r"\bó\b"), "o"), (re.compile(r"\bÓ\b"), "O"),
    (re.compile(r"\bú\b"), "u"), (re.compile(r"\bÚ\b"), "U"),
    (re.compile(r"\bfué\b"), "fue"), (re.compile(r"\bFué\b"), "Fue"),
    (re.compile(r"\bfuí\b"), "fui"), (re.compile(r"\bFuí\b"), "Fui"),
    (re.compile(r"\bvió\b"), "vio"), (re.compile(r"\bVió\b"), "Vio"),
    (re.compile(r"\bdió\b"), "dio"), (re.compile(r"\bDió\b"), "Dio"),
    (re.compile(r"\bdí\b"), "di"), (re.compile(r"\bDí\b"), "Di"),
    (re.compile(r"\bhé\b"), "he"), (re.compile(r"\bHé\b"), "He"),
]


@lru_cache(maxsize=6)
def _carregar(idioma: str) -> dict:
    """Obras do canal, indexadas por nome.

    `arquivo_fonte` aceita UM caminho (as Bíblias, que trazem os 66 livros num
    arquivo só) ou uma LISTA. O corpus estoico veio em três arquivos, um por
    tradução, porque a proveniência é por tradução e misturá-los num arquivo
    só apagaria de quem é cada texto — o que a diretriz de domínio público não
    permite. Aqui eles voltam a ser um catálogo único de obras.
    """
    arqs = idiomas.CONFIG[idioma]["arquivo_fonte"]
    if not isinstance(arqs, (list, tuple)):
        arqs = [arqs]
    livros = {}
    for arq in arqs:
        for b in json.loads(arq.read_text(encoding="utf-8"))["books"]:
            livros[b["name"]] = b
    return livros


def _limpar(texto: str, idioma: str, primeiro_do_salmo: bool,
            livro: str) -> str:
    # colchetes do KJV marcam itálico do tradutor; o conteúdo fica, a marca sai
    texto = texto.replace("[", "").replace("]", "")
    if primeiro_do_salmo and livro == "Psalms":
        texto = INSCRICAO[idioma].sub("", texto)
    texto = SELAH.sub(" ", texto)
    if idioma == "es":
        # RV1909 põe a primeira palavra do capítulo (e JEHOVÁ) em caixa alta
        texto = re.sub(r"\b([A-ZÁÉÍÓÚÑÜ]{2,})\b",
                       lambda w: w.group(1).capitalize(), texto)
        for pat, rep in ARCAISMOS_ES:
            texto = pat.sub(rep, texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    texto = re.sub(r"\s+([.,;:!?])", r"\1", texto)
    return texto


def analisar_ref(ref: str) -> tuple[str, int, int | None, int | None]:
    """'Psalms 91:1-4' -> ('Psalms', 91, 1, 4); 'Psalms 91' -> (..., None, None)."""
    m = REF_RE.match(ref.strip())
    if not m:
        raise SystemExit(f"Referência inválida: {ref}")
    livro, cap = m.group(1).strip(), int(m.group(2))
    v1 = int(m.group(3)) if m.group(3) else None
    v2 = int(m.group(4)) if m.group(4) else v1
    return livro, cap, v1, v2


def frases_da_ref(ref: str) -> tuple[int, int] | None:
    """'Meditaciones 6:75/2-3' -> (2, 3); sem parte de frase -> None."""
    m = REF_RE.match(ref.strip())
    if not m or not m.group(5):
        return None
    f1 = int(m.group(5))
    f2 = int(m.group(6)) if m.group(6) else f1
    if f2 < f1 or f1 < 1:
        raise SystemExit(f"Referência de frase inválida: {ref}")
    if m.group(3) is None or (m.group(4) and m.group(4) != m.group(3)):
        raise SystemExit(f"Ref por frase só vale para UM parágrafo: {ref}")
    return f1, f2


def frases(texto: str) -> list[str]:
    """Fatia um parágrafo em frases (ponto, ponto e vírgula, ! e ?)."""
    return [f.strip() for f in FRASE_RE.split(texto.strip()) if f.strip()]


def carregar_versos(idioma: str, ref: str) -> list[tuple[int, str]]:
    """Devolve [(número, texto limpo)] da passagem no idioma pedido."""
    livro, cap, v1, v2 = analisar_ref(ref)
    livros = _carregar(idioma)
    if livro not in livros:
        raise SystemExit(f"Livro desconhecido no JSON: {livro}")
    capitulo = next((c for c in livros[livro]["chapters"]
                     if c["chapter"] == cap), None)
    if capitulo is None:
        raise SystemExit(f"{livro} não tem capítulo {cap}")
    versos = capitulo["verses"]
    if v1 is not None:
        versos = [v for v in versos if v1 <= v["verse"] <= v2]
        if len(versos) != v2 - v1 + 1:
            raise SystemExit(
                f"{ref} ({idioma}): esperava {v2 - v1 + 1} versos, "
                f"achei {len(versos)}")
    out = []
    for v in versos:
        texto = _limpar(v["text"], idioma, v["verse"] == 1
                        or (v1 is not None and v["verse"] == v1 and v1 == 1),
                        livro)
        if texto:
            out.append((v["verse"], texto))
    if not out:
        raise SystemExit(f"{ref} ({idioma}): passagem vazia após limpeza")
    fr = frases_da_ref(ref)
    if fr:
        f1, f2 = fr
        num, texto = out[0]
        partes = frases(texto)
        if f2 > len(partes):
            raise SystemExit(
                f"{ref} ({idioma}): o parágrafo tem {len(partes)} frase(s), "
                f"pediu até a {f2}")
        out = [(num, " ".join(partes[f1 - 1:f2]))]
    return out


def ref_exibicao(idioma: str, ref: str) -> str:
    """'Psalms 91:1-4' -> 'Salmo 91:1-4' (pt/es) / 'Psalm 91:1-4' (en)."""
    livro, cap, v1, v2 = analisar_ref(ref)   # a parte "/frase" não se exibe
    if livro == "Psalms":
        nome = idiomas.CONFIG[idioma]["palavra_salmo"]
    else:
        nome = idiomas.nome_livro(idioma, livro)
    if v1 is None:
        return f"{nome} {cap}"
    if v2 == v1:
        return f"{nome} {cap}:{v1}"
    return f"{nome} {cap}:{v1}-{v2}"


def cabecalho(idioma: str, ref: str) -> str:
    """Texto do topo do vídeo: 'SALMO 91' para Salmos, ref completa nos demais."""
    livro, cap, v1, v2 = analisar_ref(ref)
    if livro == "Psalms":
        return f"{idiomas.CONFIG[idioma]['palavra_salmo']} {cap}".upper()
    return ref_exibicao(idioma, ref).upper()
