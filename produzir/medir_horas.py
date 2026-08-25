"""Horas de exibição por canal e por fonte de tráfego — a régua do projeto.

Views e inscritos são o placar visível; **hora de exibição é o que decide a
monetização**, e só o vídeo LONGO produz hora contável (Short não conta para as
4.000 h do YPP). Este script mede exatamente isso, na mesma janela de 60 dias
da linha de base gravada em conteudo/baseline_funil_horas.json (25/08/2026),
para que a comparação seja de igual para igual.

Grava a série em conteudo/horas_historico.json e imprime o veredito contra a
linha de base: quanto as horas contáveis subiram e quanto a playlist passou a
pesar. A régua combinada com o Diego é **25/11/2026**: se as horas contáveis do
ES não tiverem dobrado (de ~1.100 para ~2.200 h/ano), o teste de 2 longos/dia
fracassou e o projeto volta para 1 longo/dia, sem mais investimento.

    python produzir/medir_horas.py
    python produzir/medir_horas.py --dias 60 --canal es
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.stdout.reconfigure(encoding="utf-8")

from produzir.medir_retencao import explicar, servico  # noqa: E402

CONFIG = RAIZ / "publicador" / "config.json"
BASELINE = RAIZ / "conteudo" / "baseline_funil_horas.json"
SAIDA = RAIZ / "conteudo" / "horas_historico.json"

# A Analytics fecha o dia com ~48 h de atraso; medir até ontem devolve um dia
# pela metade e faz a série parecer que caiu.
ATRASO_DIAS = 2


def medir(canal: str, cid: str, dias: int) -> dict | None:
    yta = servico(canal)
    if yta is None:
        print(f"[{canal}] sem token_analytics.json — rode: "
              f"python produzir/autorizar.py --canal {canal} --analytics")
        return None
    fim = date.today() - timedelta(days=ATRASO_DIAS)
    ini = fim - timedelta(days=dias - 1)
    try:
        r = yta.reports().query(
            ids=f"channel=={cid}", startDate=ini.isoformat(),
            endDate=fim.isoformat(), dimensions="insightTrafficSourceType",
            metrics="views,estimatedMinutesWatched").execute()
    except Exception as exc:
        explicar(exc, canal)
        return None

    fontes = {f: {"views": v, "horas": round(m / 60, 1)}
              for f, v, m in r.get("rows", [])}
    total = round(sum(x["horas"] for x in fontes.values()), 1)
    shorts = fontes.get("SHORTS", {}).get("horas", 0)
    # O que conta para o YPP é tudo MENOS o feed de Shorts.
    contaveis = round(total - shorts, 1)
    return {
        "janela": [ini.isoformat(), fim.isoformat()],
        "fontes": fontes,
        "horas_total": total,
        "horas_contaveis": contaveis,
        "horas_ano_projetadas": round(contaveis / dias * 365),
        "playlist_pct_horas": round(
            100 * fontes.get("PLAYLIST", {}).get("horas", 0) / total, 2)
        if total else 0.0,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dias", type=int, default=60,
                    help="Janela (padrão 60, a mesma da linha de base)")
    ap.add_argument("--canal")
    args = ap.parse_args()

    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    base = (json.loads(BASELINE.read_text(encoding="utf-8"))
            if BASELINE.exists() else {"canais": {}})
    canais = ([args.canal] if args.canal else
              [c for c, d in config["canais"].items() if d.get("ativo")])

    hoje = {}
    for canal in canais:
        cid = config["canais"][canal].get("channel_id")
        if not cid:
            continue
        m = medir(canal, cid, args.dias)
        if not m:
            continue
        hoje[canal] = m
        b = base.get("canais", {}).get(canal)
        print(f"\n=== {canal} ({m['janela'][0]} a {m['janela'][1]}) ===")
        print(f"  horas contáveis: {m['horas_contaveis']} "
              f"(→ {m['horas_ano_projetadas']} h/ano de 4.000)")
        print(f"  playlist: {m['playlist_pct_horas']}% das horas")
        if b:
            delta = m["horas_contaveis"] - b["horas_contaveis_60d"]
            pct = 100 * delta / b["horas_contaveis_60d"] if b["horas_contaveis_60d"] else 0
            print(f"  vs. linha de base ({b['horas_contaveis_60d']} h): "
                  f"{delta:+.1f} h ({pct:+.1f}%)")
            print(f"  playlist na base: {b['playlist_pct_horas']}%")

    if not hoje:
        return
    serie = json.loads(SAIDA.read_text(encoding="utf-8")) if SAIDA.exists() else []
    serie.append({"medido_em": date.today().isoformat(), "dias": args.dias,
                  "canais": hoje})
    SAIDA.write_text(json.dumps(serie, ensure_ascii=False, indent=2) + "\n",
                     encoding="utf-8")
    print(f"\nSérie em {SAIDA.relative_to(RAIZ).as_posix()} "
          f"({len(serie)} medições).")


if __name__ == "__main__":
    main()
