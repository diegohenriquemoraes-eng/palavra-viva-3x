"""Gera temas "dormir" de UM salmo completo, direto do texto bíblico.

Por que existe: o poço de temas é o único gargalo HUMANO do projeto — cada
tema é um dia de publicação e era escrito à mão. Com o canal ES publicando 2
longos por dia (25/08/2026), o poço passou a durar metade do tempo. Este
script produz temas do formato que a medição elegeu como motor de horas —
"Salmo N completo", 60 min de narração — sem inventar nada: título, abertura,
tags e descrição saem de FATOS do próprio salmo (quantos versículos tem, o que
diz a inscrição, como começa).

O que ele NÃO faz, de propósito: interpretar o texto (diretriz editorial nº 4)
e afirmar autoria. A inscrição é citada como o que é — "leva por inscrição:
Salmo de Davi" —, nunca como "escrito por Davi": autoria de salmo é disputada
e datar isso seria opinião nossa entrando no canal.

    python produzir/gerar_temas_salmo.py --dry-run
    python produzir/gerar_temas_salmo.py --quantos 20
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.stdout.reconfigure(encoding="utf-8")

from nucleo import biblia, idiomas  # noqa: E402

TEMAS = RAIZ / "conteudo" / "temas.json"
IDIOMAS_TEMA = ("es", "en", "pt")

# Consultas de imagem NOTURNAS já validadas no Commons (o filtro exige 2
# termos da consulta no título da foto, então par concreto — nunca frase).
CONSULTAS = [
    ["milky way", "night clouds", "starry sky"],
    ["moon clouds", "desert night", "night sky"],
    ["night lake", "moon night", "starry sky"],
    ["night forest", "milky way", "moon clouds"],
    ["night sea", "night clouds", "starry sky"],
]

# Salmos que NÃO viram tema de um capítulo só: o 119 tem 176 versículos (a
# narração passa de duas horas e o vídeo estoura o alvo de 60 min por larga
# margem, sem o ciclo de repetição que o formato usa).
GIGANTES = {119}

UNIDADES = {
    "es": ["cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete",
           "ocho", "nueve", "diez", "once", "doce", "trece", "catorce",
           "quince", "dieciséis", "diecisiete", "dieciocho", "diecinueve"],
    "pt": ["zero", "um", "dois", "três", "quatro", "cinco", "seis", "sete",
           "oito", "nove", "dez", "onze", "doze", "treze", "catorze", "quinze",
           "dezesseis", "dezessete", "dezoito", "dezenove"],
}
DEZENAS = {
    "es": {20: "veinte", 30: "treinta", 40: "cuarenta", 50: "cincuenta",
           60: "sesenta", 70: "setenta", 80: "ochenta", 90: "noventa"},
    "pt": {20: "vinte", 30: "trinta", 40: "quarenta", 50: "cinquenta",
           60: "sessenta", 70: "setenta", 80: "oitenta", 90: "noventa"},
}
CENTENAS = {
    "es": {100: "cien", 200: "doscientos"},
    "pt": {100: "cento", 200: "duzentos"},
}


def por_extenso(n: int, idioma: str) -> str:
    """Número falado. A abertura é NARRADA — '45' viraria 'quarenta e cinco'
    na boca do TTS de qualquer jeito, mas escrever por extenso é o que garante
    a leitura certa em toda voz (edge-tts lê '105' como 'cento e cinco' em pt e
    'ciento cinco' em es, e erra em números soltos no meio da frase)."""
    if n < 20:
        return UNIDADES[idioma][n]
    if n < 100:
        d, u = divmod(n, 10)
        base = DEZENAS[idioma][d * 10]
        if not u:
            return base
        if idioma == "es" and d == 2:
            return f"veinti{UNIDADES['es'][u]}"
        liga = " y " if idioma == "es" else " e "
        return f"{base}{liga}{UNIDADES[idioma][u]}"
    c, resto = divmod(n, 100)
    if idioma == "es":
        base = "cien" if (c == 1 and not resto) else (
            "ciento" if c == 1 else CENTENAS["es"].get(c * 100, f"{c}00"))
    else:
        base = "cem" if (c == 1 and not resto) else (
            "cento" if c == 1 else CENTENAS["pt"].get(c * 100, f"{c}00"))
    if not resto:
        return base
    liga = " " if idioma == "es" else " e "
    return f"{base}{liga}{por_extenso(resto, idioma)}"


def inscricao(idioma: str, salmo: int) -> str:
    """A inscrição do salmo, como está na tradução (ou vazio se não houver).

    `biblia.carregar_versos` a REMOVE da narração de propósito (é anotação
    litúrgica, não fala do versículo). Aqui ela volta como FATO citado na
    abertura — é justamente o tipo de informação que diferencia um vídeo do
    outro sem interpretar coisa nenhuma.
    """
    livros = biblia._carregar(idioma)
    cap = next(c for c in livros["Psalms"]["chapters"] if c["chapter"] == salmo)
    bruto = cap["verses"][0]["text"].replace("[", "").replace("]", "")
    m = biblia.INSCRICAO[idioma].match(bruto)
    if not m:
        return ""
    txt = re.sub(r"\s+", " ", m.group(0)).strip().rstrip(".:").strip()
    if idioma == "es":
        # Mesma normalização de grafia do resto do canal (biblia._limpar): a
        # RV1909 é anterior à reforma ortográfica e escreve "cantó á Jehová".
        # Modernizar a GRAFIA não troca a tradução — segue RV1909.
        for pat, rep in biblia.ARCAISMOS_ES:
            txt = pat.sub(rep, txt)
    return txt[0].upper() + txt[1:] if txt else ""


# Palavras que não podem TERMINAR um corte: o texto ficaria pendurado
# ("...com todo o"). Artigos, preposições e conjunções dos dois idiomas.
ORFAS = {
    "de", "da", "do", "das", "dos", "e", "o", "a", "os", "as", "em", "no",
    "na", "com", "que", "por", "para", "ao", "à", "um", "uma", "meu", "minha",
    "seu", "sua", "y", "el", "la", "los", "las", "en", "con", "por", "su",
    "mi", "del", "al", "un", "una", "es", "se", "lo", "the", "of", "and",
    "to", "in", "my", "his", "for", "with",
}


def _aparar(palavras: list[str]) -> list[str]:
    while palavras and palavras[-1].strip(",;:.").casefold() in ORFAS:
        palavras = palavras[:-1]
    return palavras


def _frase_inicial(texto: str, max_palavras: int = 14) -> str:
    """Primeira oração do salmo, cortada em palavra inteira.

    A abertura é NARRADA e a citação é seguida de "O texto é a Bíblia Livre",
    então ela precisa fechar com ponto — terminar em vírgula ou ponto-e-vírgula
    faz a voz emendar as duas frases como se fossem uma.
    """
    corte = re.split(r"(?<=[.;:!?])\s", texto)[0]
    palavras = corte.split()
    if len(palavras) > max_palavras:
        palavras = _aparar(palavras[:max_palavras])
        return " ".join(palavras).rstrip(",;:.") + "..."
    frase = " ".join(palavras).rstrip(",;: ")
    # Verso que já termina em ? ou ! fecha sozinho; acrescentar ponto daria
    # "vanidad?." na tela e uma pausa esquisita na narração.
    return frase if frase.endswith(("?", "!", ".")) else frase + "."


def abertura(idioma: str, salmo: int, versos: list, insc: str) -> str:
    n = por_extenso(salmo, idioma)
    qtd = por_extenso(len(versos), idioma)
    inicio = _frase_inicial(versos[0][1])
    fonte = {"es": "Reina-Valera de mil ochocientos noventa y nueve",
             "pt": "Bíblia Livre"}[idioma]
    if idioma == "es":
        partes = [f"Salmo {n}, completo."]
        if insc:
            partes.append(f"Lleva por inscripción: {insc}.")
        partes += [f"Son {qtd} versículos, leídos sin prisa.",
                   f"Empieza así: {inicio}",
                   f"El texto es la {fonte}."]
    else:
        partes = [f"Salmo {n}, completo."]
        if insc:
            partes.append(f"Traz por inscrição: {insc}.")
        partes += [f"São {qtd} versículos, lidos sem pressa.",
                   f"Começa assim: {inicio}",
                   f"O texto é a {fonte}."]
    return " ".join(partes)


def titulo_short(idioma: str, salmo: int, verso: int, texto: str) -> str:
    rot = {"es": "Salmo", "en": "Psalm", "pt": "Salmo"}[idioma]
    marca = {"es": "Biblia", "en": "Bible", "pt": "Bíblia"}[idioma]
    palavras = _aparar(texto.split()[:7])
    trecho = " ".join(palavras).rstrip(",;:.")
    titulo = f"{rot} {salmo}:{verso} — {trecho} | {marca}"
    while len(titulo) > 100 and len(palavras) > 3:
        palavras = _aparar(palavras[:-1])
        trecho = " ".join(palavras).rstrip(",;:.")
        titulo = f"{rot} {salmo}:{verso} — {trecho} | {marca}"
    return titulo[:100].rstrip()


def escolher_versos(versos: dict) -> list:
    """4 versículos espalhados pelo salmo, com tamanho de Short (8 a 30
    palavras). Verso muito curto não enche 15 s; muito longo estoura o teto.

    Só entram os que existem nos TRÊS idiomas: o pacote bíblico é um só para
    es/en/pt, e na KJV o versículo 1 de vários salmos é apenas a inscrição —
    depois da limpeza ele some, e um Short apontando para ele quebraria o
    render em inglês (`passagem vazia após limpeza`).
    """
    comuns = set.intersection(*(set(dict(v)) for v in versos.values()))
    base = [v for v in versos["es"] if v[0] in comuns]
    bons = [v for v in base if 8 <= len(v[1].split()) <= 30] or base
    if len(bons) <= 4:
        return bons
    passo = len(bons) / 4
    return [bons[min(len(bons) - 1, int(i * passo))] for i in range(4)]


def montar_tema(salmo: int, idx: int) -> dict:
    versos = {i: biblia.carregar_versos(i, f"Psalms {salmo}")
              for i in IDIOMAS_TEMA}
    insc = {i: inscricao(i, salmo) for i in ("es", "pt")}
    n_versos = len(versos["es"])

    titulo = {
        "es": f"Salmos para Dormir — Salmo {salmo} Completo | Biblia Hablada",
        "en": f"Psalms for Sleep — Psalm {salmo} in Full | Audio Bible",
        "pt": f"Salmos para Dormir — Salmo {salmo} Completo | Bíblia Falada",
    }
    escolhidos = escolher_versos(versos)
    shorts = []
    for k, (num, _) in enumerate(escolhidos):
        shorts.append({
            "ref": f"Psalms {salmo}:{num}",
            "tipo": "descriptivo",
            "consulta_imagem": CONSULTAS[idx % len(CONSULTAS)][
                k % len(CONSULTAS[idx % len(CONSULTAS)])],
            "titulo": {
                i: titulo_short(i, salmo, num,
                                dict(versos[i]).get(num, versos[i][0][1]))
                for i in IDIOMAS_TEMA
            },
            # Contexto FACTUAL (não aplicação/pregação): onde o versículo está
            # dentro do salmo. É o que a política de monetização pede como
            # diferença em relação à fonte, sem atravessar a diretriz nº 4.
            "aplicacao": {
                "es": f"Versículo {num} de {n_versos}, del Salmo {salmo}.",
                "pt": f"Versículo {num} de {n_versos}, do Salmo {salmo}.",
            },
        })

    return {
        "slug": f"salmo-{salmo}-completo",
        "formato": "dormir",
        "longo": {
            "refs": [f"Psalms {salmo}"],
            "titulo": titulo,
            "thumb_titulo": {"es": f"SALMO {salmo}", "en": f"PSALM {salmo}",
                             "pt": f"SALMO {salmo}"},
            "thumb_sub": {"es": f"Salmo {salmo} completo",
                          "en": f"Psalm {salmo} in full",
                          "pt": f"Salmo {salmo} completo"},
            "consultas_imagens": CONSULTAS[idx % len(CONSULTAS)],
            "abertura": {i: abertura(i, salmo, versos[i], insc[i])
                         for i in ("es", "pt")},
            # Tags tiradas dos termos que a Analytics mostrou serem digitados
            # de verdade ("biblia hablada completa reina valera", "salmo 103").
            "tags_extra": {
                "es": [f"salmo {salmo}", f"salmo {salmo} completo",
                       "salmos para dormir", "biblia hablada para dormir",
                       "biblia hablada completa reina valera",
                       "salmos narrados"],
                "pt": [f"salmo {salmo}", f"salmo {salmo} completo",
                       "salmos para dormir", "biblia narrada para dormir",
                       "biblia falada completa", "salmos narrados"],
            },
            "descricao_busca": {
                "es": (f"Salmo {salmo} completo, {n_versos} versículos leídos "
                       f"despacio para dormir. Biblia hablada en español, "
                       f"Reina-Valera 1909."),
                "pt": (f"Salmo {salmo} completo, {n_versos} versículos lidos "
                       f"devagar para dormir. Bíblia narrada em português, "
                       f"Bíblia Livre."),
            },
        },
        "shorts": shorts,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--quantos", type=int, default=20)
    args = ap.parse_args()

    temas = json.loads(TEMAS.read_text(encoding="utf-8"))
    slugs = {t["slug"] for t in temas}
    ja_usados = set()
    for t in temas:
        for r in t["longo"]["refs"]:
            m = re.match(r"Psalms (\d+)$", r.strip())
            if m:
                ja_usados.add(int(m.group(1)))

    candidatos = [n for n in range(1, 151)
                  if n not in ja_usados and n not in GIGANTES]
    novos = []
    for idx, salmo in enumerate(candidatos):
        if len(novos) >= args.quantos:
            break
        tema = montar_tema(salmo, idx)
        if tema["slug"] in slugs:
            continue
        # Mesma validação do reabastecedor, aqui na origem: título > 100 ou ref
        # inválida só apareceria na hora de publicar, quando já é tarde.
        for i in IDIOMAS_TEMA:
            assert len(tema["longo"]["titulo"][i]) <= 100, tema["slug"]
            for s in tema["shorts"]:
                assert len(s["titulo"][i]) <= 100, (tema["slug"], s["ref"])
                biblia.carregar_versos(i, s["ref"])
        novos.append(tema)
        print(f"  {tema['slug']}: {len(tema['shorts'])} shorts | "
              f"abertura es: {tema['longo']['abertura']['es'][:90]}...")

    print(f"\n{len(novos)} temas novos "
          f"(salmos livres restantes: {len(candidatos) - len(novos)})")
    if args.dry_run or not novos:
        return
    temas.extend(novos)
    TEMAS.write_text(json.dumps(temas, ensure_ascii=False, indent=2) + "\n",
                     encoding="utf-8")
    print(f"gravado em {TEMAS.relative_to(RAIZ).as_posix()} "
          f"({len(temas)} temas no total)")


if __name__ == "__main__":
    main()
