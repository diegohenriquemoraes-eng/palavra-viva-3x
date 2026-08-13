"""Roteiro do Reel "cine": condensa o item e dá os tempos SEM depender do TTS.

No modo antigo os tempos da legenda vinham dos word boundaries da voz
sintética. Tirando a voz (decisão de 13/08/2026 — a narração robótica é a
assinatura de automação mais visível que tínhamos), quem dita o ritmo passa a
ser a LEITURA: cada bloco fica no ar o tempo de ser lido, com um piso para o
olho pegar e um teto para não parar o vídeo.

Duas coisas mudam de propósito em relação ao modo antigo:

1. **O texto é condensado.** O banco foi escrito para narração de ~28 s; lido
   na tela isso vira um Reel longo demais para o formato (os perfis de
   referência do nicho vivem entre 12 e 20 s). Aqui fica premissa + fecho:
   a primeira frase, quantas do meio couberem no orçamento, e SEMPRE a última
   — que é onde mora a virada do micro-roteiro.
2. **O fecho é retido.** A última frase entra com folga e fica mais tempo:
   é o que o espectador guarda, e é o que o faz esperar até o fim.
"""

from __future__ import annotations

import re

# ritmo de leitura
SEG_POR_CHAR = 0.045      # ~22 caracteres por segundo, com o texto grande na tela
BASE_BLOCO = 0.55         # custo fixo de trocar o bloco (o olho reencontra a linha)
MIN_BLOCO = 1.05
MAX_BLOCO = 2.40
MIN_GANCHO = 2.00         # o gancho é o 1º segundo: ninguém lê correndo
FOLGA_ANTES_FECHO = 0.35  # respiro antes da virada
RETENCAO_FECHO = 1.30     # o fecho fica mais tempo na tela
CAUDA = 0.45              # silêncio curto no fim (emenda do loop)

TETO_S = 21.0             # teto do Reel inteiro
LARGURA_BLOCO = 26        # caracteres por bloco de legenda (texto grande)
MAX_PALAVRAS_BLOCO = 5


def frases(texto: str) -> list[str]:
    """Quebra em frases inteiras, preservando a pontuação."""
    partes = re.split(r"(?<=[.!?])\s+", texto.strip())
    return [p.strip() for p in partes if p.strip()]


def condensar(texto: str, teto_chars: int) -> str:
    """Premissa + o que couber do meio + SEMPRE o fecho.

    Cortar pelo fim seria mais simples e destruiria o item: nestes
    micro-roteiros a última frase é a conclusão prática ("Diga não cedo.",
    "Só não pague por eles."). Sem ela sobra descrição de problema.
    """
    fs = frases(texto)
    if len(fs) <= 2:
        return " ".join(fs)
    primeira, ultima, meio = fs[0], fs[-1], fs[1:-1]
    escolhidas = [primeira]
    total = len(primeira) + len(ultima)
    for f in meio:
        if total + len(f) + 2 > teto_chars:
            break
        escolhidas.append(f)
        total += len(f) + 1
    escolhidas.append(ultima)
    return " ".join(escolhidas)


def _blocos_de(texto: str) -> list[str]:
    """Texto -> blocos curtos de legenda, UMA frase por vez.

    Blocar o texto corrido gerava blocos como "emocional. Mais tarde, quando":
    fim de uma frase colado no começo da outra. Na tela, sem voz para costurar,
    isso lê como erro. Fatiando por frase antes de blocar, nenhum bloco
    atravessa ponto final — o preço é algum bloco curto no fim da frase, que é
    exatamente onde a pausa faz sentido.
    """
    out: list[str] = []
    for frase in frases(texto):
        inicio = len(out)      # fronteira: nada se junta com a frase anterior
        atual: list[str] = []
        for palavra in frase.split():
            atual.append(palavra)
            linha = " ".join(atual)
            corta = palavra[-1:] in ";:" and len(linha) >= 14
            if (len(linha) >= LARGURA_BLOCO or corta
                    or len(atual) >= MAX_PALAVRAS_BLOCO):
                out.append(linha)
                atual = []
        if atual:
            resto = " ".join(atual)
            # sobra de 1-2 palavras volta para o bloco anterior DA MESMA frase,
            # senão a tela pisca com "quando" sozinho
            if (len(out) > inicio and len(resto) <= 12
                    and len(out[-1]) + len(resto) < 34):
                out[-1] = f"{out[-1]} {resto}"
            else:
                out.append(resto)
    return out


def _dur_bloco(txt: str) -> float:
    return min(MAX_BLOCO, max(MIN_BLOCO, BASE_BLOCO + len(txt) * SEG_POR_CHAR))


def montar(gancho: str, texto: str) -> tuple[list[dict], float]:
    """Devolve (blocos com tempo, duração total do Reel).

    Cada bloco: {ini, fim, texto, estilo} com estilo em
    Gancho / Verso / Fecho — o estilo é o que dá o desenho na tela.

    A ordem de montagem importa: gancho e FECHO são reservados primeiro, e só
    o que sobra de tempo vai para o miolo. Montar na ordem de leitura fazia o
    orçamento estourar no meio e o fecho chegar picado ("falar por ele." no
    lugar de "O desconforto do outro vai falar por ele.") — justo a frase que
    justifica o Reel inteiro.
    """
    orcamento_chars = int((TETO_S - MIN_GANCHO - 3.0) / SEG_POR_CHAR * 0.85)
    fs = frases(condensar(texto, orcamento_chars))
    if not fs:
        fs = [texto]
    frase_fecho, frases_miolo = fs[-1], fs[:-1]

    blocos: list[dict] = []
    t = 0.0
    for i, parte in enumerate(_blocos_de(gancho)):
        # o primeiro bloco é o frame zero do Reel: piso maior de propósito
        d = max(MIN_GANCHO if i == 0 else MIN_BLOCO, _dur_bloco(parte))
        blocos.append({"ini": t, "fim": t + d, "texto": parte, "estilo": "Gancho"})
        t += d

    # tempo que o fecho vai consumir — reservado ANTES de gastar com o miolo
    blocos_fecho = _blocos_de(frase_fecho)
    custo_fecho = (FOLGA_ANTES_FECHO + RETENCAO_FECHO
                   + sum(_dur_bloco(b) for b in blocos_fecho))

    for frase in frases_miolo:
        partes = _blocos_de(frase)
        custo = sum(_dur_bloco(p) for p in partes)
        if t + custo + custo_fecho > TETO_S:
            continue          # frase inteira fica de fora: não se corta no meio
        for p in partes:
            d = _dur_bloco(p)
            blocos.append({"ini": t, "fim": t + d, "texto": p, "estilo": "Verso"})
            t += d

    t += FOLGA_ANTES_FECHO
    for i, parte in enumerate(blocos_fecho):
        d = _dur_bloco(parte)
        if i == len(blocos_fecho) - 1:
            d += RETENCAO_FECHO       # a última linha é a que fica na cabeça
        blocos.append({"ini": t, "fim": t + d, "texto": parte, "estilo": "Fecho"})
        t += d

    return blocos, round(t + CAUDA, 2)
