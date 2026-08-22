"""Mantém a fila com pacotes-do-dia para hoje + 2 dias, na nuvem.

Um pacote = metadados de 1 vídeo longo + 4 Shorts (refs, títulos nos 3
idiomas, URLs de imagem CC0 resolvidas). NÃO renderiza nada — os MP4 são
montados na hora de publicar, então o Git não engorda com mídia.

Valida cada referência nas TRÊS Bíblias antes de gravar: se a versificação
divergir, o erro aparece aqui (barato), não na hora de publicar.

Exit 3 = poço de temas seco (o workflow abre issue).
"""

from __future__ import annotations

import argparse
import json
import sys
import zlib
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8")

from nucleo import biblia, imagens  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent

DIAS_ADIANTE = 2
IMAGENS_LONGO = 14

# Uma LINHA é um poço de temas + a fila que ele abastece + os canais que
# consomem essa fila. A linha bíblica alimenta os 3 canais de Escritura com o
# MESMO pacote (as imagens são as mesmas, muda o áudio e a legenda). A estoica
# alimenta só o Stoic by Night. Filas separadas porque os poços não se
# misturam: um pacote estoico não tem tradução para os canais bíblicos.
LINHAS = {
    "biblia": {
        "fila": RAIZ / "fila",
        "temas": RAIZ / "conteudo" / "temas.json",
        "canais": ("es", "en", "pt"),
    },
    "estoico": {
        "fila": RAIZ / "fila_stoic",
        "temas": RAIZ / "conteudo" / "temas_estoico.json",
        "canais": ("stoic",),
    },
    # 03/08/2026 — os dois canais novos em espanhol. Poço e fila próprios pelo
    # mesmo motivo dos outros: os corpora não se traduzem entre linhas.
    "poder": {
        "fila": RAIZ / "fila_poder",
        "temas": RAIZ / "conteudo" / "temas_poder.json",
        "canais": ("poder",),
    },
    "astucia": {
        "fila": RAIZ / "fila_astucia",
        "temas": RAIZ / "conteudo" / "temas_astucia.json",
        "canais": ("astucia",),
    },
    # 22/08/2026 — Sabiduría Antigua. Corpus é a MESMA RV1909 dos canais
    # bíblicos, mas a linha é separada porque o recorte é outro (Proverbios e
    # Eclesiastés) e o poço não pode se misturar com o dos Salmos: se
    # compartilhassem `temas.json`, um tema consumido aqui sumiria de lá.
    # Fica dormente até o canal existir — `abastecer` pula linha sem canal
    # ativo, então isto não cria pacote nenhum enquanto ativo=false.
    "sabiduria": {
        "fila": RAIZ / "fila_sabiduria",
        "temas": RAIZ / "conteudo" / "temas_sabiduria.json",
        "canais": ("sabiduria",),
    },
}


def slugs_usados(fila: Path) -> set[str]:
    if not fila.is_dir():
        return set()
    return {p.name[11:] for p in fila.iterdir()
            if p.is_dir() and len(p.name) > 11}


def pacote_do_dia(fila: Path, data: str) -> Path | None:
    if not fila.is_dir():
        return None
    for p in sorted(fila.iterdir()):
        if p.is_dir() and p.name.startswith(data):
            return p
    return None


def validar_tema(tema: dict, canais: tuple[str, ...]) -> None:
    refs = list(tema["longo"]["refs"]) + [s["ref"] for s in tema["shorts"]]
    for ref in refs:
        for canal in canais:
            biblia.carregar_versos(canal, ref)
    for campo in ("titulo", "thumb_titulo", "thumb_sub"):
        for canal in canais:
            if not tema["longo"][campo].get(canal):
                raise SystemExit(f"{tema['slug']}: longo.{campo}.{canal} vazio")
            if campo == "titulo" and len(tema["longo"][campo][canal]) > 100:
                raise SystemExit(f"{tema['slug']}: título longo ({canal}) > 100")
    for s in tema["shorts"]:
        for canal in canais:
            if not s["titulo"].get(canal):
                raise SystemExit(f"{tema['slug']}: short {s['ref']} sem título {canal}")
            if len(s["titulo"][canal]) > 100:
                raise SystemExit(f"{tema['slug']}: título de short ({canal}) > 100")


