"""Testa toda consulta de imagem dos poços e mostra quais não acham nada bom.

Consulta sem resultado não quebra o pipeline (o render cai no gradiente da
casa), mas vídeo com imagem real rende mais. Rodar depois de mexer em qualquer
poço de temas e reescrever as consultas reprovadas.

Até 03/09/2026 este script olhava SÓ `conteudo/temas.json`, a linha bíblica —
os poços estoico, poder e astucia nunca passaram por ele, e são justamente os
que já pagaram o erro da foto diurna num canal chamado "La Noche". Auditoria
que cobre parte da operação dá a sensação errada de que o resto está coberto.

Consulta repetida é resolvida UMA vez: os poços reaproveitam muito os mesmos
pares ("night clouds" aparece em dezenas de Shorts), e cada resolução é uma
ida à rede.

    python produzir/auditar_consultas.py
    python produzir/auditar_consultas.py --linha estoico
    python produzir/auditar_consultas.py --tudo      # inclui linha sem canal ativo
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.stdout.reconfigure(encoding="utf-8")

from nucleo import imagens          # noqa: E402
from produzir.reabastecer import LINHAS   # noqa: E402

CONFIG = RAIZ / "publicador" / "config.json"


def temas_da_linha(linha: dict) -> list[dict]:
    if not linha["temas"].exists():
        return []
    dados = json.loads(linha["temas"].read_text(encoding="utf-8"))
    return dados["temas"] if isinstance(dados, dict) else dados


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--linha", choices=sorted(LINHAS),
                    help="Auditar só esta linha (padrão: todas as ativas)")
    ap.add_argument("--tudo", action="store_true",
                    help="Incluir linhas sem canal ativo")
    args = ap.parse_args()

    canais = json.loads(CONFIG.read_text(encoding="utf-8"))["canais"]
    alvos = [args.linha] if args.linha else sorted(LINHAS)

    # (consulta, orientação) -> [slugs que a usam]. Resolver uma vez só.
    usos: dict[tuple[str, str], list[str]] = {}
    for nome in alvos:
        linha = LINHAS[nome]
        ativa = any(canais.get(c, {}).get("ativo") for c in linha["canais"])
        if not ativa and not args.tudo and not args.linha:
            continue
        temas = temas_da_linha(linha)
        if not temas:
            print(f"[{nome}] poço vazio ou ausente; pulando.")
            continue
        for t in temas:
            for q in t["longo"]["consultas_imagens"]:
                usos.setdefault((q, "wide"), []).append(f"{nome}/{t['slug']}")
            for s in t["shorts"]:
                usos.setdefault((s["consulta_imagem"], "tall"), []).append(
                    f"{nome}/{t['slug']}")

    vazias = []
    for (consulta, orient), slugs in sorted(usos.items()):
        achou = imagens.resolver(consulta, 1, 7, orient)
        if not achou:
            vazias.append((consulta, orient, slugs))
        print(f"{'OK   ' if achou else 'VAZIA'} {orient:5} {consulta:30} "
              f"({len(slugs)} tema(s))")

    print(f"\n{len(usos) - len(vazias)}/{len(usos)} consultas distintas com "
          f"imagem boa.")
    if vazias:
        print("\nReescrever estas (substantivos concretos que aparecem em "
              "títulos de fotos do Commons — 'lake sunset', 'forest path'; "
              "nos canais noturnos, pares com night/dark):")
        for consulta, orient, slugs in vazias:
            print(f"  [{orient}] {consulta:30} em {', '.join(slugs[:4])}"
                  f"{' …' if len(slugs) > 4 else ''}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
