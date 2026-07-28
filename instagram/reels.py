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

CAUDA = 0.35            # silêncio no fim quebra a emenda do loop (era 1,2s)
PAUSA = 0.7             # respiro entre gancho→versículo e entre repetições
CURTO_PALAVRAS = 16    # versículo com menos palavras é narrado 2x (loop do feed)
IDIOMA = "pt"

# GANCHO falado+escrito no 1º segundo. Em 2026, 50% decidem em 1,7s e o gancho
# dos 3 primeiros segundos é a maior alavanca de alcance (Reel com hold >60%
# alcança 5-10x mais). O versículo entrava direto — agora entra um gancho antes.
# A lista nasceu aqui e em 27/07/2026 mudou para `nucleo/idiomas.GANCHOS`, que
# é a mesma coisa nos 3 idiomas e agora também alimenta o Short do YouTube.
# Ordem preservada: o gancho é escolhido por seed do item.
GANCHOS_VIDEO = idiomas.GANCHOS[IDIOMA]


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


def montar_reel(item: dict, marca: str, outdir: Path) -> dict:
    """Renderiza o Reel de um `item` do banco. Três tipos:

    - versiculo: {tipo, ref}
    - historia:  {tipo, ref, gancho, capa_titulo, ref_disp}  (texto bíblico +
                 gancho narrativo nosso)
    - oracao:    {tipo, slug, texto, gancho, capa_titulo}     (texto original nosso)

    Todos abrem com o GANCHO (1º segundo, falado+escrito) antes do conteúdo — é
    o que segura os 3 primeiros segundos, onde metade decide continuar ou rolar.
    Devolve {arquivo, capa, ref_disp, texto, fonte, duracao_s}.
    """
    cfg = idiomas.CONFIG[IDIOMA]
    outdir.mkdir(parents=True, exist_ok=True)
    tipo = item.get("tipo", "versiculo")
    chave = item.get("ref") or item.get("slug") or item.get("capa_titulo") or "x"

    if tipo == "oracao":
        texto = item["texto"]
        gancho = item.get("gancho", "Faça esta oração. 🙏")
        capa_titulo = item.get("capa_titulo", "ORAÇÃO")
        ref_disp = capa_titulo.capitalize()
        fonte = ""                        # oração é texto NOSSO, não Bíblia
    else:  # versiculo ou historia (texto bíblico em domínio público)
        versos = biblia.carregar_versos(IDIOMA, item["ref"])
        texto = " ".join(t for _, t in versos)
        gancho = item.get("gancho") or \
            GANCHOS_VIDEO[_seed(chave, "hookv") % len(GANCHOS_VIDEO)]
        capa_titulo = item.get("capa_titulo") or biblia.cabecalho(IDIOMA, item["ref"])
        ref_disp = item.get("ref_disp") or biblia.ref_exibicao(IDIOMA, item["ref"])
        fonte = "Bíblia Livre"

    # GANCHO + conteúdo. Texto curto entra 2x (loop do feed / meditação).
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

    # topo do vídeo = capa_titulo (SALMO 23 / DAVI E GOLIAS / ORAÇÃO DA NOITE)
    legendas.ass_short(outdir / "legenda.ass", blocos, capa_titulo, marca, dur)

    da_casa = imagens.escolher_da_biblioteca(1, _seed(chave, "fundo"))
    info_img = da_casa[0] if da_casa else None
    img = _baixar_imagem(info_img, outdir / "fundo.jpg")
    # abre direto no gancho (sem preto), fecha em corte seco e o fundo volta ao
    # enquadramento inicial — o Reel foi feito para dar a segunda passada
    video = render.render_short(outdir, voz.name, "legenda.ass", img, dur,
                                _seed(chave, "reel"), saida="reel.mp4")

    # Capa DESENHADA (cover_url): a capa da grade/feed, à parte do vídeo.
    capa_img = capa.gerar_capa(capa_titulo, _gancho(texto),
                               outdir / "capa.jpg", _seed(chave, "capa"))

    return {
        "arquivo": video,
        "capa": capa_img,
        "ref_disp": ref_disp,
        "texto": texto,
        "fonte": fonte,
        "duracao_s": round(dur, 1),
    }
