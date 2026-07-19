"""Publicador multi-canal — roda no GitHub Actions de hora em hora.

Para cada canal ativo (es/en/pt) decide o que está devido NESTA hora:
- vídeo longo: 1 por dia, a partir de hora_longo_utc;
- Shorts: até shorts_por_dia por dia UTC, com gap mínimo entre eles.
No máximo 1 publicação por canal por execução (espalha carga e quota).

O render acontece AQUI, na hora de publicar (a fila só tem metadados leves).
Cota por canal/dia: 4 Shorts + 1 longo = 5 uploads x1600 + thumbnail 50
= ~8.050 de 10.000 — margem para um retry.

Lições herdadas (pagas caro nos outros canais):
- cron horário + janela no estado, nunca cron esparso (disparo do GitHub atrasa);
- state.json versionado: o runner é descartado, sem commit republicaria;
- validar o channel_id do token antes de qualquer upload.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.stdout.reconfigure(encoding="utf-8")

from nucleo import fabrica, idiomas, youtube_api  # noqa: E402

CONFIG = Path(__file__).parent / "config.json"
STATE = Path(__file__).parent / "state.json"
LOCK = Path(__file__).parent / "publicador.lock"
REGISTRO = RAIZ / "publicacoes.md"
FILA = RAIZ / "fila"
SAIDA = RAIZ / "saida"
LOCK_VELHO_S = 3 * 3600


def log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).isoformat(timespec='seconds')}] {msg}",
          flush=True)


def carregar(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def gravar(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                    encoding="utf-8")


def pacote_de_hoje() -> tuple[Path, dict] | None:
    data = datetime.now(timezone.utc).date().isoformat()
    if not FILA.is_dir():
        return None
    for p in sorted(FILA.iterdir()):
        if p.is_dir() and p.name.startswith(data):
            meta = carregar(p / "pacote.json", None)
            if meta and meta.get("aprovado_em"):
                return p, meta
    return None


def estado_canal(state: dict, idioma: str) -> dict:
    return state.setdefault("canais", {}).setdefault(idioma, {
        "publicados": [], "ultimo_short": None,
        "shorts_dia": {"data": "", "n": 0}, "longo_data": "",
    })


def decidir(canal_cfg: dict, ec: dict, agora: datetime) -> str | None:
    """'longo', 'short' ou None — o que está devido nesta hora."""
    hoje = agora.date().isoformat()

    if ec["longo_data"] != hoje and agora.hour >= canal_cfg["hora_longo_utc"]:
        return "longo"

    sd = ec["shorts_dia"]
    n_hoje = sd["n"] if sd["data"] == hoje else 0
    if n_hoje >= canal_cfg["shorts_por_dia"]:
        return None
    if ec["ultimo_short"]:
        decorrido = (agora - datetime.fromisoformat(ec["ultimo_short"])
                     ).total_seconds() / 60
        if decorrido < canal_cfg["gap_shorts_min"]:
            return None
    return "short"


def registrar(idioma: str, canal_cfg: dict, item: dict, video_id: str) -> None:
    with REGISTRO.open("a", encoding="utf-8") as fh:
        fh.write(
            f"\n## [{idioma}] {video_id} — {item['titulo']}\n\n"
            f"- URL: https://youtu.be/{video_id}\n"
            f"- Canal: {canal_cfg['titulo_canal']} (`{canal_cfg['channel_id']}`)\n"
            f"- Item: {item['tipo_item']} — {item['referencia']}\n"
            f"- Duração: {item['duracao_s']}s\n"
            f"- Publicado em: {datetime.now(timezone.utc).isoformat(timespec='seconds')}\n"
        )


def publicar_item(idioma: str, canal_cfg: dict, config: dict, item: dict,
                  pasta_pacote: Path, tipo: str, state: dict) -> None:
    cred_dir = RAIZ / "credenciais" / idioma
    youtube = youtube_api.servico(cred_dir)
    cid, ctitulo = youtube_api.canal_do_token(youtube)
    if cid != canal_cfg["channel_id"]:
        raise SystemExit(f"[{idioma}] token é do canal {cid} ({ctitulo}); "
                         f"esperado {canal_cfg['channel_id']}")

    log(f"[{idioma}] subindo {item['tipo_item']}: {item['titulo']}")
    video_id = youtube_api.upload(
        youtube, item["arquivo"], item["titulo"], item["descricao"],
        item["tags"], idiomas.CONFIG[idioma]["bcp47"])

    espera = (config["espera_longo_s"] if tipo == "longo"
              else config["espera_short_s"])
    info = youtube_api.esperar_processamento(youtube, video_id, espera)
    if item["thumb"]:
        # Thumbnail custom exige canal verificado por telefone. Falhar aqui
        # NÃO pode impedir a publicação — em 19/07 um longo já renderizado e
        # enviado ficou preso em privado por causa de um 403 de thumbnail.
        try:
            youtube_api.definir_thumbnail(youtube, video_id, item["thumb"])
        except Exception as exc:
            log(f"[{idioma}] thumbnail não aplicada ({exc}); seguindo. "
                f"Canal precisa de verificação por telefone em "
                f"youtube.com/verify_phone_number")
    youtube_api.tornar_publico(youtube, video_id, info)
    log(f"[{idioma}] PUBLICADO: https://youtu.be/{video_id}")

    agora = datetime.now(timezone.utc)
    hoje = agora.date().isoformat()
    ec = estado_canal(state, idioma)
    ec["publicados"].append({
        "pacote": pasta_pacote.name, "item": item["tipo_item"],
        "video_id": video_id, "titulo": item["titulo"],
        "em": agora.isoformat(timespec="seconds"),
    })
    if tipo == "longo":
        ec["longo_data"] = hoje
    else:
        sd = ec["shorts_dia"]
        ec["shorts_dia"] = {"data": hoje,
                            "n": (sd["n"] if sd["data"] == hoje else 0) + 1}
        ec["ultimo_short"] = agora.isoformat(timespec="seconds")
    gravar(STATE, state)
    registrar(idioma, canal_cfg, item, video_id)


def main() -> None:
    ap = argparse.ArgumentParser(description="Publica o que está devido nesta hora")
    ap.add_argument("--dry-run", action="store_true",
                    help="Só decide e valida; não renderiza nem sobe")
    ap.add_argument("--canal", choices=list(idiomas.IDIOMAS),
                    help="Limita a um canal (testes)")
    ap.add_argument("--render-apenas", action="store_true",
                    help="Renderiza em saida/ sem publicar (não precisa de token)")
    ap.add_argument("--forcar-tipo", choices=["short", "longo"],
                    help="Ignora a agenda e monta este tipo (testes)")
    args = ap.parse_args()

    config = carregar(CONFIG, None)
    if config is None:
        raise SystemExit(f"Config ausente: {CONFIG}")
    state = carregar(STATE, {})
    agora = datetime.now(timezone.utc)

    achado = pacote_de_hoje()
    if achado is None:
        log("SEM PACOTE para hoje — o reabastecedor precisa rodar. Nada a fazer.")
        return
    pasta_pacote, pacote = achado

    if LOCK.exists() and time.time() - LOCK.stat().st_mtime < LOCK_VELHO_S:
        log("Outra execução em andamento (lock). Saindo.")
        return
    LOCK.write_text(str(os.getpid()), encoding="utf-8")
    try:
        for idioma, canal_cfg in config["canais"].items():
            if args.canal and idioma != args.canal:
                continue
            if not canal_cfg.get("ativo") and not args.render_apenas:
                log(f"[{idioma}] inativo; pulando.")
                continue

            cred_dir = RAIZ / "credenciais" / idioma
            if not args.render_apenas and not (cred_dir / "token.json").exists():
                log(f"[{idioma}] sem credenciais no runner; pulando.")
                continue

            ec = estado_canal(state, idioma)
            tipo = args.forcar_tipo or decidir(canal_cfg, ec, agora)
            if tipo is None:
                log(f"[{idioma}] nada devido nesta hora.")
                continue

            if args.dry_run:
                log(f"[{idioma}] [dry-run] publicaria: {tipo} do pacote "
                    f"{pasta_pacote.name}")
                continue

            outdir = SAIDA / idioma / f"{pasta_pacote.name}-{tipo}"
            if tipo == "longo":
                item = fabrica.montar_longo(pacote, idioma,
                                            canal_cfg["handle"], outdir)
            else:
                idx = (ec["shorts_dia"]["n"]
                       if ec["shorts_dia"]["data"] == agora.date().isoformat()
                       else 0)
                idx = min(idx, len(pacote["shorts"]) - 1)
                item = fabrica.montar_short(pacote, idx, idioma,
                                            canal_cfg["handle"], outdir)
            log(f"[{idioma}] render ok: {item['arquivo']} "
                f"({item['arquivo'].stat().st_size / 1e6:.1f} MB, "
                f"{item['duracao_s']}s)")

            if args.render_apenas:
                continue
            publicar_item(idioma, canal_cfg, config, item, pasta_pacote,
                          tipo, state)
    finally:
        LOCK.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
