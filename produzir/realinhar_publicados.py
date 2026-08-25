"""Atualiza título, descrição e tags dos vídeos JÁ publicados para o padrão atual.

Os vídeos do primeiro dia saíram antes do benchmark (produzir/benchmark.py):
com emoji no título, 7 tags e sem o bloco de afiliado. Este script regera os
metadados a partir de conteudo/temas.json + publicador/config.json e aplica
via API, sem tocar no vídeo em si.

Custo: 1 unidade por leitura + 50 por vídeo atualizado.

    python produzir/realinhar_publicados.py --dry-run
    python produzir/realinhar_publicados.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.stdout.reconfigure(encoding="utf-8")

from nucleo import biblia, fabrica, idiomas, youtube_api  # noqa: E402

STATE = RAIZ / "publicador" / "state.json"
CONFIG = RAIZ / "publicador" / "config.json"
TEMAS = RAIZ / "conteudo" / "temas.json"

# Caminho de fallback dos canais antigos, quando se roda no PC do Diego. No
# runner (workflow Realinhar) as credenciais vêm dos Secrets para
# credenciais/<idioma>/ — que tem precedência por existir lá.
LEGADO = {
    "es": Path(r"C:\Users\NOTE\Desktop\Projetos\Palabra-Viva\youtube-api"),
    "en": Path(r"C:\Users\NOTE\Desktop\Projetos\Corte-em-Pauta\youtube-api"),
}
CREDS = {
    idioma: (RAIZ / "credenciais" / idioma
             if (RAIZ / "credenciais" / idioma / "token.json").exists()
             else LEGADO.get(idioma, RAIZ / "credenciais" / idioma))
    for idioma in ("es", "en", "pt")
}


def tema_por_slug(temas: list[dict], pacote: str) -> dict | None:
    slug = pacote[11:] if len(pacote) > 11 else ""
    return next((t for t in temas if t["slug"] == slug), None)


def metadados(tema: dict, item: str, idioma: str, canal_cfg: dict) -> dict:
    """Título e descrição no padrão de hoje. Descrição sem capítulos: eles
    dependem da cronometragem do render, que não vamos refazer aqui."""
    cfg = idiomas.CONFIG[idioma]
    afiliado = (canal_cfg.get("afiliado") if item == "longo"
                else canal_cfg.get("afiliado_short")) or ""
    bloco = f"\n\n{afiliado.strip()}" if afiliado.strip() else ""

    # SEO POR TEMA nos vídeos JÁ publicados (15/08/2026). O `fabrica.py` usa
    # `tags_extra` e `descricao_busca` do poço desde 04/08, mas este script
    # continuava reescrevendo tudo com as 16 tags fixas do idioma — ou seja,
    # realinhar um canal APAGAVA o SEO por tema dos longos novos e mantinha os
    # antigos genéricos. Agora os dois caminhos montam os metadados igual.
    tags = list(cfg["tags"])
    busca = ""
    if item == "longo":
        longo = tema["longo"]
        for t in (longo.get("tags_extra") or {}).get(idioma, []):
            if t not in tags and sum(len(x) + 1 for x in tags) + len(t) < 470:
                tags.append(t)
        busca = ((longo.get("descricao_busca") or {}).get(idioma, "") or "").strip()

    if item == "longo":
        titulo = tema["longo"]["titulo"][idioma]
        refs = ", ".join(biblia.ref_exibicao(idioma, r)
                         for r in tema["longo"]["refs"])
        corpo = (f"{titulo}"
                 + (f"\n\n{busca}" if busca else "")
                 + bloco
                 + fabrica.bloco_playlist(idioma, tema.get("formato", "tema"))
                 + f"\n\n{cfg['rotulo_capitulos']} {refs}"
                 f"\n\n{cfg['fonte_texto']}.\n\n{cfg['cta']}\n\n"
                 f"{cfg['hashtags']}")
    else:
        idx = int(item.split("-")[1]) - 1
        short = tema["shorts"][idx]
        titulo = short["titulo"][idioma]
        ref = biblia.ref_exibicao(idioma, short["ref"])
        corpo = (f"{ref} — {cfg['fonte_texto']}.{bloco}\n\n{cfg['cta']}\n\n"
                 f"{cfg['hashtags']} #Shorts")
    return {"titulo": titulo, "descricao": corpo, "tags": tags}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    # Sem --canal ele varre os três; um realinhamento cego gastaria cota (50
    # por vídeo) em canal que não mudou. Ao trocar a oferta de UM canal, passe
    # o idioma dele.
    ap.add_argument("--canal", choices=sorted(CREDS))
    # Cota: 50 por vídeo. O ES tem ~86 Shorts + 27 longos publicados; realinhar
    # tudo custa ~5.650 e estoura o orçamento diário (a publicação já come
    # ~7.200 de 10.000). O SEO por tema só muda o LONGO — nos Shorts o texto é
    # o mesmo. Por isso o padrão passou a ser só os longos em 15/08/2026.
    ap.add_argument("--tudo", action="store_true",
                    help="realinha também os Shorts (cuidado com a cota)")
    # Teto de ATUALIZAÇÕES por execução. O ES tem 38 longos (~1.900 de cota) e
    # a publicação do dia já come ~7.200 dos 10.000 — realinhar tudo numa
    # janela deixaria margem de meio upload, e um retry derrubaria o longo do
    # dia. Com --limite a rodada é fatiada em duas janelas; como o script agora
    # PULA o que já está no padrão, a segunda execução continua de onde parou.
    ap.add_argument("--limite", type=int, default=0,
                    help="máximo de vídeos ATUALIZADOS nesta execução (0 = sem teto)")
    args = ap.parse_args()
    atualizados = 0

    state = json.loads(STATE.read_text(encoding="utf-8"))
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    temas = json.loads(TEMAS.read_text(encoding="utf-8"))

    for idioma, ec in state.get("canais", {}).items():
        if idioma not in CREDS or not ec.get("publicados"):
            continue
        if args.canal and idioma != args.canal:
            continue
        canal_cfg = config["canais"][idioma]
        yt = None if args.dry_run else youtube_api.servico(CREDS[idioma])
        print(f"\n=== {canal_cfg['titulo_canal']} ({idioma}) ===")

        for p in ec["publicados"]:
            if not args.tudo and p["item"] != "longo":
                continue
            if args.limite and atualizados >= args.limite:
                print(f"  limite de {args.limite} atualizações atingido; "
                      f"rode de novo na próxima janela de cota para continuar.")
                break
            tema = tema_por_slug(temas, p["pacote"])
            if not tema:
                print(f"  {p['video_id']}: tema não encontrado; pulando")
                continue
            m = metadados(tema, p["item"], idioma, canal_cfg)
            print(f"  {p['video_id']} [{p['item']}]")
            print(f"    antes: {p['titulo'][:66]}")
            print(f"    novo : {m['titulo'][:66]}")
            if args.dry_run:
                continue

            atual = yt.videos().list(part="snippet", id=p["video_id"]
                                     ).execute().get("items", [])
            if not atual:
                print("    vídeo não existe mais; pulando")
                continue
            sn = atual[0]["snippet"]
            novo = {
                "title": youtube_api.limpar_texto(m["titulo"]),
                "description": youtube_api.limpar_texto(m["descricao"]),
                "tags": m["tags"],
                "defaultLanguage": idiomas.CONFIG[idioma]["bcp47"],
            }
            # Já está no padrão: não gastar as 50 unidades do update. É o que
            # torna a rodada RETOMÁVEL — com --limite, a execução seguinte pula
            # o que já foi feito em vez de refazer os primeiros da lista.
            #
            # ⚠ A API devolve as tags em ordem ALFABÉTICA, não na ordem em que
            # foram enviadas: comparar as listas posição a posição dá sempre
            # "diferente" e o script reescreveria tudo a cada rodada. Tag é
            # conjunto para o YouTube, então é como conjunto que se compara.
            def _igual(campo: str, valor) -> bool:
                if campo == "tags":
                    return (sorted(t.casefold() for t in (sn.get("tags") or []))
                            == sorted(t.casefold() for t in valor))
                return sn.get(campo) == valor

            if all(_igual(k, v) for k, v in novo.items()):
                print("    já está no padrão; pulando")
                continue
            sn.update(novo)
            yt.videos().update(part="snippet",
                               body={"id": p["video_id"], "snippet": sn}
                               ).execute()
            p["titulo"] = m["titulo"]
            atualizados += 1
            print("    atualizado")

    if not args.dry_run:
        STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2),
                         encoding="utf-8")
        print("\nstate.json sincronizado com os títulos novos.")


if __name__ == "__main__":
    main()
