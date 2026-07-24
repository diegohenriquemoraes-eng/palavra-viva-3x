"""Teste controlado de vídeo longo: renderiza ~N minutos e publica NÃO LISTADO.

Serve para responder a única pergunta que trava o crescimento da duração
(ver ALVO_MIN em nucleo/fabrica.py): **um arquivo grande, gerado por render
único, passa pelo upload e pelo processamento do YouTube?** Em 20/07 os longos
de 62 e 26 min falharam — mas aqueles eram feitos por `concat -c copy`, que
gera DTS não monotônico. Render único nunca foi testado nesse tamanho.

Não toca em `publicador/state.json` nem em `fila/`: o vídeo sobe como
`unlisted` e o publicador do dia segue o curso dele. Se o teste passar, sobe-se
ALVO_MIN; se falhar, ficou registrado o motivo com número na mão.

    python produzir/teste_longo.py --alvo-min 60 --render-apenas
    python produzir/teste_longo.py --alvo-min 60 --canal pt
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.stdout.reconfigure(encoding="utf-8")

from nucleo import biblia, fabrica, idiomas, youtube_api  # noqa: E402

SAIDA = RAIZ / "saida"
CONFIG = RAIZ / "publicador" / "config.json"

# Estimativa para ESCOLHER as passagens antes de narrar: a voz longa roda a
# -15%, o que dá ~2,3 palavras/s, e cada versículo ainda leva a pausa
# contemplativa de PAUSA_VERSO. O script imprime o erro dessa estimativa contra
# a duração real medida — é assim que ela melhora.
PALAVRAS_POR_S = 2.3

# Poço do teste: Salmos na ordem. Domínio público nas 3 Bíblias e é o material
# que o nicho de fato usa em vídeo longo ("salmos para dormir").
CANDIDATOS = [f"Psalms {c}" for c in range(1, 51)]


def duracao_estimada(idioma: str, refs: list[str], ciclos: int) -> float:
    total = 0.0
    for ref in refs:
        for _, texto in biblia.carregar_versos(idioma, ref):
            total += len(texto.split()) / PALAVRAS_POR_S + fabrica.PAUSA_VERSO
    return total * ciclos


def escolher_refs(idioma: str, alvo_s: float, ciclos: int) -> list[str]:
    """Salmos na ordem até bater o alvo. Um salmo que estoure o alvo em mais de
    8% é pulado (o 18 tem 50 versos e sozinho joga 12 min a mais) — a próxima
    passagem menor encaixa e a duração fica onde se pediu."""
    refs: list[str] = []
    for ref in CANDIDATOS:
        try:
            if not biblia.carregar_versos(idioma, ref):
                continue
        except Exception:
            continue
        candidato = refs + [ref]
        dur = duracao_estimada(idioma, candidato, ciclos)
        if dur > alvo_s * 1.08 and refs:
            continue
        refs = candidato
        if dur >= alvo_s * 0.95:
            break
    return refs


def montar_pacote(idioma: str, refs: list[str], alvo_min: int) -> dict:
    titulos = {
        "pt": f"Salmos para Dormir — {alvo_min//60}h de Bíblia Narrada com Voz Calma",
        "es": f"Salmos para Dormir — {alvo_min//60}h de Biblia Hablada con Voz Calmada",
        "en": f"Psalms for Sleep — {alvo_min//60}h of Audio Bible with a Calm Voice",
    }
    if alvo_min < 60:
        titulos = {k: v.replace(f"{alvo_min//60}h", f"{alvo_min} min")
                   for k, v in titulos.items()}
    return {
        "slug": f"teste-longo-{alvo_min}",
        "formato": "dormir",
        "longo": {
            "refs": refs,
            "titulo": titulos,
            "thumb_titulo": {"pt": "SALMOS PARA DORMIR",
                             "es": "SALMOS PARA DORMIR",
                             "en": "PSALMS FOR SLEEP"},
            "thumb_sub": {"pt": f"{alvo_min} minutos de Bíblia",
                          "es": f"{alvo_min} minutos de Biblia",
                          "en": f"{alvo_min} minutes of Scripture"},
            "imagens": [],
        },
        "shorts": [],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--alvo-min", type=int, default=60)
    ap.add_argument("--canal", default="pt", choices=list(idiomas.IDIOMAS))
    ap.add_argument("--render-apenas", action="store_true")
    ap.add_argument("--privacidade", default="unlisted",
                    choices=["private", "unlisted", "public"])
    ap.add_argument("--espera-s", type=int, default=3600,
                    help="quanto esperar o processamento do YouTube")
    args = ap.parse_args()

    idioma = args.canal
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    canal_cfg = config["canais"][idioma]
    alvo_s = args.alvo_min * 60

    refs = escolher_refs(idioma, alvo_s, fabrica.CICLOS_DORMIR)
    est = duracao_estimada(idioma, refs, fabrica.CICLOS_DORMIR)
    print(f"[{idioma}] {len(refs)} passagens ({refs[0]}..{refs[-1]}), "
          f"{fabrica.CICLOS_DORMIR} ciclos → estimativa {est/60:.1f} min")

    pacote = montar_pacote(idioma, refs, args.alvo_min)
    outdir = SAIDA / idioma / f"teste-longo-{args.alvo_min}"

    t0 = time.time()
    item = fabrica.montar_longo(pacote, idioma, canal_cfg["handle"], outdir,
                                afiliado=canal_cfg.get("afiliado", ""))
    t_render = time.time() - t0
    arquivo = Path(item["arquivo"])
    mb = arquivo.stat().st_size / 1024 / 1024
    print(f"\nRENDER: {t_render/60:.1f} min | duração {item['duracao_s']/60:.1f} min "
          f"| {mb:.0f} MB | {arquivo}")
    print(f"erro da estimativa: {(est - item['duracao_s'])/60:+.1f} min")

    if args.render_apenas:
        print("--render-apenas: parando antes do upload.")
        return

    cred = RAIZ / "credenciais" / idioma
    youtube = youtube_api.servico(cred)
    canal_id, nome = youtube_api.canal_do_token(youtube)
    if canal_id != canal_cfg["channel_id"]:
        raise SystemExit(f"token é do canal errado: {nome} ({canal_id})")

    t0 = time.time()
    video_id = youtube_api.upload(youtube, arquivo, item["titulo"],
                                  item["descricao"], item["tags"],
                                  idiomas.CONFIG[idioma]["bcp47"],
                                  privacidade=args.privacidade)
    t_upload = time.time() - t0
    print(f"UPLOAD: {t_upload/60:.1f} min → https://youtu.be/{video_id}")

    t0 = time.time()
    info = youtube_api.esperar_processamento(youtube, video_id, args.espera_s)
    t_proc = time.time() - t0
    estado = info.get("processingDetails", {}).get("processingStatus", "?")
    print(f"PROCESSAMENTO: {t_proc/60:.1f} min | status={estado}")

    if item["thumb"]:
        try:
            youtube_api.definir_thumbnail(youtube, video_id, Path(item["thumb"]))
            print("capa aplicada")
        except Exception as exc:
            print(f"capa falhou: {str(exc)[:120]}")

    if item.get("legenda_srt"):
        try:
            youtube_api.enviar_legenda(youtube, video_id,
                                       Path(item["legenda_srt"]),
                                       idiomas.CONFIG[idioma]["bcp47"])
            print("legenda .srt enviada")
        except Exception as exc:
            print(f"legenda falhou: {str(exc)[:120]}")

    print(f"\nRESUMO {args.alvo_min} min: render {t_render/60:.1f} + upload "
          f"{t_upload/60:.1f} + processamento {t_proc/60:.1f} = "
          f"{(t_render+t_upload+t_proc)/60:.1f} min | {mb:.0f} MB | {estado}")
    print(f"O vídeo ficou como {args.privacidade} — conferir e decidir se "
          f"vira padrão (ALVO_MIN em nucleo/fabrica.py).")


if __name__ == "__main__":
    main()
