"""Configuração por idioma: voz, Bíblia, nomes de livros, strings de canal.

Regra editorial inegociável: só tradução em DOMÍNIO PÚBLICO —
ES = Reina-Valera 1909, EN = King James Version, PT = Bíblia Livre.
Traduções modernas (NVI, RVR1960, ARC/NAA etc.) são protegidas: nunca usar.
"""

from __future__ import annotations

from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BIBLIA_DIR = RAIZ / "biblia"
FONTES_DIR = RAIZ / "marca" / "fontes"

IDIOMAS = ("es", "en", "pt")

# Nome da playlist por formato de conteúdo, em cada idioma. Playlist curta e
# bem nichada é o que faz o espectador emendar um vídeo no outro em vez de sair.
PLAYLISTS = {
    "dormir": {
        "es": "Salmos para dormir 🌙",
        "en": "Psalms for sleep 🌙",
        "pt": "Salmos para dormir 🌙",
    },
    "tema": {
        "es": "Promesas de Dios por tema 🙏",
        "en": "God's promises by theme 🙏",
        "pt": "Promessas de Deus por tema 🙏",
    },
    "historia": {
        "es": "Historias de la Biblia narradas 📖",
        "en": "Bible stories narrated 📖",
        "pt": "Histórias da Bíblia narradas 📖",
    },
}

CONFIG = {
    "es": {
        "arquivo_biblia": BIBLIA_DIR / "rv1909.json",
        "fonte_texto": "Reina-Valera 1909 (dominio público)",
        "voz": "es-MX-JorgeNeural",
        "rate_short": "-8%",
        "rate_longo": "-15%",
        "bcp47": "es",
        "palavra_salmo": "Salmo",
        "cta": ("La Palabra de Dios en audio y subtítulos en español. "
                "Contenido nuevo todos los días. Suscríbete \U0001F64F"),
        "hashtags": "#Biblia #Fe #PalabraDeDios #Versiculos #Cristiano",
        # 16 tags: mediana do nicho medida em produzir/benchmark.py (19/07).
        # Inclui os termos que dominam os títulos campeões: "oración",
        # "poderosa", "salmo 91", "para dormir".
        "tags": ["biblia", "biblia hablada", "salmos", "salmo 91",
                 "salmos para dormir", "oración", "oración poderosa",
                 "palabra de dios", "versículos bíblicos", "fe", "cristiano",
                 "reina valera", "biblia en español", "dormir con la biblia",
                 "paz", "protección"],
        "rotulo_capitulos": "Pasajes en este video:",
        "rotulo_repeticao": "repetición",
        "rotulo_completo": "Video completo",
    },
    "en": {
        "arquivo_biblia": BIBLIA_DIR / "kjv.json",
        "fonte_texto": "King James Version (public domain)",
        "voz": "en-US-ChristopherNeural",
        "rate_short": "-8%",
        "rate_longo": "-15%",
        "bcp47": "en",
        "palavra_salmo": "Psalm",
        "cta": ("God's Word in audio with subtitles. "
                "New Scripture every day. Subscribe \U0001F64F"),
        "hashtags": "#Bible #Faith #GodsWord #BibleVerses #Christian",
        "tags": ["bible", "audio bible", "bible verses", "psalms", "psalm 91",
                 "bible for sleep", "scriptures for sleep",
                 "fall asleep with the bible", "prayer", "faith", "christian",
                 "king james version", "kjv", "god's promises", "peace",
                 "protection"],
        "rotulo_capitulos": "Passages in this video:",
        "rotulo_repeticao": "repeat",
        "rotulo_completo": "Full video",
    },
    "pt": {
        "arquivo_biblia": BIBLIA_DIR / "blivre.json",
        "fonte_texto": "Bíblia Livre (domínio público)",
        "voz": "pt-BR-AntonioNeural",
        "rate_short": "-8%",
        "rate_longo": "-15%",
        "bcp47": "pt",
        "palavra_salmo": "Salmo",
        "cta": ("A Palavra de Deus em áudio e legenda em português. "
                "Conteúdo novo todos os dias. Inscreva-se \U0001F64F"),
        "hashtags": "#Bíblia #Fé #PalavraDeDeus #Versículos #Cristão",
        "tags": ["bíblia", "bíblia narrada", "salmos", "salmo 91",
                 "salmos para dormir", "oração", "oração poderosa",
                 "palavra de deus", "versículos bíblicos", "fé", "cristão",
                 "bíblia falada", "dormir com a bíblia", "paz", "proteção",
                 "promessas de deus"],
        "rotulo_capitulos": "Passagens neste vídeo:",
        "rotulo_repeticao": "repetição",
        "rotulo_completo": "Vídeo completo",
    },
}

