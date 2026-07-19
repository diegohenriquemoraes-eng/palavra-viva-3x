"""Legendas ASS queimadas no vídeo (não gastam quota de captions da API).

Estilo herdado do Palabra Viva: bloco central grande sincronizado por palavra
nos Shorts; nos longos, texto na parte de baixo (para as imagens respirarem)
com a referência da seção no topo.

As fontes são as do repo (marca/fontes), passadas ao ffmpeg via fontsdir —
assim o vídeo sai IGUAL no PC e no runner do GitHub.
"""

from __future__ import annotations

from pathlib import Path


def _ts(seg: float) -> str:
    h = int(seg // 3600)
    m = int(seg % 3600 // 60)
    s = seg % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def agrupar(palavras: list[dict], largura: int = 20, max_palavras: int = 5
            ) -> list[dict]:
    """Palavras -> blocos de legenda (~20 caracteres, quebra em pontuação)."""
    bloques, atual = [], []
    for p in palavras:
        atual.append(p)
        linha = " ".join(w["disp"] for w in atual)
        corta = p["disp"][-1:] in ".;:?!," and len(linha) >= 12
        if len(linha) >= largura or corta or len(atual) >= max_palavras:
            bloques.append(atual)
            atual = []
    if atual:
        bloques.append(atual)

    out = []
    for i, b in enumerate(bloques):
        ini = b[0]["t"]
        if i + 1 < len(bloques):
            fim = bloques[i + 1][0]["t"]
        else:
            fim = b[-1]["t"] + b[-1]["d"] + 0.8
        out.append({"ini": ini, "fim": fim,
                    "texto": " ".join(w["disp"] for w in b)})
    return out


def alinhar_display(texto: str, palavras: list[dict]) -> None:
    """Recupera a pontuação: o boundary traz só a palavra, o texto tem as vírgulas."""
    pos = 0
    for p in palavras:
        i = texto.find(p["w"], pos)
        if i < 0:
            p["disp"] = p["w"]
            continue
        j = i + len(p["w"])
        while j < len(texto) and not texto[j].isspace():
            j += 1
        p["disp"] = texto[i:j]
        pos = j


_ESTILOS_SHORT = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Verso,Montserrat,86,&H00FFFFFF,&H00FFFFFF,&H00251505,&H80000000,-1,0,0,0,100,100,0,0,1,5,2,5,60,60,0,1
Style: Ref,Bebas Neue,64,&H007AC9E8,&H007AC9E8,&H00251505,&H80000000,0,0,0,0,100,100,7,0,1,3,1,8,40,40,170,1
Style: Marca,Montserrat,38,&H00C8C0B0,&H00C8C0B0,&H00251505,&H80000000,0,0,0,0,100,100,3,0,1,2,0,2,40,40,120,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

_ESTILOS_LONGO = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Verso,Montserrat,58,&H00FFFFFF,&H00FFFFFF,&H00251505,&H80000000,-1,0,0,0,100,100,0,0,1,4,2,2,220,220,80,1
Style: Ref,Bebas Neue,72,&H007AC9E8,&H007AC9E8,&H00251505,&H80000000,0,0,0,0,100,100,6,0,1,3,1,8,40,40,50,1
Style: Marca,Montserrat,32,&H00C8C0B0,&H00C8C0B0,&H00251505,&H80000000,0,0,0,0,100,100,2,0,1,2,0,3,40,40,40,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def ass_short(path: Path, blocos: list[dict], cabecalho: str, marca: str,
              dur: float) -> None:
    linhas = [_ESTILOS_SHORT]
    fim = _ts(dur)
    linhas.append(f"Dialogue: 0,0:00:00.00,{fim},Ref,,0,0,0,,{cabecalho}\n")
    linhas.append(f"Dialogue: 0,0:00:00.00,{fim},Marca,,0,0,0,,{marca}\n")
    for b in blocos:
        linhas.append(
            f"Dialogue: 0,{_ts(b['ini'])},{_ts(b['fim'])},Verso,,0,0,0,,{b['texto']}\n"
        )
    path.write_text("".join(linhas), encoding="utf-8-sig")


def ass_longo(path: Path, secoes: list[dict], marca: str, dur: float) -> None:
    """secoes: [{"cabecalho": str, "ini": s, "fim": s, "blocos": [...]}]"""
    linhas = [_ESTILOS_LONGO]
    linhas.append(f"Dialogue: 0,0:00:00.00,{_ts(dur)},Marca,,0,0,0,,{marca}\n")
    for s in secoes:
        linhas.append(
            f"Dialogue: 0,{_ts(s['ini'])},{_ts(s['fim'])},Ref,,0,0,0,,{s['cabecalho']}\n"
        )
        for b in s["blocos"]:
            linhas.append(
                f"Dialogue: 0,{_ts(b['ini'])},{_ts(b['fim'])},Verso,,0,0,0,,{b['texto']}\n"
            )
    path.write_text("".join(linhas), encoding="utf-8-sig")
