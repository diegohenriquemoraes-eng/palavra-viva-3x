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

from nucleo import fabrica, idiomas, playlists, youtube_api  # noqa: E402

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


def pacotes_de_hoje(fila: Path = FILA) -> list[tuple[Path, dict]]:
    """TODOS os pacotes com a data de hoje, em ordem estável.

    Cada canal aponta para a SUA fila (`canal_cfg["fila"]`): os canais bíblicos
    compartilham `fila/`, o estoico tem `fila_stoic/`. Um pacote estoico não
    tem texto para os canais de Escritura, e vice-versa.

    A lista virou plural em 25/08/2026: com `longos_por_dia: 2` a linha bíblica
    passa a ter dois pacotes na mesma data (temas diferentes), e o segundo
    longo do canal ES sai do segundo pacote. O PRIMEIRO da lista continua sendo
    "o pacote do dia" para todo o resto (Shorts e canais de 1 longo), então
    nada muda para quem não pediu o segundo.
    """
    data = datetime.now(timezone.utc).date().isoformat()
    if not fila.is_dir():
        return []
    achados = []
    for p in sorted(fila.iterdir()):
        if p.is_dir() and p.name.startswith(data):
            meta = carregar(p / "pacote.json", None)
            if meta and meta.get("aprovado_em"):
                achados.append((p, meta))
    return achados


def pacote_de_hoje(fila: Path = FILA) -> tuple[Path, dict] | None:
    achados = pacotes_de_hoje(fila)
    return achados[0] if achados else None


def pacote_do_longo(achados: list[tuple[Path, dict]],
                    ec: dict) -> tuple[Path, dict] | None:
    """O pacote de hoje cujo vídeo longo este canal ainda NÃO publicou.

    É o que impede o segundo longo do dia de repetir o tema do primeiro — e
    também o que faz a segunda execução escolher sozinha o pacote certo depois
    de uma falha, sem estado extra para manter.
    """
    feitos = {p["pacote"] for p in ec.get("publicados", [])
              if p["item"] == "longo"}
    for pasta, meta in achados:
        if pasta.name not in feitos:
            return pasta, meta
    return None


def estado_canal(state: dict, idioma: str) -> dict:
    ec = state.setdefault("canais", {}).setdefault(idioma, {
        "publicados": [], "ultimo_short": None,
        "shorts_dia": {"data": "", "n": 0}, "longo_data": "",
    })
    # Migração do contador de longos (25/08/2026): antes bastava a data do
    # único longo do dia; com 2/dia é preciso contar. O `longo_data` antigo
    # continua sendo escrito para não quebrar quem o lê (vigia, relatórios).
    if "longos_dia" not in ec:
        ec["longos_dia"] = {"data": ec.get("longo_data", ""),
                            "n": 1 if ec.get("longo_data") else 0}
    return ec


def decidir(canal_cfg: dict, ec: dict, agora: datetime) -> str | None:
    """'longo', 'short' ou None — o que está devido nesta hora."""
    hoje = agora.date().isoformat()

    # hora_longo_utc = null desliga o vídeo longo no canal (o Stoic by Night
    # roda só Shorts durante o teste dos 30 dias — ver CLAUDE.md).
    hora_longo = canal_cfg.get("hora_longo_utc")
    ld = ec["longos_dia"]
    n_longos = ld["n"] if ld["data"] == hoje else 0
    if (hora_longo is not None and agora.hour >= hora_longo
            and n_longos < canal_cfg.get("longos_por_dia", 1)):
        # Gap entre os longos do mesmo dia: sem ele os dois sairiam em
        # execuções seguidas do cron horário, e o canal publicaria duas horas
        # de vídeo em duas horas de relógio — pico de cota e de banda no
        # runner, e dois vídeos disputando a mesma janela de entrega.
        gap = canal_cfg.get("gap_longos_min", 0)
        ultimo = ec.get("ultimo_longo")
        if n_longos and gap and not ultimo:
            # Estado migrado de antes de 25/08 não tem `ultimo_longo`. Sem esta
            # busca no histórico, o segundo longo sairia na execução seguinte à
            # do primeiro, ignorando o gap justamente no dia da virada.
            ultimo = next((p["em"] for p in reversed(ec.get("publicados", []))
                           if p["item"] == "longo"), None)
        if n_longos and gap and ultimo:
            decorrido = (agora - datetime.fromisoformat(ultimo)
                         ).total_seconds() / 60
            if decorrido < gap:
                return None
        return "longo"

    sd = ec["shorts_dia"]
    n_hoje = sd["n"] if sd["data"] == hoje else 0
    if n_hoje >= canal_cfg["shorts_por_dia"]:
        return None
    # hora_short_utc fixa a hora da publicação diária. "Mesmo horário todo dia"
    # é regra do método de canal novo: sem isso o Short sai na primeira
    # execução do cron depois da virada do dia UTC, que é madrugada nos EUA.
    hora_short = canal_cfg.get("hora_short_utc")
    if hora_short is not None and agora.hour < hora_short:
        return None
    if ec["ultimo_short"]:
        decorrido = (agora - datetime.fromisoformat(ec["ultimo_short"])
                     ).total_seconds() / 60
        if decorrido < canal_cfg["gap_shorts_min"]:
            return None
    return "short"


