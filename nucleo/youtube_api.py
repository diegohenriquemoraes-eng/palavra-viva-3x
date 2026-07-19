"""Upload e publicação na YouTube Data API — multi-canal.

Cada canal (es/en/pt) tem projeto Google Cloud PRÓPRIO (para não dividir a
quota de 10.000/dia) e credenciais em credenciais/{idioma}/. Escopo
youtube.force-ssl. Custos de quota: upload 1600, thumbnail 50, update 50.
"""

from __future__ import annotations

import json
import random
import time
from pathlib import Path

import httplib2
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
RETRIABLE = {500, 502, 503, 504}


def credenciais(pasta: Path) -> Credentials:
    token = pasta / "token.json"
    if not token.exists():
        raise SystemExit(f"token.json ausente em {pasta}")
    # utf-8-sig: o caminho PowerShell -> gh secret pode enfiar BOM no JSON
    info = json.loads(token.read_text(encoding="utf-8-sig"))
    creds = Credentials.from_authorized_user_info(info, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token.write_text(creds.to_json(), encoding="utf-8")
    if not creds.valid:
        raise SystemExit(f"Token inválido em {pasta}; reautorizar localmente.")
    return creds


def servico(pasta_cred: Path):
    return build("youtube", "v3", credentials=credenciais(pasta_cred),
                 cache_discovery=False)


def canal_do_token(youtube) -> tuple[str, str]:
    itens = youtube.channels().list(part="id,snippet", mine=True
                                    ).execute().get("items", [])
    if len(itens) != 1:
        raise SystemExit("Token não identifica um único canal")
    return itens[0]["id"], itens[0]["snippet"]["title"]


def upload(youtube, arquivo: Path, titulo: str, descricao: str,
           tags: list[str], idioma_bcp47: str, categoria: str = "22",
           privacidade: str = "private") -> str:
    if len(titulo) > 100:
        raise SystemExit(f"Título com {len(titulo)} caracteres (máx. 100)")
    body = {
        "snippet": {
            "title": titulo,
            "description": descricao,
            "categoryId": categoria,
            "tags": tags,
            "defaultLanguage": idioma_bcp47,
            "defaultAudioLanguage": idioma_bcp47,
        },
        "status": {
            "privacyStatus": privacidade,
            "selfDeclaredMadeForKids": False,
            "embeddable": True,
            "publicStatsViewable": True,
        },
    }
    media = MediaFileUpload(str(arquivo), chunksize=8 * 1024 * 1024,
                            resumable=True)
    req = youtube.videos().insert(part="snippet,status", body=body,
                                  media_body=media)
    resposta = None
    tentativa = 0
    while resposta is None:
        try:
            progresso, resposta = req.next_chunk()
            if progresso:
                print(f"  upload: {progresso.progress() * 100:.0f}%", flush=True)
        except HttpError as exc:
            if exc.resp.status not in RETRIABLE:
                raise
            tentativa += 1
            if tentativa > 8:
                raise
            espera = min(64, 2 ** tentativa) + random.random()
            print(f"  erro {exc.resp.status}; retry em {espera:.0f}s", flush=True)
            time.sleep(espera)
        except (OSError, httplib2.HttpLib2Error) as exc:
            tentativa += 1
            if tentativa > 8:
                raise
            espera = min(64, 2 ** tentativa) + random.random()
            print(f"  falha de rede; retry em {espera:.0f}s: {exc}", flush=True)
            time.sleep(espera)
    return resposta["id"]


def esperar_processamento(youtube, video_id: str, limite_s: int) -> dict:
    fim = time.time() + limite_s
    while True:
        item = youtube.videos().list(part="status,processingDetails",
                                     id=video_id).execute()["items"][0]
        st = item.get("processingDetails", {}).get("processingStatus", "unknown")
        if st == "succeeded":
            return item
        if st in {"failed", "terminated"}:
            raise SystemExit(f"Processamento falhou: {st}")
        if time.time() >= fim:
            raise SystemExit("Tempo esgotado no processamento; vídeo ficou privado")
        time.sleep(15)


def tornar_publico(youtube, video_id: str, item: dict) -> None:
    status = dict(item["status"])
    status["privacyStatus"] = "public"
    status["selfDeclaredMadeForKids"] = False
    youtube.videos().update(part="status",
                            body={"id": video_id, "status": status}).execute()


def definir_thumbnail(youtube, video_id: str, thumb: Path) -> None:
    youtube.thumbnails().set(
        videoId=video_id,
        media_body=MediaFileUpload(str(thumb), mimetype="image/jpeg"),
    ).execute()
