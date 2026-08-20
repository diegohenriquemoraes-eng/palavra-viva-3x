"""Renderiza uma biblioteca local de Shorts do Palavra Viva (pt) para o TikTok.

Reaproveita EXATAMENTE o mesmo motor de render do canal do YouTube
(nucleo.fabrica.montar_short) — mesmo vídeo, mesma voz, mesma legenda. A
diferença é só a LEGENDA/caption: no TikTok não vai link nenhum (nem clicável
nem em texto), porque link em legenda de TikTok não clica e link na bio exige
limite de seguidores. Cada vídeo sai com um .txt de legenda pronto para colar.

Uso:
    python tiktok/montar_biblioteca_tiktok.py --quantidade 6

Saída: tiktok/biblioteca/NNN-slug-refN/  (video.mp4 + legenda.txt)
       tiktok/biblioteca/fila.json       (ordem de publicação + status)
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

from nucleo import fabrica, idiomas  # noqa: E402

IDIOMA = "pt"
HANDLE = "@palavravivadiaria"   # ajustar ao handle real do TikTok quando decidido
FILA = RAIZ / "fila"
BIB = Path(__file__).parent / "biblioteca"
TMP = Path(__file__).parent / "_tmp_render"


def legenda_tiktok(item: dict) -> str:
    """Legenda de TikTok: SEM link (nem clicável nem em texto)."""
    titulo = item["titulo"]
    ref = item["referencia"]
    hashtags = ("#biblia #versiculododia #palavradedeus #fe #Deus #jesus "
                "#oracao #cristao #gospel #reflexao #fyp #foryou")
    return (
        f"{titulo}\n\n"
        f"📖 {ref} — Bíblia Livre\n\n"
        f"🙏 Uma Palavra de Deus todos os dias. Siga {HANDLE} e ative o sininho.\n\n"
        f"{hashtags}"
    )


def pacotes() -> list[tuple[Path, dict]]:
    out = []
    for p in sorted(FILA.iterdir()):
        if not p.is_dir():
            continue
        meta = p / "pacote.json"
        if meta.exists():
            out.append((p, json.loads(meta.read_text(encoding="utf-8"))))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quantidade", type=int, default=6,
                    help="Quantos Shorts renderizar (round-robin nos pacotes)")
    args = ap.parse_args()

    BIB.mkdir(parents=True, exist_ok=True)
    fila_path = BIB / "fila.json"
    fila = json.loads(fila_path.read_text(encoding="utf-8")) if fila_path.exists() else []
    ja = {f["id"] for f in fila}

    pks = pacotes()
    if not pks:
        raise SystemExit("Sem pacotes em fila/.")

    # round-robin: 1 short de cada pacote por rodada, para variar o tema
    alvos: list[tuple[Path, dict, int]] = []
    max_idx = max(len(pk["shorts"]) for _, pk in pks)
    for idx in range(max_idx):
        for pasta, pk in pks:
            if idx < len(pk["shorts"]):
                alvos.append((pasta, pk, idx))

    feitos = 0
    for pasta, pk, idx in alvos:
        if feitos >= args.quantidade:
            break
        vid_id = f"{pasta.name}-s{idx + 1}"
        if vid_id in ja:
            continue
        destino = BIB / vid_id
        if (destino / "video.mp4").exists():
            continue
        try:
            item = fabrica.montar_short(
                pk, idx, IDIOMA, HANDLE, TMP / vid_id,
                url_longo="", afiliado="")
        except Exception as exc:  # noqa: BLE001
            print(f"[falha] {vid_id}: {exc}", flush=True)
            continue
        destino.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item["arquivo"], destino / "video.mp4")
        (destino / "legenda.txt").write_text(legenda_tiktok(item), encoding="utf-8")
        fila.append({
            "id": vid_id,
            "titulo": item["titulo"],
            "referencia": item["referencia"],
            "arquivo": str((destino / "video.mp4").resolve()),
            "duracao_s": item["duracao_s"],
            "publicado": False,
        })
        ja.add(vid_id)
        feitos += 1
        mb = (destino / "video.mp4").stat().st_size / 1e6
        print(f"[ok] {vid_id}  {item['duracao_s']}s  {mb:.1f}MB  «{item['titulo']}»",
              flush=True)

    fila_path.write_text(json.dumps(fila, ensure_ascii=False, indent=2),
                         encoding="utf-8")
    if TMP.exists():
        shutil.rmtree(TMP, ignore_errors=True)
    print(f"\nBiblioteca: {feitos} novos. Total na fila: {len(fila)}.")
    print(f"Pasta: {BIB}")


if __name__ == "__main__":
    main()