def longo_do_dia(ec: dict, pacote_nome: str, formato: str, idioma: str) -> str:
    """URL do longo para a ponte na descrição do Short.

    Preferência: o longo do MESMO pacote (mesmo tema do Short). Se o longo do
    dia falhou, cai no último longo do mesmo formato — link de ontem é melhor
    que Short sem ponte (as entradas do estado guardam `formato` desde 25/08;
    as anteriores ficam de fora do fallback e envelhecem sozinhas).

    Com o id da playlist em cache, o link sai como watch?v=...&list=...: o
    longo abre DENTRO da playlist do formato e, acabando, o YouTube emenda o
    próximo — é o que transforma o clique vindo do Short em sessão de horas,
    e hora de exibição é a trilha de monetização que temos.
    """
    vid = ""
    for p in reversed(ec.get("publicados", [])):
        if p["item"] != "longo":
            continue
        if p["pacote"] == pacote_nome:
            vid = p["video_id"]
            break
        if not vid and p.get("formato") == formato:
            vid = p["video_id"]   # guarda o fallback; segue procurando o do dia
    if not vid:
        return ""
    lista = playlists.obter(idioma, formato)
    return (f"https://www.youtube.com/watch?v={vid}&list={lista}" if lista
            else f"https://youtu.be/{vid}")


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
                  pasta_pacote: Path, tipo: str, state: dict,
                  pacote_formato: str = "tema") -> None:
    cred_dir = RAIZ / "credenciais" / idioma
    youtube = youtube_api.servico(cred_dir)
    cid, ctitulo = youtube_api.canal_do_token(youtube)
    if cid != canal_cfg["channel_id"]:
        raise SystemExit(f"[{idioma}] token é do canal {cid} ({ctitulo}); "
                         f"esperado {canal_cfg['channel_id']}")

    # Guarda contra duplicata: o canal é a fonte de verdade, não o state.json
    # (ver youtube_api.ja_publicado — custou um vídeo longo duplicado no EN).
    existente = youtube_api.ja_publicado(youtube, item["titulo"])
    if existente:
        log(f"[{idioma}] JÁ EXISTE no canal: https://youtu.be/{existente} "
            f"— não vou publicar de novo. Registrando no estado.")
        registrar_no_estado(state, idioma, canal_cfg, item, existente,
                            pasta_pacote, tipo, pacote_formato)
        return

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
    # Faixa de legenda (.srt): é o texto que a busca do YouTube lê — a legenda
    # queimada é pixel. Custa 400 de cota e, como tudo que é acessório aqui,
    # não pode derrubar a publicação se falhar.
    if item.get("legenda_srt"):
        try:
            youtube_api.enviar_legenda(youtube, video_id, item["legenda_srt"],
                                       idiomas.CONFIG[idioma]["bcp47"])
            log(f"[{idioma}] legenda enviada")
        except Exception as exc:
            log(f"[{idioma}] legenda não enviada ({str(exc)[:120]}); seguindo.")

    youtube_api.tornar_publico(youtube, video_id, info)
    log(f"[{idioma}] PUBLICADO: https://youtu.be/{video_id}")

    # Só o longo entra em playlist: Shorts não aparecem em playlist no feed e
    # a lista ficaria poluída. Falha aqui não pode derrubar a publicação.
    if tipo == "longo":
        nomes = idiomas.PLAYLISTS.get(pacote_formato, {})
        titulo_pl = nomes.get(idioma)
        if titulo_pl:
            try:
                pl = youtube_api.playlist_por_titulo(
                    youtube, titulo_pl, idiomas.CONFIG[idioma]["cta"])
                playlists.definir(idioma, pacote_formato, pl)
                youtube_api.adicionar_na_playlist(youtube, pl, video_id)
                log(f"[{idioma}] adicionado à playlist '{titulo_pl}'")
            except Exception as exc:
                log(f"[{idioma}] playlist falhou ({exc}); seguindo.")

    registrar_no_estado(state, idioma, canal_cfg, item, video_id,
                        pasta_pacote, tipo, pacote_formato)


