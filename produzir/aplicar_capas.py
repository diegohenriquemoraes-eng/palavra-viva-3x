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

from nucleo import fabrica, idiomas, imagens, thumbnail, youtube_api  # noqa: E402

FUNDOS = RAIZ / "marca" / "fundos"

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


def fundo_do(slug: str, idioma: str) -> Path | None:
    """A MESMA foto que o render do longo usaria — não o gradiente.

    Corrigido em 30/07/2026: este script passava `imagem=None` e seed fixa 7,
    então as 31 capas dos 3 canais saíam com o MESMO gradiente roxo e só o texto
    mudando. Isso perde duas coisas de uma vez: a fotografia real (que é a
    receita de CTR do nicho) e a variedade entre vídeos — capa idêntica em série
    é justamente o sinal de conteúdo produzido em massa. A escolha aqui repete
    a de fabrica.montar_longo, seed com idioma incluído.
    """
    escolha = imagens.escolher_da_biblioteca(
        1, fabrica._seed({"slug": slug}, f"fundos-{idioma}"))
    if not escolha:
        return None
    p = FUNDOS / escolha[0]["arquivo"]
    return p if p.exists() else None


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
        try:
            yt = youtube_api.servico(cred)
        except Exception as exc:
            # Token morto de um canal (ex.: EN em invalid_grant) não pode
            # impedir de testar/aplicar capa nos canais saudáveis.
            print(f"[{idioma}] token inválido ({str(exc)[:80]}); pulando.")
            continue
        cfg = idiomas.CONFIG[idioma]
        for p in longos:
            total += 1
            slug = p["pacote"][11:]
            tema = tema_do(slug, temas)
            if not tema:
                continue
            thumbnail.gerar(tmp, fundo_do(slug, idioma),
                            tema["longo"]["thumb_titulo"][idioma],
                            tema["longo"]["thumb_sub"][idioma],
                            f"@{cfg['tags'][0]}",
                            seed=fabrica._seed({"slug": slug},
                                               f"thumb-{idioma}"))
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
