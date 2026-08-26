"""Aplica a descrição de canal (`bio` em publicador/config.json) via API.

A mudança de oferta de 25/08 (devocional acima do piano) entrou nas descrições
dos vídeos pelo config + realinhar, mas a descrição do CANAL ficou para trás —
ela não passa por nenhum caminho do pipeline. Este script é esse caminho:
channels.update part=brandingSettings, o mesmo usado para a capa em 19/08.

A seção "Links" do canal (os botões clicáveis) NÃO tem API pública; ela só
muda no Studio, à mão.

Custo de quota: 1 (list) + 50 (update). Uso:

    python produzir/atualizar_bio.py --canal es [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nucleo.youtube_api import limpar_texto, servico  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--canal", default="es")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    config = json.loads(
        (RAIZ / "publicador" / "config.json").read_text(encoding="utf-8"))
    canal = config["canais"].get(args.canal)
    if not canal:
        raise SystemExit(f"Canal desconhecido: {args.canal}")
    bio = canal.get("bio")
    if not bio:
        raise SystemExit(f"Canal {args.canal} sem campo 'bio' no config.")
    bio = limpar_texto(bio)

    youtube = servico(RAIZ / "credenciais" / args.canal)

    # mine=True em vez de id=: garante que o token na mão é o do canal pedido.
    itens = youtube.channels().list(
        part="id,brandingSettings", mine=True).execute().get("items", [])
    if len(itens) != 1:
        raise SystemExit("Token não identifica um único canal")
    item = itens[0]
    if item["id"] != canal["channel_id"]:
        raise SystemExit(
            f"Token é do canal {item['id']}, config espera {canal['channel_id']}")

    branding = item["brandingSettings"]
    atual = branding.get("channel", {}).get("description", "")
    print(f"=== descrição atual ({len(atual)} chars) ===\n{atual}\n")
    print(f"=== descrição nova ({len(bio)} chars) ===\n{bio}\n")
    if atual == bio:
        print("Já está no padrão; nada a fazer.")
        return
    if args.dry_run:
        print("[dry-run] nada enviado.")
        return

    # O PUT de brandingSettings apaga o que não for reenviado (trailer,
    # keywords, país): manda o objeto inteiro que veio no GET, só com a
    # descrição trocada. O title volta idêntico — mudar título aqui é recusado.
    branding.setdefault("channel", {})["description"] = bio
    youtube.channels().update(
        part="brandingSettings",
        body={"id": item["id"], "brandingSettings": branding},
    ).execute()
    print("Descrição do canal atualizada.")


if __name__ == "__main__":
    main()
