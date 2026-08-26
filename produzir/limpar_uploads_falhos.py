"""Lista (e apaga) uploads FALHADOS de um canal + status de vídeo longo.

O caso que motivou (26/08): o Studio da La Noche Estoica mostrava dois
"1 Hour of Stoic Wisdom…" com "Falha no envio: vídeo muito longo" — testes
de longo da era Stoic by Night (julho). A conta não é verificada por
telefone, então o teto de upload é 15 minutos; o rascunho falho fica no
Studio para sempre até alguém apagar.

O script também imprime `status.longUploadsStatus` do canal: enquanto ele
não for `allowed`, ligar o vídeo longo (Passo 4 da monetização, ≈03/09)
só produz falha e queima 1.600 de cota por tentativa. Verificar é humano:
youtube.com/verify logado na conta do canal (SMS).

Só apaga vídeo com uploadStatus in {failed, rejected} — nunca vídeo no ar.
Custo: ~2 + 1/50 vídeos de leitura; 50 por delete. Uso:

    python produzir/limpar_uploads_falhos.py --canal stoic [--apagar]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nucleo.youtube_api import servico  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--canal", default="stoic")
    ap.add_argument("--apagar", action="store_true")
    args = ap.parse_args()

    config = json.loads(
        (RAIZ / "publicador" / "config.json").read_text(encoding="utf-8"))
    canal = config["canais"][args.canal]

    youtube = servico(RAIZ / "credenciais" / args.canal)
    resp = youtube.channels().list(
        part="id,status,contentDetails", mine=True).execute()["items"]
    if len(resp) != 1 or resp[0]["id"] != canal["channel_id"]:
        raise SystemExit("Token não é do canal esperado")
    item = resp[0]

    longos = item["status"].get("longUploadsStatus", "desconhecido")
    print(f"longUploadsStatus: {longos}")
    if longos != "allowed":
        print("⚠ Upload acima de 15 min VAI FALHAR — verificar a conta em "
              "youtube.com/verify antes de ligar o vídeo longo.")

    uploads = item["contentDetails"]["relatedPlaylists"]["uploads"]
    ids: list[str] = []
    pagina = None
    while True:
        r = youtube.playlistItems().list(
            part="contentDetails", playlistId=uploads,
            maxResults=50, pageToken=pagina).execute()
        ids += [i["contentDetails"]["videoId"] for i in r.get("items", [])]
        pagina = r.get("nextPageToken")
        if not pagina:
            break

    # Rascunho falho nem sempre entra na playlist de uploads; o search.list
    # forMine (100 de cota) é o que enxerga o resto do acervo do dono.
    pagina = None
    while True:
        r = youtube.search().list(
            part="id", forMine=True, type="video",
            maxResults=50, pageToken=pagina).execute()
        ids += [i["id"]["videoId"] for i in r.get("items", [])
                if i["id"]["videoId"] not in ids]
        pagina = r.get("nextPageToken")
        if not pagina:
            break
    ids = list(dict.fromkeys(ids))

    falhos = []
    for i in range(0, len(ids), 50):
        r = youtube.videos().list(
            part="status,snippet", id=",".join(ids[i:i + 50])).execute()
        for v in r.get("items", []):
            st = v["status"].get("uploadStatus")
            if st in {"failed", "rejected"}:
                falhos.append(v)

    print(f"{len(ids)} vídeos no canal; {len(falhos)} com upload falho/rejeitado")
    for v in falhos:
        print(f"  {v['id']}  {v['status'].get('uploadStatus')}"
              f"/{v['status'].get('failureReason', v['status'].get('rejectionReason', '?'))}"
              f"  {v['snippet']['title'][:60]}")
        if args.apagar:
            youtube.videos().delete(id=v["id"]).execute()
            print("    apagado.")
    if falhos and not args.apagar:
        print("[dry-run] nada apagado; repita com --apagar.")


if __name__ == "__main__":
    main()
