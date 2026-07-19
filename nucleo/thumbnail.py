"""Thumbnail dos vídeos longos (Shorts não usam thumbnail no feed).

Receita de CTR do nicho: fundo fotográfico escurecido à esquerda, título
GRANDE em Bebas Neue dourado (3-5 palavras), subtítulo curto em Montserrat,
marca discreta embaixo. 1280x720, JPG < 2 MB (limite do YouTube).
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

from . import idiomas

OURO = (242, 200, 121)
BRANCO = (245, 243, 238)
CINZA = (200, 192, 176)


def _fonte(nome: str, tamanho: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(idiomas.FONTES_DIR / nome), tamanho)


def _cobrir(img: Image.Image, w: int, h: int) -> Image.Image:
    razao = max(w / img.width, h / img.height)
    img = img.resize((round(img.width * razao), round(img.height * razao)))
    x = (img.width - w) // 2
    y = (img.height - h) // 2
    return img.crop((x, y, x + w, y + h))


def gerar(destino: Path, imagem: Path | None, titulo: str, subtitulo: str,
          marca: str, seed: int = 0) -> Path:
    W, H = 1280, 720
    if imagem is not None and imagem.exists():
        base = _cobrir(Image.open(imagem).convert("RGB"), W, H)
        base = ImageEnhance.Brightness(base).enhance(0.75)
    else:
        from . import imagens as _imgs
        tmp = destino.with_suffix(".fundo.jpg")
        _imgs.gerar_gradiente(tmp, W, H, seed)
        base = Image.open(tmp).convert("RGB")
        tmp.unlink(missing_ok=True)

    # véu escuro que cresce para a esquerda: o texto sempre legível
    veu = Image.new("L", (W, H), 0)
    dv = ImageDraw.Draw(veu)
    for x in range(W):
        alpha = int(200 * max(0.0, 1.0 - x / (W * 0.72)))
        dv.line([(x, 0), (x, H)], fill=alpha)
    base = Image.composite(Image.new("RGB", (W, H), (8, 10, 22)), base, veu)

    dr = ImageDraw.Draw(base)

    # título em até 2 linhas, autoajuste do corpo
    linhas = _quebrar(titulo.upper(), 14)
    corpo = 150 if max(len(li) for li in linhas) <= 11 else 118
    if len(linhas) > 2:
        linhas = linhas[:2]
    f_tit = _fonte("BebasNeue-Regular.ttf", corpo)
    y = 150 if len(linhas) > 1 else 210
    for li in linhas:
        dr.text((64, y), li, font=f_tit, fill=OURO,
                stroke_width=4, stroke_fill=(10, 8, 4))
        y += corpo + 8

    f_sub = _fonte("Montserrat-Bold.ttf", 46)
    dr.text((68, y + 18), subtitulo, font=f_sub, fill=BRANCO,
            stroke_width=2, stroke_fill=(10, 8, 4))

    f_marca = _fonte("Montserrat-Bold.ttf", 30)
    dr.text((68, H - 74), marca, font=f_marca, fill=CINZA)

    base.save(destino, quality=88)
    if destino.stat().st_size > 2_000_000:
        base.save(destino, quality=76)
    return destino


def _quebrar(texto: str, largura: int) -> list[str]:
    palavras = texto.split()
    linhas, atual = [], ""
    for p in palavras:
        cand = f"{atual} {p}".strip()
        if len(cand) > largura and atual:
            linhas.append(atual)
            atual = p
        else:
            atual = cand
    if atual:
        linhas.append(atual)
    return linhas
