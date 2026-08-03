"""Capa (thumbnail) do Reel — uma peça DESENHADA, não um frame do vídeo.

Identidade do Psicologia Fria: fundo azul quase preto, luz fria (azul-gelo),
TÍTULO gigante e o gancho embaixo — o que para o scroll no feed e na grade.
Passada como `cover_url` na criação do container REELS (ver publicar_ig.py).
Todo o conteúdo importante fica na FAIXA CENTRAL, que sobrevive ao corte 1:1
da grade do perfil.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONTES = Path(__file__).resolve().parent.parent / "marca" / "fontes"
BEBAS = str(FONTES / "BebasNeue-Regular.ttf")
MONT = str(FONTES / "Montserrat-Bold.ttf")

W, H = 1080, 1920
FUNDO_TOPO = (7, 10, 18)
FUNDO_MEIO = (12, 18, 30)
FUNDO_BASE = (18, 30, 48)
GELO = (140, 195, 235)
GELO_CLARO = (210, 235, 250)
BRANCO = (240, 246, 252)
CINZA = (150, 170, 190)


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


def _brilho(cx: int, cy: int, raio: int, cor=GELO, forca=70) -> Image.Image:
    """Glow radial frio (aditivo) para dar foco atrás do texto."""
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(glow)
    passos = 60
    for i in range(passos, 0, -1):
        r = int(raio * i / passos)
        f = (1 - i / passos) ** 2
        c = tuple(int(cor[j] * f * forca / 100) for j in range(3))
        d.ellipse([cx - r, cy - int(r * 1.15), cx + r, cy + int(r * 1.15)], fill=c)
    return glow.filter(ImageFilter.GaussianBlur(60))


def _particulas(img: Image.Image, seed: int) -> None:
    """Pontinhos de luz fria esparsos — neve suspensa, sem poluir."""
    import random
    rng = random.Random(seed)
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(60):
        x, y = rng.randint(0, W), rng.randint(0, int(H * 0.9))
        r = rng.choice([1, 1, 1, 2])
        a = rng.randint(25, 100)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(210, 235, 250, a))


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


def _iceberg(d: ImageDraw.ImageDraw, cx: float, cy: float, esc: float) -> None:
    """Glifo da marca: iceberg minimalista com linha d'água."""
    top = [(cx - 44 * esc, cy), (cx - 18 * esc, cy - 52 * esc),
           (cx + 3 * esc, cy - 35 * esc), (cx + 26 * esc, cy - 67 * esc),
           (cx + 50 * esc, cy)]
    sub = [(cx - 61 * esc, cy), (cx - 35 * esc, cy + 96 * esc),
           (cx + 12 * esc, cy + 122 * esc), (cx + 55 * esc, cy + 76 * esc),
           (cx + 68 * esc, cy)]
    d.polygon(sub, fill=(70, 130, 180, 90))
    d.polygon(top, fill=GELO_CLARO)
    d.line([(cx - 110 * esc, cy), (cx + 110 * esc, cy)], fill=GELO, width=max(2, int(4 * esc)))


def gerar_capa(titulo: str, gancho: str, destino: Path, seed: int = 0) -> Path:
    """titulo: 'O SILÊNCIO' (âncora gigante). gancho: frase de apoio."""
    img = _gradiente()
    img = _somar(img, _brilho(W // 2, 980, 620))
    _particulas(img, seed)

    d = ImageDraw.Draw(img, "RGBA")

    # wordmark topo + fio frio
    fw = ImageFont.truetype(MONT, 40)
    _centrado(d, "PSICOLOGIA FRIA", fw, 250, GELO, espac=8)
    d.line([(W / 2 - 170, 320), (W / 2 + 170, 320)], fill=GELO, width=3)

    # âncora gigante (título do item)
    ref = titulo.upper()
    fref = _fit(d, ref, BEBAS, W - 200, 300, 120)
    bb = d.textbbox((0, 0), ref, font=fref)
    hy = 760
    _centrado(d, ref, fref, hy + 6, (0, 0, 0), espac=6)
    _centrado(d, ref, fref, hy, GELO_CLARO, espac=6)
    y = hy + (bb[3] - bb[1]) + 70

    # gancho (frase de apoio)
    fg = ImageFont.truetype(MONT, 62)
    linhas = _quebrar(d, gancho, fg, W - 200)[:3]
    for ln in linhas:
        _centrado(d, ln, fg, y, BRANCO)
        y += 88

    # rodapé + glifo do iceberg
    ftag = ImageFont.truetype(MONT, 38)
    tag = "1 VERDADE FRIA POR DIA"
    _centrado(d, tag, ftag, 1680, CINZA, espac=4)
    _iceberg(d, W / 2, 1560, 0.55)

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
    """Soma aditiva sem numpy: base + glow, saturando em 255."""
    from PIL import ImageChops
    return ImageChops.add(base, glow)
