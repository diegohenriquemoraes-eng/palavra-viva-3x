"""Monta um Reel vertical (1080x1920) do perfil Psicologia Fria.

Reaproveita o núcleo do pipeline do YouTube: mesma voz TTS pt-BR, mesma
legenda ASS queimada, mesmos fundos da biblioteca da casa e o MESMO render de
Short (que já sai em 9:16). O CONTEÚDO agora é 100% original do canal
(instagram/frases.json): micro-roteiros de psicologia/estoicismo escritos por
nós — exigência de originalidade do Instagram (2026) e zero risco de direitos.

O que muda vs. a era bíblica: não há mais Bíblia nem tipos versículo/história/
oração — todo item é uma "frase" {slug, tipo, titulo, gancho, texto}.
"""

from __future__ import annotations

import sys
import zlib
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from nucleo import idiomas, imagens, legendas, render, tts  # noqa: E402

from instagram import capa  # noqa: E402

CAUDA = 0.35            # silêncio no fim quebra a emenda do loop
PAUSA = 0.7             # respiro entre gancho→texto
CURTO_PALAVRAS = 16     # texto com menos palavras é narrado 2x (loop do feed)
IDIOMA = "pt"


def _seed(chave: str, extra: str) -> int:
    return zlib.crc32(f"{chave}-{extra}".encode()) % 999_983


def _frase_capa(texto: str) -> str:
    """1ª frase do texto, para a capa. Corta na pontuação forte, senão na
    vírgula, senão em ~70 caracteres — sempre em limite de palavra."""
    for sep in (". ", "; ", "! ", "? "):
        i = texto.find(sep)
        if 0 < i <= 80:
            return texto[:i] + "."
    i = texto.find(", ")
    if 40 <= i <= 80:
        return texto[:i]
    return texto[:70].rsplit(" ", 1)[0] if len(texto) > 70 else texto


def _esfriar_cores(ass: Path) -> None:
    """Troca o dourado da era bíblica (estilo do núcleo, compartilhado com o
    YouTube) pelo azul-gelo da identidade Psicologia Fria — só neste pipeline.
    Cores ASS são &HAABBGGRR (BGR)."""
    t = ass.read_text(encoding="utf-8-sig")
    t = t.replace("&H007AC9E8", "&H00EBC38C")   # dourado -> azul-gelo
    t = t.replace("&H00C8C0B0", "&H00BEAA96")   # cinza-quente -> cinza-frio
    ass.write_text(t, encoding="utf-8-sig")


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
    """Renderiza o Reel de um item de instagram/frases.json:

        {slug, tipo, titulo, gancho, texto}

    Abre com o GANCHO (1º segundo, falado+escrito) antes do texto — é o que
    segura os 3 primeiros segundos, onde metade decide continuar ou rolar.
    Devolve {arquivo, capa, ref_disp, texto, fonte, duracao_s}.
    """
    cfg = idiomas.CONFIG[IDIOMA]
    outdir.mkdir(parents=True, exist_ok=True)
    chave = item.get("slug") or item.get("titulo") or "x"

    texto = item["texto"]
    gancho = item["gancho"]
    capa_titulo = item.get("titulo", "PSICOLOGIA FRIA").upper()

    # GANCHO + texto. Texto curto entra 2x (loop do feed).
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

    # topo do vídeo = titulo do item (O SILÊNCIO / MEMENTO MORI / ...)
    legendas.ass_short(outdir / "legenda.ass", blocos, capa_titulo, marca, dur)
    _esfriar_cores(outdir / "legenda.ass")

    da_casa = imagens.escolher_da_biblioteca(1, _seed(chave, "fundo"))
    info_img = da_casa[0] if da_casa else None
    img = _baixar_imagem(info_img, outdir / "fundo.jpg")
    # abre direto no gancho (sem preto), fecha em corte seco e o fundo volta ao
    # enquadramento inicial — o Reel foi feito para dar a segunda passada
    video = render.render_short(outdir, voz.name, "legenda.ass", img, dur,
                                _seed(chave, "reel"), saida="reel.mp4")

    # Capa DESENHADA (cover_url): a capa da grade/feed, à parte do vídeo.
    capa_img = capa.gerar_capa(capa_titulo, gancho,
                               outdir / "capa.jpg", _seed(chave, "capa"))

    return {
        "arquivo": video,
        "capa": capa_img,
        "ref_disp": capa_titulo,
        "texto": texto,
        "fonte": "",
        "duracao_s": round(dur, 1),
    }
