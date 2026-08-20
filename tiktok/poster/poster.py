"""Robô de postagem no TikTok (Playwright, local) — Palavra Viva Diária.

Posta UM Short por execução, escolhido de tiktok/biblioteca/fila.json (o mais
antigo ainda não publicado), com a legenda do arquivo legenda.txt ao lado do
vídeo. SEM link na legenda (link só no campo "site" da bio, via Conta Comercial).

A cadência (3/dia) é do Agendador de Tarefas do Windows: cada disparo posta 1.

Modos:
    python poster.py --login     # 1ª vez: abre o navegador p/ VOCÊ logar no TikTok
    python poster.py --dry-run   # faz tudo, MENOS clicar em Publicar (teste seguro)
    python poster.py             # posta 1 vídeo de verdade

Sessão fica em tiktok/poster/perfil_chrome/ (login persistente — loga 1 vez só).

IMPORTANTE: os seletores do TikTok mudam. A 1ª execução DEVE ser com --dry-run e
você olhando: se algum passo não achar o elemento, o log diz qual, e a gente
ajusta o seletor. Não deixe no automático antes de um --dry-run limpo.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
FILA = RAIZ / "tiktok" / "biblioteca" / "fila.json"
PERFIL = AQUI / "perfil_chrome"
LOG = AQUI / "poster.log"

UPLOAD_URL = "https://www.tiktok.com/tiktokstudio/upload"
PERFIL.mkdir(parents=True, exist_ok=True)
sys.stdout.reconfigure(encoding="utf-8")


def log(msg: str) -> None:
    linha = f"[{datetime.now(timezone.utc).isoformat(timespec='seconds')}] {msg}"
    print(linha, flush=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(linha + "\n")


def carregar_fila() -> list[dict]:
    if not FILA.exists():
        return []
    return json.loads(FILA.read_text(encoding="utf-8"))


def gravar_fila(fila: list[dict]) -> None:
    FILA.write_text(json.dumps(fila, ensure_ascii=False, indent=2),
                    encoding="utf-8")


def proximo(fila: list[dict]) -> dict | None:
    for item in fila:
        if not item.get("publicado"):
            v = Path(item["arquivo"])
            if v.exists():
                return item
            log(f"[aviso] arquivo sumiu, pulando: {item['arquivo']}")
    return None


def legenda_de(item: dict) -> str:
    leg = Path(item["arquivo"]).with_name("legenda.txt")
    if leg.exists():
        return leg.read_text(encoding="utf-8").strip()
    return f"{item.get('titulo','')}\n\n📖 {item.get('referencia','')} — Bíblia Livre"


def esta_logado(page) -> bool:
    """Heurística: se a página de upload mostra o input de arquivo, está logado."""
    try:
        page.wait_for_selector("input[type=file]", timeout=8000)
        return True
    except Exception:
        # Página de login costuma ter botões/《Entrar》
        url = page.url
        return "login" not in url and "upload" in url


def fazer_login(pw) -> None:
    ctx = pw.chromium.launch_persistent_context(
        str(PERFIL), headless=False, args=["--start-maximized"],
        viewport=None)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto("https://www.tiktok.com/login", timeout=60000)
    log("Janela aberta na tela de login. Clique em 'Usar código QR' e escaneie "
        "pelo app do TikTok. NÃO vou mexer na tela — só fico esperando o login "
        "(até 15 min). Não feche a janela antes de aparecer 'Login detectado'.")
    fim = time.time() + 900
    while time.time() < fim:
        try:
            cookies = ctx.cookies()
            if any(c.get("name") == "sessionid" and c.get("value")
                   for c in cookies):
                log("Login detectado (sessionid). Sessão salva em "
                    "perfil_chrome/. Pode fechar a janela.")
                time.sleep(2)
                ctx.close()
                return
        except Exception:
            pass
        time.sleep(3)
    log("Não detectei login em 8 min. Rode de novo com --login.")
    ctx.close()


def preencher_legenda(page, texto: str) -> bool:
    seletores = [
        'div[contenteditable="true"]',
        'div[role="combobox"][contenteditable="true"]',
        'div.public-DraftEditor-content',
    ]
    for sel in seletores:
        cxt = page.query_selector(sel)
        if cxt:
            cxt.click()
            page.keyboard.press("Control+A")
            page.keyboard.press("Delete")
            for linha in texto.split("\n"):
                page.keyboard.type(linha, delay=8)
                page.keyboard.press("Shift+Enter")
            log(f"Legenda preenchida via seletor: {sel}")
            return True
    log("[ERRO] não achei o campo de legenda (contenteditable).")
    return False


def clicar_publicar(page, dry: bool) -> bool:
    # O botão aparece como Post/Publicar; fica desabilitado até o vídeo processar.
    rotulos = ["Publicar", "Post", "Postar"]
    fim = time.time() + 240
    while time.time() < fim:
        for r in rotulos:
            btn = page.query_selector(f'button:has-text("{r}")')
            if btn and btn.is_enabled():
                if dry:
                    log(f"[dry-run] acharia e clicaria em «{r}» (habilitado). "
                        "Nada publicado.")
                    return True
                btn.click()
                log(f"Cliquei em «{r}». Aguardando confirmação...")
                time.sleep(8)
                return True
        time.sleep(3)
    log("[ERRO] botão Publicar não ficou habilitado em 4 min "
        "(vídeo pode não ter terminado de processar).")
    return False


def postar(item: dict, dry: bool) -> bool:
    from playwright.sync_api import sync_playwright
    legenda = legenda_de(item)
    video = str(Path(item["arquivo"]).resolve())
    with sync_playwright() as pw:
        ctx = pw.chromium.launch_persistent_context(
            str(PERFIL), headless=not dry, viewport=None,
            args=["--start-maximized"])
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            page.goto(UPLOAD_URL, timeout=60000)
            if not esta_logado(page):
                log("[ERRO] não está logado. Rode: python poster.py --login")
                return False
            inp = page.wait_for_selector("input[type=file]", timeout=20000)
            inp.set_input_files(video)
            log(f"Vídeo enviado ao formulário: {Path(video).name}")
            page.wait_for_timeout(6000)  # começa a processar
            if not preencher_legenda(page, legenda):
                return False
            page.wait_for_timeout(1500)
            if not clicar_publicar(page, dry):
                return False
            if not dry:
                page.wait_for_timeout(6000)
            return True
        finally:
            ctx.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--login", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.login:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            fazer_login(pw)
        return

    fila = carregar_fila()
    item = proximo(fila)
    if item is None:
        log("Sem vídeo para postar (biblioteca vazia ou tudo publicado). "
            "Rode: python tiktok/montar_biblioteca_tiktok.py --quantidade 6")
        return

    log(f"{'[DRY-RUN] ' if args.dry_run else ''}Postando: {item['id']} "
        f"«{item.get('titulo','')}»")
    ok = postar(item, args.dry_run)
    if ok and not args.dry_run:
        for it in fila:
            if it["id"] == item["id"]:
                it["publicado"] = True
                it["publicado_em"] = datetime.now(timezone.utc).isoformat(
                    timespec="seconds")
        gravar_fila(fila)
        log(f"OK — marcado como publicado: {item['id']}")
    elif ok:
        log("[dry-run] fluxo completo sem erro. Pronto para valer.")
    else:
        log(f"FALHOU: {item['id']} — ver erros acima. Nada marcado.")
        sys.exit(1)


if __name__ == "__main__":
    main()
