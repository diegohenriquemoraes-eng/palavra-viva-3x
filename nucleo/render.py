"""Render dos vídeos com ffmpeg: Short 1080x1920 e longo 1920x1080.

Short: 1 imagem de fundo com Ken Burns lento (ou gradiente da casa como
fallback) + narração + legenda ASS queimada. Sem música.

Longo: sequência de imagens com Ken Burns, narração versículo a versículo e
pad ambiente procedural mixado baixinho. Preset mais rápido (veryfast) porque
o runner do Actions tem 2 núcleos e o vídeo tem 10+ minutos.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from . import idiomas

FPS = 30


def _fontsdir(pasta: Path) -> str:
    """Caminho RELATIVO à pasta de trabalho: 'C:' dentro de filtro ffmpeg
    quebra o parser (o dois-pontos vira separador de opção)."""
    return Path(os.path.relpath(idiomas.FONTES_DIR, pasta)).as_posix()


def _run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def _zoompan(dur: float, w: int, h: int, seed: int) -> str:
    frames = int(dur * FPS)
    # alterna zoom-in/zoom-out pelo seed para não ficar tudo igual
    if seed % 2 == 0:
        z = f"zoom='min(1.10,1+0.10*on/{frames})'"
    else:
        z = f"zoom='max(1.0,1.10-0.10*on/{frames})'"
    return (
        f"scale={int(w * 1.3)}:{int(h * 1.3)}:force_original_aspect_ratio=increase,"
        f"crop={int(w * 1.3)}:{int(h * 1.3)},"
        f"zoompan={z}:x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d=1:"
        f"s={w}x{h}:fps={FPS},"
        "eq=brightness=-0.16:saturation=0.88,vignette=PI/4.5"
    )


def render_short(pasta: Path, voz: str, ass: str, imagem: Path | None,
                 dur: float, seed: int, saida: str = "short.mp4") -> Path:
    fontsdir = _fontsdir(pasta)
    if imagem is not None:
        entrada = ["-loop", "1", "-t", f"{dur:.2f}", "-i", imagem.name]
        fundo = _zoompan(dur, 1080, 1920, seed)
    else:
        entrada = ["-f", "lavfi", "-i",
                   (f"gradients=s=1080x1920:c0=0x0B1230:c1=0x1B0F3B:c2=0x2A1450:"
                    f"nb_colors=3:seed={seed}:speed=0.015:r={FPS}:d={dur:.2f}")]
        fundo = "null"
    filtro = (
        f"[0:v]{fundo},ass={ass}:fontsdir='{fontsdir}',"
        f"fade=t=in:st=0:d=0.4,fade=t=out:st={dur - 0.6:.2f}:d=0.6,"
        f"format=yuv420p[v];[1:a]apad=whole_dur={dur:.2f}[a]"
    )
    _run(["ffmpeg", "-y", "-loglevel", "error", *entrada, "-i", voz,
          "-filter_complex", filtro, "-map", "[v]", "-map", "[a]",
          "-t", f"{dur:.2f}", "-c:v", "libx264", "-preset", "medium",
          "-crf", "20", "-c:a", "aac", "-b:a", "160k",
          "-movflags", "+faststart", saida], pasta)
    return pasta / saida


FPS_ESTATICO = 15      # tela parada não precisa de 30 fps: metade dos frames,
                       # metade do tempo de encode, nenhum prejuízo visível


def render_longo_estatico(pasta: Path, voz_wav: str, pad_wav: str, ass: str,
                          imagem: Path | None, dur: float, seed: int,
                          saida: str = "longo.mp4") -> Path:
    """Longo com fundo ESCURO e parado + legenda queimada — o formato do nicho.

    Conferido em 24/07/2026 nos dois líderes de "salmos para dormir" em
    português: "Salmo 91 91 vezes" (48M views, 3h48) é tela preta com o
    versículo no rodapé, e "Os 6 Salmos mais poderosos" (10,5M, 3h16) é fundo
    escuro quase imóvel com o versículo no rodapé. Ninguém anima imagem: quem
    põe para dormir não quer o quarto piscando.

    Para nós, a economia é o que destrava a duração. O caminho com imagens
    renderiza um clipe com zoompan por imagem (30 deles numa hora de vídeo);
    aqui é UMA passada, sem zoompan, a 15 fps e com -tune stillimage.
    """
    fontsdir = _fontsdir(pasta)
    if imagem is not None:
        entrada = ["-loop", "1", "-framerate", str(FPS_ESTATICO),
                   "-t", f"{dur:.2f}", "-i", imagem.name]
        # a imagem entra bem escura: é fundo de quarto no escuro, não paisagem
        fundo = (f"scale=1920:1080:force_original_aspect_ratio=increase,"
                 f"crop=1920:1080,eq=brightness=-0.34:saturation=0.7,"
                 f"vignette=PI/4,fps={FPS_ESTATICO}")
    else:
        entrada = ["-f", "lavfi", "-i",
                   f"color=c=0x05070F:s=1920x1080:r={FPS_ESTATICO}:d={dur:.2f}"]
        fundo = "null"
    filtro = (
        f"[0:v]{fundo},ass={ass}:fontsdir='{fontsdir}',"
        f"fade=t=in:st=0:d=1.0,fade=t=out:st={dur - 2.0:.2f}:d=2.0,"
        f"format=yuv420p[v];"
        f"[1:a]apad=whole_dur={dur:.2f},volume=1.0[nar];"
        f"[2:a]apad=whole_dur={dur:.2f},volume=0.55[pad];"
        f"[nar][pad]amix=inputs=2:duration=first:normalize=0,"
        f"afade=t=out:st={dur - 3.0:.2f}:d=3.0[a]"
    )
    _run(["ffmpeg", "-y", "-loglevel", "error", *entrada,
          "-i", voz_wav, "-i", pad_wav,
          "-filter_complex", filtro, "-map", "[v]", "-map", "[a]",
          "-t", f"{dur:.2f}", "-c:v", "libx264", "-preset", "veryfast",
          "-tune", "stillimage", "-crf", "24", "-g", str(FPS_ESTATICO * 10),
          "-c:a", "aac", "-b:a", "160k",
          "-movflags", "+faststart", saida], pasta)
    return pasta / saida


def render_longo(pasta: Path, voz_wav: str, pad_wav: str, ass: str,
                 imagens: list[Path], dur: float, seed: int,
                 saida: str = "longo.mp4") -> Path:
    """Render em 3 etapas, uma imagem de cada vez.

    A versão anterior abria as 30 imagens como entradas simultâneas do ffmpeg
    e montava um filtro com 30 zoompan em paralelo. Funcionou com o vídeo de
    8 min (17 imagens) e MORREU no de 16 min no runner do Actions (2 núcleos):
    "Nothing was written into output file" / exit 234 — o zoompan segura frames
    grandes na memória e 30 deles ao mesmo tempo estouram a máquina.

    Agora cada imagem vira um clipe curto sozinha (memória constante, não
    importa se são 10 ou 40), os clipes são concatenados por cópia (sem
    recodificar) e só a última passada junta legenda e áudio.
    """
    fontsdir = _fontsdir(pasta)
    n = len(imagens)
    if n == 0:
        raise SystemExit("render_longo precisa de pelo menos 1 imagem")
    seg = dur / n

    # 1) um clipe por imagem
    nomes = []
    for i, img in enumerate(imagens):
        nome = f"bg{i:03d}.mp4"
        _run(["ffmpeg", "-y", "-loglevel", "error",
              "-loop", "1", "-t", f"{seg:.3f}", "-i", img.name,
              "-vf", _zoompan(seg, 1920, 1080, seed + i),
              "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
              "-pix_fmt", "yuv420p", nome], pasta)
        nomes.append(nome)

    # 2) concatenação sem recodificar
    (pasta / "bg.txt").write_text(
        "".join(f"file '{nome}'\n" for nome in nomes), encoding="utf-8")
    _run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
          "-i", "bg.txt", "-c", "copy", "bg.mp4"], pasta)

    # 3) legenda queimada + mixagem narração/pad
    filtro = (
        f"[0:v]ass={ass}:fontsdir='{fontsdir}',"
        f"fade=t=in:st=0:d=1.0,fade=t=out:st={dur - 2.0:.2f}:d=2.0,"
        f"format=yuv420p[v];"
        f"[1:a]apad=whole_dur={dur:.2f},volume=1.0[nar];"
        f"[2:a]apad=whole_dur={dur:.2f},volume=0.55[pad];"
        f"[nar][pad]amix=inputs=2:duration=first:normalize=0,"
        f"afade=t=out:st={dur - 3.0:.2f}:d=3.0[a]"
    )
    _run(["ffmpeg", "-y", "-loglevel", "error",
          "-i", "bg.mp4", "-i", voz_wav, "-i", pad_wav,
          "-filter_complex", filtro, "-map", "[v]", "-map", "[a]",
          "-t", f"{dur:.2f}", "-c:v", "libx264", "-preset", "veryfast",
          "-crf", "21", "-c:a", "aac", "-b:a", "160k",
          "-movflags", "+faststart", saida], pasta)

    for nome in nomes:  # os clipes intermediários não servem mais
        (pasta / nome).unlink(missing_ok=True)
    (pasta / "bg.mp4").unlink(missing_ok=True)
    return pasta / saida


def repetir_video(pasta: Path, arquivo: str, vezes: int,
                  saida: str = "longo.mp4") -> Path:
    """Repete o vídeo pronto N vezes SEM recodificar (concat -c copy).

    É assim que se chega às horas de duração que o nicho exige gastando quase
    nada de máquina: o ciclo é renderizado uma vez (imagem, narração e legenda
    juntas) e só o container é repetido. Benchmark de 19/07/2026 sobre 252
    vídeos: mediana dos longos é 38 min (es), 165 min (en) e 68 min (pt) — o
    campeão do nicho é literalmente "SALMO 91 91 VEZES", 228 min. Repetir é o
    formato, não um truque: o público deixa rolando a noite inteira.
    """
    if vezes <= 1:
        return pasta / arquivo
    lista = pasta / "ciclos.txt"
    lista.write_text("".join(f"file '{arquivo}'\n" for _ in range(vezes)),
                     encoding="utf-8")
    _run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
          "-i", "ciclos.txt", "-c", "copy", "-movflags", "+faststart",
          saida], pasta)
    return pasta / saida
