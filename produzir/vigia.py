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
        # canal de 1 Short/dia (Protocolo Fantasma) passa ~24h entre
        # publicações por desenho: 14h ali é alarme falso todo santo dia.
        limite = LIMITE_MUDO_H if canal.get("shorts_por_dia", 3) >= 3 else 30
        if horas > limite:
            alarmes.append(
                f"- **{canal['titulo_canal']}** ({idioma}): sem publicar há "
                f"**{horas:.0f}h** (último: {ultima.isoformat(timespec='minutes')}); "
                f"o limite deste canal é {limite}h.")
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

    # 3) QUEDA DE AUDIÊNCIA — o alarme que faltava em 15/08/2026
    #
    # Canal publicando e poço cheio não quer dizer canal vivo: em 12 e 13/08 o
    # Palabra Viva Cortes caiu de ~2.700 para ~1.100 views/dia sem nenhum aviso,
    # e só apareceu porque alguém foi olhar.
    #
    # A taxa entre duas medições do histórico é views/dia. Comparar as duas
    # últimas, porém, é ruído puro: a série diária do ES tem dias de 1.025 e de
    # 3.398 na mesma semana. Então a comparação é de MÉDIA MÓVEL — as 3 taxas
    # mais recentes contra as 4 anteriores — e só cai para o modo simples
    # (2 medições) enquanto não houver série suficiente.
    hist = carregar(RAIZ / "conteudo" / "desempenho_historico.json", [])

    def taxas(canal: str) -> list[float]:
        """views/dia entre medições consecutivas, na ordem da série."""
        out = []
        for antes_, depois in zip(hist, hist[1:]):
            a = depois["canais"].get(canal, {}).get("views_totais")
            b = antes_["canais"].get(canal, {}).get("views_totais")
            if a is None or b is None:
                continue
            dias = (datetime.fromisoformat(depois["data"])
                    - datetime.fromisoformat(antes_["data"])).days
            if dias >= 1:
                out.append((a - b) / dias)
        return out

    for idioma, canal in config.get("canais", {}).items():
        if not canal.get("ativo"):
            continue
        série = taxas(idioma)
        if len(série) >= 7:
            recente = sum(série[-3:]) / 3
            base = sum(série[-7:-3]) / 4
        elif len(série) >= 2:
            recente, base = série[-1], série[-2]
        else:
            continue
        if base < 200:
            continue          # canal pequeno demais: a razão vira ruído
        queda = 1 - recente / base
        if queda >= 0.35:
            alarmes.append(
                f"- **{canal['titulo_canal']}** ({idioma}): audiência caiu "
                f"**{queda*100:.0f}%** — de {base:.0f} para {recente:.0f} "
                f"views/dia. Não é falha de publicação: o canal está publicando "
                f"e sendo menos entregue. Olhar retenção da coorte de 2 a 7 "
                f"dias antes de mexer em qualquer coisa.")
        else:
            print(f"ok  {idioma}: {recente:.0f} views/dia ({queda*-100:+.0f}%)")

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