# Nome canônico (scrollmapper, em inglês) -> nome exibido por idioma.
# A ordem segue os 66 livros do JSON.
_CANONICOS = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua",
    "Judges", "Ruth", "I Samuel", "II Samuel", "I Kings", "II Kings",
    "I Chronicles", "II Chronicles", "Ezra", "Nehemiah", "Esther", "Job",
    "Psalms", "Proverbs", "Ecclesiastes", "Song of Solomon", "Isaiah",
    "Jeremiah", "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel", "Amos",
    "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai",
    "Zechariah", "Malachi", "Matthew", "Mark", "Luke", "John", "Acts",
    "Romans", "I Corinthians", "II Corinthians", "Galatians", "Ephesians",
    "Philippians", "Colossians", "I Thessalonians", "II Thessalonians",
    "I Timothy", "II Timothy", "Titus", "Philemon", "Hebrews", "James",
    "I Peter", "II Peter", "I John", "II John", "III John", "Jude",
    "Revelation of John",
]

_ES = [
    "Génesis", "Éxodo", "Levítico", "Números", "Deuteronomio", "Josué",
    "Jueces", "Rut", "1 Samuel", "2 Samuel", "1 Reyes", "2 Reyes",
    "1 Crónicas", "2 Crónicas", "Esdras", "Nehemías", "Ester", "Job",
    "Salmos", "Proverbios", "Eclesiastés", "Cantares", "Isaías",
    "Jeremías", "Lamentaciones", "Ezequiel", "Daniel", "Oseas", "Joel", "Amós",
    "Abdías", "Jonás", "Miqueas", "Nahúm", "Habacuc", "Sofonías", "Hageo",
    "Zacarías", "Malaquías", "Mateo", "Marcos", "Lucas", "Juan", "Hechos",
    "Romanos", "1 Corintios", "2 Corintios", "Gálatas", "Efesios",
    "Filipenses", "Colosenses", "1 Tesalonicenses", "2 Tesalonicenses",
    "1 Timoteo", "2 Timoteo", "Tito", "Filemón", "Hebreos", "Santiago",
    "1 Pedro", "2 Pedro", "1 Juan", "2 Juan", "3 Juan", "Judas",
    "Apocalipsis",
]

_EN = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua",
    "Judges", "Ruth", "1 Samuel", "2 Samuel", "1 Kings", "2 Kings",
    "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah", "Esther", "Job",
    "Psalms", "Proverbs", "Ecclesiastes", "Song of Solomon", "Isaiah",
    "Jeremiah", "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel", "Amos",
    "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai",
    "Zechariah", "Malachi", "Matthew", "Mark", "Luke", "John", "Acts",
    "Romans", "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians",
    "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians",
    "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews", "James",
    "1 Peter", "2 Peter", "1 John", "2 John", "3 John", "Jude",
    "Revelation",
]

_PT = [
    "Gênesis", "Êxodo", "Levítico", "Números", "Deuteronômio", "Josué",
    "Juízes", "Rute", "1 Samuel", "2 Samuel", "1 Reis", "2 Reis",
    "1 Crônicas", "2 Crônicas", "Esdras", "Neemias", "Ester", "Jó",
    "Salmos", "Provérbios", "Eclesiastes", "Cânticos", "Isaías",
    "Jeremias", "Lamentações", "Ezequiel", "Daniel", "Oseias", "Joel", "Amós",
    "Obadias", "Jonas", "Miqueias", "Naum", "Habacuque", "Sofonias", "Ageu",
    "Zacarias", "Malaquias", "Mateus", "Marcos", "Lucas", "João", "Atos",
    "Romanos", "1 Coríntios", "2 Coríntios", "Gálatas", "Efésios",
    "Filipenses", "Colossenses", "1 Tessalonicenses", "2 Tessalonicenses",
    "1 Timóteo", "2 Timóteo", "Tito", "Filemom", "Hebreus", "Tiago",
    "1 Pedro", "2 Pedro", "1 João", "2 João", "3 João", "Judas",
    "Apocalipse",
]

LIVROS = {
    "es": dict(zip(_CANONICOS, _ES)),
    "en": dict(zip(_CANONICOS, _EN)),
    "pt": dict(zip(_CANONICOS, _PT)),
}


def nome_livro(idioma: str, canonico: str) -> str:
    return LIVROS[idioma][canonico]
