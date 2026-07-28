"""Configuração por idioma: voz, Bíblia, nomes de livros, strings de canal.

Regra editorial inegociável: só tradução em DOMÍNIO PÚBLICO —
ES = Reina-Valera 1909, EN = King James Version, PT = Bíblia Livre.
Traduções modernas (NVI, RVR1960, ARC/NAA etc.) são protegidas: nunca usar.
"""

from __future__ import annotations

from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BIBLIA_DIR = RAIZ / "biblia"
FONTES_TEXTO_DIR = RAIZ / "fontes"   # corpora não-bíblicos (estoicos etc.)
FONTES_DIR = RAIZ / "marca" / "fontes"   # fontes tipográficas do render

# "idioma" aqui significa CANAL: cada chave é uma linha de produto com voz,
# corpus e textos próprios. "stoic" é o primeiro canal não-bíblico (inglês,
# filosofia estoica em domínio público) — ver `fontes/PROVENIENCIA.md`.
IDIOMAS = ("es", "en", "pt", "stoic")
# Os canais que o reabastecedor bíblico atende. O estoico tem poço próprio
# (conteudo/temas_estoico.json) e NÃO entra aqui.
IDIOMAS_BIBLIA = ("es", "en", "pt")

# Nome da playlist por formato de conteúdo, em cada idioma. Playlist curta e
# bem nichada é o que faz o espectador emendar um vídeo no outro em vez de sair.
PLAYLISTS = {
    "dormir": {
        "es": "Salmos para dormir 🌙",
        "en": "Psalms for sleep 🌙",
        "pt": "Salmos para dormir 🌙",
        "stoic": "Stoic philosophy to fall asleep to 🌙",
    },
    "tema": {
        "es": "Promesas de Dios por tema 🙏",
        "en": "God's promises by theme 🙏",
        "pt": "Promessas de Deus por tema 🙏",
        "stoic": "Stoic wisdom by theme 🏛",
    },
    "historia": {
        "es": "Historias de la Biblia narradas 📖",
        "en": "Bible stories narrated 📖",
        "pt": "Histórias da Bíblia narradas 📖",
    },
}

# GANCHO falado+escrito no 1º segundo de todo Short/Reel. É a peça que decide
# se o vídeo é distribuído: o YouTube só impulsiona Short com view ratio acima
# de 70% (80% é o nível que viraliza), e esse número se decide nos 3 primeiros
# segundos — metade da audiência resolve em 1,7 s. Até 27/07/2026 o Short do
# YouTube entrava direto no versículo; só o Reel do Instagram tinha gancho.
#
# São CHAMADOS curtos (~1,5-2,5 s falados), não pregação: a diretriz editorial
# nº 4 (só o texto bíblico) continua valendo para o CONTEÚDO — o gancho é
# embalagem, e não interpreta nem acrescenta doutrina à passagem.
#
# As três listas são traduções uma da outra, na MESMA ordem de propósito: o
# gancho de índice N diz a mesma coisa nos 3 canais. Isso é o que permite
# comparar desempenho de gancho entre idiomas sem confundir com o conteúdo.
GANCHOS = {
    "es": [
        "Para ti, que estás cansado.",
        "Si te apareció, no fue casualidad.",
        "Escucha esto antes de dormir.",
        "Dios quiere hablarte ahora.",
        "Respira y lee despacio.",
        "Guarda esta promesa en tu corazón.",
        "No sigas sin leer esto.",
        "La Palabra que necesitabas hoy.",
        "Una promesa de Dios para ti.",
        "Deja que Dios calme tu corazón.",
        "Esto es para ti, hoy.",
        "Cuando llegue la ansiedad, recuerda esto.",
    ],
    "en": [
        "For you, who are tired.",
        "If this found you, it wasn't chance.",
        "Hear this before you sleep.",
        "God wants to speak to you now.",
        "Breathe, and read slowly.",
        "Keep this promise in your heart.",
        "Don't scroll past this one.",
        "The Word you needed today.",
        "A promise from God, for you.",
        "Let God quiet your heart.",
        "This one is for you, today.",
        "When anxiety comes, remember this.",
    ],
    # A lista PT nasceu no Reel do Instagram (24/07) e está no ar desde então.
    # A ORDEM não muda: o gancho é escolhido por seed do item, e reordenar
    # trocaria o gancho de posts que já existem.
    "pt": [
        "Pra você que está cansado.",
        "Se apareceu pra você, não foi por acaso.",
        "Ouça isto antes de dormir.",
        "Deus quer te falar agora.",
        "Respire e leia devagar.",
        "Guarde esta promessa no coração.",
        "Não role sem ler isto.",
        "A Palavra que você precisava hoje.",
        "Uma promessa de Deus pra você.",
        "Deixe Deus acalmar o seu coração.",
        "Isto aqui é pra você, hoje.",
        "Quando a ansiedade bater, lembre disto.",
    ],
    # O canal estoico não chama para a fé, chama para a razão — mesmo trabalho
    # de gancho, outro registro. Nada de promessa de resultado ("isto vai mudar
    # sua vida"): o que o texto entrega é uma ideia, e prometer mais do que se
    # entrega é o que o algoritmo lê como insatisfação.
    "stoic": [
        "For you, who cannot switch off tonight.",
        "Marcus Aurelius wrote this for himself.",
        "Read this slowly, before you sleep.",
        "Two thousand years old. Still true.",
        "Keep this one where you can find it.",
        "Don't scroll past this one.",
        "The line that ends the argument.",
        "Seneca, on the thing you're avoiding.",
        "Epictetus said it plainer than anyone.",
        "This is what you actually control.",
        "One thought, for a restless mind.",
        "When the worry comes back, remember this.",
    ],
}

