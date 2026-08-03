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
# corpus e textos próprios. "stoic" é o primeiro canal não-bíblico (filosofia
# estoica em domínio público) — ver `fontes/PROVENIENCIA.md`. Nasceu em inglês
# (Stoic by Night); em 02/08/2026 virou ESPANHOL (Noche Estoica), decisão do
# Diego — a chave segue "stoic" porque canal, token e fila são os mesmos.
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
        "stoic": "Filosofía estoica para dormir 🌙",
    },
    "tema": {
        "es": "Promesas de Dios por tema 🙏",
        "en": "God's promises by theme 🙏",
        "pt": "Promessas de Deus por tema 🙏",
        "stoic": "Sabiduría estoica por tema 🏛",
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
# CTA queimada no FIM do Short (28/07/2026). O gancho resolve a entrada; isto
# resolve a saída — pedir uma ação barata converte quem ficou até o fim em
# sinal de engajamento, que é o que o algoritmo usa depois da retenção.
#
# Três regras que vieram do que já se sabe do formato:
#  - SOBREPOSTA, não acrescentada: aparece por cima dos últimos segundos e NÃO
#    estende o vídeo. O Short é um ciclo fechado de propósito (render_short) e
#    a retenção só passa de 100% na segunda passada — cauda extra quebraria a
#    emenda que custou o trabalho de ontem.
#  - Curta e no fim, nunca no começo: quem acabou de chegar não tem motivo
#    para atender a um pedido, e CTA longa vira spam.
#  - Combina com o público: chamado de fé no canal bíblico, chamado de
#    reflexão no estoico. CTA fora do assunto derruba a retenção.
#
# Chamado de fé acelera canal novo mas cansa se repetido para sempre — é
# alavanca de largada, não motor de cruzeiro. Revisar quando o canal crescer.
CTA_VIDEO = {
    "es": "Escribe AMÉN si crees",
    "en": "Type AMEN if you believe",
    "pt": "Escreva AMÉM se você crê",
    # Pedir SAVE, não inscrição: em 2026 o "guardar" é o sinal nº 1 do
    # algoritmo de Reels/Shorts (pesquisa de 02/08, ESTRATEGIA-STOIC-ES.md).
    "stoic": "Guárdalo para cuando lo necesites.",
}

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
    # 02/08/2026: canal virou espanhol. A lista traduz a EN original na MESMA
    # ordem de propósito (compara desempenho de gancho sem confundir com o
    # conteúdo) — exceto o 8º, que citava Sêneca: o corpus ES não tem Sêneca
    # (só existe tradução PD não transcrita — ver PROVENIENCIA.md §7).
    "stoic": [
        "Para ti, que no puedes apagar la mente esta noche.",
        "Marco Aurelio escribió esto solo para él.",
        "Lee esto despacio, antes de dormir.",
        "Tiene dos mil años. Sigue siendo verdad.",
        "Guárdalo donde puedas volver a leerlo.",
        "No sigas bajando sin leer esto.",
        "La frase que termina la discusión.",
        "Un emperador escribió esto de noche.",
        "Epicteto lo dijo más claro que nadie.",
        "Esto es lo único que de verdad controlas.",
        "Un solo pensamiento para una mente inquieta.",
        "Cuando vuelva la preocupación, recuerda esto.",
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
    # ---- Noche Estoica (ex-Stoic by Night) — canal estoico em ESPANHOL ----
    # 02/08/2026: mesmo canal/token/fila, agora para o público hispanohablante
    # (plano em ESTRATEGIA-STOIC-ES.md). Voz ≠ es-MX-Jorge (Palabra Viva):
    # dois canais da mesma conta com a mesma voz é assinatura de fábrica.
    # es-US-Alonso é masculina, grave e de espanhol neutro (a massa do público
    # é LATAM). Alternativas testadas no render: es-CO-Gonzalo, es-ES-Alvaro.
    "stoic": {
        "arquivo_fonte": [FONTES_TEXTO_DIR / "marco_aurelio_diaz.json",
                          FONTES_TEXTO_DIR / "epicteto_brum.json"],
        "fonte_texto": ("Marco Aurelio, trad. J. Díaz de Miranda (1785/1888); "
                        "Epicteto, trad. Antonio Brum (1669/1888) — "
                        "dominio público"),
        "voz": "es-US-AlonsoNeural",
        # A biblioteca marca/fundos foi curada para conteúdo bíblico; este
        # canal usa as imagens que o próprio poço resolve (ver fabrica.py).
        "biblioteca_local": False,
        "rate_short": "-8%",
        "rate_longo": "-15%",
        "bcp47": "es",
        "palavra_salmo": "Salmo",      # não usado: o corpus não tem Salmos
        "cta": ("Filosofía estoica leída en voz alta, para pensar o para "
                "dormir. Un pasaje nuevo cada día. Suscríbete \U0001F3DB"),
        "ctas": [
            "Filosofía estoica leída en voz alta, para pensar o para "
            "dormir. Un pasaje nuevo cada día. Suscríbete \U0001F3DB",
            "Marco Aurelio y Epicteto — texto íntegro, sin comentarios. "
            "Suscríbete y recibe un pasaje nuevo cada día \U0001F3DB",
            "Sin consejos y sin opiniones: los estoicos en sus propias "
            "palabras. Suscríbete \U0001F3DB",
            "Dos mil años de sabiduría, leídos despacio para el final "
            "del día. Suscríbete \U0001F3DB",
        ],
        # 28/07: de 5 hashtags para 3, e descrição enxuta. O método de canal
        # novo põe a dose em 2-3 do nicho — é metadado para o YouTube entender
        # a quem entregar, não campo de SEO. Teto de Short em 20s pelo mesmo
        # manual (10-20s segura melhor do início ao fim).
        "hashtags": "#Estoicismo #FilosofíaEstoica #MarcoAurelio",
        "descricao_curta": True,
        "max_short_s": 20.0,
        # Tags do nicho em espanhol (espelho das medidas em EN em 28/07,
        # conferidas contra os títulos dos canais ES em 02/08).
        "tags": ["estoicismo", "estoico", "filosofía estoica", "filosofía",
                 "marco aurelio", "meditaciones marco aurelio",
                 "frases estoicas", "epicteto", "enquiridión",
                 "sabiduría estoica", "sabiduría antigua", "mentalidad",
                 "estoicismo para dormir", "filosofía para dormir",
                 "meditaciones", "disciplina"],
        "rotulo_capitulos": "Pasajes en este video:",
        "rotulo_repeticao": "repetición",
        "rotulo_completo": "Video completo",
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
