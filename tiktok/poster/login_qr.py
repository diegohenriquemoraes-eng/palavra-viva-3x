"""Login assistido: abre a janela, tenta ir direto pro QR, traz pra frente,
tira prints (login_state.png) pra eu enxergar, e espera o sessionid."""
from __future__ import annotations
import time
from datetime import datetime, timezone
from pathlib import Path
from playwright.sync_api import sync_playwright

AQUI = Path(__file__).resolve().parent
PERFIL = AQUI / "perfil_chrome"
SHOT = AQUI / "login_state.png"
LOG = AQUI / "poster.log"
PERFIL.mkdir(parents=True, exist_ok=True)


def log(m: str) -> None:
    l = f"[{datetime.now(timezone.utc).isoformat(timespec='seconds')}] {m}"
    print(l, flush=True)
    LOG.open("a", encoding="utf-8").write(l + "\n")


def tem_sessao(ctx) -> bool:
    try:
        return any(c.get("name") == "sessionid" and c.get("value")
                   for c in ctx.cookies())
    except Exception:
        return False


def main() -> None:
    with sync_playwright() as pw:
        ctx = pw.chromium.launch_persistent_context(
            str(PERFIL), headless=False, viewport=None,
            args=["--start-maximized"])
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.bring_to_front()
        try:
            page.goto("https://www.tiktok.com/login", timeout=60000)
        except Exception as e:
            log(f"goto login falhou: {e}")
        page.bring_to_front()
        # tenta clicar em "Usar código QR" / "Use QR code"
        for txt in ["Usar código QR", "Use QR code", "código QR", "QR"]:
            try:
                el = page.get_by_text(txt, exact=False).first
                if el and el.is_visible():
                    el.click(timeout=3000)
                    log(f"cliquei em '{txt}'")
                    break
            except Exception:
                continue
        fim = time.time() + 900
        i = 0
        while time.time() < fim:
            if tem_sessao(ctx):
                log("LOGIN OK — sessionid gravado. Pode fechar a janela.")
                time.sleep(2)
                ctx.close()
                return
            try:
                page.screenshot(path=str(SHOT))
            except Exception:
                pass
            i += 1
            time.sleep(4)
        log("timeout 15 min sem login.")
        ctx.close()


if __name__ == "__main__":
    main()
