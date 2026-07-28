"""Identidade do canal Stoic by Night — coluna sob a lua.

Deliberadamente LONGE do Palavra Viva (livro+chama, azul-marinho e dourado):
outro público, outra prateleira. Se os dois parecerem a mesma fábrica com
roupa trocada, é o rastro de operação em massa que a política de conteúdo
inautêntico procura.

Paleta: ardósia quase preta -> índigo profundo, com mármore frio e bronze
apagado. É canal para ouvir no escuro — nada aqui brilha.

Símbolo: uma coluna dórica recortada contra a lua. Lê a 32px (o tamanho real
do avatar no celular), que é a única prova que importa.

Gera:
- marca/stoic-avatar.png   (800x800)
- marca/stoic-banner.png   (2560x1440; texto na área segura central de
                            1546x423 — fora dela só o desktop enxerga)

    python marca/gerar_marca_stoic.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.stdout.reconfigure(encoding="utf-8")

AQUI = Path(__file__).resolve().parent
FONTES = AQUI / "fontes"

ARDOSIA = (12, 14, 18)
INDIGO = (26, 30, 48)
MARMORE = (226, 226, 220)
MARMORE_SOMBRA = (150, 152, 150)
BRONZE = (176, 141, 98)
CINZA = (138, 140, 146)


def fundo(w: int, h: int) -> Image.Image:
    """Gradiente vertical ardósia -> índigo. Linha a linha: o gradiente por
    pixel do gerador bíblico leva minutos num banner de 2560x1440."""
    img = Image.new("RGB", (1, h))
    px = img.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        px[0, y] = tuple(round(ARDOSIA[i] + (INDIGO[i] - ARDOSIA[i]) * t)
                         for i in range(3))
    return img.resize((w, h))


def lua(img: Image.Image, cx: int, cy: int, r: int) -> None:
    """Lua cheia difusa atrás da coluna — a fonte de luz da cena."""
    halo = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(halo)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    halo = halo.filter(ImageFilter.GaussianBlur(r * 0.10))
    img.paste(Image.new("RGB", img.size, (238, 236, 226)), (0, 0), halo)
    brilho = Image.new("L", img.size, 0)
    ImageDraw.Draw(brilho).ellipse(
        (cx - r * 2.1, cy - r * 2.1, cx + r * 2.1, cy + r * 2.1), fill=46)
    brilho = brilho.filter(ImageFilter.GaussianBlur(r * 0.55))
    img.paste(Image.new("RGB", img.size, (120, 132, 168)), (0, 0), brilho)


def coluna(img: Image.Image, cx: int, topo: int, base: int, larg: int) -> None:
    """Coluna dórica: capitel, fuste com caneluras, plinto."""
    d = ImageDraw.Draw(img)
    meia = larg // 2
    cap_h = int(larg * 0.30)
    plinto_h = int(larg * 0.26)
    fuste_topo = topo + cap_h
    fuste_base = base - plinto_h

    # capitel (ábaco + equino)
    d.rectangle((cx - meia * 1.34, topo, cx + meia * 1.34, topo + cap_h * 0.46),
                fill=MARMORE)
    d.polygon([(cx - meia * 1.30, topo + cap_h * 0.46),
               (cx + meia * 1.30, topo + cap_h * 0.46),
               (cx + meia * 1.02, fuste_topo), (cx - meia * 1.02, fuste_topo)],
              fill=MARMORE_SOMBRA)
    # fuste com leve êntase (afina para cima, como as de verdade)
    d.polygon([(cx - meia, fuste_topo), (cx + meia, fuste_topo),
               (cx + meia * 1.10, fuste_base), (cx - meia * 1.10, fuste_base)],
              fill=MARMORE)
    # caneluras: sombras verticais que dão volume sem desenhar sombra nenhuma
    for i in range(1, 6):
        x = cx - meia + larg * i / 6
        d.line((x, fuste_topo + larg * 0.06, x, fuste_base - larg * 0.04),
               fill=MARMORE_SOMBRA, width=max(2, larg // 46))
    # plinto
    d.rectangle((cx - meia * 1.42, fuste_base, cx + meia * 1.42, base),
                fill=MARMORE)
    d.rectangle((cx - meia * 1.42, fuste_base, cx + meia * 1.42,
                 fuste_base + plinto_h * 0.22), fill=MARMORE_SOMBRA)


def fonte(nome: str, tam: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTES / nome), tam)


def largura(d: ImageDraw.ImageDraw, txt: str, f, esp: int = 0) -> int:
    cx = d.textbbox((0, 0), txt, font=f)[2]
    return cx + esp * (len(txt) - 1)


def texto_espacado(d: ImageDraw.ImageDraw, xy, txt: str, f, cor, esp: int):
    """Bebas Neue sem espaçamento fica apertada em caixa alta."""
    x, y = xy
    for ch in txt:
        d.text((x, y), ch, font=f, fill=cor)
        x += d.textbbox((0, 0), ch, font=f)[2] + esp


def avatar(caminho: Path, lado: int = 800) -> None:
    # Proporções decididas na prova de 32px, não no olho do arquivo grande:
    # com a coluna larga (0,20) e a lua colada nela, o conjunto fundia num "P"
    # no tamanho real do celular. Coluna mais fina e alta (proporção dórica de
    # verdade, ~6:1) e a lua afastada para o alto, com fundo escuro entre as
    # duas, é o que mantém as formas separadas quando some a resolução.
    img = fundo(lado, lado)
    lua(img, int(lado * 0.71), int(lado * 0.25), int(lado * 0.13))
    coluna(img, int(lado * 0.44), int(lado * 0.16), int(lado * 0.85),
           int(lado * 0.135))
    # máscara circular: o YouTube corta o avatar em círculo
    mascara = Image.new("L", (lado, lado), 0)
    ImageDraw.Draw(mascara).ellipse((0, 0, lado, lado), fill=255)
    saida = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    saida.paste(img, (0, 0), mascara)
    saida.save(caminho)
    print(f"avatar: {caminho.name}")


def banner(caminho: Path, w: int = 2560, h: int = 1440) -> None:
    img = fundo(w, h)
    # A área segura do banner (1546x423 no centro) é do TEXTO, e só dela.
    # Na primeira versão a coluna passava por cima do "T" de STOIC e a lua
    # comia o "NIGHT" — ilustração e wordmark disputando o mesmo espaço.
    # Agora os dois ficam FORA da caixa: coluna à esquerda de x=507, lua
    # acima de y=508.
    seguro_x0, seguro_y0 = (w - 1546) // 2, (h - 423) // 2
    lua(img, w - int(h * 0.23), int(h * 0.19), int(h * 0.125))
    coluna(img, seguro_x0 - int(h * 0.115), int(h * 0.13), int(h * 0.88),
           int(h * 0.10))
    d = ImageDraw.Draw(img)

    f_nome = fonte("BebasNeue-Regular.ttf", 190)
    f_sub = fonte("Montserrat-Bold.ttf", 50)
    nome, esp = "STOIC BY NIGHT", 14
    sub = "Marcus Aurelius · Seneca · Epictetus — read aloud for sleep"

    # área segura central: 1546x423 é o que TODO dispositivo mostra
    cx, cy = w // 2, h // 2
    ln = largura(d, nome, f_nome, esp)
    if ln > 1400:                      # nunca deixar o wordmark cortar
        f_nome = fonte("BebasNeue-Regular.ttf", int(190 * 1400 / ln))
        ln = largura(d, nome, f_nome, esp)
    texto_espacado(d, (cx - ln // 2, cy - 150), nome, f_nome, MARMORE, esp)
    ls = d.textbbox((0, 0), sub, font=f_sub)[2]
    d.text((cx - ls // 2, cy + 76), sub, font=f_sub, fill=CINZA)
    d.line((cx - 250, cy + 46, cx + 250, cy + 46), fill=BRONZE, width=3)
    img.save(caminho)
    print(f"banner: {caminho.name} ({w}x{h})")


if __name__ == "__main__":
    avatar(AQUI / "stoic-avatar.png")
    banner(AQUI / "stoic-banner.png")
    # prova dos 32px: se o símbolo não lê aqui, não lê no celular
    Image.open(AQUI / "stoic-avatar.png").resize(
        (32, 32), Image.LANCZOS).resize((256, 256), Image.NEAREST).save(
        AQUI / "stoic-avatar-32.png")
    print("prova de 32px: stoic-avatar-32.png")
