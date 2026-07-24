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

from instagram import capa  # noqa: E402

CAUDA = 1.2
PAUSA = 0.7             # respiro entre gancho→versículo e entre repetições
CURTO_PALAVRAS = 16    # versículo com menos palavras é narrado 2x (loop do feed)
IDIOMA = "pt"

# GANCHO falado+escrito no 1º segundo. Em 2026, 50% decidem em 1,7s e o gancho
# dos 3 primeiros segundos é a maior alavanca de alcance (Reel com hold >60%
# alcança 5-10x mais). O versículo entrava direto — agora entra um gancho antes.
# Curtos de propósito (~1,5-2,5s falados). Giram por versículo, sem aleatório.
GANCHOS_VIDEO = [
    "Pra você que está cansado.",
    "Se apareceu pra você, não foi por acaso.",
    "Ouça isto antes de dormir.",
    "Deus quer te falar agora.",
    "Respire e leia devagar.",
    "Guarde esta promessa no coração.",
    "Não role sem ler isto.",
    "A Palavra que você precisava hoje.",
    "Uma promessa de Deus pra você.",
    "Deixe Deus acalmar o seu coração.",
    "Isto aqui é pra você, hoje.",
    "Quando a ansiedade bater, lembre disto.",
]


def _seed(ref: str, extra: str) -> int:
    return zlib.crc32(f"{ref}-{extra}".encode()) % 999_983


def _gancho(texto: str) -> str:
    """1ª frase do versículo, para a capa. Corta na pontuação forte, senão na
    vírgula, senão em ~70 caracteres — sempre em limite de palavra."""
    for sep in (". ", "; ", "! ", "? "):
        i = texto.find(sep)
        if 0 < i <= 80:
            return texto[:i]
    i = texto.find(", ")
    if 40 <= i <= 80:
        return texto[:i]
    return texto[:70].rsplit(" ", 1)[0] if len(texto) > 70 else texto


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
    gancho = GANCHOS_VIDEO[_seed(ref, "hookv") % len(GANCHOS_VIDEO)]

    # Estrutura: GANCHO (1º) + versículo. Versículo curto entra 2x (loop do
    # feed / meditação). O gancho é o que segura os 3 primeiros segundos —
    # onde metade do público decide continuar ou rolar.
    partes = [(0, gancho), (1, texto)]
    if len(texto.split()) < CURTO_PALAVRAS:
        partes.append((2, texto))

    voz = outdir / "voz.wav"
    segmentos, dur_voz = tts.narrar_versos(partes, cfg["voz"], cfg["rate_short"],
                                           PAUSA, voz, outdir / "tts")
    dur = dur_voz + CAUDA

    blocos = []
    for seg in segmentos:
        legendas.alinhar_display(seg["texto"], seg["palavras"])
        blocos += legendas.agrupar(seg["palavras"])

    cab = biblia.cabecalho(IDIOMA, ref)
    legendas.ass_short(outdir / "legenda.ass", blocos, cab, marca, dur)

    da_casa = imagens.escolher_da_biblioteca(1, _seed(ref, "fundo"))
    info_img = da_casa[0] if da_casa else None
    img = _baixar_imagem(info_img, outdir / "fundo.jpg")
    # fade_in=0: o Reel abre DIRETO no gancho, sem preto no 1º frame
    video = render.render_short(outdir, voz.name, "legenda.ass", img, dur,
                                _seed(ref, "reel"), saida="reel.mp4", fade_in=0.0)

    # Capa DESENHADA (cover_url): a capa da grade/feed, à parte do vídeo.
    capa_img = capa.gerar_capa(biblia.cabecalho(IDIOMA, ref), _gancho(texto),
                               outdir / "capa.jpg", _seed(ref, "capa"))

    return {
        "arquivo": video,
        "capa": capa_img,
        "ref_disp": biblia.ref_exibicao(IDIOMA, ref),
        "texto": texto,
        "duracao_s": round(dur, 1),
    }
