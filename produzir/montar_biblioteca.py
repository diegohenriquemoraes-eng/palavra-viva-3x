"""Baixa candidatos a fundo e monta folhas de contato para revisão humana.

Por que existe: a busca ao vivo no Commons erra. Mesmo com filtro de licença,
de título e de assunto, um vídeo do Salmo 23 saiu com um navio cargueiro de
fundo (19/07/2026). Num canal devocional a imagem errada destrói o clima —
e identidade visual consistente é justamente o que sustenta um canal dark.

Fluxo:
    python produzir/montar_biblioteca.py --baixar     # candidatos + folhas
    (revisão humana: olhar marca/fundos/_folhas/*.jpg e anotar os índices bons)
    python produzir/montar_biblioteca.py --aprovar 3,7,12,15

Os aprovados viram marca/fundos/NNN.jpg + marca/fundos/creditos.json e são
versionados: a partir daí o render usa a biblioteca, sem depender de rede.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.stdout.reconfigure(encoding="utf-8")

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from nucleo import imagens  # noqa: E402

FUNDOS = RAIZ / "marca" / "fundos"
BRUTO = FUNDOS / "_bruto"
FOLHAS = FUNDOS / "_folhas"
CREDITOS = FUNDOS / "creditos.json"
FONTE = RAIZ / "marca" / "fontes" / "Montserrat-Bold.ttf"

# Consultas escolhidas para o clima do canal: natureza ampla, luz, silêncio.
# Nada de cidade, gente, objeto ou veículo — o fundo é contemplativo.
CONSULTAS = [
    ("starry sky", "noite"), ("milky way", "noite"), ("aurora sky", "noite"),
    ("moon clouds", "noite"), ("forest night", "noite"),
    ("mountain sunrise", "luz"), ("sunrise field", "luz"),
    ("clouds sunlight", "luz"), ("hill sunrise", "luz"),
    ("desert sunrise", "luz"), ("sunrise mist", "luz"),
    ("lake reflection", "agua"), ("river valley", "agua"),
    ("ocean waves", "agua"), ("waterfall forest", "agua"),
    ("lake mountains", "agua"),
    ("meadow flowers", "campo"), ("wheat field", "campo"),
    ("forest path", "campo"), ("green valley", "campo"),
    ("olive trees", "campo"), ("mountain valley", "montanha"),
    ("canyon sunrise", "montanha"), ("snow mountains", "montanha"),
]
POR_CONSULTA = 3
COLS, LINHAS = 5, 4


def baixar() -> None:
    BRUTO.mkdir(parents=True, exist_ok=True)
    FOLHAS.mkdir(parents=True, exist_ok=True)
    catalogo = []
    idx = 0
    for consulta, grupo in CONSULTAS:
        achadas = imagens.resolver(consulta, POR_CONSULTA, 11, "wide")
        for info in achadas:
            destino = BRUTO / f"{idx:03d}.jpg"
            if imagens.baixar(info["url"], destino):
                catalogo.append({"idx": idx, "grupo": grupo,
                                 "consulta": consulta, **info})
                print(f"  {idx:03d} [{grupo}] {consulta}")
                idx += 1
    (BRUTO / "catalogo.json").write_text(
        json.dumps(catalogo, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n{len(catalogo)} candidatos baixados.")
    montar_folhas(catalogo)


def montar_folhas(catalogo: list[dict]) -> None:
    """Folhas de contato numeradas: revisar 20 imagens de uma vez."""
    cel_w, cel_h = 380, 214
    fonte = ImageFont.truetype(str(FONTE), 26)
    por_folha = COLS * LINHAS
    for f in range(0, len(catalogo), por_folha):
        lote = catalogo[f:f + por_folha]
        folha = Image.new("RGB", (COLS * cel_w, LINHAS * cel_h), (18, 18, 24))
        dr = ImageDraw.Draw(folha)
        for i, item in enumerate(lote):
            arq = BRUTO / f"{item['idx']:03d}.jpg"
            if not arq.exists():
                continue
            im = Image.open(arq).convert("RGB")
            razao = max(cel_w / im.width, cel_h / im.height)
            im = im.resize((round(im.width * razao), round(im.height * razao)))
            x = (im.width - cel_w) // 2
            y = (im.height - cel_h) // 2
            im = im.crop((x, y, x + cel_w, y + cel_h))
            px, py = (i % COLS) * cel_w, (i // COLS) * cel_h
            folha.paste(im, (px, py))
            dr.rectangle([px + 4, py + 4, px + 74, py + 40], fill=(0, 0, 0))
            dr.text((px + 12, py + 8), f"{item['idx']:03d}", font=fonte,
                    fill=(255, 220, 130))
        saida = FOLHAS / f"folha{f // por_folha:02d}.jpg"
        folha.save(saida, quality=82)
        print(f"  folha: {saida.name}")


def aprovar(indices: list[int]) -> None:
    catalogo = json.loads((BRUTO / "catalogo.json").read_text(encoding="utf-8"))
    por_idx = {c["idx"]: c for c in catalogo}
    aprovados = []
    for n, i in enumerate(sorted(indices)):
        if i not in por_idx:
            print(f"  ignorado: {i} não está no catálogo")
            continue
        origem = BRUTO / f"{i:03d}.jpg"
        destino = FUNDOS / f"{n:03d}.jpg"
        # padroniza em 1920 de largura: o repo não precisa de 4000px
        im = Image.open(origem).convert("RGB")
        if im.width > 1920:
            im = im.resize((1920, round(im.height * 1920 / im.width)))
        im.save(destino, quality=88)
        item = dict(por_idx[i])
        item["arquivo"] = destino.name
        aprovados.append(item)
    CREDITOS.write_text(json.dumps(aprovados, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    print(f"{len(aprovados)} fundos aprovados em {FUNDOS}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baixar", action="store_true")
    ap.add_argument("--folhas", action="store_true")
    ap.add_argument("--aprovar", help="Índices separados por vírgula")
    ap.add_argument("--limpar", action="store_true",
                    help="Apaga os candidatos brutos depois de aprovar")
    args = ap.parse_args()
    if args.baixar:
        baixar()
    elif args.folhas:
        montar_folhas(json.loads((BRUTO / "catalogo.json").read_text(encoding="utf-8")))
    elif args.aprovar:
        aprovar([int(x) for x in args.aprovar.split(",") if x.strip()])
    elif args.limpar:
        shutil.rmtree(BRUTO, ignore_errors=True)
        shutil.rmtree(FOLHAS, ignore_errors=True)
        print("candidatos brutos removidos")


if __name__ == "__main__":
    main()
