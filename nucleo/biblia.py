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

REF_RE = re.compile(r"^(.+?)\s+(\d+)(?::(\d+)(?:-(\d+))?)?$")

# Inscrições de Salmos que não fazem sentido narradas ("Al Músico principal...",
# "To the chief Musician...", "Salmo de Davi:"). Removidas só do versículo 1.
INSCRICAO = {
    "es": re.compile(
        r"^(?:(?:Al Músico principal|Salmo|Cántico|Canción|Oración|Masquil|"
        r"Michtam|Mictam)[^.]*\.\s*)+",
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


@lru_cache(maxsize=3)
def _carregar(idioma: str) -> dict:
    arq = idiomas.CONFIG[idioma]["arquivo_biblia"]
    data = json.loads(arq.read_text(encoding="utf-8"))
    return {b["name"]: b for b in data["books"]}


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
    return out


def ref_exibicao(idioma: str, ref: str) -> str:
    """'Psalms 91:1-4' -> 'Salmo 91:1-4' (pt/es) / 'Psalm 91:1-4' (en)."""
    livro, cap, v1, v2 = analisar_ref(ref)
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
