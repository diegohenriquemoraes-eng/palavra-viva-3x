"""Gera 10 temas novos de formato "dormir" e anexa a conteudo/temas.json.

Motivo: os vídeos de ~1 h (motor das horas de exibição p/ AdSense) só saem dos
temas "dormir", e eles eram 3 de 16. Este script leva a 13, sem repetir slug.

Só Salmos (domínio público nas 3 Bíblias) e propositalmente SEM os salmos
gigantes (119, 78, 89, 105, 106) — cada tema fica com ~8 salmos, um ciclo de
~14 min, e o pipeline repete até ~60 min (ALVO_MIN). Imagens de consulta são
noturnas/escuras, que é o fundo do formato.

Valida cada ref nas 3 Bíblias e o tamanho dos títulos ANTES de gravar.

    python produzir/gerar_temas_dormir.py --dry-run
    python produzir/gerar_temas_dormir.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.stdout.reconfigure(encoding="utf-8")

from nucleo import biblia  # noqa: E402

TEMAS = RAIZ / "conteudo" / "temas.json"

# Frases-título curtas de versículos famosos, reutilizadas entre os temas.
SHORTS = {
    "Psalms 4:8": {"img": "starry sky night",
        "pt": "Salmo 4:8 — Em paz me deito e durmo | Bíblia",
        "es": "Salmo 4:8 — En paz me acostaré y dormiré | Biblia",
        "en": "Psalm 4:8 — I Will Lie Down and Sleep in Peace | Bible"},
    "Psalms 3:5": {"img": "moon clouds night",
        "pt": "Salmo 3:5 — Eu me deitei e dormi; despertei | Bíblia",
        "es": "Salmo 3:5 — Yo me acosté y dormí, y desperté | Biblia",
        "en": "Psalm 3:5 — I Laid Down and Slept; I Awaked | Bible"},
    "Psalms 23:1-4": {"img": "meadow moonlight",
        "pt": "Salmo 23 — O Senhor é o meu pastor | Bíblia narrada",
        "es": "Salmo 23 — Jehová es mi pastor, nada me faltará | Biblia",
        "en": "Psalm 23 — The Lord Is My Shepherd | Bible"},
    "Psalms 91:1-4": {"img": "night sky stars",
        "pt": "Salmo 91 — À sombra do Altíssimo | Bíblia narrada",
        "es": "Salmo 91 — Bajo la sombra del Altísimo | Biblia",
        "en": "Psalm 91 — Under the Shadow of the Almighty | Bible"},
    "Psalms 121:1-4": {"img": "mountains night stars",
        "pt": "Salmo 121 — O meu socorro vem do Senhor | Bíblia",
        "es": "Salmo 121 — Mi socorro viene de Jehová | Biblia",
        "en": "Psalm 121 — My Help Comes from the Lord | Bible"},
    "Psalms 27:1": {"img": "dark forest light",
        "pt": "Salmo 27:1 — O Senhor é a minha luz | Bíblia",
        "es": "Salmo 27:1 — Jehová es mi luz y mi salvación | Biblia",
        "en": "Psalm 27:1 — The Lord Is My Light | Bible Verses"},
    "Psalms 46:1-3": {"img": "calm ocean night",
        "pt": "Salmo 46 — Deus é o nosso refúgio e fortaleza | Bíblia",
        "es": "Salmo 46 — Dios es nuestro amparo y fortaleza | Biblia",
        "en": "Psalm 46 — God Is Our Refuge and Strength | Bible"},
    "Psalms 34:4-7": {"img": "night sky peace",
        "pt": "Salmo 34 — Busquei ao Senhor, e ele me respondeu | Bíblia",
        "es": "Salmo 34 — Busqué a Jehová, y él me oyó | Biblia",
        "en": "Psalm 34 — I Sought the Lord, and He Heard Me | Bible"},
    "Psalms 62:1-2": {"img": "still lake night",
        "pt": "Salmo 62 — A minha alma descansa em Deus | Bíblia",
        "es": "Salmo 62 — En Dios solamente reposa mi alma | Biblia",
        "en": "Psalm 62 — My Soul Waits in Silence for God | Bible"},
    "Psalms 63:6-8": {"img": "night bed window moon",
        "pt": "Salmo 63 — De noite me lembro de ti | Bíblia narrada",
        "es": "Salmo 63 — Me acuerdo de ti en mi lecho | Biblia",
        "en": "Psalm 63 — I Remember You Upon My Bed | Bible"},
    "Psalms 16:8-9": {"img": "starlight calm",
        "pt": "Salmo 16 — O Senhor está à minha direita | Bíblia",
        "es": "Salmo 16 — Jehová está a mi diestra | Biblia",
        "en": "Psalm 16 — The Lord Is at My Right Hand | Bible"},
    "Psalms 116:7": {"img": "quiet night stars",
        "pt": "Salmo 116:7 — Volta, minha alma, ao teu repouso | Bíblia",
        "es": "Salmo 116:7 — Vuelve, alma mía, a tu reposo | Biblia",
        "en": "Psalm 116:7 — Return to Your Rest, O My Soul | Bible"},
    "Psalms 127:2": {"img": "moon night calm",
        "pt": "Salmo 127:2 — Ele dá o sono aos seus amados | Bíblia",
        "es": "Salmo 127:2 — Él da a su amado el sueño | Biblia",
        "en": "Psalm 127:2 — He Gives Sleep to His Beloved | Bible"},
    "Psalms 131:2": {"img": "calm water moon",
        "pt": "Salmo 131 — Serenei e aquietei a minha alma | Bíblia",
        "es": "Salmo 131 — He calmado y aquietado mi alma | Biblia",
        "en": "Psalm 131 — I Have Calmed and Quieted My Soul | Bible"},
    "Psalms 130:5-6": {"img": "dawn dark sky",
        "pt": "Salmo 130 — A minha alma espera no Senhor | Bíblia",
        "es": "Salmo 130 — Mi alma espera a Jehová | Biblia",
        "en": "Psalm 130 — My Soul Waits for the Lord | Bible"},
    "Psalms 103:1-5": {"img": "night sky vast",
        "pt": "Salmo 103 — Bendize, ó minha alma, ao Senhor | Bíblia",
        "es": "Salmo 103 — Bendice, alma mía, a Jehová | Biblia",
        "en": "Psalm 103 — Bless the Lord, O My Soul | Bible"},
    "Psalms 145:8-9": {"img": "gentle night light",
        "pt": "Salmo 145 — O Senhor é clemente e misericordioso | Bíblia",
        "es": "Salmo 145 — Clemente y misericordioso es Jehová | Biblia",
        "en": "Psalm 145 — The Lord Is Gracious and Merciful | Bible"},
    "Psalms 61:1-4": {"img": "rock night sky",
        "pt": "Salmo 61 — Leva-me à rocha mais alta do que eu | Bíblia",
        "es": "Salmo 61 — Llévame a la roca que es más alta que yo | Biblia",
        "en": "Psalm 61 — Lead Me to the Rock Higher Than I | Bible"},
    "Psalms 42:1-2": {"img": "night stream forest",
        "pt": "Salmo 42 — Como a corça anseia pelas águas | Bíblia",
        "es": "Salmo 42 — Como el ciervo brama por las aguas | Biblia",
        "en": "Psalm 42 — As the Deer Pants for the Water | Bible"},
    "Psalms 51:10": {"img": "dark sky dawn",
        "pt": "Salmo 51:10 — Cria em mim um coração puro | Bíblia",
        "es": "Salmo 51:10 — Crea en mí un corazón limpio | Biblia",
        "en": "Psalm 51:10 — Create in Me a Clean Heart | Bible"},
    "Psalms 143:8": {"img": "sunrise dark",
        "pt": "Salmo 143:8 — De manhã ouvirei da tua bondade | Bíblia",
        "es": "Salmo 143:8 — Hazme oír por la mañana tu misericordia | Biblia",
        "en": "Psalm 143:8 — Let Me Hear Your Love in the Morning | Bible"},
    "Psalms 1:1-3": {"img": "tree river night",
        "pt": "Salmo 1 — Como a árvore plantada junto ao rio | Bíblia",
        "es": "Salmo 1 — Como árbol plantado junto a las aguas | Biblia",
        "en": "Psalm 1 — Like a Tree Planted by the Water | Bible"},
    "Psalms 133:1": {"img": "night dew calm",
        "pt": "Salmo 133 — Quão bom é habitarem unidos os irmãos | Bíblia",
        "es": "Salmo 133 — Cuán bueno es habitar los hermanos juntos | Biblia",
        "en": "Psalm 133 — How Good It Is to Dwell in Unity | Bible"},
    "Psalms 84:1-2": {"img": "temple night light",
        "pt": "Salmo 84 — Quão amáveis são os teus tabernáculos | Bíblia",
        "es": "Salmo 84 — Cuán amables son tus moradas | Biblia",
        "en": "Psalm 84 — How Lovely Is Your Dwelling Place | Bible"},
    "Psalms 139:7-10": {"img": "night sky infinite",
        "pt": "Salmo 139 — Para onde me irei do teu Espírito | Bíblia",
        "es": "Salmo 139 — ¿A dónde me iré de tu Espíritu? | Biblia",
        "en": "Psalm 139 — Where Can I Go from Your Spirit | Bible"},
    "Psalms 5:3": {"img": "dawn light dark",
        "pt": "Salmo 5:3 — De manhã ouvirás a minha voz | Bíblia",
        "es": "Salmo 5:3 — De mañana oirás mi voz | Biblia",
        "en": "Psalm 5:3 — In the Morning You Hear My Voice | Bible"},
    "Psalms 118:5-6": {"img": "open sky night",
        "pt": "Salmo 118 — O Senhor está comigo, não temerei | Bíblia",
        "es": "Salmo 118 — Jehová está conmigo; no temeré | Biblia",
        "en": "Psalm 118 — The Lord Is with Me; I Will Not Fear | Bible"},
}

# Cada tema: (slug, nome pt/es/en, refs do longo, subtítulo de 3 salmos,
# consultas de imagem noturnas, 4 refs de short do dicionário acima).
TEMAS_NOVOS = [
    ("salmos-dormir-4", ("Descanso e Paz", "Descanso y Paz", "Rest and Peace"),
     ["Psalms 23", "Psalms 4", "Psalms 3", "Psalms 5", "Psalms 16",
      "Psalms 62", "Psalms 116", "Psalms 127"],
     ("23", "4", "62"), ["starry sky night", "still lake night", "moon clouds"],
     ["Psalms 4:8", "Psalms 3:5", "Psalms 62:1-2", "Psalms 127:2"]),
    ("salmos-dormir-5", ("Proteção à Noite", "Protección de Noche", "Protection at Night"),
     ["Psalms 91", "Psalms 121", "Psalms 27", "Psalms 46", "Psalms 34",
      "Psalms 118", "Psalms 125", "Psalms 61"],
     ("91", "121", "46"), ["night sky stars", "mountains night", "dark forest light"],
     ["Psalms 91:1-4", "Psalms 121:1-4", "Psalms 27:1", "Psalms 46:1-3"]),
    ("salmos-dormir-6", ("Refúgio e Confiança", "Refugio y Confianza", "Refuge and Trust"),
     ["Psalms 46", "Psalms 61", "Psalms 62", "Psalms 63", "Psalms 71",
      "Psalms 84", "Psalms 90", "Psalms 142"],
     ("46", "62", "63"), ["calm ocean night", "rock night sky", "still lake night"],
     ["Psalms 62:1-2", "Psalms 63:6-8", "Psalms 61:1-4", "Psalms 46:1-3"]),
    ("salmos-dormir-7", ("Louvor da Noite", "Alabanza de la Noche", "Praise at Night"),
     ["Psalms 103", "Psalms 145", "Psalms 146", "Psalms 147", "Psalms 148",
      "Psalms 150", "Psalms 100", "Psalms 92"],
     ("103", "145", "148"), ["night sky vast", "gentle night light", "starlight calm"],
     ["Psalms 103:1-5", "Psalms 145:8-9", "Psalms 63:6-8", "Psalms 116:7"]),
    ("salmos-dormir-8", ("Alívio da Ansiedade", "Alivio de la Ansiedad", "Relief from Anxiety"),
     ["Psalms 42", "Psalms 43", "Psalms 55", "Psalms 77", "Psalms 94",
      "Psalms 116", "Psalms 130", "Psalms 131"],
     ("42", "116", "131"), ["night stream forest", "quiet night stars", "calm water moon"],
     ["Psalms 42:1-2", "Psalms 116:7", "Psalms 131:2", "Psalms 130:5-6"]),
    ("salmos-dormir-9", ("O Senhor é Minha Luz", "El Señor es mi Luz", "The Lord Is My Light"),
     ["Psalms 27", "Psalms 36", "Psalms 43", "Psalms 97", "Psalms 104",
      "Psalms 113", "Psalms 139", "Psalms 121"],
     ("27", "139", "121"), ["dark forest light", "night sky infinite", "mountains night"],
     ["Psalms 27:1", "Psalms 139:7-10", "Psalms 121:1-4", "Psalms 34:4-7"]),
    ("salmos-dormir-10", ("Misericórdia e Perdão", "Misericordia y Perdón", "Mercy and Forgiveness"),
     ["Psalms 32", "Psalms 51", "Psalms 103", "Psalms 130", "Psalms 143",
      "Psalms 25", "Psalms 40", "Psalms 86"],
     ("103", "130", "51"), ["dark sky dawn", "sunrise dark", "night sky peace"],
     ["Psalms 103:1-5", "Psalms 130:5-6", "Psalms 143:8", "Psalms 51:10"]),
    ("salmos-dormir-11", ("Gratidão e Descanso", "Gratitud y Descanso", "Gratitude and Rest"),
     ["Psalms 92", "Psalms 95", "Psalms 96", "Psalms 98", "Psalms 100",
      "Psalms 111", "Psalms 138", "Psalms 145"],
     ("100", "103", "145"), ["gentle night light", "night sky vast", "quiet night stars"],
     ["Psalms 145:8-9", "Psalms 103:1-5", "Psalms 116:7", "Psalms 63:6-8"]),
    ("salmos-dormir-12", ("Paz Interior", "Paz Interior", "Inner Peace"),
     ["Psalms 1", "Psalms 15", "Psalms 19", "Psalms 24", "Psalms 84",
      "Psalms 122", "Psalms 128", "Psalms 133"],
     ("1", "84", "133"), ["tree river night", "temple night light", "night dew calm"],
     ["Psalms 1:1-3", "Psalms 133:1", "Psalms 84:1-2", "Psalms 19:1"]),
    ("salmos-dormir-13", ("Deus Nunca Dorme", "Dios Nunca Duerme", "God Never Sleeps"),
     ["Psalms 121", "Psalms 91", "Psalms 34", "Psalms 37", "Psalms 40",
      "Psalms 56", "Psalms 57", "Psalms 63"],
     ("121", "91", "34"), ["mountains night stars", "night sky stars", "night sky peace"],
     ["Psalms 121:1-4", "Psalms 91:1-4", "Psalms 34:4-7", "Psalms 63:6-8"]),
]

# Salmo 19:1 não está no dicionário de shorts (usado só no tema 12); defino aqui.
SHORTS["Psalms 19:1"] = {"img": "starry sky vast",
    "pt": "Salmo 19:1 — Os céus proclamam a glória de Deus | Bíblia",
    "es": "Salmo 19:1 — Los cielos cuentan la gloria de Dios | Biblia",
    "en": "Psalm 19:1 — The Heavens Declare the Glory of God | Bible"}


def titulo_longo(nome: dict) -> dict:
    return {
        "pt": f"Salmos para Dormir — {nome['pt']} | Bíblia Narrada com Voz Calma",
        "es": f"Salmos para Dormir — {nome['es']} | Biblia Hablada con Voz Calmada",
        "en": f"Psalms for Sleep — {nome['en']} | Audio Bible with a Calm Voice",
    }


def monta(t) -> dict:
    slug, (npt, nes, nen), refs, sub, imgs, short_refs = t
    nome = {"pt": npt, "es": nes, "en": nen}
    a, b, c = sub
    return {
        "slug": slug,
        "formato": "dormir",
        "longo": {
            "refs": refs,
            "titulo": titulo_longo(nome),
            "thumb_titulo": {"pt": "SALMOS PARA DORMIR",
                             "es": "SALMOS PARA DORMIR",
                             "en": "PSALMS FOR SLEEP"},
            "thumb_sub": {"pt": f"Salmo {a} • {b} • {c}",
                          "es": f"Salmo {a} • {b} • {c}",
                          "en": f"Psalm {a} • {b} • {c}"},
            "consultas_imagens": imgs,
        },
        "shorts": [
            {"ref": r, "tipo": "promesa", "consulta_imagem": SHORTS[r]["img"],
             "titulo": {"pt": SHORTS[r]["pt"], "es": SHORTS[r]["es"],
                        "en": SHORTS[r]["en"]}}
            for r in short_refs
        ],
    }


def valida(tema: dict) -> None:
    todas = list(tema["longo"]["refs"]) + [s["ref"] for s in tema["shorts"]]
    for ref in todas:
        for idioma in ("es", "en", "pt"):
            vs = biblia.carregar_versos(idioma, ref)
            if not vs:
                raise SystemExit(f"{tema['slug']}: {ref} vazio em {idioma}")
    for campo in ("titulo", "thumb_titulo", "thumb_sub"):
        for idioma in ("es", "en", "pt"):
            v = tema["longo"][campo].get(idioma, "")
            if not v:
                raise SystemExit(f"{tema['slug']}: longo.{campo}.{idioma} vazio")
            if campo == "titulo" and len(v) > 100:
                raise SystemExit(f"{tema['slug']}: título ({idioma}) {len(v)}>100")
    for s in tema["shorts"]:
        for idioma in ("es", "en", "pt"):
            if not s["titulo"].get(idioma):
                raise SystemExit(f"{tema['slug']}: short {s['ref']} sem {idioma}")
            if len(s["titulo"][idioma]) > 100:
                raise SystemExit(f"{tema['slug']}: short {s['ref']} ({idioma})>100")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    existentes = json.loads(TEMAS.read_text(encoding="utf-8"))
    ja = {t["slug"] for t in existentes}

    novos = []
    for t in TEMAS_NOVOS:
        tema = monta(t)
        if tema["slug"] in ja:
            print(f"  já existe, pulando: {tema['slug']}")
            continue
        valida(tema)
        mins = sum(len(biblia.carregar_versos("pt", r)) for r in tema["longo"]["refs"])
        print(f"  OK {tema['slug']:18s} {len(tema['longo']['refs'])} salmos, "
              f"{mins} versos/ciclo, {len(tema['shorts'])} shorts")
        novos.append(tema)

    if not novos:
        print("nada a adicionar.")
        return
    if args.dry_run:
        print(f"\n[dry-run] adicionaria {len(novos)} temas dormir.")
        return

    existentes.extend(novos)
    TEMAS.write_text(json.dumps(existentes, ensure_ascii=False, indent=1),
                     encoding="utf-8")
    print(f"\n{len(novos)} temas dormir adicionados. Total agora: {len(existentes)}.")


if __name__ == "__main__":
    main()
