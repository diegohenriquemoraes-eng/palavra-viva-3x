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
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.stdout.reconfigure(encoding="utf-8")

from nucleo import youtube_api  # noqa: E402

STATE = RAIZ / "publicador" / "state.json"
FILA = RAIZ / "fila"
SAIDA = RAIZ / "conteudo" / "desempenho.json"
HISTORICO = RAIZ / "conteudo" / "desempenho_historico.json"

REGUA_MIN, REGUA_MAX = 6.0, 9.0

# A janela de idade que torna a comparação honesta. Vídeo velho acumulou views
# por mais tempo: comparar a mediana de TUDO antes e depois de uma mudança de
# formato só mede quem está no ar há mais tempo. Então a métrica de decisão é
# sempre a mesma coorte — Shorts com 2 a 7 dias de vida — medida toda semana.
# Cada snapshot vira uma linha comparável com a anterior.
IDADE_MIN_D, IDADE_MAX_D = 2, 7

# Quando o pacote de embalagem do Short entrou no ar (gancho de 3s, abertura
# sem preto, fim em loop, teto de 25s e a correção do vídeo 17% mais curto que
# o áudio). Vídeo publicado antes disso é do formato ANTIGO.
CORTE_FORMATO = "2026-07-28"


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


def _idade_dias(em: str) -> float | None:
    """Dias inteiros desde a publicação; None se o registro não tem data."""
    if not em:
        return None
    try:
        pub = datetime.fromisoformat(em)
    except ValueError:
        return None
    if pub.tzinfo is None:
        pub = pub.replace(tzinfo=timezone.utc)
    return round((datetime.now(timezone.utc) - pub).total_seconds() / 86400, 2)


def coorte(todas: list[dict], canal: str) -> list[dict]:
    """Shorts do canal dentro da janela de idade comparável."""
    return [l for l in todas
            if l["canal"] == canal and l["item"].startswith("short")
            and l["idade_d"] is not None
            and IDADE_MIN_D <= l["idade_d"] <= IDADE_MAX_D]


def registrar_snapshot(todas: list[dict]) -> dict:
    """Grava a linha da semana no histórico e devolve o que foi gravado.

    É este arquivo, e não o desempenho.json (que é sempre só a foto de agora),
    que responde à única pergunta que importa depois de mudar o formato: a
    mediana de views da MESMA janela de idade subiu ou não?
    """
    hist = (json.loads(HISTORICO.read_text(encoding="utf-8"))
            if HISTORICO.exists() else [])
    linha = {"data": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
             "janela_idade_d": [IDADE_MIN_D, IDADE_MAX_D], "canais": {}}
    for canal in sorted({l["canal"] for l in todas}):
        c = coorte(todas, canal)
        total = [l for l in todas if l["canal"] == canal]
        linha["canais"][canal] = {
            "shorts_na_janela": len(c),
            "views_medianas": (round(statistics.median(v["views"] for v in c))
                               if c else None),
            "eng_mediano": (round(statistics.median(v["engajamento"]
                                                    for v in c), 2)
                            if c else None),
            "formatos_na_janela": sorted({v["formato"] for v in c}),
            "videos_totais": len(total),
            "views_totais": sum(v["views"] for v in total),
        }
    # a data é a chave: rodar duas vezes no mesmo dia corrige, não duplica
    hist = [h for h in hist if h["data"] != linha["data"]] + [linha]
    hist.sort(key=lambda h: h["data"])
    HISTORICO.write_text(json.dumps(hist, ensure_ascii=False, indent=2),
                         encoding="utf-8")
    return linha


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
        try:
            yt = youtube_api.servico(cred_dir)
        except Exception as exc:
            # Token morto (ex.: invalid_grant) não pode abortar a medição dos
            # outros canais saudáveis — mede o que dá e segue.
            print(f"[{idioma}] token inválido ({str(exc)[:80]}); pulando "
                  f"{len(publicados)} vídeos.")
            continue
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
                "em": p.get("em", ""),
                "idade_d": _idade_dias(p.get("em", "")),
                "formato": ("novo" if p.get("em", "")[:10] >= CORTE_FORMATO
                            else "antigo"),
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

    # ---- a régua de decisão: mesma janela de idade, semana a semana --------
    linha = registrar_snapshot(todas)
    hist = json.loads(HISTORICO.read_text(encoding="utf-8"))
    print(f"\n\nCOORTE COMPARÁVEL — Shorts com {IDADE_MIN_D} a {IDADE_MAX_D} "
          f"dias de vida (é esta a linha que decide, não a média geral):\n")
    print(f"{'data':11} {'canal':5} {'n':>3} {'views med':>10} {'eng%':>6}  formato")
    for h in hist[-8:]:
        for canal, d in sorted(h["canais"].items()):
            if not d["shorts_na_janela"]:
                continue
            print(f"{h['data']:11} {canal:5} {d['shorts_na_janela']:>3} "
                  f"{d['views_medianas']:>10,} {d['eng_mediano']:>6.2f}  "
                  f"{'+'.join(d['formatos_na_janela'])}")
    if len(hist) >= 2:
        ant, at = hist[-2], hist[-1]
        print("\nVariação contra a medição anterior:")
        for canal, d in sorted(at["canais"].items()):
            a = ant["canais"].get(canal, {})
            if not (d["views_medianas"] and a.get("views_medianas")):
                continue
            var = (d["views_medianas"] / a["views_medianas"] - 1) * 100
            print(f"  {canal}: {a['views_medianas']:,} → "
                  f"{d['views_medianas']:,} views medianas ({var:+.0f}%)")
    print("\nFoto de agora em conteudo/desempenho.json; série semanal em "
          "conteudo/desempenho_historico.json. Tipo/formato abaixo da régua "
          "por 2+ semanas → podar de conteudo/temas.json.")


if __name__ == "__main__":
    main()