def criar_pacote(tema: dict, data: str, dry: bool, linha: dict) -> None:
    validar_tema(tema, linha["canais"])
    FILA = linha["fila"]
    seed = zlib.crc32(f"{data}-{tema['slug']}".encode()) % 999_983

    if dry:
        print(f"  [dry-run] criaria {data}-{tema['slug']}")
        return

    consultas = tema["longo"]["consultas_imagens"]
    por_consulta = max(2, IMAGENS_LONGO // len(consultas) + 1)
    imgs_longo: list[dict] = []
    for k, consulta in enumerate(consultas):
        imgs_longo += imagens.resolver(consulta, por_consulta, seed + k, "wide")
    imgs_longo = imgs_longo[:IMAGENS_LONGO]

    shorts = []
    for k, s in enumerate(tema["shorts"]):
        achadas = imagens.resolver(s["consulta_imagem"], 1, seed + 100 + k, "tall")
        shorts.append({
            "ref": s["ref"],
            "tipo": s.get("tipo", ""),
            "titulo": s["titulo"],
            # Camada AUTORAL (03/08/2026, só nos canais poder/astucia): uma
            # frase nossa aplicando o trecho ao presente. Não é enfeite — a
            # política oficial do YouTube lista "readings of other materials
            # you did not originally create" como inelegível para monetização,
            # e o critério de aprovação é haver "meaningful difference" entre
            # a fonte e o vídeo. Domínio público resolve copyright, não
            # monetização. Vazio nos canais bíblicos (diretriz editorial nº 4).
            "aplicacao": s.get("aplicacao", ""),
            "imagem": achadas[0] if achadas else None,
        })

    pasta = FILA / f"{data}-{tema['slug']}"
    pasta.mkdir(parents=True, exist_ok=True)
    agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    pacote = {
        "slug": tema["slug"],
        "formato": tema.get("formato", "tema"),
        "data": data,
        "criado_em": agora,
        # auto-aprovação é segura: conteúdo determinístico de domínio público
        "aprovado_em": agora,
        "longo": {
            "refs": tema["longo"]["refs"],
            "titulo": tema["longo"]["titulo"],
            "thumb_titulo": tema["longo"]["thumb_titulo"],
            "thumb_sub": tema["longo"]["thumb_sub"],
            # Camadas do longo (04/08/2026): abertura falada de 20-40s (o que
            # tira o vídeo de "leitura crua") e SEO por tema (tags/descrição
            # de busca), tudo por idioma. Vazio = comportamento antigo.
            "abertura": tema["longo"].get("abertura", {}),
            "tags_extra": tema["longo"].get("tags_extra", {}),
            "descricao_busca": tema["longo"].get("descricao_busca", {}),
            "imagens": imgs_longo,
        },
        "shorts": shorts,
    }
    (pasta / "pacote.json").write_text(
        json.dumps(pacote, ensure_ascii=False, indent=2), encoding="utf-8")
    sem_img = sum(1 for s in shorts if not s["imagem"])
    print(f"  criado {pasta.name} (longo: {len(imgs_longo)} imagens; "
          f"shorts sem imagem: {sem_img} — fallback gradiente)")


def abastecer(nome: str, linha: dict, dias: int, dry: bool) -> int:
    """Devolve 3 se o poço secou (o workflow abre issue), 0 se está saudável."""
    temas = json.loads(linha["temas"].read_text(encoding="utf-8"))
    temas = temas["temas"] if isinstance(temas, dict) else temas
    usados = slugs_usados(linha["fila"])
    livres = [t for t in temas if t["slug"] not in usados]

    hoje = datetime.now(timezone.utc).date()
    faltantes = []
    for d in range(dias + 1):
        data = (hoje + timedelta(days=d)).isoformat()
        if pacote_do_dia(linha["fila"], data) is None:
            faltantes.append(data)

    if not faltantes:
        print(f"[{nome}] fila saudável: já existe pacote para hoje e os "
              f"próximos dias.")
        return 0

    print(f"[{nome}] datas sem pacote: {', '.join(faltantes)}; "
          f"temas livres no poço: {len(livres)}.")
    if len(livres) < len(faltantes):
        print(f"[{nome}] POÇO SECO — temas insuficientes em "
              f"{linha['temas'].relative_to(RAIZ).as_posix()}.")
        return 3

    for data, tema in zip(faltantes, livres):
        criar_pacote(tema, data, dry, linha)
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description="Cria pacotes-do-dia que faltam")
    ap.add_argument("--dias", type=int, default=DIAS_ADIANTE)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--linha", choices=sorted(LINHAS),
                    help="Só esta linha (padrão: todas)")
    args = ap.parse_args()

    nomes = [args.linha] if args.linha else sorted(LINHAS)
    # Poço seco de UMA linha não pode impedir as outras de abastecer — o
    # estoico secar não é motivo para os 3 canais bíblicos ficarem sem pacote.
    cfg = json.loads((RAIZ / "publicador" / "config.json")
                     .read_text(encoding="utf-8"))["canais"]
    codigo = 0
    for nome in nomes:
        if not any(cfg.get(c, {}).get("ativo") for c in LINHAS[nome]["canais"]):
            print(f"[{nome}] todos os canais da linha estão inativos — pulando.")
            continue
        codigo = max(codigo, abastecer(nome, LINHAS[nome], args.dias,
                                       args.dry_run))
    if codigo:
        sys.exit(codigo)


if __name__ == "__main__":
    main()
