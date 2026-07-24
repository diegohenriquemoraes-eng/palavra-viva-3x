"""Monta um Reel vertical (1080x1920) de um versículo em português.

Reaproveita o núcleo do pipeline do YouTube: mesma Bíblia (Bíblia Livre,
domínio público), mesma voz TTS (pt-BR-Antonio), mesma legenda ASS queimada,
mesmos fundos curados da casa e o MESMO render de Short (que já sai em 9:16).
O que muda é a LEGENDA DO POST (caption), pensada para o Instagram — ver
`instagram/legenda.py`.

Regra editorial idêntica à do canal (inegociável): só texto bíblico em
domínio público, sem pregação, imagem CC0/PD ou gradiente da casa, sem música.
"""

from __future__ import annotations

import sys
import zlib
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from nucleo import biblia, idiomas, imagens, legendas, render, tts  # noqa: E402

CAUDA = 1.2
MIN_REEL_S = 15.0        # abaixo disto o versículo é narrado 2x (formato do nicho)
PAUSA_REPETICAO = 1.6
IDIOMA = "pt"


def _seed(ref: str, extra: str) -> int:
    return zlib.crc32(f"{ref}-{extra}".encode()) % 999_983


def _baixar_imagem(info: dict | None, destino: Path) -> Path | None:
    if not info:
        return None
    local = info.get("caminho")
    if local and Path(local).exists():
        import shutil
        shutil.copyfile(local, destino)
        return destino
    if info.get("url") and imagens.baixar(info["url"], destino):
        return destino
    return None


def montar_reel(ref: str, marca: str, outdir: Path) -> dict:
    """Renderiza o Reel do versículo `ref` (ex.: 'Psalms 23:1-3').

    Devolve {arquivo, ref_disp, texto, duracao_s}. A caption é montada à parte
    (legenda.py), porque depende do afiliado e das hashtags do config.
    """
    cfg = idiomas.CONFIG[IDIOMA]
    outdir.mkdir(parents=True, exist_ok=True)

    versos = biblia.carregar_versos(IDIOMA, ref)
    texto = " ".join(t for _, t in versos)

    mp3 = outdir / "voz.mp3"
    palavras = tts.narrar(texto, cfg["voz"], cfg["rate_short"], mp3)
    legendas.alinhar_display(texto, palavras)
    blocos = legendas.agrupar(palavras)
    dur = max(tts.duracao_audio(mp3), blocos[-1]["fim"]) + CAUDA

    # Versículo curto rende Reel de ~9s, fino demais para o loop do feed. Nesses
    # casos o texto é narrado DUAS vezes com pausa — repetição para meditar,
    # formato consagrado do nicho, não enchimento (igual ao Short do YouTube).
    if dur < MIN_REEL_S:
        segmentos, dur_voz = tts.narrar_versos(
            [(1, texto), (2, texto)], cfg["voz"], cfg["rate_short"],
            PAUSA_REPETICAO, outdir / "voz.wav", outdir / "tts")
        blocos = []
        for seg in segmentos:
            legendas.alinhar_display(seg["texto"], seg["palavras"])
            blocos += legendas.agrupar(seg["palavras"])
        mp3 = outdir / "voz.wav"
        dur = dur_voz + CAUDA

    cab = biblia.cabecalho(IDIOMA, ref)
    legendas.ass_short(outdir / "legenda.ass", blocos, cab, marca, dur)

    da_casa = imagens.escolher_da_biblioteca(1, _seed(ref, "fundo"))
    info_img = da_casa[0] if da_casa else None
    img = _baixar_imagem(info_img, outdir / "fundo.jpg")
    video = render.render_short(outdir, Path(mp3).name, "legenda.ass", img, dur,
                                _seed(ref, "reel"), saida="reel.mp4")

    return {
        "arquivo": video,
        "ref_disp": biblia.ref_exibicao(IDIOMA, ref),
        "texto": texto,
        "duracao_s": round(dur, 1),
    }
