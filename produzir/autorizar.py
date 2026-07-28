"""Gera o token.json de um canal — o único passo que precisa de um humano.

O Google não deixa um robô se autorizar sozinho: a tela de consentimento tem
que ser clicada por alguém logado na conta. Este script abre essa tela, recebe
o retorno e grava `credenciais/<canal>/token.json`.

    python produzir/autorizar.py --canal stoic

Antes de gravar, CONFIRMA de qual canal é o token e exige que bata com o
`channel_id` do publicador/config.json. Token do canal errado publica vídeo no
canal errado, e isso já aconteceu nesta operação.

Pré-requisitos no projeto Cloud do canal: YouTube Data API v3 habilitada,
credencial OAuth do tipo "App para computador" salva em
`credenciais/<canal>/client_secret.json`, e o app EM PRODUÇÃO — em modo de
teste o refresh token morre em 7 dias e o canal emudece.
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.stdout.reconfigure(encoding="utf-8")

# Nesta máquina o Python trava em googleapis quando resolve IPv6 (blackhole).
# Forçar IPv4 é local; o runner do Actions não precisa disso.
_getaddrinfo = socket.getaddrinfo
socket.getaddrinfo = (lambda h, p, f=0, t=0, pr=0, fl=0:
                      _getaddrinfo(h, p, socket.AF_INET, t, pr, fl))

from google_auth_oauthlib.flow import InstalledAppFlow  # noqa: E402
from googleapiclient.discovery import build             # noqa: E402

from nucleo import youtube_api                          # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--canal", required=True)
    ap.add_argument("--porta", type=int, default=8765)
    args = ap.parse_args()

    pasta = RAIZ / "credenciais" / args.canal
    segredo = pasta / "client_secret.json"
    if not segredo.exists():
        raise SystemExit(f"Falta {segredo} (baixe a credencial OAuth do "
                         f"projeto Cloud deste canal).")

    cfg = json.loads((RAIZ / "publicador" / "config.json").read_text(
        encoding="utf-8"))
    esperado = cfg.get("canais", {}).get(args.canal, {}).get("channel_id", "")

    flow = InstalledAppFlow.from_client_secrets_file(
        str(segredo), youtube_api.SCOPES)
    print(f"\nAbrindo a tela de consentimento para o canal '{args.canal}'.")
    print("Na tela do Google, ESCOLHA A CONTA/CANAL CERTO e clique em "
          "Permitir.\n")
    creds = flow.run_local_server(port=args.porta, prompt="consent",
                                  access_type="offline",
                                  authorization_prompt_message="Abra: {url}",
                                  success_message="Pronto, pode fechar esta "
                                                  "aba e voltar ao Claude.")

    yt = build("youtube", "v3", credentials=creds, cache_discovery=False)
    cid, titulo = youtube_api.canal_do_token(yt)
    print(f"\nToken autorizado para: {titulo}  ({cid})")

    if esperado and cid != esperado:
        raise SystemExit(
            f"CANAL ERRADO. O config espera {esperado} e o token veio de "
            f"{cid} ({titulo}). Nada foi gravado — rode de novo e escolha o "
            f"canal certo na tela do Google.")
    if not creds.refresh_token:
        raise SystemExit(
            "Vieram credenciais SEM refresh token: elas expiram em uma hora e "
            "o canal emudeceria. Revogue o acesso do app na conta e rode de "
            "novo (o consent precisa vir com prompt=consent).")

    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "token.json").write_text(creds.to_json(), encoding="utf-8")
    print(f"Gravado em {pasta / 'token.json'}")
    if not esperado:
        print(f"\nPonha este channel_id no publicador/config.json: {cid}")


if __name__ == "__main__":
    main()
