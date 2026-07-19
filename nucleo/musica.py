"""Trilha ambiente PROCEDURAL para os vídeos longos — zero copyright.

Em vez de biblioteca de música (que sempre carrega risco de claim), o pad é
sintetizado aqui: acordes menores suaves em camadas de senos com envelope
lento. É nosso, determinístico (seed) e gratuito. Shorts seguem SEM música
(regra editorial herdada do Palabra Viva).

Sai um WAV mono 32 kHz; o render mixa baixinho sob a narração.
"""

from __future__ import annotations

import wave
from pathlib import Path

import numpy as np

SR = 32000

# progressões em lá menor (graus como semitons a partir da tônica)
PROGRESSOES = [
    [0, -4, 5, -2],   # Am - F - Dm - G (relativo)
    [0, 5, -4, -2],
    [0, -2, -4, 5],
]
ACORDE_MENOR = [0, 3, 7, 12]
ACORDE_MAIOR = [0, 4, 7, 12]


def _acorde(freq_base: float, semitons: list[int], dur: float,
            rng: np.random.Generator) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n, dtype=np.float32) / SR
    out = np.zeros(n, dtype=np.float32)
    for st in semitons:
        f = freq_base * (2 ** (st / 12))
        detune = rng.uniform(0.9985, 1.0015)
        fase = rng.uniform(0, 2 * np.pi)
        # fundamental + 2º harmônico fraco: pad escuro, sem brilho agressivo
        out += np.sin(2 * np.pi * f * detune * t + fase).astype(np.float32)
        out += 0.35 * np.sin(2 * np.pi * 2 * f * detune * t + fase).astype(np.float32)
    # envelope lento (ataque/queda de 2,5 s) evita cliques na troca de acorde
    env = np.ones(n, dtype=np.float32)
    borda = min(int(2.5 * SR), n // 2)
    rampa = np.linspace(0, 1, borda, dtype=np.float32)
    env[:borda] = rampa
    env[-borda:] = rampa[::-1]
    return out * env


def gerar_pad(dur: float, seed: int, destino: Path) -> Path:
    rng = np.random.default_rng(seed)
    prog = PROGRESSOES[seed % len(PROGRESSOES)]
    base = 110.0 * (2 ** (int(seed) % 5 / 12))  # tônica entre A2 e C#3
    dur_acorde = 18.0
    sobre = 2.5  # sobreposição = crossfade natural dos envelopes

    total = int(dur * SR)
    mix = np.zeros(total + int(dur_acorde * SR), dtype=np.float32)
    pos = 0.0
    i = 0
    while pos < dur:
        grau = prog[i % len(prog)]
        tipo = ACORDE_MENOR if i % len(prog) != 1 else ACORDE_MAIOR
        bloco = _acorde(base * (2 ** (grau / 12)), tipo, dur_acorde, rng)
        ini = int(pos * SR)
        mix[ini:ini + len(bloco)] += bloco
        pos += dur_acorde - sobre
        i += 1
    mix = mix[:total]

    # respiração de volume bem lenta (LFO de ~40 s)
    t = np.arange(total, dtype=np.float32) / SR
    mix *= (0.8 + 0.2 * np.sin(2 * np.pi * t / 40.0 + 1.0)).astype(np.float32)

    pico = np.max(np.abs(mix)) or 1.0
    mix = (mix / pico * 0.22 * 32767).astype(np.int16)

    with wave.open(str(destino), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(mix.tobytes())
    return destino