CONFIG = {
    "es": {
        "arquivo_fonte": BIBLIA_DIR / "rv1909.json",
        "fonte_texto": "Reina-Valera 1909 (dominio público)",
        "voz": "es-MX-JorgeNeural",
        "rate_short": "-8%",
        "rate_longo": "-15%",
        "bcp47": "es",
        "palavra_salmo": "Salmo",
        "cta": ("La Palabra de Dios en audio y subtítulos en español. "
                "Contenido nuevo todos los días. Suscríbete \U0001F64F"),
        # Variantes de cierre (27/07/2026): el pie idéntico en todos los
        # videos es una firma de automatización. Se elige una por seed del
        # paquete — mismo mensaje, redacción distinta.
        "ctas": [
            "La Palabra de Dios en audio y subtítulos en español. "
            "Contenido nuevo todos los días. Suscríbete \U0001F64F",
            "Escritura narrada, para escuchar y meditar. "
            "Suscríbete y recibe un pasaje nuevo cada día \U0001F64F",
            "Aquí la Biblia se lee sola: audio claro y subtítulos. "
            "Suscríbete para no perder el pasaje de mañana \U0001F64F",
            "Un pasaje por día, sin prisa y sin comentarios: "
            "solo la Palabra. Suscríbete \U0001F64F",
        ],
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
        "arquivo_fonte": BIBLIA_DIR / "kjv.json",
        "fonte_texto": "King James Version (public domain)",
        "voz": "en-US-ChristopherNeural",
        "rate_short": "-8%",
        "rate_longo": "-15%",
        "bcp47": "en",
        "palavra_salmo": "Psalm",
        "cta": ("God's Word in audio with subtitles. "
                "New Scripture every day. Subscribe \U0001F64F"),
        "ctas": [
            "God's Word in audio with subtitles. "
            "New Scripture every day. Subscribe \U0001F64F",
            "Scripture read aloud, to listen to and rest in. "
            "Subscribe for a new passage each day \U0001F64F",
            "The Bible, plainly read: clear audio and subtitles. "
            "Subscribe so tomorrow's passage finds you \U0001F64F",
            "One passage a day — no commentary, just the Word. "
            "Subscribe \U0001F64F",
        ],
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
        "arquivo_fonte": BIBLIA_DIR / "blivre.json",
        "fonte_texto": "Bíblia Livre (domínio público)",
        "voz": "pt-BR-AntonioNeural",
        "rate_short": "-8%",
        "rate_longo": "-15%",
        "bcp47": "pt",
        "palavra_salmo": "Salmo",
        "cta": ("A Palavra de Deus em áudio e legenda em português. "
                "Conteúdo novo todos os dias. Inscreva-se \U0001F64F"),
        "ctas": [
            "A Palavra de Deus em áudio e legenda em português. "
            "Conteúdo novo todos os dias. Inscreva-se \U0001F64F",
            "Escritura narrada, para ouvir e meditar. "
            "Inscreva-se e receba uma passagem nova por dia \U0001F64F",
            "Aqui a Bíblia é lida em voz alta: áudio limpo e legenda. "
            "Inscreva-se para não perder a passagem de amanhã \U0001F64F",
            "Uma passagem por dia, sem pressa e sem comentário: "
            "só a Palavra. Inscreva-se \U0001F64F",
        ],
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
    # ---- Stoic by Night (@StoicByNight) — primeiro canal não-bíblico -------
    # Voz britânica de propósito: a prosa é a tradução vitoriana de Long e de
    # Gummere, e o registro combina. Também separa o canal das vozes do
    # Palavra Viva — dois canais da mesma conta com a mesma voz é assinatura
    # de fábrica.
    "stoic": {
        "arquivo_fonte": [FONTES_TEXTO_DIR / "marco_aurelio_long.json",
                          FONTES_TEXTO_DIR / "seneca_gummere.json",
                          FONTES_TEXTO_DIR / "epicteto_long.json"],
        "fonte_texto": ("Marcus Aurelius, trans. George Long (1862); "
                        "Seneca, trans. R. M. Gummere (1917–25); "
                        "Epictetus, trans. George Long — all public domain"),
        "voz": "en-GB-RyanNeural",
        # A biblioteca marca/fundos foi curada para conteúdo bíblico; este
        # canal usa as imagens que o próprio poço resolve (ver fabrica.py).
        "biblioteca_local": False,
        "rate_short": "-8%",
        "rate_longo": "-15%",
        "bcp47": "en",
        "palavra_salmo": "Psalm",      # não usado: o corpus não tem Salmos
        "cta": ("Stoic philosophy read aloud, to think with or to sleep to. "
                "New passage every day. Subscribe \U0001F3DB"),
        "ctas": [
            "Stoic philosophy read aloud, to think with or to sleep to. "
            "New passage every day. Subscribe \U0001F3DB",
            "Marcus Aurelius, Seneca and Epictetus — unabridged, plainly read. "
            "Subscribe for a new passage each day \U0001F3DB",
            "No commentary, no advice: the Stoics in their own words. "
            "Subscribe so tomorrow's passage finds you \U0001F3DB",
            "Two thousand years old, read slowly for the end of the day. "
            "Subscribe \U0001F3DB",
        ],
        "hashtags": ("#Stoicism #StoicPhilosophy #MarcusAurelius #Seneca "
                     "#Epictetus"),
        # Tags medidas nos 5 canais líderes do nicho (mineração de 28/07):
        # são praticamente as mesmas entre eles, e é esse conjunto que a busca
        # do YouTube já associa ao assunto.
        "tags": ["stoicism", "stoic", "stoic philosophy", "philosophy",
                 "marcus aurelius", "marcus aurelius meditations",
                 "stoic quotes", "seneca", "epictetus", "stoic wisdom",
                 "ancient wisdom", "stoic mindset", "stoicism for sleep",
                 "philosophy for sleep", "meditations", "discipline"],
        "rotulo_capitulos": "Passages in this video:",
        "rotulo_repeticao": "repeat",
        "rotulo_completo": "Full video",
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
    """Nome exibido do livro. Fora da Bíblia, o próprio nome canônico.

    O motor deixou de ser só bíblico em 28/07/2026: a mesma fábrica narra
    qualquer corpus em domínio público com a estrutura obra/capítulo/passagem
    (o primeiro fora da Bíblia é o estoico — Meditations, Letters, Discourses).
    Esses nomes não têm tradução por idioma nem entram na tabela dos 66 livros,
    então o fallback é devolvê-los como estão, em vez de estourar KeyError.
    """
    return LIVROS.get(idioma, {}).get(canonico, canonico)
