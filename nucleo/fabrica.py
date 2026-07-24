"""Monta um item do pacote do dia (short ou longo) num idioma.

O pacote (fila/AAAA-MM-DD-slug/pacote.json) traz refs, títulos por idioma e
URLs de imagem já resolvidas — aqui só se baixa, narra, legenda e renderiza.
O visual (imagens, movimento) é o MESMO nos 3 idiomas; muda áudio, legenda,
título, descrição e thumbnail.
"""

from __future__ import annotations

import math
import re
import shutil
import zlib
from pathlib import Path

from . import biblia, idiomas, imagens, legendas, musica, render, thumbnail, tts

PAUSA_VERSO = 2.0       # silêncio contemplativo entre versículos do longo
                        # (2,0s: leva o longo típico acima dos 8 min de mid-roll)
CAUDA_LONGO = 3.5
CAUDA_SHORT = 1.2
MIN_SHORT_S = 15.0      # abaixo disto o versículo é repetido (ver montar_short)
PAUSA_REPETICAO = 1.6
CICLOS_DORMIR = 2       # repetições NARRADAS (dão variação de legenda/imagem)
# Duração-alvo do vídeo longo, por formato, em minutos.
#
# O benchmark (produzir/benchmark.py) mostra que o nicho usa vídeos MUITO
# longos (mediana 38–165 min, campeões +200 min), e o caminho certo é crescer
# nessa direção. MAS: um vídeo de 62 min vira ~1 GB, e o upload+processamento
# de 1 GB no runner falhou no primeiro contato real (20/07). Vídeo de ~16 min
# publicou sem problema. Então a duração fica em terreno PROVADO enquanto o
# upload grande não for validado ponta a ponta — reabastecer com vídeo de
# 62 min antes disso é trocar frequência (o que o Diego pediu) por ambição.
# Crescer daqui só depois de um teste manual de upload grande dar certo.
# Alvo de minutos por formato. "dormir" mira o padrão do nicho (60 min+; o
# campeão tem 228). "tema" cresce moderado. "historia" fica na duração natural
# (alvo 0 = sem repetição): repetir uma narrativa como Davi e Golias soa
# estranho, ao contrário de repetir salmos para dormir.
ALVO_MIN = {"dormir": 60, "tema": 30, "historia": 0}
TETO_REPETICOES = 12    # guarda contra runaway; quem manda é ALVO_MIN
                        # (nicho chega a 91 repetições — 12 é folga sã)
SEG_POR_IMAGEM = 28.0   # troca de imagem no longo a cada ~28 s (modo antigo)
# Fundo do vídeo longo: UMA imagem escura e parada, em vez da sequência com
# Ken Burns. Decisão de 24/07/2026, depois de olhar os dois líderes de "salmos
# para dormir" em português — nenhum dos dois anima imagem (um é tela preta
# pura), e ambos queimam o versículo no rodapé. Além de ser o formato do nicho,
# é o que cabe no runner: a versão com imagens renderiza um clipe com zoompan
# por imagem (30 numa hora de vídeo), e é esse custo que prendia a duração.
FUNDO_ESTATICO_LONGO = True


def _seed(pacote: dict, extra: str) -> int:
    return zlib.crc32(f"{pacote['slug']}-{extra}".encode()) % 999_983


def _baixar_imagem(info: dict | None, destino: Path) -> Path | None:
    """Resolve a imagem: biblioteca local (já revisada) tem prioridade."""
    if not info:
        return None
    local = info.get("caminho")
    if local and Path(local).exists():
        # copiar (não referenciar): o ffmpeg roda com cwd na pasta de saída e
        # caminho com "C:" quebra o parser de filtro no Windows
        shutil.copyfile(local, destino)
        return destino
    if not info.get("url"):
        return None
    if imagens.baixar(info["url"], destino):
        return destino
    return None


def _limpar_html(txt: str) -> str:
    """Delega para o limpador único (ver imagens.limpar_autor)."""
    return imagens.limpar_autor(txt)


def creditos(usadas: list[dict]) -> str:
    """Bloco de atribuição das imagens CC BY (obrigatório) — dedup por autor.

    Imagens CC0/domínio público não exigem crédito, mas creditar todas é mais
    simples e não custa nada além de algumas linhas na descrição.
    """
    linhas, vistos = [], set()
    for info in usadas:
        if not info:
            continue
        chave = (info.get("autor", ""), info.get("licenca", ""))
        if chave in vistos:
            continue
        vistos.add(chave)
        linhas.append(f"• {_limpar_html(info.get('autor'))} "
                      f"({info.get('licenca', 'CC0')}) — "
                      f"{info.get('origem', '')}")
    if not linhas:
        return ""
    return ("\n\nImagens: Wikimedia Commons\n" + "\n".join(linhas[:12]))


