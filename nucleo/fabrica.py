"""Monta um item do pacote do dia (short ou longo) num idioma.

O pacote (fila/AAAA-MM-DD-slug/pacote.json) traz refs, títulos por idioma e
URLs de imagem já resolvidas — aqui só se baixa, narra, legenda e renderiza.
O visual (imagens, movimento) é o MESMO nos 3 idiomas; muda áudio, legenda,
título, descrição e thumbnail.
"""

from __future__ import annotations

import math
import zlib
from pathlib import Path

from . import biblia, idiomas, imagens, legendas, musica, render, thumbnail, tts

PAUSA_VERSO = 2.0       # silêncio contemplativo entre versículos do longo
                        # (2,0s: leva o longo típico acima dos 8 min de mid-roll)
CAUDA_LONGO = 3.5
CAUDA_SHORT = 1.2
MIN_SHORT_S = 15.0      # abaixo disto o versículo é repetido (ver montar_short)
PAUSA_REPETICAO = 1.6
SEG_POR_IMAGEM = 28.0   # troca de imagem no longo a cada ~28 s


def _seed(pacote: dict, extra: str) -> int:
    return zlib.crc32(f"{pacote['slug']}-{extra}".encode()) % 999_983


def _baixar_imagem(info: dict | None, destino: Path) -> Path | None:
    if not info or not info.get("url"):
        return None
    if imagens.baixar(info["url"], destino):
        return destino
    return None


