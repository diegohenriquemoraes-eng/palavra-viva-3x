"""Mede os 3 canais contra a régua do nicho (6–9% de engajamento).

Puxa as estatísticas reais de tudo que o publicador subiu (state.json guarda
o video_id por canal), calcula engajamento por vídeo e agrupa por canal, por
formato (short/longo) e por `tipo` de passagem (conflicto/promesa/descriptivo,
gravado no pacote). Rodar toda semana; formato/tipo consistentemente abaixo
da régua é podado de conteudo/temas.json.

Precisa das credenciais locais em credenciais/{es,en,pt}/ (só os canais que
existirem são medidos). Custo: ~1 unidade por 50 vídeos por canal.

    python produzir/medir_desempenho.py
"""

from __future__ import annotations

import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.stdout.reconfigure(encoding="utf-8")

from nucleo import youtube_api  # noqa: E402

STATE = RAIZ / "publicador" / "state.json"
FILA = RAIZ / "fila"
SAIDA = RAIZ / "conteudo" / "desempenho.json"

REGUA_MIN, REGUA_MAX = 6.0, 9.0


def tipo_do_item(pacote_nome: str, item: str) -> str:
    """'short-2' -> tipo da passagem no pacote.json; 'longo' -> 'longo'."""
    if item == "longo":
        return "longo"
    pj = FILA / pacote_nome / "pacote.json"
    if pj.exists():
        pacote = json.loads(pj.read_text(encoding="utf-8"))
        idx = int(item.split("-")[1]) - 1
        if 0 <= idx < len(pacote["shorts"]):
            return pacote["shorts"][idx].get("tipo") or "?"
    return "?"


def main() -> None:
    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    canais = state.get("canais", {})
    if not canais:
        print("Nada publicado ainda pelos canais.")
        return

    todas = []
    for idioma, ec in canais.items():
        publicados = ec.get("publicados", [])
        if not publicados:
            continue
        cred_dir = RAIZ / "credenciais" / idioma
        if not (cred_dir / "token.json").exists():
            print(f"[{idioma}] sem credenciais locais; pulando {len(publicados)} vídeos.")
            continue
        yt = youtube_api.servico(cred_dir)
        ids = [p["video_id"] for p in publicados]
        stats = {}
        for i in range(0, len(ids), 50):
            for v in yt.videos().list(part="statistics",
                                      id=",".join(ids[i:i + 50])
                                      ).execute().get("items", []):
                stats[v["id"]] = v["statistics"]
        for p in publicados:
            st = stats.get(p["video_id"])
            if not st:
                continue
            vw = int(st.get("viewCount", 0))
            lk = int(st.get("likeCount", 0))
            cm = int(st.get("commentCount", 0))
            eng = round((lk + cm) / vw * 100, 2) if vw else 0.0
            todas.append({
                "canal": idioma,
                "item": p["item"],
                "tipo": tipo_do_item(p["pacote"], p["item"]),
                "titulo": p["titulo"],
                "views": vw, "likes": lk, "comentarios": cm,
                "engajamento": eng,
                "video_id": p["video_id"],
            })

    if not todas:
        print("Nenhum vídeo com estatísticas ainda.")
        return

    todas.sort(key=lambda x: -x["engajamento"])
    SAIDA.write_text(json.dumps(todas, ensure_ascii=False, indent=2),
                     encoding="utf-8")

    print(f"{len(todas)} vídeos medidos (régua do nicho: {REGUA_MIN}–{REGUA_MAX}%)\n")
    print(f"{'canal':5} {'eng%':>6}  {'views':>7}  {'tipo':11} título")
    for l in todas:
        marca = "✓" if l["engajamento"] >= REGUA_MIN else " "
        print(f"{l['canal']:5} {l['engajamento']:>6.2f}{marca} {l['views']:>7,}  "
              f"{l['tipo']:11} {l['titulo'][:40]}")

    for chave in ("canal", "tipo"):
        grupos = defaultdict(list)
        for l in todas:
            if l["views"] >= 50:  # sem amostra não é sinal
                grupos[l[chave]].append(l["engajamento"])
        if not grupos:
            continue
        print(f"\nMediana por {chave}:")
        for g, es in sorted(grupos.items(),
                            key=lambda x: -statistics.median(x[1])):
            print(f"  {g:11} {statistics.median(es):5.2f}%  (n={len(es)})")

    print("\nHistórico em conteudo/desempenho.json. Tipo/formato abaixo da "
          "régua por 2+ semanas → podar de conteudo/temas.json.")


if __name__ == "__main__":
    main()