def _ts_capitulo(seg: float) -> str:
    m, s = divmod(int(seg), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def bloco_afiliado(texto: str) -> str:
    """Bloco de afiliado da descrição, com a divulgação exigida.

    Fica no config por CANAL, não global: o produto tem idioma. Oferta em
    espanhol num canal inglês não converte e ainda cheira a spam — o que
    machuca justamente a satisfação do espectador que o algoritmo mede.
    """
    return f"\n\n{texto.strip()}" if texto and texto.strip() else ""


def montar_short(pacote: dict, idx: int, idioma: str, marca: str,
                 outdir: Path, url_longo: str = "",
                 afiliado: str = "") -> dict:
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

    da_casa = imagens.escolher_da_biblioteca(1, _seed(pacote, f"fundo{idx}"))
    info_img = da_casa[0] if da_casa else short.get("imagem")
    img = _baixar_imagem(info_img, outdir / "fundo.jpg")
    seed = _seed(pacote, f"short{idx}")
    video = render.render_short(outdir, mp3.name, "legenda.ass", img, dur, seed)

    ref_disp = biblia.ref_exibicao(idioma, ref)
    # Ponte Short -> vídeo longo do MESMO dia. O algoritmo deixou de tratar
    # Shorts e vídeos longos como mundos separados: quem vê o Short passa a
    # receber o longo. Dar o link explícito reforça esse caminho.
    ponte = (f"\n\n▶ {cfg['rotulo_completo']}: {url_longo}\n"
             if url_longo else "\n")
    descricao = (
        f"{ref_disp} — {cfg['fonte_texto']}."
        + ponte
        + bloco_afiliado(afiliado)
        + f"\n\n{cfg['cta']}\n\n{cfg['hashtags']} #Shorts"
        + (creditos([info_img]) if img else "")
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


_PALAVRAS_POR_S = 2.3   # voz longa a -15% ≈ 2,3 palavras/s (só p/ estimar)


def _estimar_min(idioma: str, refs: list[str]) -> float:
    total = 0.0
    for ref in refs:
        for _, texto in biblia.carregar_versos(idioma, ref):
            total += len(texto.split()) / _PALAVRAS_POR_S + PAUSA_VERSO
    return (total + CAUDA_LONGO) / 60


def _estender_para_alvo(idioma: str, base: list[str], alvo_min: int) -> list[str]:
    """Repete o ciclo de passagens do tema até bater o alvo de minutos.

    Isto é o oposto do concat -c copy que quebrou em 20/07: lá o MESMO MP4 era
    colado por cópia (DTS não monotônico, YouTube rejeitava); aqui as passagens
    são NARRADAS de novo, gerando áudio/legenda contínuos e um arquivo válido.
    Repetir os salmos do tema a noite toda é o formato do nicho ("Salmo 91 91
    vezes", 48M views), não enchimento. Teto de TETO_REPETICOES ciclos evita
    um vídeo fora de escala se o tema já for longo.
    """
    if not base:
        return base
    por_ciclo = _estimar_min(idioma, base)
    if por_ciclo <= 0:
        return base
    ciclos = max(1, min(TETO_REPETICOES, math.ceil(alvo_min / por_ciclo)))
    return base * ciclos


def montar_longo(pacote: dict, idioma: str, marca: str, outdir: Path,
                 afiliado: str = "") -> dict:
    cfg = idiomas.CONFIG[idioma]
    longo = pacote["longo"]
    outdir.mkdir(parents=True, exist_ok=True)

    # 1) narração seção a seção (uma seção por referência)
    #
    # Conteúdo para dormir é ouvido de olhos fechados e em repetição — o gênero
    # trabalha com leituras longas (o público deixa rolando). Além disso vídeo
    # mais longo rende mais: acima de 8 min o YouTube libera anúncio no meio, e
    # o consumo em TV (hoje a maior tela da plataforma) premia vídeo longo.
    # Cada formato tem um alvo de minutos (ALVO_MIN); o ciclo de passagens é
    # repetido (narrado de novo, não colado) até chegar perto dele.
    refs = list(longo["refs"])
    alvo = ALVO_MIN.get(pacote.get("formato", ""), 0)
    if alvo:
        refs = _estender_para_alvo(idioma, refs, alvo)
    todos_versos: list[tuple[int, str]] = []
    limites: list[tuple[str, int]] = []  # (ref, nº de versos)
    for ref in refs:
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
    srt = outdir / "legenda.srt"
    legendas.srt_longo(srt, secoes)

    # 3) fundo. UMA imagem parada e escura (FUNDO_ESTATICO_LONGO) — é o que os
    # líderes do nicho fazem e é o que torna a hora de duração viável no runner.
    n_alvo = 1 if FUNDO_ESTATICO_LONGO else max(6, min(30, math.ceil(dur / SEG_POR_IMAGEM)))
    baixadas: list[Path] = []
    usadas_info: list[dict] = []
    # biblioteca curada primeiro; o que o pacote resolveu na busca é reserva
    fontes = imagens.escolher_da_biblioteca(n_alvo, _seed(pacote, "fundos")) \
        or longo.get("imagens", [])
    for j, info in enumerate(fontes):
        p = _baixar_imagem(info, outdir / f"img{j:02d}.jpg")
        if p:
            baixadas.append(p)
            usadas_info.append(info)
        if len(baixadas) >= n_alvo:
            break
    if not baixadas:
        for j in range(6):
            g = outdir / f"grad{j}.jpg"
            imagens.gerar_gradiente(g, 2048, 1152, _seed(pacote, f"g{j}"))
            baixadas.append(g)
    lista = [baixadas[j % len(baixadas)] for j in range(n_alvo)]

    # 4) pad ambiente procedural + render (uma passada única)
    #
    # NÃO repetir o ciclo por concat -c copy: em 20/07 os dois longos feitos
    # assim (62 e 26 min) subiram a 98% e o YouTube FALHOU o processamento —
    # viraram "Deleted video" e queimaram 1600 de cota cada. Concatenar o mesmo
    # MP4 por cópia gera tempos (DTS) não monotônicos que o processador rejeita.
    # Os longos que deram certo (8 e 16 min) eram render único. Duração maior
    # virá de um método que gere arquivo válido (re-encode ou narração nativa
    # mais longa), testado à mão antes de virar padrão. Reliabilidade primeiro.
    pad = outdir / "pad.wav"
    musica.gerar_pad(dur, _seed(pacote, "pad"), pad)
    if FUNDO_ESTATICO_LONGO:
        video = render.render_longo_estatico(
            outdir, "voz.wav", "pad.wav", "legenda.ass",
            lista[0] if lista else None, dur, _seed(pacote, "longo"))
    else:
        video = render.render_longo(outdir, "voz.wav", "pad.wav", "legenda.ass",
                                    lista, dur, _seed(pacote, "longo"))

    # 5) thumbnail localizada
    thumb = outdir / "thumb.jpg"
    thumbnail.gerar(thumb, baixadas[0] if baixadas else None,
                    longo["thumb_titulo"][idioma],
                    longo["thumb_sub"][idioma], marca,
                    _seed(pacote, "thumb"))

    # 6) descrição com capítulos (SEO + navegação). Capítulo repetido no ciclo
    # 2 do formato "dormir" ganha marcação, senão a lista fica confusa.
    caps = []
    vistos = set()
    for s in secoes:
        rot = biblia.ref_exibicao(idioma, s["ref"])
        if rot in vistos:
            rot = f"{rot} ({cfg['rotulo_repeticao']})"
        vistos.add(biblia.ref_exibicao(idioma, s["ref"]))
        caps.append(f"{_ts_capitulo(s['ini'])} {rot}")
    caps[0] = f"0:00 {biblia.ref_exibicao(idioma, secoes[0]['ref'])}"
    # Ordem pensada: título, oferta (o YouTube corta a descrição depois de
    # ~3 linhas — o que converte precisa estar acima do "mostrar mais"),
    # depois capítulos, fonte, CTA e créditos. Os capítulos continuam válidos
    # em qualquer posição desde que o primeiro seja 0:00.
    descricao = (
        f"{longo['titulo'][idioma]}"
        + bloco_afiliado(afiliado)
        + f"\n\n{cfg['rotulo_capitulos']}\n" + "\n".join(caps) + "\n\n"
        f"{cfg['fonte_texto']}.\n\n{cfg['cta']}\n\n{cfg['hashtags']}"
        + creditos(usadas_info)
    )
    return {
        "arquivo": video,
        "titulo": longo["titulo"][idioma],
        "descricao": descricao,
        "tags": cfg["tags"],
        "thumb": thumb,
        "legenda_srt": srt,
        "duracao_s": round(dur, 1),
        "referencia": ", ".join(biblia.ref_exibicao(idioma, r)
                                for r in longo["refs"]),
        "tipo_item": "longo",
    }