def registrar_no_estado(state: dict, idioma: str, canal_cfg: dict, item: dict,
                        video_id: str, pasta_pacote: Path, tipo: str,
                        formato: str = "tema") -> None:
    agora = datetime.now(timezone.utc)
    hoje = agora.date().isoformat()
    ec = estado_canal(state, idioma)
    if any(p["video_id"] == video_id for p in ec["publicados"]):
        return
    ec["publicados"].append({
        "pacote": pasta_pacote.name, "item": item["tipo_item"],
        "formato": formato,
        "video_id": video_id, "titulo": item["titulo"],
        "em": agora.isoformat(timespec="seconds"),
    })
    if tipo == "longo":
        ec["longo_data"] = hoje
        ld = ec["longos_dia"]
        ec["longos_dia"] = {"data": hoje,
                            "n": (ld["n"] if ld["data"] == hoje else 0) + 1}
        ec["ultimo_longo"] = agora.isoformat(timespec="seconds")
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

    # Fila por canal: a falta de pacote numa linha não pode calar a outra.
    # Antes o pacote era procurado UMA vez, antes do laço de canais, e a
    # ausência abortava a execução inteira.
    filas = {idioma: RAIZ / cfg.get("fila", "fila")
             for idioma, cfg in config["canais"].items()}
    do_dia = {idioma: pacotes_de_hoje(f) for idioma, f in filas.items()}
    achados = {idioma: (lista[0] if lista else None)
               for idioma, lista in do_dia.items()}
    if not any(achados.values()):
        log("SEM PACOTE para hoje em nenhuma fila — o reabastecedor precisa "
            "rodar. Nada a fazer.")
        return

    if LOCK.exists() and time.time() - LOCK.stat().st_mtime < LOCK_VELHO_S:
        log("Outra execução em andamento (lock). Saindo.")
        return
    LOCK.write_text(str(os.getpid()), encoding="utf-8")
    falhas_longo: list[str] = []
    falhas_canal: list[str] = []
    try:
        for idioma, canal_cfg in config["canais"].items():
            if args.canal and idioma != args.canal:
                continue
            if not canal_cfg.get("ativo") and not args.render_apenas:
                log(f"[{idioma}] inativo; pulando.")
                continue

            if achados.get(idioma) is None:
                log(f"[{idioma}] sem pacote para hoje em "
                    f"{filas[idioma].name}/; pulando.")
                continue
            pasta_pacote, pacote = achados[idioma]

            cred_dir = RAIZ / "credenciais" / idioma
            if not args.render_apenas and not (cred_dir / "token.json").exists():
                log(f"[{idioma}] sem credenciais no runner; pulando.")
                continue

            ec = estado_canal(state, idioma)
            tipo = args.forcar_tipo or decidir(canal_cfg, ec, agora)
            if tipo is None:
                log(f"[{idioma}] nada devido nesta hora.")
                continue

            # O longo tem pacote próprio: o primeiro de hoje que ESTE canal
            # ainda não publicou (com 2 longos/dia, o 2º cai no 2º pacote).
            # O Short continua SEMPRE no pacote do dia — são duas variáveis
            # separadas de propósito: quando o longo falha, a execução cai para
            # o Short, e ele não pode sair do tema do longo que acabou de
            # falhar (o índice do Short é contado no pacote do dia).
            pasta_longo, pacote_longo = pasta_pacote, pacote
            if tipo == "longo":
                escolha = pacote_do_longo(do_dia[idioma], ec)
                if escolha is None:
                    log(f"[{idioma}] todos os longos de hoje já foram "
                        f"publicados; nada a fazer.")
                    continue
                pasta_longo, pacote_longo = escolha

            if args.dry_run:
                alvo = pasta_longo if tipo == "longo" else pasta_pacote
                log(f"[{idioma}] [dry-run] publicaria: {tipo} do pacote "
                    f"{alvo.name}")
                continue

            def montar(t: str):
                if t == "longo":
                    return fabrica.montar_longo(pacote_longo, idioma,
                                                canal_cfg["handle"],
                                                SAIDA / idioma /
                                                f"{pasta_longo.name}-longo",
                                                afiliado=canal_cfg.get("afiliado", ""))
                idx = (ec["shorts_dia"]["n"]
                       if ec["shorts_dia"]["data"] == agora.date().isoformat()
                       else 0)
                idx = min(idx, len(pacote["shorts"]) - 1)
                return fabrica.montar_short(
                    pacote, idx, idioma, canal_cfg["handle"],
                    SAIDA / idioma / f"{pasta_pacote.name}-short",
                    url_longo=longo_do_dia(ec, pasta_pacote.name,
                                           pacote.get("formato", "tema"),
                                           idioma),
                    # versão curta no Short: o bloco inteiro repetido em cada
                    # publicação deixa o canal com cara de anúncio, e descrição
                    # de Short quase não é aberta — quem converte é o longo
                    afiliado=(canal_cfg.get("afiliado_short")
                              or canal_cfg.get("afiliado", "")))

            # O longo é a peça frágil (60+ min, ~1 GB): render pesado, upload
            # longo e processamento demorado no YouTube. Ele NUNCA pode deixar
            # o canal mudo. Por isso todo o caminho do longo — render E
            # publicação — está sob o mesmo try: se qualquer etapa falhar, a
            # execução cai para o Short e o canal publica mesmo assim.
            # (Antes só o render estava protegido; uma falha no upload do longo
            # em 20/07 matou a execução e o Short do dia não saiu.)
            def render_e_publica(t: str) -> None:
                item = montar(t)
                log(f"[{idioma}] render ok: {item['arquivo']} "
                    f"({item['arquivo'].stat().st_size / 1e6:.1f} MB, "
                    f"{item['duracao_s']}s)")
                if args.render_apenas:
                    return
                origem, meta = ((pasta_longo, pacote_longo) if t == "longo"
                                else (pasta_pacote, pacote))
                publicar_item(idioma, canal_cfg, config, item, origem,
                              t, state, meta.get("formato", "tema"))

            # BaseException, não Exception: os erros de publicação levantam
            # SystemExit (via raise SystemExit), que NÃO é subclasse de
            # Exception — por isso o fallback não pegava a falha do longo em
            # 20/07 e o Short não saía. KeyboardInterrupt segue propagando.
            # Isolamento por canal: a falha de UM canal (ex.: token revogado,
            # como o EN em 24/07) não pode abortar o loop e calar os canais
            # seguintes. Antes, um Short que falhava fazia `raise` e derrubava
            # a execução inteira — como a ordem é es→en→pt, um EN morto deixava
            # o PT (que vem depois) sem publicar em toda execução. Cada canal é
            # independente; a falha é registrada e a execução segue.
            try:
                try:
                    render_e_publica(tipo)
                except KeyboardInterrupt:
                    raise
                except BaseException as exc:
                    if tipo != "longo":
                        raise
                    log(f"[{idioma}] LONGO FALHOU ({exc!r}); caindo para Short "
                        f"nesta execução. O longo será tentado na próxima hora.")
                    falhas_longo.append(idioma)
                    render_e_publica("short")
            except KeyboardInterrupt:
                raise
            except BaseException as exc:
                log(f"[{idioma}] CANAL FALHOU nesta execução ({exc!r}); "
                    f"seguindo para o próximo canal.")
                falhas_canal.append(idioma)
                continue
    finally:
        LOCK.unlink(missing_ok=True)

    # Sair com erro faz o GitHub avisar por e-mail — mas só DEPOIS de os demais
    # canais terem publicado. Falha visível, canais vivos.
    if falhas_longo or falhas_canal:
        partes: list[str] = []
        if falhas_longo:
            partes.append(
                f"Render do vídeo longo falhou em: {', '.join(falhas_longo)} "
                f"(os Shorts foram publicados normalmente)")
        if falhas_canal:
            partes.append(
                f"Canal falhou por completo em: {', '.join(falhas_canal)} "
                f"(os demais canais publicaram normalmente)")
        raise SystemExit(". ".join(partes) + ".")


if __name__ == "__main__":
    main()
