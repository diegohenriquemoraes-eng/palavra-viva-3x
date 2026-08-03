"""Caption do Reel — perfil dark de psicologia/estoicismo (Psicologia Fria).

Princípios (o que faz o post performar no Instagram de 2026):

1. GANCHO na 1ª linha. O feed corta a legenda em ~125 caracteres; a primeira
   linha tem que parar o dedo sozinha.
2. A FRASE-NÚCLEO do vídeo, curta. É o conteúdo que se salva.
3. MICRO-CTA de engajamento. Salvamento e compartilhamento são os sinais que
   o algoritmo mais premia — pedimos UM por post, girando (pedir tudo de uma
   vez lê como spam).
4. PONTE PARA O PERFIL. Link em legenda não clica; o convite é seguir.
5. HASHTAGS ao final: grandes + médias + de nicho, girando por post (o mesmo
   bloco em todo post é rastro de bot).

Tudo determinístico pelo índice do post (mesmo post, mesma caption).
"""

from __future__ import annotations

# Ganchos: primeira linha, o que segura o scroll. Giram por post.
GANCHOS = [
    "Leia até o fim. Vai doer um pouco. 🧊",
    "Ninguém te ensinou isso — de propósito.",
    "Salve antes que você precise e não lembre onde viu.",
    "Isso explica muita coisa da sua vida.",
    "Frio, mas verdadeiro. 🥶",
    "Você já viveu isso e não tinha nome.",
    "Quanto antes você aceitar, menos vai sofrer.",
    "A maioria descobre tarde demais.",
    "Releia quantas vezes precisar.",
    "Guarde isso para o próximo teste da vida.",
    "Não é pessimismo. É lucidez.",
    "Depois que você vê, não consegue desver.",
]

# Micro-CTA de engajamento — UM por post, girando.
CTAS = [
    "Salve para reler no dia em que precisar. 📌",
    "Envie para alguém que precisa ouvir isso. ↗️",
    'Comente "FRIO" se você já passou por isso. 🧊',
    "Marque quem vive isso e ainda não percebeu. 💬",
    "Salve. Você vai precisar antes do que imagina.",
    'Comente "🥶" se concorda.',
    "Compartilhe com quem está aprendendo do jeito difícil.",
    "Siga para a próxima verdade fria. 🧠",
]

# Conjuntos de hashtags: grandes + médias + nicho. Giram por post.
HASHTAGS = [
    "#psicologia #estoicismo #mentalidade #desenvolvimentopessoal "
    "#autoconhecimento #disciplina #sabedoria #reflexao #mindset "
    "#inteligenciaemocional #frases #crescimentopessoal",
    "#estoicismo #psicologiafria #mentalidadeforte #foco #autocontrole "
    "#filosofia #marcoaurelio #disciplina #frasesdodia #maturidade "
    "#comportamento #vidareal",
    "#psicologia #comportamentohumano #inteligenciaemocional #limites "
    "#autoestima #mentalidade #sabedoriadevida #estoico #reflexaododia "
    "#disciplinamental #frasesfortes #evolucaopessoal",
    "#mindset #estoicismo #psicologia #autoconhecimento #resiliencia "
    "#mentefria #filosofiadevida #disciplina #frasesmotivacionais "
    "#comportamento #maturidadeemocional #forcamental",
    "#desenvolvimentopessoal #psicologia #estoicismo #autocontrole "
    "#mentalidade #sabedoria #frasesparastatus #reflexoes #foco "
    "#inteligencia #vidaadulta #verdades",
]


def montar_caption(titulo: str, texto: str, ponte_bio: str,
                   assinatura: str, idx: int, fonte: str = "") -> str:
    """Monta a caption completa do Reel nº `idx` (idx cresce a cada post).

    titulo: o título do item (vira a linha-âncora depois do gancho).
    fonte: mantido por compatibilidade de assinatura; não é usado (todo texto
    é original do canal)."""
    gancho = GANCHOS[idx % len(GANCHOS)]
    cta = CTAS[idx % len(CTAS)]
    tags = HASHTAGS[idx % len(HASHTAGS)]

    # Frase-núcleo enxuta. Se passar de ~220 caracteres, corta no limite de
    # frase — o resto está no vídeo.
    nucleo = texto.strip()
    if len(nucleo) > 220:
        corte = nucleo.rfind(". ", 0, 220)
        nucleo = (nucleo[:corte + 1] if corte > 80 else nucleo[:220].rstrip() + "…")

    partes = [
        gancho,
        "",
        f"{titulo.upper()} — {nucleo}",
        "",
        cta,
        "",
        ponte_bio.strip(),
    ]
    if assinatura.strip():
        partes += ["", assinatura.strip()]
    partes += ["", tags]
    return "\n".join(partes)
