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
FILA = RAIZ / "fila"
TEMAS = RAIZ / "conteudo" / "temas.json"

DIAS_ADIANTE = 2
IMAGENS_LONGO = 14


def slugs_usados() -> set[str]:
    if not FILA.is_dir():
        return set()
    return {p.name[11:] for p in FILA.iterdir()
            if p.is_dir() and len(p.name) > 11}


def pacote_do_dia(data: str) -> Path | None:
    if not FILA.is_dir():
        return None
    for p in sorted(FILA.iterdir()):
        if p.is_dir() and p.name.startswith(data):
            return p
    return None


def validar_tema(tema: dict) -> None:
    refs = list(tema["longo"]["refs"]) + [s["ref"] for s in tema["shorts"]]
    for ref in refs:
        for idioma in ("es", "en", "pt"):
            biblia.carregar_versos(idioma, ref)
    for campo in ("titulo", "thumb_titulo", "thumb_sub"):
        for idioma in ("es", "en", "pt"):
            if not tema["longo"][campo].get(idioma):
                raise SystemExit(f"{tema['slug']}: longo.{campo}.{idioma} vazio")
            if campo == "titulo" and len(tema["longo"][campo][idioma]) > 100:
                raise SystemExit(f"{tema['slug']}: título longo ({idioma}) > 100")
    for s in tema["shorts"]:
        for idioma in ("es", "en", "pt"):
            if not s["titulo"].get(idioma):
                raise SystemExit(f"{tema['slug']}: short {s['ref']} sem título {idioma}")
            if len(s["titulo"][idioma]) > 100:
                raise SystemExit(f"{tema['slug']}: título de short ({idioma}) > 100")


def criar_pacote(tema: dict, data: str, dry: bool) -> None:
    validar_tema(tema)
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
            "imagens": imgs_longo,
        },
        "shorts": shorts,
    }
    (pasta / "pacote.json").write_text(
        json.dumps(pacote, ensure_ascii=False, indent=2), encoding="utf-8")
    sem_img = sum(1 for s in shorts if not s["imagem"])
    print(f"  criado {pasta.name} (longo: {len(imgs_longo)} imagens; "
          f"shorts sem imagem: {sem_img} — fallback gradiente)")


def main() -> None:
    ap = argparse.ArgumentParser(description="Cria pacotes-do-dia que faltam")
    ap.add_argument("--dias", type=int, default=DIAS_ADIANTE)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    temas = json.loads(TEMAS.read_text(encoding="utf-8"))
    usados = slugs_usados()
    livres = [t for t in temas if t["slug"] not in usados]

    hoje = datetime.now(timezone.utc).date()
    faltantes = []
    for d in range(args.dias + 1):
        data = (hoje + timedelta(days=d)).isoformat()
        if pacote_do_dia(data) is None:
            faltantes.append(data)

    if not faltantes:
        print("Fila saudável: já existe pacote para hoje e os próximos dias.")
        return

    print(f"Datas sem pacote: {', '.join(faltantes)}; "
          f"temas livres no poço: {len(livres)}.")
    if len(livres) < len(faltantes):
        print("POÇO SECO — temas insuficientes em conteudo/temas.json. "
              "Adicionar temas novos (refs + títulos nos 3 idiomas).")
        sys.exit(3)

    for data, tema in zip(faltantes, livres):
        criar_pacote(tema, data, args.dry_run)


if __name__ == "__main__":
    main()
