"""Mede o que os canais LÍDERES do nicho fazem, para modelarmos em cima.

Regra do projeto: decisão de estratégia (título, duração, cadência, formato,
descrição) começa medindo a concorrência — não por raciocínio nem intuição.

Levanta os vídeos mais vistos do nicho por idioma e extrai os padrões que dá
para copiar: duração, formato de título, uso de emoji/números, tamanho da
descrição, quantidade de tags, cadência de publicação dos canais.

Custo de quota: ~100 por busca + 1 por lote de 50 vídeos. Usa as credenciais
do canal EN por padrão (projeto Cloud com mais folga).

    python produzir/benchmark.py
    python produzir/benchmark.py --idioma es --consultas "salmos para dormir"
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.stdout.reconfigure(encoding="utf-8")

from nucleo import youtube_api  # noqa: E402

CRED_PADRAO = Path(r"C:\Users\NOTE\Desktop\Projetos\Corte-em-Pauta\youtube-api")
SAIDA = RAIZ / "conteudo" / "benchmark.json"

CONSULTAS = {
    "es": ["salmos para dormir", "biblia hablada", "versiculos biblicos",
           "salmo 91"],
    "en": ["psalms for sleep", "bible verses", "audio bible", "psalm 91"],
    "pt": ["salmos para dormir", "bíblia narrada", "versículos bíblicos",
           "salmo 91"],
}

DUR = re.compile(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?")


def segundos(iso: str) -> int:
    m = DUR.match(iso or "")
    if not m:
        return 0
    h, mi, s = (int(x) if x else 0 for x in m.groups())
    return h * 3600 + mi * 60 + s


def coletar(yt, consulta: str, idioma: str, n: int = 25) -> list[dict]:
    r = yt.search().list(part="id", q=consulta, type="video",
                         relevanceLanguage=idioma, order="viewCount",
                         maxResults=n, videoDuration="any").execute()
    ids = [i["id"]["videoId"] for i in r.get("items", []) if i["id"].get("videoId")]
    if not ids:
        return []
    det = yt.videos().list(part="snippet,contentDetails,statistics",
                           id=",".join(ids)).execute()
    out = []
    for v in det.get("items", []):
        sn, st = v["snippet"], v.get("statistics", {})
        out.append({
            "id": v["id"],
            "canal": sn["channelTitle"],
            "titulo": sn["title"],
            "dur_s": segundos(v["contentDetails"]["duration"]),
            "views": int(st.get("viewCount", 0)),
            "likes": int(st.get("likeCount", 0)),
            "desc_len": len(sn.get("description", "")),
            "tags": len(sn.get("tags", [])),
            "publicado": sn["publishedAt"][:10],
            "consulta": consulta,
        })
    return out


def padroes(videos: list[dict], rotulo: str) -> None:
    if not videos:
        print(f"\n[{rotulo}] nada coletado")
        return
    longos = [v for v in videos if v["dur_s"] >= 180]
    shorts = [v for v in videos if v["dur_s"] < 180]
    print(f"\n=== {rotulo} — {len(videos)} vídeos ({len(longos)} longos, "
          f"{len(shorts)} curtos) ===")

    if longos:
        d = sorted(v["dur_s"] for v in longos)
        print(f"  duração dos longos (min): mediana {statistics.median(d)/60:.0f} | "
              f"faixa {d[0]/60:.0f}–{d[-1]/60:.0f} | "
              f"25% mais longos acima de {d[int(len(d)*0.75)]/60:.0f}")
    if shorts:
        d = sorted(v["dur_s"] for v in shorts)
        print(f"  duração dos curtos (s): mediana {statistics.median(d):.0f} | "
              f"faixa {d[0]}–{d[-1]}")

    titulos = [v["titulo"] for v in videos]
    com_emoji = sum(1 for t in titulos
                    if any(ord(c) > 0x2600 for c in t))
    com_num = sum(1 for t in titulos if re.search(r"\d", t))
    com_pipe = sum(1 for t in titulos if "|" in t or "—" in t or "-" in t)
    maiuscula = sum(1 for t in titulos
                    if sum(c.isupper() for c in t) > len(t) * 0.5)
    print(f"  títulos: {len(max(titulos, key=len))} chars no maior | "
          f"mediana {statistics.median([len(t) for t in titulos]):.0f}")
    print(f"    com emoji {com_emoji*100//len(titulos)}% | "
          f"com número {com_num*100//len(titulos)}% | "
          f"com separador {com_pipe*100//len(titulos)}% | "
          f"caixa alta {maiuscula*100//len(titulos)}%")

    print(f"  descrição: mediana {statistics.median([v['desc_len'] for v in videos]):.0f} chars")
    print(f"  tags: mediana {statistics.median([v['tags'] for v in videos]):.0f}")

    palavras = Counter()
    for t in titulos:
        for p in re.findall(r"[A-Za-zÁÉÍÓÚÑÜáéíóúñüÃÕÂÊÔÇãõâêôç]{4,}", t.lower()):
            palavras[p] += 1
    print(f"  palavras mais usadas nos títulos: "
          f"{', '.join(p for p, _ in palavras.most_common(12))}")

    print("  campeões de views:")
    for v in sorted(videos, key=lambda x: -x["views"])[:5]:
        print(f"    {v['views']:>12,} | {v['dur_s']//60:>3}min | "
              f"{v['canal'][:22]:22} | {v['titulo'][:60]}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--idioma", choices=["es", "en", "pt"], action="append")
    ap.add_argument("--consultas", nargs="*")
    ap.add_argument("--cred", default=str(CRED_PADRAO))
    args = ap.parse_args()

    yt = youtube_api.servico(Path(args.cred))
    idiomas = args.idioma or ["es", "en", "pt"]
    tudo = {}
    for idioma in idiomas:
        consultas = args.consultas or CONSULTAS[idioma]
        videos = []
        for c in consultas:
            try:
                videos += coletar(yt, c, idioma)
            except Exception as exc:
                print(f"  busca '{c}' falhou: {exc}")
        vistos, unicos = set(), []
        for v in videos:
            if v["id"] not in vistos:
                vistos.add(v["id"])
                unicos.append(v)
        tudo[idioma] = unicos
        padroes(unicos, idioma.upper())

    SAIDA.write_text(json.dumps(tudo, ensure_ascii=False, indent=2),
                     encoding="utf-8")
    print(f"\nDados brutos em {SAIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