def _ts_capitulo(seg: float) -> str:
    m, s = divmod(int(seg), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def montar_short(pacote: dict, idx: int, idioma: str, marca: str,
                 outdir: Path) -> dict:
    cfg = idiomas.CONFIG[idioma]
    short = pacote["shorts"][idx]
    ref = short["ref"]
    outdir.mkdir(parents=True, exist_ok=True)

    versos = biblia.carregar_versos(idioma, ref)
    texto = " ".join(t for _, t in versos)

    mp3 = outdir / "voz.mp3"
    palavras = tts.narrar(texto, cfg["voz"], cfg["rate_short"], mp3)
    legendas.alinhar_display(texto, palavras)
    blocos = legendas.agrupar(palavras)
    dur = max(tts.duracao_audio(mp3), blocos[-1]["fim"]) + CAUDA_SHORT

    # Versículo curto (Salmo 4:8, Josué 1:9...) dava Short de ~9s: fino demais
    # para reter e para o loop do feed. Nesses casos o texto é narrado DUAS
    # vezes com pausa — formato consagrado no nicho (repetição para meditar),
    # não enchimento: o espectador ouve, respira e ouve de novo.
    if dur < MIN_SHORT_S:
        segmentos, dur_voz = tts.narrar_versos(
            [(1, texto), (2, texto)], cfg["voz"], cfg["rate_short"],
            PAUSA_REPETICAO, outdir / "voz.wav", outdir / "tts")
        blocos = []
        for seg in segmentos:
            legendas.alinhar_display(seg["texto"], seg["palavras"])
            blocos += legendas.agrupar(seg["palavras"])
        mp3 = outdir / "voz.wav"
        dur = dur_voz + CAUDA_SHORT

    cab = biblia.cabecalho(idioma, ref)
    legendas.ass_short(outdir / "legenda.ass", blocos, cab, marca, dur)

    img = _baixar_imagem(short.get("imagem"), outdir / "fundo.jpg")
    seed = _seed(pacote, f"short{idx}")
    video = render.render_short(outdir, mp3.name, "legenda.ass", img, dur, seed)

    ref_disp = biblia.ref_exibicao(idioma, ref)
    descricao = (
        f"{ref_disp} — {cfg['fonte_texto']}.\n\n"
        f"{cfg['cta']}\n\n{cfg['hashtags']} #Shorts"
    )
    return {
        "arquivo": video,
        "titulo": short["titulo"][idioma],
        "descricao": descricao,
        "tags": cfg["tags"] + ["shorts"],
        "thumb": None,
        "duracao_s": round(dur, 1),
        "referencia": ref_disp,
        "tipo_item": f"short-{idx + 1}",
    }


def montar_longo(pacote: dict, idioma: str, marca: str, outdir: Path) -> dict:
    cfg = idiomas.CONFIG[idioma]
    longo = pacote["longo"]
    outdir.mkdir(parents=True, exist_ok=True)

    # 1) narração seção a seção (uma seção por referência)
    todos_versos: list[tuple[int, str]] = []
    limites: list[tuple[str, int]] = []  # (ref, nº de versos)
    for ref in longo["refs"]:
        vs = biblia.carregar_versos(idioma, ref)
        todos_versos += vs
        limites.append((ref, len(vs)))

    voz = outdir / "voz.wav"
    segmentos, dur_voz = tts.narrar_versos(
        todos_versos, cfg["voz"], cfg["rate_longo"], PAUSA_VERSO,
        voz, outdir / "tts")
    dur = dur_voz + CAUDA_LONGO

    # 2) seções -> legenda + capítulos
    secoes = []
    i = 0
    for ref, n in limites:
        parte = segmentos[i:i + n]
        i += n
        blocos = []
        for seg in parte:
            legendas.alinhar_display(seg["texto"], seg["palavras"])
            blocos += legendas.agrupar(seg["palavras"], largura=34,
                                       max_palavras=7)
        secoes.append({
            "cabecalho": biblia.cabecalho(idioma, ref),
            "ini": parte[0]["ini"],
            "fim": parte[-1]["fim"] + PAUSA_VERSO,
            "blocos": blocos,
            "ref": ref,
        })
    legendas.ass_longo(outdir / "legenda.ass", secoes, marca, dur)

    # 3) imagens (mesmas nos 3 idiomas; fallback = gradiente da casa)
    n_alvo = max(6, min(30, math.ceil(dur / SEG_POR_IMAGEM)))
    baixadas: list[Path] = []
    for j, info in enumerate(longo.get("imagens", [])):
        p = _baixar_imagem(info, outdir / f"img{j:02d}.jpg")
        if p:
            baixadas.append(p)
        if len(baixadas) >= n_alvo:
            break
    if not baixadas:
        for j in range(6):
            g = outdir / f"grad{j}.jpg"
            imagens.gerar_gradiente(g, 2048, 1152, _seed(pacote, f"g{j}"))
            baixadas.append(g)
    lista = [baixadas[j % len(baixadas)] for j in range(n_alvo)]

    # 4) pad ambiente procedural + render
    pad = outdir / "pad.wav"
    musica.gerar_pad(dur, _seed(pacote, "pad"), pad)
    video = render.render_longo(outdir, "voz.wav", "pad.wav", "legenda.ass",
                                lista, dur, _seed(pacote, "longo"))

    # 5) thumbnail localizada
    thumb = outdir / "thumb.jpg"
    thumbnail.gerar(thumb, baixadas[0] if baixadas else None,
                    longo["thumb_titulo"][idioma],
                    longo["thumb_sub"][idioma], marca,
                    _seed(pacote, "thumb"))

    # 6) descrição com capítulos (SEO + navegação)
    caps = [f"{_ts_capitulo(s['ini'])} {biblia.ref_exibicao(idioma, s['ref'])}"
            for s in secoes]
    caps[0] = f"0:00 {biblia.ref_exibicao(idioma, secoes[0]['ref'])}"
    descricao = (
        f"{longo['titulo'][idioma]}\n\n"
        f"{cfg['rotulo_capitulos']}\n" + "\n".join(caps) + "\n\n"
        f"{cfg['fonte_texto']}.\n\n{cfg['cta']}\n\n{cfg['hashtags']}"
    )
    return {
        "arquivo": video,
        "titulo": longo["titulo"][idioma],
        "descricao": descricao,
        "tags": cfg["tags"],
        "thumb": thumb,
        "duracao_s": round(dur, 1),
        "referencia": ", ".join(biblia.ref_exibicao(idioma, r)
                                for r in longo["refs"]),
        "tipo_item": "longo",
    }
