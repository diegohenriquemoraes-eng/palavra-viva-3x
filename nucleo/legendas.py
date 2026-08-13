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
Style: Cta,Bebas Neue,62,&H007AC9E8,&H007AC9E8,&H00251505,&H80000000,0,0,0,0,100,100,5,0,1,3,1,2,40,40,215,1

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
Style: Cta,Bebas Neue,54,&H007AC9E8,&H007AC9E8,&H00251505,&H80000000,0,0,0,0,100,100,5,0,1,3,1,2,40,40,260,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


CTA_SHORT_S = 3.2       # quanto tempo a CTA fica na tela, no fim do Short


def ass_short(path: Path, blocos: list[dict], cabecalho: str, marca: str,
              dur: float, cta: str = "") -> None:
    linhas = [_ESTILOS_SHORT]
    fim = _ts(dur)
    linhas.append(f"Dialogue: 0,0:00:00.00,{fim},Ref,,0,0,0,,{cabecalho}\n")
    linhas.append(f"Dialogue: 0,0:00:00.00,{fim},Marca,,0,0,0,,{marca}\n")
    # CTA SOBREPOSTA aos últimos segundos: não estende o vídeo, para não meter
    # silêncio no fim e quebrar a emenda do loop (ver render.render_short).
    # Em Short muito curto ela pega o vídeo quase inteiro — é o que se quer,
    # porque aí não existe "fim" separado da segunda passada.
    if cta:
        linhas.append(
            f"Dialogue: 0,{_ts(max(0.0, dur - CTA_SHORT_S))},{fim},"
            f"Cta,,0,0,0,,{cta}\n")
    for i, b in enumerate(blocos):
        if i == 0:
            # o gancho tem que estar ESCRITO no frame zero: o TTS começa a
            # falar por volta de 0,1s e o vídeo abria com 3 frames sem texto
            b = {**b, "ini": 0.0}
        linhas.append(
            f"Dialogue: 0,{_ts(b['ini'])},{_ts(b['fim'])},Verso,,0,0,0,,{b['texto']}\n"
        )
    path.write_text("".join(linhas), encoding="utf-8-sig")


_ESTILOS_CINE = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Gancho,Montserrat,112,&H00FFFFFF,&H00FFFFFF,&H00140A02,&HB4000000,-1,0,0,0,100,100,0,0,1,7,4,5,70,70,0,1
Style: Verso,Montserrat,96,&H00F5F0EA,&H00F5F0EA,&H00140A02,&HB4000000,-1,0,0,0,100,100,0,0,1,6,3,5,80,80,0,1
Style: Fecho,Montserrat,104,&H00EBC38C,&H00EBC38C,&H00140A02,&HB4000000,-1,0,0,0,100,100,0,0,1,7,4,5,70,70,0,1
Style: Ref,Bebas Neue,60,&H00EBC38C,&H00EBC38C,&H00140A02,&H80000000,0,0,0,0,100,100,8,0,1,3,1,8,40,40,150,1
Style: Marca,Montserrat,34,&H00A8BACB,&H00A8BACB,&H00140A02,&H80000000,0,0,0,0,100,100,3,0,1,2,0,2,40,40,120,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

FADE_CINE = "{\\fad(180,160)}"


def ass_reel_cine(path: Path, blocos: list[dict], cabecalho: str, marca: str,
                  dur: float) -> None:
    """Legenda do Reel sem narração: um bloco de cada vez, grande e centrado.

    Diferenças que existem por causa da medição de 13/08/2026 (Reels do
    @psicologiafria.br com 6 a 118 views, contra 21-58 mil dos perfis de
    referência do nicho):

    - **Corpo bem maior** (96-112 contra 86) e contorno mais grosso: no feed o
      vídeo é visto em miniatura, e quem lê de relance não lê linha fina.
    - **Três estilos** — Gancho, Verso e Fecho. O fecho entra em azul-gelo:
      marca visualmente a virada do micro-roteiro, que é o motivo de ficar até
      o fim.
    - **Fade curto por bloco** (`\\fad`): sem a voz para costurar, o corte seco
      de texto pisca. O fade é o que faz o Reel parecer editado, não gerado.
    """
    linhas = [_ESTILOS_CINE]
    fim = _ts(dur)
    linhas.append(f"Dialogue: 0,0:00:00.00,{fim},Ref,,0,0,0,,{cabecalho}\n")
    linhas.append(f"Dialogue: 0,0:00:00.00,{fim},Marca,,0,0,0,,{marca}\n")
    for i, b in enumerate(blocos):
        ini = 0.0 if i == 0 else b["ini"]   # nada de frame vazio na abertura
        estilo = b.get("estilo", "Verso")
        linhas.append(
            f"Dialogue: 0,{_ts(ini)},{_ts(min(b['fim'], dur))},{estilo},,0,0,0,,"
            f"{FADE_CINE}{b['texto']}\n")
    path.write_text("".join(linhas), encoding="utf-8-sig")


def _ts_srt(seg: float) -> str:
    h = int(seg // 3600)
    m = int(seg % 3600 // 60)
    s = int(seg % 60)
    ms = int(round((seg - int(seg)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def srt_longo(path: Path, secoes: list[dict]) -> None:
    """Mesma legenda do vídeo, em .srt, para subir como faixa de legenda.

    A legenda queimada é PIXEL: o YouTube não lê o que está nela. Quem indexa
    (busca, sugestão, tradução automática) é a faixa de legenda enviada pela
    API. Como o texto e os tempos já existem para queimar, gerar o .srt sai
    de graça — o custo é só a cota de captions.insert na publicação.
    """
    linhas, n = [], 0
    for s in secoes:
        for b in s["blocos"]:
            if b["fim"] <= b["ini"]:
                continue
            n += 1
            linhas.append(f"{n}\n{_ts_srt(b['ini'])} --> {_ts_srt(b['fim'])}\n"
                          f"{b['texto']}\n\n")
    path.write_text("".join(linhas), encoding="utf-8")


CTA_LONGO_S = 12.0      # a CTA do longo fica mais tempo: quem chegou ao fim
                        # de 30 min não está deslizando, está sentado


def ass_longo(path: Path, secoes: list[dict], marca: str, dur: float,
              cta: str = "") -> None:
    """secoes: [{"cabecalho": str, "ini": s, "fim": s, "blocos": [...]}]"""
    linhas = [_ESTILOS_LONGO]
    linhas.append(f"Dialogue: 0,0:00:00.00,{_ts(dur)},Marca,,0,0,0,,{marca}\n")
    # Só chega aqui quem NÃO é conteúdo para dormir (ver fabrica.montar_longo).
    if cta:
        linhas.append(
            f"Dialogue: 0,{_ts(max(0.0, dur - CTA_LONGO_S))},{_ts(dur)},"
            f"Cta,,0,0,0,,{cta}\n")
    for s in secoes:
        linhas.append(
            f"Dialogue: 0,{_ts(s['ini'])},{_ts(s['fim'])},Ref,,0,0,0,,{s['cabecalho']}\n"
        )
        for b in s["blocos"]:
            linhas.append(
                f"Dialogue: 0,{_ts(b['ini'])},{_ts(b['fim'])},Verso,,0,0,0,,{b['texto']}\n"
            )
    path.write_text("".join(linhas), encoding="utf-8-sig")
