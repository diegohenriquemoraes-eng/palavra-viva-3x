"""Imagens de fundo gratuitas e SEM risco de copyright.

Fonte: Wikimedia Commons (API sem chave), aceitando SÓ CC0 e domínio público
— a licença de cada resultado é conferida no extmetadata, não confiamos na
busca. (Openverse foi descartado em 18/07/2026: passou a exigir OAuth para
qualquer chamada.) As URLs são resolvidas UMA vez, na criação do pacote do
dia, e gravadas no pacote — assim os 3 idiomas renderizam com as MESMAS
imagens mesmo publicando em horas (e runners) diferentes. Baixamos o thumb
de 1920px do Commons, nunca o original (que pode ter 100+ MB).

Se a busca falhar ou a URL morrer, o render cai para o fundo gradiente da
casa (gerar_gradiente) — o vídeo nunca deixa de sair por falta de imagem.
"""

from __future__ import annotations

import random
import time
from pathlib import Path

import requests
from PIL import Image, ImageDraw

API = "https://commons.wikimedia.org/w/api.php"
# UA descritivo com contato: exigência da robot policy do Wikimedia
UA = {"User-Agent": ("PalavraViva3x/1.0 "
                     "(https://github.com/diegohenriquemoraes-eng/palavra-viva-3x; "
                     "diegohenriquemoraes@gmail.com)")}

# paleta da casa (a mesma família do logo: azul profundo + dourado)
COR_TOPO = (11, 18, 48)
COR_MEIO = (27, 15, 59)
COR_BASE = (42, 20, 80)


def _licenca_livre(lic: str) -> bool:
    return lic.startswith("CC0") or lic.lower().startswith("public domain")


_ultima_busca = 0.0


def _buscar_com_calma(params: dict) -> requests.Response:
    """Commons devolve 429 para rajadas: espaça 3s e retenta uma vez."""
    global _ultima_busca
    for tentativa in (1, 2):
        espera = 3.0 - (time.monotonic() - _ultima_busca)
        if espera > 0:
            time.sleep(espera)
        _ultima_busca = time.monotonic()
        r = requests.get(API, params=params, headers=UA, timeout=30)
        if r.status_code == 429 and tentativa == 1:
            print("  Commons 429; aguardando 30s para retentar...")
            time.sleep(30)
            continue
        r.raise_for_status()
        return r
    raise RuntimeError("inalcançável")


def resolver(consulta: str, n: int, seed: int, orientacao: str = "wide"
             ) -> list[dict]:
    """Busca n imagens CC0/PD no Wikimedia Commons. [{url, autor, origem}]."""
    try:
        r = _buscar_com_calma({
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrsearch": f"filetype:bitmap {consulta}",
            "gsrnamespace": 6,
            "gsrlimit": 40,
            "prop": "imageinfo",
            "iiprop": "url|size|extmetadata",
            "iiurlwidth": 1920,
        })
        paginas = (r.json().get("query") or {}).get("pages", {})
    except Exception as exc:  # rede/API fora: o render tem fallback
        print(f"  Commons falhou para '{consulta}': {exc}")
        return []

    candidatos = []
    for pg in paginas.values():
        infos = pg.get("imageinfo") or []
        if not infos:
            continue
        ii = infos[0]
        meta = ii.get("extmetadata") or {}
        lic = (meta.get("LicenseShortName") or {}).get("value", "")
        if not _licenca_livre(lic):
            continue
        w, h = ii.get("width") or 0, ii.get("height") or 0
        if w < 1280 or h < 720:
            continue
        prefere_wide = orientacao == "wide"
        candidatos.append({
            "url": ii.get("thumburl") or ii.get("url"),
            "autor": (meta.get("Artist") or {}).get("value", "")[:120]
                     or "desconhecido",
            "origem": ii.get("descriptionurl") or ii.get("url"),
            "licenca": lic,
            # orientação certa primeiro; a errada ainda serve (cover-crop)
            "_prio": 0 if (w >= h) == prefere_wide else 1,
        })
    if not candidatos:
        print(f"  Commons: nada CC0/PD utilizável para '{consulta}'")
        return []
    rng = random.Random(seed)
    rng.shuffle(candidatos)
    candidatos.sort(key=lambda c: c["_prio"])
    for c in candidatos:
        c.pop("_prio", None)
    return candidatos[:n]


def baixar(url: str, destino: Path) -> bool:
    """Download educado: 2,5s entre pedidos e um retry no 429 — o upload.
    wikimedia.org corta rajadas (aprendido em 19/07: 10 de 14 caíram)."""
    global _ultima_busca
    try:
        for tentativa in (1, 2):
            espera = 2.5 - (time.monotonic() - _ultima_busca)
            if espera > 0:
                time.sleep(espera)
            _ultima_busca = time.monotonic()
            r = requests.get(url, headers=UA, timeout=60)
            if r.status_code == 429 and tentativa == 1:
                time.sleep(20)
                continue
            r.raise_for_status()
            break
        if len(r.content) < 30_000:
            return False
        destino.write_bytes(r.content)
        Image.open(destino).verify()  # arquivo é imagem de verdade?
        return True
    except Exception as exc:
        print(f"  download de imagem falhou ({url[:60]}...): {exc}")
        destino.unlink(missing_ok=True)
        return False


def gerar_gradiente(destino: Path, w: int, h: int, seed: int) -> Path:
    """Fallback: gradiente vertical da paleta da casa, com vinheta suave."""
    rng = random.Random(seed)
    desloc = rng.uniform(-0.15, 0.15)
    img = Image.new("RGB", (w, h))
    dr = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h + desloc * (0.5 - abs(y / h - 0.5))
        t = min(1.0, max(0.0, t))
        if t < 0.5:
            a, b, tt = COR_TOPO, COR_MEIO, t * 2
        else:
            a, b, tt = COR_MEIO, COR_BASE, (t - 0.5) * 2
        cor = tuple(int(a[i] + (b[i] - a[i]) * tt) for i in range(3))
        dr.line([(0, y), (w, y)], fill=cor)
    img.save(destino, quality=92)
    return destino
