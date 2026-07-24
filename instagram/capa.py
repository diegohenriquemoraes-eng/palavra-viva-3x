"""Capa (thumbnail) do Reel — uma peça DESENHADA, não um frame do vídeo.

O vídeo abre com fade a partir do preto, então a capa automática do Instagram
pegava um quadro preto. Aqui geramos uma imagem 1080x1920 na identidade do
canal (mesma paleta azul-marinho + dourado dos 3 canais, mesmas fontes) com a
REFERÊNCIA gigante e um gancho — o que para o scroll no feed e na grade.

Passada como `cover_url` na criação do container REELS (ver publicar_ig.py).
Todo o conteúdo importante fica na FAIXA CENTRAL, que sobrevive ao corte 1:1
da grade do perfil.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONTES = Path(__file__).resolve().parent.parent / "marca" / "fontes"
BEBAS = str(FONTES / "BebasNeue-Regular.ttf")
MONT = str(FONTES / "Montserrat-Bold.ttf")

W, H = 1080, 1920
FUNDO_TOPO = (10, 16, 44)
FUNDO_MEIO = (26, 14, 58)
FUNDO_BASE = (44, 21, 82)
OURO = (232, 200, 122)
OURO_CLARO = (245, 224, 168)
BRANCO = (245, 243, 238)
CINZA = (196, 190, 176)


def _gradiente() -> Image.Image:
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        t = y / H
        if t < 0.5:
            a, b, tt = FUNDO_TOPO, FUNDO_MEIO, t * 2
        else:
            a, b, tt = FUNDO_MEIO, FUNDO_BASE, (t - 0.5) * 2
        cor = tuple(int(a[i] + (b[i] - a[i]) * tt) for i in range(3))
        for x in range(W):
            px[x, y] = cor
    return img


def _brilho(cx: int, cy: int, raio: int, cor=OURO, forca=90) -> Image.Image:
    """Glow radial dourado (aditivo) para dar foco atrás do texto."""
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(glow)
    passos = 60
    for i in range(passos, 0, -1):
        r = int(raio * i / passos)
        f = (1 - i / passos) ** 2
        c = tuple(int(cor[j] * f * forca / 100) for j in range(3))
        d.ellipse([cx - r, cy - int(r * 1.15), cx + r, cy + int(r * 1.15)], fill=c)
    return glow.filter(ImageFilter.GaussianBlur(60))


def _estrelas(img: Image.Image, seed: int) -> None:
    """Pontinhos de luz esparsos — céu, sem poluir. Determinístico pelo seed."""
    import random
    rng = random.Random(seed)
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(70):
        x, y = rng.randint(0, W), rng.randint(0, int(H * 0.9))
        r = rng.choice([1, 1, 1, 2])
        a = rng.randint(30, 120)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 250, 235, a))


def _fit(draw, texto, fonte_path, alvo_larg, tam_ini, tam_min=40):
    """Maior tamanho de fonte em que `texto` cabe em `alvo_larg`."""
    t = tam_ini
    while t > tam_min:
        f = ImageFont.truetype(fonte_path, t)
        if draw.textlength(texto, font=f) <= alvo_larg:
            return f
        t -= 4
    return ImageFont.truetype(fonte_path, tam_min)


def _quebrar(draw, texto, fonte, larg):
    palavras, linhas, atual = texto.split(), [], ""
    for p in palavras:
        teste = (atual + " " + p).strip()
        if draw.textlength(teste, font=fonte) <= larg:
            atual = teste
        else:
            if atual:
                linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    return linhas


def _centrado(draw, texto, fonte, y, cor, espac=0):
    larg = draw.textlength(texto, font=fonte) + espac * (len(texto) - 1)
    x = (W - larg) / 2
    if espac:
        for ch in texto:
            draw.text((x, y), ch, font=fonte, fill=cor)
            x += draw.textlength(ch, font=fonte) + espac
    else:
        draw.text((x, y), texto, font=fonte, fill=cor)


def gerar_capa(referencia: str, gancho: str, destino: Path, seed: int = 0) -> Path:
    """referencia: 'SALMO 23' (âncora gigante). gancho: 1ª frase do versículo."""
    img = _gradiente()
    # glow dourado (soma aditiva) atrás da âncora, no centro vertical
    img = _somar(img, _brilho(W // 2, 980, 620))
    _estrelas(img, seed)

    d = ImageDraw.Draw(img)

    # wordmark topo + fio dourado
    fw = ImageFont.truetype(MONT, 40)
    _centrado(d, "PALAVRA VIVA DIÁRIA", fw, 250, OURO, espac=8)
    d.line([(W / 2 - 190, 320), (W / 2 + 190, 320)], fill=OURO, width=3)

    # âncora gigante (referência)
    ref = referencia.upper()
    fref = _fit(d, ref, BEBAS, W - 200, 300, 120)
    bb = d.textbbox((0, 0), ref, font=fref)
    hy = 760
    # sombra + texto
    _centrado(d, ref, fref, hy + 6, (0, 0, 0), espac=6)
    _centrado(d, ref, fref, hy, OURO_CLARO, espac=6)
    y = hy + (bb[3] - bb[1]) + 70

    # gancho (1ª frase do versículo)
    fg = ImageFont.truetype(MONT, 66)
    linhas = _quebrar(d, gancho, fg, W - 200)[:3]
    for ln in linhas:
        _centrado(d, ln, fg, y, BRANCO)
        y += 92

    # rodapé + dois losangos dourados desenhados (o glifo ✦ não existe na fonte)
    ftag = ImageFont.truetype(MONT, 38)
    tag = "A PALAVRA DE DEUS, TODO DIA"
    tw = d.textlength(tag, font=ftag) + 4 * (len(tag) - 1)
    tx, ty = (W - tw) / 2, 1680
    _centrado(d, tag, ftag, ty, CINZA, espac=4)
    for dx in (tx - 46, tx + tw + 26):
        cy2 = ty + 24
        d.polygon([(dx, cy2 - 9), (dx + 9, cy2), (dx, cy2 + 9), (dx - 9, cy2)],
                  fill=OURO)

    # vinheta suave para focar o centro
    vin = Image.new("L", (W, H), 0)
    dv = ImageDraw.Draw(vin)
    dv.ellipse([-260, -260, W + 260, H + 260], fill=255)
    vin = vin.filter(ImageFilter.GaussianBlur(220))
    escuro = Image.new("RGB", (W, H), (0, 0, 0))
    img = Image.composite(img, escuro, vin)

    img.save(destino, quality=92)
    return destino


def _somar(base: Image.Image, glow: Image.Image) -> Image.Image:
    """Soma aditiva sem numpy (fallback): base + glow, saturando em 255."""
    from PIL import ImageChops
    return ImageChops.add(base, glow)
