"""Retenção e fonte de tráfego por vídeo — o que a Data API não dá.

`medir_desempenho.py` mede o que é público (views, likes, comentários). Isso
responde "quantos vieram", nunca "o que segurou". A moeda do Short é RETENÇÃO:
o YouTube só impulsiona acima de ~70% de view ratio. Sem este número, mexer em
gancho, teto de duração e loop é decidir no escuro.

Usa um token SEPARADO, só de leitura (`credenciais/<canal>/token_analytics.json`,
escopo `yt-analytics.readonly`), gerado por:

    python produzir/autorizar.py --canal es --analytics

O token de publicar não é tocado — se este aqui quebrar, nada para de publicar.

    python produzir/medir_retencao.py
    python produzir/medir_retencao.py --canal pt --dias 60

Pré-requisito no projeto Cloud do canal: **YouTube Analytics API habilitada**.
Se não estiver, o Google devolve 403 SERVICE_DISABLED com o link de ativação —
o script imprime esse link em vez de estourar.
"""

from __future__ import annotations

import argparse
import json
import socket
import statistics
import sys
from datetime import date, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.stdout.reconfigure(encoding="utf-8")

# Mesmo motivo do autorizar.py: nesta máquina o IPv6 para googleapis é buraco
# negro. No runner do Actions isto é inofensivo.
_getaddrinfo = socket.getaddrinfo
socket.getaddrinfo = (lambda h, p, f=0, t=0, pr=0, fl=0:
                      _getaddrinfo(h, p, socket.AF_INET, t, pr, fl))

from google.auth.transport.requests import Request       # noqa: E402
from google.oauth2.credentials import Credentials        # noqa: E402
from googleapiclient.discovery import build              # noqa: E402

ESCOPO = "https://www.googleapis.com/auth/yt-analytics.readonly"
STATE = RAIZ / "publicador" / "state.json"
CONFIG = RAIZ / "publicador" / "config.json"
SAIDA = RAIZ / "conteudo" / "retencao.json"

# A API de Analytics aceita no máximo 200 linhas por consulta de vídeo e é
# paginada por startIndex; 200 cobre folgado o que cada canal publicou.
MAX_LINHAS = 200


def servico(canal: str):
    arq = RAIZ / "credenciais" / canal / "token_analytics.json"
    if not arq.exists():
        return None
    creds = Credentials.from_authorized_user_info(
        json.loads(arq.read_text(encoding="utf-8")), [ESCOPO])
    if not creds.valid and creds.refresh_token:
        creds.refresh(Request())
        arq.write_text(creds.to_json(), encoding="utf-8")
    return build("youtubeAnalytics", "v2", credentials=creds,
                 cache_discovery=False)


def explicar(exc: Exception, canal: str) -> None:
    """403 de API desabilitada é o erro esperado na primeira vez — o que o
    Diego precisa é do LINK, não do stack trace."""
    txt = str(exc)
    if "SERVICE_DISABLED" in txt or "has not been used in project" in txt:
        print(f"[{canal}] a YouTube Analytics API ainda NÃO está habilitada no "
              f"projeto Cloud deste canal.")
        for pedaco in txt.split():
            if "console.developers.google.com" in pedaco or \
               "console.cloud.google.com" in pedaco:
                print(f"        habilitar em: {pedaco.strip('.,)\"')}")
                break
        return
    print(f"[{canal}] falhou: {txt[:200]}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--canal", help="Só este canal (padrão: todos os ativos)")
    ap.add_argument("--dias", type=int, default=90,
                    help="Janela do relatório (padrão 90)")
    args = ap.parse_args()

    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    state = json.loads(STATE.read_text(encoding="utf-8"))
    fim = date.today()
    ini = fim - timedelta(days=args.dias)

    canais = ([args.canal] if args.canal else
              [c for c, d in config["canais"].items() if d.get("ativo")])

    tudo = {}
    for canal in canais:
        yta = servico(canal)
        if yta is None:
            print(f"[{canal}] sem token_analytics.json — rode: "
                  f"python produzir/autorizar.py --canal {canal} --analytics")
            continue
        cid = config["canais"][canal]["channel_id"]
        try:
            r = yta.reports().query(
                ids=f"channel=={cid}",
                startDate=ini.isoformat(), endDate=fim.isoformat(),
                metrics="views,averageViewDuration,averageViewPercentage",
                dimensions="video", sort="-views",
                maxResults=MAX_LINHAS).execute()
        except Exception as exc:
            explicar(exc, canal)
            continue

        # o item do state diz se o vídeo é short ou longo; a API não sabe
        por_id = {p["video_id"]: p for p in
                  state.get("canais", {}).get(canal, {}).get("publicados", [])}
        linhas = []
        for v, views, dur, pct in r.get("rows", []):
            p = por_id.get(v, {})
            linhas.append({
                "video_id": v, "views": views,
                "duracao_media_s": dur, "retencao_pct": round(pct, 1),
                "item": p.get("item", "?"), "titulo": p.get("titulo", ""),
            })
        tudo[canal] = linhas

        shorts = [l for l in linhas if l["item"].startswith("short")]
        longos = [l for l in linhas if l["item"] == "longo"]
        print(f"\n=== {canal} — {len(linhas)} vídeos com dados "
              f"({ini} a {fim}) ===")
        for rot, grupo in (("SHORTS", shorts), ("LONGOS", longos)):
            if not grupo:
                continue
            ret = statistics.median(l["retencao_pct"] for l in grupo)
            seg = statistics.median(l["duracao_media_s"] for l in grupo)
            print(f"  {rot}: n={len(grupo)}  retenção mediana {ret:.1f}%  "
                  f"tempo médio assistido {seg:.0f}s")
        print(f"  {'ret%':>6} {'seg':>5} {'views':>7}  título")
        for l in linhas[:15]:
            print(f"  {l['retencao_pct']:>6.1f} {l['duracao_media_s']:>5.0f} "
                  f"{l['views']:>7,}  {l['titulo'][:44]}")

    if tudo:
        SAIDA.write_text(json.dumps(tudo, ensure_ascii=False, indent=2),
                         encoding="utf-8")
        print(f"\nGravado em {SAIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
