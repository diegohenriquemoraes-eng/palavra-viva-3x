"""Publicador de Reels no Instagram — roda no GitHub Actions de hora em hora.

Decide se um Reel está devido NESTA hora (agenda com rampa de frequência,
janela de horário e intervalo mínimo), renderiza o versículo da vez, hospeda
o MP4 como asset de uma Release do próprio repo (URL pública que o Instagram
consegue baixar) e publica pela Graph API de Conteúdo do Instagram.

Por que Release e não commit do MP4: o repo é público e vídeo no Git incharia
o histórico para sempre. Release é armazenamento à parte, com URL pública —
e a Graph API precisa de uma URL pública para buscar o vídeo (não aceita
upload direto de arquivo para Reels).

Estado em instagram/state.json (versionado): o runner é descartado; sem
commit, o disparo seguinte repetiria o mesmo versículo.

Segredos (Secrets do repo):
  IG_USER_ID        - id numérico da conta profissional do Instagram
  IG_ACCESS_TOKEN   - token de longa duração com instagram_content_publish
  GITHUB_TOKEN      - fornecido pelo Actions (upload do asset via gh)

Sem os secrets do Instagram, o script NÃO falha: renderiza (se pedido) e sai
avisando — igual ao publicador do YouTube quando um canal ainda não tem token.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ))
sys.stdout.reconfigure(encoding="utf-8")

import requests  # noqa: E402

from instagram import legenda, reels  # noqa: E402

CONFIG = AQUI / "config.json"
STATE = AQUI / "state.json"
REGISTRO = AQUI / "publicacoes_ig.md"
BANCO = AQUI / "versiculos.json"
SAIDA = RAIZ / "saida" / "instagram"


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


# ---------------------------------------------------------------- agenda ----

def por_dia_hoje(cfg: dict, agora: datetime) -> int:
    """Quantos Reels por dia hoje, pela rampa de aquecimento da conta."""
    inicio = datetime.fromisoformat(cfg["inicio"]).replace(tzinfo=timezone.utc)
    dias = (agora.date() - inicio.date()).days
    for faixa in cfg["agenda_rampa"]:
        if dias <= faixa["ate_dia"]:
            return min(faixa["por_dia"], cfg["cap_diario_absoluto"])
    return min(cfg["agenda_rampa"][-1]["por_dia"], cfg["cap_diario_absoluto"])


def _hora_na_janela(cfg: dict, agora: datetime) -> bool:
    ini, fim = cfg["janela_utc"]["ini"], cfg["janela_utc"]["fim"]
    h = agora.hour + (24 if agora.hour < ini else 0)
    return ini <= h < fim


def decidir(cfg: dict, ec: dict, agora: datetime) -> bool:
    """True se um Reel está devido nesta hora."""
    if not _hora_na_janela(cfg, agora):
        return False
    hoje = agora.date().isoformat()
    alvo = por_dia_hoje(cfg, agora)
    feitos = ec["dia"]["n"] if ec["dia"]["data"] == hoje else 0
    if feitos >= alvo:
        return False
    # intervalo mínimo: espalha os posts pela janela, com um piso de segurança
    janela_min = (cfg["janela_utc"]["fim"] - cfg["janela_utc"]["ini"]) * 60
    gap = max(cfg["gap_min_piso"], janela_min / max(alvo, 1))
    if ec.get("ultimo"):
        decorrido = (agora - datetime.fromisoformat(ec["ultimo"])
                     ).total_seconds() / 60
        if decorrido < gap:
            return False
    return True


def proximo_versiculo(ec: dict) -> str:
    """Próxima referência do banco, sem repetir enquanto houver nova.

    A ordem é a do banco; ao esgotar, recomeça (versículo popular pode voltar
    semanas depois, o que é normal no nicho). O ponteiro fica no estado.
    """
    refs = carregar(BANCO, {}).get("referencias", [])
    if not refs:
        raise SystemExit("Banco de versículos vazio (instagram/versiculos.json)")
    i = ec.get("ponteiro", 0) % len(refs)
    ec["ponteiro"] = (i + 1) % len(refs)
    return refs[i]


# ------------------------------------------------------- hospedar o vídeo ----

def hospedar_no_release(cfg: dict, arquivo: Path, nome_asset: str) -> str:
    """Sobe o MP4 como asset de uma Release fixa e devolve a URL pública.

    Usa o gh CLI (presente no runner; autentica pelo GITHUB_TOKEN). A tag é
    reaproveitada (uma só Release rolando); --clobber troca o asset de mesmo
    nome. A URL de download do GitHub é pública e o Instagram a resolve.
    """
    tag = cfg["release_tag"]
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    # cria a release se ainda não existe (idempotente)
    existe = subprocess.run(["gh", "release", "view", tag],
                            capture_output=True, text=True).returncode == 0
    if not existe:
        subprocess.run(
            ["gh", "release", "create", tag, "--title", "Reels (mídia temporária)",
             "--notes", "Vídeos hospedados para publicação no Instagram. "
                        "Assets são efêmeros; podem ser apagados a qualquer hora."],
            check=True)
    destino = arquivo.parent / nome_asset
    if destino != arquivo:
        arquivo.replace(destino)
    subprocess.run(["gh", "release", "upload", tag, str(destino), "--clobber"],
                   check=True)
    if not repo:
        raise SystemExit("GITHUB_REPOSITORY ausente — não sei montar a URL do asset")
    return f"https://github.com/{repo}/releases/download/{tag}/{nome_asset}"


def limpar_assets_antigos(cfg: dict, manter: int = 6) -> None:
    """Mantém só os últimos `manter` assets na Release (higiene, não quebra nada)."""
    tag = cfg["release_tag"]
    out = subprocess.run(
        ["gh", "release", "view", tag, "--json", "assets",
         "-q", ".assets[].name"],
        capture_output=True, text=True)
    nomes = [n for n in out.stdout.splitlines() if n.strip()]
    for nome in sorted(nomes)[:-manter]:
        subprocess.run(["gh", "release", "delete-asset", tag, nome, "--yes"],
                       capture_output=True, text=True)


# ----------------------------------------------------------- Graph API ------

def _graph(cfg: dict) -> str:
    return f"https://graph.facebook.com/{cfg['graph_version']}"


def dentro_do_limite(cfg: dict, ig_id: str, token: str) -> bool:
    """Confere o content_publishing_limit da conta (teto da própria API)."""
    try:
        r = requests.get(
            f"{_graph(cfg)}/{ig_id}/content_publishing_limit",
            params={"fields": "quota_usage,config", "access_token": token},
            timeout=30)
        data = r.json().get("data", [{}])[0]
        uso = data.get("quota_usage", 0)
        teto = (data.get("config") or {}).get("quota_total", 25)
        log(f"cota de publicação do Instagram: {uso}/{teto} nas últimas 24h")
        return uso < teto
    except Exception as exc:
        log(f"não consegui ler o content_publishing_limit ({exc}); seguindo")
        return True


def publicar_reel(cfg: dict, ig_id: str, token: str, video_url: str,
                  caption: str) -> str:
    """Cria o container REELS, espera processar e publica. Devolve o media id."""
    g = _graph(cfg)
    r = requests.post(f"{g}/{ig_id}/media", data={
        "media_type": "REELS", "video_url": video_url,
        "caption": caption, "share_to_feed": "true",
        "access_token": token}, timeout=120)
    j = r.json()
    if "id" not in j:
        raise SystemExit(f"Falha ao criar container: {j}")
    creation_id = j["id"]
    log(f"container criado: {creation_id} — aguardando o Instagram baixar/processar")

    # o Instagram baixa a URL e transcodifica; esperar FINISHED antes de publicar
    for tentativa in range(30):  # ~5 min
        time.sleep(10)
        s = requests.get(f"{g}/{creation_id}", params={
            "fields": "status_code,status", "access_token": token},
            timeout=30).json()
        code = s.get("status_code")
        if code == "FINISHED":
            break
        if code == "ERROR":
            raise SystemExit(f"Instagram falhou ao processar o Reel: {s}")
        log(f"  status {code}... ({tentativa + 1}/30)")
    else:
        raise SystemExit("Timeout esperando o Reel processar")

    p = requests.post(f"{g}/{ig_id}/media_publish", data={
        "creation_id": creation_id, "access_token": token}, timeout=60).json()
    if "id" not in p:
        raise SystemExit(f"Falha no media_publish: {p}")
    return p["id"]


# --------------------------------------------------------------- registro ---

def registrar(ref_disp: str, media_id: str, conta: str) -> None:
    with REGISTRO.open("a", encoding="utf-8") as fh:
        fh.write(
            f"\n## {media_id} — {ref_disp}\n\n"
            f"- Conta: @{conta}\n"
            f"- Link: https://www.instagram.com/reel/{media_id}/\n"
            f"- Publicado em: "
            f"{datetime.now(timezone.utc).isoformat(timespec='seconds')}\n")


# ------------------------------------------------------------------- main ---

def estado(cfg: dict) -> dict:
    st = carregar(STATE, {})
    st.setdefault("ponteiro", 0)
    st.setdefault("dia", {"data": "", "n": 0})
    st.setdefault("ultimo", None)
    st.setdefault("publicados", [])
    return st


def main() -> None:
    ap = argparse.ArgumentParser(description="Publica um Reel se estiver devido")
    ap.add_argument("--dry-run", action="store_true",
                    help="Só decide; não renderiza nem publica")
    ap.add_argument("--render-apenas", action="store_true",
                    help="Renderiza em saida/ sem publicar (não precisa de token)")
    ap.add_argument("--forcar", action="store_true",
                    help="Ignora a agenda e publica agora (testes)")
    args = ap.parse_args()

    cfg = carregar(CONFIG, None)
    if cfg is None:
        raise SystemExit(f"Config ausente: {CONFIG}")
    st = estado(cfg)
    agora = datetime.now(timezone.utc)
    hoje = agora.date().isoformat()

    if not args.forcar and not decidir(cfg, st, agora):
        alvo = por_dia_hoje(cfg, agora)
        feitos = st["dia"]["n"] if st["dia"]["data"] == hoje else 0
        log(f"nada devido nesta hora (meta de hoje {feitos}/{alvo}, "
            f"janela {cfg['janela_utc']['ini']}-{cfg['janela_utc']['fim']}h UTC)")
        return

    if args.dry_run:
        log(f"[dry-run] publicaria o próximo versículo "
            f"({carregar(BANCO, {}).get('referencias', [])[st['ponteiro']]})")
        return

    ig_id = os.environ.get("IG_USER_ID", "").strip()
    token = os.environ.get("IG_ACCESS_TOKEN", "").strip()
    if not args.render_apenas and (not ig_id or not token):
        # Sem credenciais não há por que gastar render a cada hora — sai cedo,
        # igual ao publicador do YouTube quando um canal ainda não tem token.
        log("SEM IG_USER_ID/IG_ACCESS_TOKEN nos secrets — nada a publicar. "
            "Configure os secrets para ativar a conta (ver instagram/README.md).")
        return

    ref = proximo_versiculo(st)
    outdir = SAIDA / f"{hoje}-{st['ponteiro']:03d}"
    log(f"renderizando Reel: {ref}")
    item = reels.montar_reel(ref, cfg["marca_handle"], outdir)
    log(f"render ok: {item['arquivo']} "
        f"({item['arquivo'].stat().st_size / 1e6:.1f} MB, {item['duracao_s']}s)")

    caption = legenda.montar_caption(
        item["ref_disp"], item["texto"], cfg["ponte_bio"],
        cfg["assinatura"], st["dia"]["n"] if st["dia"]["data"] == hoje else 0)

    if args.render_apenas:
        (outdir / "caption.txt").write_text(caption, encoding="utf-8")
        log(f"[render-apenas] vídeo e caption em {outdir}")
        return

    if not dentro_do_limite(cfg, ig_id, token):
        log("cota de publicação do Instagram esgotada nas últimas 24h; saindo.")
        return

    nome_asset = f"reel-{hoje}-{st['ponteiro']:03d}.mp4"
    video_url = hospedar_no_release(cfg, item["arquivo"], nome_asset)
    log(f"vídeo hospedado: {video_url}")

    media_id = publicar_reel(cfg, ig_id, token, video_url, caption)
    log(f"PUBLICADO: https://www.instagram.com/reel/{media_id}/")

    # estado + registro
    st["dia"] = {"data": hoje,
                 "n": (st["dia"]["n"] if st["dia"]["data"] == hoje else 0) + 1}
    st["ultimo"] = agora.isoformat(timespec="seconds")
    st["publicados"].append({
        "ref": ref, "media_id": media_id,
        "em": agora.isoformat(timespec="seconds")})
    gravar(STATE, st)
    registrar(item["ref_disp"], media_id, cfg["conta"])

    try:
        limpar_assets_antigos(cfg)
    except Exception as exc:
        log(f"limpeza de assets antigos falhou ({exc}); ignorando")


if __name__ == "__main__":
    main()
