"""Vigia: avisa quando um canal para de publicar ou o estoque de temas acaba.

Existe porque "roda sozinho" não é o mesmo que "avisa quando quebra". Até
19/07/2026 o único aviso era o e-mail de falha do GitHub — se ninguém abrisse
o e-mail, um canal podia ficar dias parado sem que se notasse (o canal EN
ficou 5 horas travado naquele dia e só descobrimos por acaso).

Dois alarmes:
  1. CANAL MUDO — canal ativo sem publicar há mais de LIMITE_MUDO_H horas.
     O intervalo natural máximo é ~7h (3 Shorts espalhados + 1 longo), então
     14h já é anomalia, não folga de agenda.
  2. ESTOQUE BAIXO — menos de LIMITE_TEMAS dias de tema no poço. Avisa ANTES
     de secar; o aviso de poço seco do reabastecedor chega tarde demais.

Sai com código 7 quando há alarme (o workflow abre/atualiza uma issue, que
vira e-mail). Sem alarme, sai 0 e não faz barulho.

    python produzir/vigia.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.stdout.reconfigure(encoding="utf-8")

CONFIG = RAIZ / "publicador" / "config.json"
STATE = RAIZ / "publicador" / "state.json"
TEMAS = RAIZ / "conteudo" / "temas.json"
FILA = RAIZ / "fila"

LIMITE_MUDO_H = 14
LIMITE_TEMAS = 5


def carregar(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def ultima_publicacao(ec: dict) -> datetime | None:
    pubs = ec.get("publicados", [])
    if not pubs:
        return None
    return max(datetime.fromisoformat(p["em"]) for p in pubs)


def main() -> None:
    config = carregar(CONFIG, {})
    state = carregar(STATE, {})
    temas = carregar(TEMAS, [])
    agora = datetime.now(timezone.utc)

    alarmes: list[str] = []

    # 1) canais mudos
    for idioma, canal in config.get("canais", {}).items():
        if not canal.get("ativo"):
            continue
        ec = state.get("canais", {}).get(idioma, {})
        ultima = ultima_publicacao(ec)
        if ultima is None:
            alarmes.append(
                f"- **{canal['titulo_canal']}** ({idioma}): está ativo e "
                f"**nunca publicou nada**. Provável problema de credencial "
                f"(secret `YT_TOKEN_{idioma.upper()}`) ou de canal errado no "
                f"`channel_id`.")
            continue
        horas = (agora - ultima).total_seconds() / 3600
        if horas > LIMITE_MUDO_H:
            alarmes.append(
                f"- **{canal['titulo_canal']}** ({idioma}): sem publicar há "
                f"**{horas:.0f}h** (último: {ultima.isoformat(timespec='minutes')}). "
                f"O normal é no máximo ~7h entre publicações.")
        else:
            print(f"ok  {idioma}: publicou há {horas:.1f}h")

    # 2) estoque de temas
    usados = set()
    if FILA.is_dir():
        usados = {p.name[11:] for p in FILA.iterdir()
                  if p.is_dir() and len(p.name) > 11}
    livres = [t for t in temas if t["slug"] not in usados]
    print(f"ok  estoque: {len(livres)} tema(s) livre(s) no poço")
    if len(livres) < LIMITE_TEMAS:
        alarmes.append(
            f"- **Estoque de temas baixo**: restam **{len(livres)} dia(s)** de "
            f"conteúdo em `conteudo/temas.json`. Quando zerar, os canais param. "
            f"Adicionar temas novos (1 longo + 4 Shorts, títulos nos 3 idiomas) "
            f"e validar com `python produzir/reabastecer.py --dry-run`.")

    if not alarmes:
        print("\nSem alarmes.")
        return

    print("\n=== ALARMES ===")
    for a in alarmes:
        print(a)
    (RAIZ / "alarmes.md").write_text(
        "\n".join(alarmes) + "\n\n_Gerado por `produzir/vigia.py` em "
        f"{agora.isoformat(timespec='minutes')}._\n", encoding="utf-8")
    sys.exit(7)


if __name__ == "__main__":
    main()
