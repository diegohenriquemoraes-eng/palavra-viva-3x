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

from nucleo import biblia, idiomas, youtube_api  # noqa: E402

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

    if item == "longo":
        titulo = tema["longo"]["titulo"][idioma]
        refs = ", ".join(biblia.ref_exibicao(idioma, r)
                         for r in tema["longo"]["refs"])
        corpo = (f"{titulo}\n\n{cfg['rotulo_capitulos']} {refs}"
                 f"{bloco}\n\n{cfg['fonte_texto']}.\n\n{cfg['cta']}\n\n"
                 f"{cfg['hashtags']}")
    else:
        idx = int(item.split("-")[1]) - 1
        short = tema["shorts"][idx]
        titulo = short["titulo"][idioma]
        ref = biblia.ref_exibicao(idioma, short["ref"])
        corpo = (f"{ref} — {cfg['fonte_texto']}.{bloco}\n\n{cfg['cta']}\n\n"
                 f"{cfg['hashtags']} #Shorts")
    return {"titulo": titulo, "descricao": corpo, "tags": cfg["tags"]}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    # Sem --canal ele varre os três; um realinhamento cego gastaria cota (50
    # por vídeo) em canal que não mudou. Ao trocar a oferta de UM canal, passe
    # o idioma dele.
    ap.add_argument("--canal", choices=sorted(CREDS))
    args = ap.parse_args()

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
            sn["title"] = youtube_api.limpar_texto(m["titulo"])
            sn["description"] = youtube_api.limpar_texto(m["descricao"])
            sn["tags"] = m["tags"]
            sn["defaultLanguage"] = idiomas.CONFIG[idioma]["bcp47"]
            yt.videos().update(part="snippet",
                               body={"id": p["video_id"], "snippet": sn}
                               ).execute()
            p["titulo"] = m["titulo"]
            print("    atualizado")

    if not args.dry_run:
        STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2),
                         encoding="utf-8")
        print("\nstate.json sincronizado com os títulos novos.")


if __name__ == "__main__":
    main()
