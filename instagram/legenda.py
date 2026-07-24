"""Caption do Reel — no estilo de um canal 'dark' (sem rosto) de versículos.

Princípios (o que faz um post de nicho bíblico performar no Instagram):

1. GANCHO na 1ª linha. O feed corta a legenda em ~125 caracteres; a primeira
   linha tem que parar o dedo sozinha. Nada de "Bom dia!" — é emoção/promessa.
2. O VERSÍCULO curto, entre aspas, com a referência. É o conteúdo.
3. MICRO-CTA de engajamento. Comentário, salvamento e compartilhamento são os
   sinais que o algoritmo de 2026 mais premia (mais que like). Pedimos UM só
   por post, girando entre eles — pedir tudo de uma vez lê como spam.
4. PONTE PARA A BIO. Link em legenda do Instagram NÃO clica: a oferta de
   afiliado mora na bio, e a legenda só aponta para lá.
5. HASHTAGS ao final: um punhado de tags grandes + médias + de nicho. Muitas
   tags idênticas em todo post é rastro de bot; giramos o conjunto pelo índice.

Tudo é determinístico pelo índice do post (girar sem aleatoriedade real, que
não sobrevive a resume no runner) — mesmo post, mesma caption.
"""

from __future__ import annotations

# Ganchos: primeira linha, o que segura o scroll. Giram por post.
GANCHOS = [
    "Leia isso antes de dormir hoje. 🙏",
    "Deus quer te falar algo agora. 👇",
    "Se este vídeo apareceu pra você, não foi por acaso.",
    "Guarde esta promessa no coração. ❤️",
    "A Palavra que você precisava ouvir hoje.",
    "Respire fundo e leia devagar. 🕊️",
    "Deixe Deus acalmar o seu coração agora.",
    "Uma promessa pra você que está cansado. 🙌",
    "Não role o feed sem ler isto.",
    "Comece o dia com esta Palavra. ☀️",
    "Quando a ansiedade bater, lembre disto.",
    "Fé é confiar mesmo sem ver. Creia. 🙏",
]

# Micro-CTA de engajamento — UM por post, girando.
CTAS = [
    'Comente "AMÉM" se você crê nesta Palavra. 🙏',
    "Salve este versículo para lembrar depois. 📌",
    "Marque alguém que precisa ler isto hoje. 💬",
    "Compartilhe para abençoar mais alguém. ↗️",
    'Escreva "AMÉM" e receba esta promessa. ✨',
    "Salve e volte aqui quando precisar de paz. 🕊️",
    "Comente 🙏 se você recebe esta Palavra.",
    "Marque um irmão na fé aqui embaixo. 👇",
]

# Conjuntos de hashtags: grandes + médias + nicho. Giram por post para não
# repetir o mesmo bloco em todos (rastro de automação). Sem tags banidas.
HASHTAGS = [
    "#Deus #fé #versículododia #palavradedeus #Jesus #bíblia #oração #salmos "
    "#gratidão #devocional #cristão #evangelho",
    "#versículododia #Deusnocontrole #fé #Jesus #palavradedeus #esperança "
    "#biblia #oração #paz #cristãos #reelscristãos #amémm",
    "#Deus #Jesus #fé #promessasdedeus #versículo #palavradedeus #salmos "
    "#confiaremDeus #devocionaldiário #cristão #bíbliasagrada #graça",
    "#fé #Deuséfiel #versículododia #oração #Jesuscristo #palavradedeus "
    "#bíblia #esperança #gratidão #reelsdefé #cristãos #amém",
    "#Deus #versículododia #fé #palavradedeus #salmos #Jesus #devocional "
    "#oração #paz #bíblia #confiaremDeus #jovenscristãos",
]


def montar_caption(ref_disp: str, texto: str, ponte_bio: str,
                   assinatura: str, idx: int) -> str:
    """Monta a caption completa do Reel nº `idx` (idx cresce a cada post)."""
    gancho = GANCHOS[idx % len(GANCHOS)]
    cta = CTAS[idx % len(CTAS)]
    tags = HASHTAGS[idx % len(HASHTAGS)]

    # Versículo enxuto entre aspas. Reels muito longos na legenda cansam; se o
    # texto passar de ~220 caracteres, corta no limite de frase.
    verso = texto.strip()
    if len(verso) > 220:
        corte = verso.rfind(". ", 0, 220)
        verso = (verso[:corte + 1] if corte > 80 else verso[:220].rstrip() + "…")

    partes = [
        gancho,
        "",
        f'"{verso}"',
        f"— {ref_disp} (Bíblia Livre)",
        "",
        cta,
        "",
        ponte_bio.strip(),
    ]
    if assinatura.strip():
        partes += ["", assinatura.strip()]
    partes += ["", tags]
    return "\n".join(partes)
