"""Confere e preenche as playlists por formato com os longos JÁ publicados.

O publicador adiciona o longo à playlist do formato na hora de publicar, mas
"playlist falhou; seguindo" nunca derrubou publicação — então pode haver longo
fora da lista sem ninguém saber. Este script é a auditoria: para cada canal com
longos, garante que a playlist de cada formato existe, lista o que ela já tem e
insere só o que falta, em ordem cronológica de publicação. Também grava os ids
em publicador/playlists.json — o cache que o render usa para pôr o link da
lista na descrição do longo e o `&list=` na ponte do Short.

Custo de cota: playlists.list ~1/página + playlistItems.list ~1/página +
50 por INSERÇÃO faltante (nada é removido nem atualizado). Rodar de preferência
logo após a virada da cota (07:00 UTC), como o realinhar.

    python produzir/preencher_playlists.py --dry-run
    python produzir/preencher_playlists.py --canal es
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.stdout.reconfigure(encoding="utf-8")

from nucleo import idiomas, playlists, youtube_api  # noqa: E402

STATE = RAIZ / "publicador" / "state.json"
CONFIG = RAIZ / "publicador" / "config.json"
TEMAS = RAIZ / "conteudo" / "temas.json"


def formato_do_pacote(nome: str, config_canal: dict, temas: list[dict]) -> str:
    """Formato (dormir/tema/historia) do pacote pelo nome da pasta.

    Primeiro a fila do canal (o pacote.json guarda o formato); se a pasta já
    não existir, cai no poço pelo slug. Entradas antigas do estado não têm o
    campo `formato` — é daqui que ele sai no backfill.
    """
    fila = RAIZ / config_canal.get("fila", "fila") / nome / "pacote.json"
    if fila.exists():
        return json.loads(fila.read_text(encoding="utf-8")).get("formato", "tema")
    slug = nome[11:] if len(nome) > 11 else ""
    tema = next((t for t in temas if t.get("slug") == slug), None)
    return (tema or {}).get("formato", "tema")


def itens_da_playlist(youtube, playlist_id: str) -> set[str]:
    """videoIds já presentes na playlist (1 unidade por página de 50)."""
    ids: set[str] = set()
    pagina = None
    while True:
        r = youtube.playlistItems().list(
            part="contentDetails", playlistId=playlist_id,
            maxResults=50, pageToken=pagina).execute()
        ids.update(i["contentDetails"]["videoId"] for i in r.get("items", []))
        pagina = r.get("nextPageToken")
        if not pagina:
            break
    return ids


def playlist_existente(youtube, titulo: str) -> str:
    """Como youtube_api.playlist_por_titulo, mas SEM criar (para o dry-run)."""
    pagina = None
    while True:
        r = youtube.playlists().list(part="id,snippet", mine=True,
                                     maxResults=50, pageToken=pagina).execute()
        for pl in r.get("items", []):
            if pl["snippet"]["title"] == titulo:
                return pl["id"]
        pagina = r.get("nextPageToken")
        if not pagina:
            break
    return ""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="Só relatar o que falta; não cria nem insere nada")
    ap.add_argument("--canal", choices=list(idiomas.IDIOMAS),
                    help="Limita a um canal")
    args = ap.parse_args()

    state = json.loads(STATE.read_text(encoding="utf-8"))
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    temas = json.loads(TEMAS.read_text(encoding="utf-8"))
    inseridos_total = 0

    for idioma, ec in state.get("canais", {}).items():
        if args.canal and idioma != args.canal:
            continue
        canal_cfg = config["canais"].get(idioma)
        longos = [p for p in ec.get("publicados", []) if p["item"] == "longo"]
        if not canal_cfg or not longos:
            continue
        cred = RAIZ / "credenciais" / idioma
        if not (cred / "token.json").exists():
            print(f"[{idioma}] sem credenciais; pulando.")
            continue

        youtube = youtube_api.servico(cred)
        cid, ctitulo = youtube_api.canal_do_token(youtube)
        if cid != canal_cfg["channel_id"]:
            raise SystemExit(f"[{idioma}] token é do canal {cid} ({ctitulo}); "
                             f"esperado {canal_cfg['channel_id']}")
        print(f"\n=== {ctitulo} ({idioma}) — {len(longos)} longos ===")

        # agrupa por formato preservando a ordem de publicação
        por_formato: dict[str, list[dict]] = {}
        for p in longos:
            f = p.get("formato") or formato_do_pacote(p["pacote"], canal_cfg,
                                                      temas)
            por_formato.setdefault(f, []).append(p)

        for formato, videos in por_formato.items():
            titulo_pl = idiomas.PLAYLISTS.get(formato, {}).get(idioma)
            if not titulo_pl:
                print(f"  [{formato}] sem nome de playlist definido; "
                      f"{len(videos)} longos ficam de fora.")
                continue
            if args.dry_run:
                pl = playlist_existente(youtube, titulo_pl)
                if not pl:
                    print(f"  [{formato}] playlist '{titulo_pl}' NÃO existe; "
                          f"criaria e inseriria {len(videos)} longos "
                          f"(~{50 + 50 * len(videos)} de cota).")
                    continue
            else:
                pl = youtube_api.playlist_por_titulo(
                    youtube, titulo_pl, idiomas.CONFIG[idioma]["cta"])
                playlists.definir(idioma, formato, pl)
            presentes = itens_da_playlist(youtube, pl)
            faltam = [v for v in videos if v["video_id"] not in presentes]
            print(f"  [{formato}] '{titulo_pl}': {len(presentes)} na lista, "
                  f"{len(faltam)} faltando de {len(videos)} no estado.")
            for v in faltam:
                if args.dry_run:
                    print(f"    faltaria inserir {v['video_id']} — "
                          f"{v['titulo'][:60]}")
                    continue
                try:
                    youtube_api.adicionar_na_playlist(youtube, pl,
                                                      v["video_id"])
                    inseridos_total += 1
                    print(f"    inserido {v['video_id']} — {v['titulo'][:60]}")
                except Exception as exc:
                    # vídeo apagado/privado não pode travar o resto
                    print(f"    FALHOU {v['video_id']}: {str(exc)[:100]}")

    if not args.dry_run:
        print(f"\n{inseridos_total} inserções "
              f"(~{50 * inseridos_total} de cota). Cache em "
              f"{playlists.ARQUIVO.relative_to(RAIZ)}.")


if __name__ == "__main__":
    main()
