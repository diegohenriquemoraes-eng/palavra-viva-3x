"""Identidade dos 3 canais: UM símbolo (Bíblia aberta + chama, portado do
Palabra Viva), wordmark localizado por canal.

Gera:
- marca/avatar.png            (mesmo avatar nos 3 canais — marca única)
- marca/banner-{es,en,pt}.png (2560x1440; texto dentro da área segura
                               1546x423 central, que é o que aparece em TODO
                               dispositivo — fora dela só o desktop vê)

    python marca/gerar_marca.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.stdout.reconfigure(encoding="utf-8")

AQUI = Path(__file__).resolve().parent
FONTES = AQUI / "fontes"

FUNDO_TOPO = (11, 18, 48)
FUNDO_BASE = (42, 20, 80)
OURO = (232, 200, 122)
OURO_ESCURO = (198, 158, 74)
PAGINA = (247, 243, 233)
PAGINA_SOMBRA = (214, 205, 186)
CINZA = (206, 199, 185)

CANAIS = {
    "es": ("PALABRA VIVA CORTES", "La Palabra de Dios en audio, cada día"),
    "en": ("LIVING WORD DAILY", "God's Word in audio, every day"),
    "pt": ("PALAVRA VIVA DIÁRIA", "A Palavra de Deus em áudio, todos os dias"),
}


def fundo_gradiente(w: int, h: int) -> Image.Image:
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        for x in range(w):
            t = (x / w * 0.35 + y / h * 0.65)
            px[x, y] = tuple(
                round(FUNDO_TOPO[i] + (FUNDO_BASE[i] - FUNDO_TOPO[i]) * t)
                for i in range(3))
    return img


def _perfil_chama(t: float, larg: float) -> float:
    return larg * math.sin(math.pi * t**0.75) ** 1.6 * (1 - t * 0.3)


def chama(d: ImageDraw.ImageDraw, cx: float, base_y: float, alt: float) -> None:
    larg = alt * 0.46
    esq, dir_ = [], []
    for i in range(61):
        t = i / 60
        y = base_y - alt * t
        w = _perfil_chama(t, larg)
        esq.append((cx - w, y))
        dir_.append((cx + w, y))
    d.polygon(esq + dir_[::-1], fill=OURO)
    nucleo_alt, nucleo_base = alt * 0.62, base_y - alt * 0.06
    esq, dir_ = [], []
    for i in range(61):
        t = i / 60
        y = nucleo_base - nucleo_alt * t
        w = _perfil_chama(t, larg * 0.44)
        esq.append((cx - w, y))
        dir_.append((cx + w, y))
    d.polygon(esq + dir_[::-1], fill=PAGINA)


def livro(d: ImageDraw.ImageDraw, cx: float, cy: float, larg: float) -> None:
    meia = larg / 2
    alt = larg * 0.30
    subida = alt * 0.95
    capa = alt * 0.42
    for lado in (-1, 1):
        borda_x = cx + lado * meia
        topo = []
        for i in range(25):
            t = i / 24
            topo.append((cx + lado * meia * t, cy - subida * t**0.75))
        base = []
        for i in range(24, -1, -1):
            t = i / 24
            base.append((cx + lado * meia * t,
                         cy + alt - subida * t**0.75 * 0.55 + alt * 0.10 * (1 - t)))
        d.polygon(topo + base, fill=PAGINA)
        capa_pts = base + [(borda_x, base[0][1] + capa), (cx, cy + alt + capa * 0.85)]
        d.polygon(capa_pts, fill=OURO_ESCURO)
        d.line(base, fill=PAGINA_SOMBRA, width=max(3, int(larg * 0.010)))
    fenda = larg * 0.016
    topo_fenda = cy + alt * 0.55
    d.polygon(
        [(cx - fenda, topo_fenda), (cx + fenda, topo_fenda),
         (cx + fenda * 0.45, cy + alt + capa * 0.45),
         (cx - fenda * 0.45, cy + alt + capa * 0.45)],
        fill=FUNDO_BASE,
    )


def simbolo(tamanho: int) -> Image.Image:
    """Livro+chama num quadrado transparente, para compor no banner."""
    img = Image.new("RGBA", (tamanho, tamanho), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    chama(d, tamanho / 2, tamanho * 0.62, tamanho * 0.34)
    livro(d, tamanho / 2, tamanho * 0.60, tamanho * 0.62)
    return img


def brilho(size: int) -> Image.Image:
    camada = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(camada)
    cx, cy, r = size // 2, int(size * 0.30), int(size * 0.26)
    for i in range(28):
        raio = r * (1 - i / 28)
        d.ellipse([cx - raio, cy - raio * 1.25, cx + raio, cy + raio * 1.25],
                  fill=int(8 + i * 2.2))
    return camada.filter(ImageFilter.GaussianBlur(size // 28))


def gerar_avatar() -> None:
    S = 1600
    img = fundo_gradiente(S, S)
    img.paste(Image.new("RGB", (S, S), OURO), (0, 0), brilho(S))
    d = ImageDraw.Draw(img)
    chama(d, S / 2, S * 0.62, S * 0.34)
    livro(d, S / 2, S * 0.60, S * 0.62)
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, S - 1, S - 1], fill=255)
    img = Image.composite(img, Image.new("RGB", (S, S), (7, 11, 30)), mask)
    ImageDraw.Draw(img).ellipse(
        [S * 0.012, S * 0.012, S * 0.988, S * 0.988],
        outline=OURO, width=int(S * 0.018))
    img.resize((800, 800), Image.LANCZOS).save(AQUI / "avatar.png", "PNG")
    print("OK avatar.png")


def gerar_banner(idioma: str) -> None:
    W, H = 2560, 1440
    nome, tagline = CANAIS[idioma]
    img = fundo_gradiente(W, H)

    # halo dourado suave atrás do conjunto central
    halo = Image.new("L", (W, H), 0)
    dh = ImageDraw.Draw(halo)
    for i in range(30):
        r = 620 * (1 - i / 30)
        dh.ellipse([W / 2 - r * 1.7, H / 2 - r * 0.75,
                    W / 2 + r * 1.7, H / 2 + r * 0.75], fill=int(4 + i * 1.6))
    img.paste(Image.new("RGB", (W, H), OURO), (0, 0),
              halo.filter(ImageFilter.GaussianBlur(60)))

    # área segura: 1546x423 centrada — TODO o conteúdo fica dentro dela
    sx, sy = (W - 1546) / 2, (H - 423) / 2

    simb = simbolo(390)
    d = ImageDraw.Draw(img)

    f_nome = ImageFont.truetype(str(FONTES / "BebasNeue-Regular.ttf"), 168)
    f_tag = ImageFont.truetype(str(FONTES / "Montserrat-Bold.ttf"), 44)

    larg_nome = d.textlength(nome, font=f_nome)
    while larg_nome > 1546 - 420 - 40:  # símbolo + respiro
        f_nome = ImageFont.truetype(str(FONTES / "BebasNeue-Regular.ttf"),
                                    f_nome.size - 8)
        larg_nome = d.textlength(nome, font=f_nome)
    larg_tag = d.textlength(tagline, font=f_tag)

    bloco_w = 420 + max(larg_nome, larg_tag)
    x0 = (W - bloco_w) / 2
    img.paste(simb, (int(x0), int(H / 2 - 195)), simb)

    tx = x0 + 420
    ty = H / 2 - (f_nome.size * 1.02 + 24 + 52) / 2
    d.text((tx, ty), nome, font=f_nome, fill=OURO)
    d.text((tx + 4, ty + f_nome.size * 1.02 + 24), tagline,
           font=f_tag, fill=CINZA)

    img.save(AQUI / f"banner-{idioma}.png", "PNG")
    print(f"OK banner-{idioma}.png (texto dentro da área segura "
          f"{int(sx)},{int(sy)})")


if __name__ == "__main__":
    gerar_avatar()
    for lang in CANAIS:
        gerar_banner(lang)
