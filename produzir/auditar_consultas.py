"""Testa toda consulta de imagem do poço e mostra quais não acham nada bom.

Consulta sem resultado não quebra o pipeline (o render cai no gradiente da
casa), mas vídeo com imagem real rende mais. Rodar depois de mexer em
conteudo/temas.json e reescrever as consultas reprovadas.

    python produzir/auditar_consultas.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.stdout.reconfigure(encoding="utf-8")

from nucleo import imagens  # noqa: E402

TEMAS = RAIZ / "conteudo" / "temas.json"


def main() -> None:
    temas = json.loads(TEMAS.read_text(encoding="utf-8"))
    vazias, total = [], 0
    for t in temas:
        pares = [(q, "wide") for q in t["longo"]["consultas_imagens"]]
        pares += [(s["consulta_imagem"], "tall") for s in t["shorts"]]
        for consulta, orient in pares:
            total += 1
            achou = imagens.resolver(consulta, 1, 7, orient)
            if not achou:
                vazias.append((t["slug"], consulta))
            print(f"{'OK ' if achou else 'VAZIA'} {t['slug']:20} {consulta}")

    print(f"\n{total - len(vazias)}/{total} consultas com imagem boa.")
    if vazias:
        print("\nReescrever estas (usar substantivos que aparecem em títulos "
              "de fotos do Commons — 'lake sunset', 'forest path'):")
        for slug, q in vazias:
            print(f"  {slug:20} {q}")


if __name__ == "__main__":
    main()
