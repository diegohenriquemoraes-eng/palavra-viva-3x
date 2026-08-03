"""Identidade dos canais El Poder Crudo e Astucia Fría (criados em 03/08/2026).

Os dois nascem na MESMA conta de canais que já existem, e é justamente por
isso que precisam ser visualmente distantes uns dos outros: várias marcas
parecidas na mesma conta é o rastro de fábrica que a política de conteúdo
inautêntico procura. Então nada de repetir a coluna e a lua da Noche Estoica
nem o livro e a chama do Palavra Viva.

- **El Poder Crudo**: coroa de ferro sobre preto tinto. Paleta seca — carvão,
  sangue apagado, osso. Sem brilho, sem dourado de realeza: o canal fala de
  poder como custo, não como luxo.
- **Astucia Fría**: um olho, porque o assunto é ler gente. Paleta fria de
  aço e gelo, oposta à do Poder de propósito — quem vir os dois no feed não
  deve pensar que é o mesmo canal.

Ambos testados no tamanho que importa: 32px, que é o avatar no celular.

Gera:
- marca/poder-avatar.png, marca/poder-banner.png
- marca/astucia-avatar.png, marca/astucia-banner.png

    python marca/gerar_marca_es2.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.stdout.reconfigure(encoding="utf-8")

AQUI = Path(__file__).resolve().parent
FONTES = AQUI / "fontes"

# área segura do banner: só ela aparece no celular e na TV
SEGURA_W, SEGURA_H = 1546, 423

MARCAS = {
    "poder": {
        "fundo_a": (10, 8, 9),        # carvão
        "fundo_b": (46, 14, 16),      # sangue apagado
        "tinta": (222, 216, 208),     # osso
        "realce": (150, 46, 40),      # tinto
        "apoio": (128, 124, 120),
        "wordmark": "EL PODER CRUDO",
        "sub": "MAQUIAVELO · UN PASAJE CADA DÍA",
    },
    "astucia": {
        "fundo_a": (8, 10, 13),       # quase preto
        "fundo_b": (22, 34, 46),      # aço frio
        "tinta": (226, 234, 240),     # gelo
        "realce": (108, 168, 196),    # azul frio
        "apoio": (126, 138, 148),
        "wordmark": "ASTUCIA FRÍA",
        "sub": "GRACIÁN · UN AFORISMO CADA DÍA",
    },
}


def fundo(w: int, h: int, a: tuple, b: tuple) -> Image.Image:
    """Gradiente diagonal suave. Linha a linha e depois resize: gradiente por
    pixel num banner de 2560x1440 leva minutos e não melhora nada."""
    img = Image.new("RGB", (1, h))
    px = img.load()
    for y in range(h):
        t = (y / max(h - 1, 1)) ** 0.85
        px[0, y] = tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))
    return img.resize((w, h))


def coroa(d: ImageDraw.ImageDraw, cx: int, cy: int, r: int, cor, realce) -> None:
    """Coroa de ferro: 5 pontas retas e um aro grosso. Reta e sem serrilha
    porque em 32px qualquer detalhe vira sujeira."""
    larg = int(r * 1.7)
    alt = int(r * 1.15)
    x0, x1 = cx - larg // 2, cx + larg // 2
    base = cy + alt // 2
    topo = cy - alt // 2
    pontas = 5
    passo = (x1 - x0) / (pontas - 1)
    pts = [(x0, base)]
    for i in range(pontas):
        x = x0 + passo * i
        # ponta central mais alta: dá eixo e leitura imediata
        h = alt if i == pontas // 2 else int(alt * 0.62)
        if i:
            pts.append((x - passo / 2, base - int(alt * 0.18)))
        pts.append((x, topo + (alt - h)))
    pts.append((x1, base))
    d.polygon(pts, fill=cor)
    aro = int(r * 0.30)
    d.rectangle([x0, base, x1, base + aro], fill=cor)
    # fio de tinto no aro: a única cor da peça
    d.rectangle([x0, base + aro - max(2, aro // 6), x1, base + aro],
                fill=realce)


def olho(d: ImageDraw.ImageDraw, cx: int, cy: int, r: int, cor, realce,
         apoio) -> None:
    """Olho: duas curvas e uma íris. Símbolo de 'ler a gente'."""
    larg, alt = int(r * 1.9), int(r * 1.05)
    caixa = [cx - larg // 2, cy - alt // 2, cx + larg // 2, cy + alt // 2]
    grosso = max(3, r // 12)
    d.arc(caixa, start=200, end=340, fill=cor, width=grosso)
    d.arc(caixa, start=20, end=160, fill=cor, width=grosso)
    ri = int(r * 0.34)
    d.ellipse([cx - ri, cy - ri, cx + ri, cy + ri], outline=cor, width=grosso)
    rp = int(ri * 0.46)
    d.ellipse([cx - rp, cy - rp, cx + rp, cy + rp], fill=realce)
    # brilho deslocado: o olho fica "olhando de lado", que é o tom do canal
    rb = max(2, int(rp * 0.42))
    d.ellipse([cx + rp // 3, cy - rp, cx + rp // 3 + rb, cy - rp + rb],
              fill=apoio)


def desenhar_simbolo(img: Image.Image, canal: str, cx: int, cy: int,
                     r: int) -> None:
    m = MARCAS[canal]
    # halo: separa o símbolo do fundo sem precisar de contorno
    halo = Image.new("RGB", img.size, (0, 0, 0))
    dh = ImageDraw.Draw(halo)
    dh.ellipse([cx - r * 2, cy - r * 2, cx + r * 2, cy + r * 2],
               fill=tuple(min(255, c + 26) for c in m["fundo_b"]))
    halo = halo.filter(ImageFilter.GaussianBlur(r // 2))
    img.paste(Image.blend(img, halo, 0.55), (0, 0))
    d = ImageDraw.Draw(img)
    if canal == "poder":
        coroa(d, cx, cy, r, m["tinta"], m["realce"])
    else:
        olho(d, cx, cy, r, m["tinta"], m["realce"], m["apoio"])


def fonte(nome: str, tam: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTES / nome), tam)


def cabe(texto: str, arquivo: str, largura: int, tam_max: int) -> ImageFont.FreeTypeFont:
    """Maior corpo que ainda cabe na largura pedida. Sem isto o wordmark
    estoura a área segura de 1546px e o texto sai cortado no celular — foi o
    que aconteceu no banner do Living Word Daily."""
    for tam in range(tam_max, 20, -2):
        f = fonte(arquivo, tam)
        if f.getbbox(texto)[2] <= largura:
            return f
    return fonte(arquivo, 20)


def gerar_avatar(canal: str) -> Path:
    m = MARCAS[canal]
    L = 800
    img = fundo(L, L, m["fundo_a"], m["fundo_b"])
    desenhar_simbolo(img, canal, L // 2, L // 2, int(L * 0.21))
    alvo = AQUI / f"{canal}-avatar.png"
    img.save(alvo)
    # a prova que importa: o avatar no celular tem 32px
    img.resize((32, 32), Image.LANCZOS).save(AQUI / f"{canal}-avatar-32.png")
    return alvo


def gerar_banner(canal: str) -> Path:
    m = MARCAS[canal]
    W, H = 2560, 1440
    img = fundo(W, H, m["fundo_a"], m["fundo_b"])
    cx, cy = W // 2, H // 2
    sx = cx - SEGURA_W // 2

    desenhar_simbolo(img, canal, sx + 150, cy, 96)

    d = ImageDraw.Draw(img)
    tx = sx + 300
    largura_texto = SEGURA_W - 320
    f_word = cabe(m["wordmark"], "BebasNeue-Regular.ttf", largura_texto, 210)
    f_sub = cabe(m["sub"], "Montserrat-Bold.ttf", largura_texto, 46)

    bw = f_word.getbbox(m["wordmark"])
    d.text((tx, cy - (bw[3] - bw[1]) - 26), m["wordmark"], font=f_word,
           fill=m["tinta"])
    d.rectangle([tx, cy + 6, tx + largura_texto * 0.42, cy + 12],
                fill=m["realce"])
    d.text((tx, cy + 44), m["sub"], font=f_sub, fill=m["apoio"])

    alvo = AQUI / f"{canal}-banner.png"
    img.save(alvo)
    return alvo


def main() -> None:
    for canal in MARCAS:
        a = gerar_avatar(canal)
        b = gerar_banner(canal)
        print(f"{canal}: {a.name} + {b.name}")


if __name__ == "__main__":
    main()
