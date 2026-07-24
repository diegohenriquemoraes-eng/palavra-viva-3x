"""Aplica capa personalizada a todos os vídeos longos já publicados.

Só roda quando a conta tiver a verificação de identidade que libera thumbnail
custom (a verificação por telefone deixou de bastar em 2026 — o Google passou
a exigir a verificação por vídeo). Antes disso, a API devolve 403 e este
script relata "ainda bloqueado" sem quebrar nada.

Regenera a thumb a partir do tema do pacote (mesma arte do pipeline) e aplica.

    python produzir/aplicar_capas.py            # aplica onde puder
    python produzir/aplicar_capas.py --teste    # só testa se está liberado
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.stdout.reconfigure(encoding="utf-8")

from nucleo import idiomas, thumbnail, youtube_api  # noqa: E402

STATE = RAIZ / "publicador" / "state.json"
TEMAS = RAIZ / "conteudo" / "temas.json"
# No runner (workflow Aplicar capas) as credenciais vêm dos Secrets para
# credenciais/<idioma>/; no PC do Diego os canais antigos ainda moram nas
# pastas dos repos aposentados. Quem existir primeiro vale — sem isto o script
# simplesmente PULA o canal e imprime "0/0", que parece sucesso e não é.
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


def tema_do(slug: str, temas: list[dict]) -> dict | None:
    return next((t for t in temas if t["slug"] == slug), None)


def bloqueado(exc: Exception) -> bool:
    m = str(exc).lower()
    return "403" in m and "thumbnail" in m


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--teste", action="store_true",
                    help="Só verifica se a capa já está liberada, sem aplicar")
    args = ap.parse_args()

    state = json.loads(STATE.read_text(encoding="utf-8"))
    temas = json.loads(TEMAS.read_text(encoding="utf-8"))
    tmp = RAIZ / "saida" / "capa_tmp.jpg"
    tmp.parent.mkdir(exist_ok=True)

    total = aplicadas = 0
    liberado_em = []
    for idioma, ec in state.get("canais", {}).items():
        cred = CREDS.get(idioma)
        if not cred or not (cred / "token.json").exists():
            continue
        longos = [p for p in ec.get("publicados", []) if p["item"] == "longo"]
        if not longos:
            continue
        yt = youtube_api.servico(cred)
        cfg = idiomas.CONFIG[idioma]
        for p in longos:
            total += 1
            tema = tema_do(p["pacote"][11:], temas)
            if not tema:
                continue
            thumbnail.gerar(tmp, None, tema["longo"]["thumb_titulo"][idioma],
                            tema["longo"]["thumb_sub"][idioma],
                            f"@{cfg['tags'][0]}", seed=7)
            try:
                youtube_api.definir_thumbnail(yt, p["video_id"], tmp)
                aplicadas += 1
                if idioma not in liberado_em:
                    liberado_em.append(idioma)
                print(f"[{idioma}] capa aplicada: {p['video_id']}")
                if args.teste:
                    print("LIBERADO — pare aqui (--teste).")
                    return
            except Exception as exc:
                if bloqueado(exc):
                    print(f"[{idioma}] AINDA BLOQUEADO (verificação de "
                          f"identidade pendente).")
                    return
                print(f"[{idioma}] erro em {p['video_id']}: {str(exc)[:120]}")

    print(f"\n{aplicadas}/{total} capas aplicadas.")
    if aplicadas:
        print("Capa personalizada LIBERADA. 🎉")


if __name__ == "__main__":
    main()
