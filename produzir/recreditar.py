"""Rebusca a autoria correta das imagens da biblioteca no Wikimedia Commons.

Necessário porque a primeira coleta truncava o campo Artist (HTML) antes de
limpá-lo, guardando lixo do tipo 'a href="//commons.wikimedia.org/...'.
Crédito errado em imagem CC BY é problema de licença, não de estética.

    python produzir/recreditar.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import unquote

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.stdout.reconfigure(encoding="utf-8")

from nucleo import imagens  # noqa: E402

CREDITOS = RAIZ / "marca" / "fundos" / "creditos.json"


def titulo_do_arquivo(origem: str) -> str:
    """'https://commons.wikimedia.org/wiki/File:Foo.jpg' -> 'File:Foo.jpg'"""
    return unquote(origem.rsplit("/", 1)[-1])


def main() -> None:
    itens = json.loads(CREDITOS.read_text(encoding="utf-8"))
    corrigidos = 0
    for item in itens:
        titulo = titulo_do_arquivo(item.get("origem", ""))
        if not titulo.startswith("File:"):
            continue
        try:
            r = imagens._buscar_com_calma({
                "action": "query", "format": "json", "titles": titulo,
                "prop": "imageinfo", "iiprop": "extmetadata",
            })
            paginas = (r.json().get("query") or {}).get("pages", {})
        except Exception as exc:
            print(f"  falhou {titulo}: {exc}")
            continue
        for pg in paginas.values():
            infos = pg.get("imageinfo") or []
            if not infos:
                continue
            meta = infos[0].get("extmetadata") or {}
            autor = imagens.limpar_autor(
                (meta.get("Artist") or {}).get("value", ""))
            lic = (meta.get("LicenseShortName") or {}).get("value", "")
            if autor and autor != item.get("autor"):
                print(f"  {item['arquivo']}: {item.get('autor', '')[:28]}"
                      f" -> {autor}")
                item["autor"] = autor
                corrigidos += 1
            if lic:
                item["licenca"] = lic

    CREDITOS.write_text(json.dumps(itens, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    print(f"\n{corrigidos} crédito(s) corrigido(s) de {len(itens)}.")


if __name__ == "__main__":
    main()
