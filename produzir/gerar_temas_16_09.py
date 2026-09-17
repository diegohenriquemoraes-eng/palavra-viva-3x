# -*- coding: utf-8 -*-
"""Reabastecimento do poço bíblico de 16/09/2026 — 24 temas escritos à mão.

Todo salmo não-gigante já era tema `salmo-N-completo`; este lote é de outro
desenho: 16 combos "para dormir" (o formato que rende 76 % das horas do PT),
4 "tema" (Provérbios, Isaías, Romanos, João) e 4 "historia" (Abraão e Isaque,
o filho pródigo, Lázaro, Pedro sobre as águas). Cada Short traz `gancho` em
es/pt — factual, nomeia o que o texto diz ou de onde vem, nunca interpreta —
e não traz `aplicacao` (que tomava o lugar da 2ª narração da passagem).

    python produzir/gerar_temas_16_09.py            # valida e mostra
    python produzir/gerar_temas_16_09.py --gravar   # anexa a conteudo/temas.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "produzir"))
sys.stdout.reconfigure(encoding="utf-8")

from nucleo import biblia  # noqa: E402
import gerar_temas_salmo as G  # noqa: E402

TEMAS = RAIZ / "conteudo" / "temas.json"
NOITE = [["milky way", "night clouds", "starry sky"],
         ["moon clouds", "desert night", "night sky"],
         ["night lake", "moon night", "starry sky"],
         ["night clouds", "moon clouds", "milky way"]]

# ---------------------------------------------------------------------------
# Banco de versículos com gancho (es, pt). Chave = ref scrollmapper.
# ---------------------------------------------------------------------------
V = {
 "Psalms 3:5": ("David escribió esto huyendo de su propio hijo.", "Davi escreveu isto fugindo do próprio filho."),
 "Psalms 4:8": ("Ocho palabras para antes de apagar la luz.", "Oito palavras para antes de apagar a luz."),
 "Psalms 16:8": ("Por qué David dice que no será movido.", "Por que Davi diz que não será abalado."),
 "Psalms 18:2": ("Siete nombres que David le da a Dios en un versículo.", "Sete nomes que Davi dá a Deus num versículo."),
 "Psalms 20:7": ("Con qué contaban los otros, y con qué contaba David.", "Com o que contavam os outros, e com o que contava Davi."),
 "Psalms 23:1": ("El versículo más conocido de la Biblia, completo.", "O versículo mais conhecido da Bíblia, completo."),
 "Psalms 23:4": ("El valle de sombra de muerte, según David.", "O vale da sombra da morte, segundo Davi."),
 "Psalms 25:4-5": ("Lo que David pide antes de tomar una decisión.", "O que Davi pede antes de tomar uma decisão."),
 "Psalms 27:1": ("La pregunta de David que responde al miedo.", "A pergunta de Davi que responde ao medo."),
 "Psalms 27:14": ("Dos veces la misma orden en un versículo.", "Duas vezes a mesma ordem num versículo."),
 "Psalms 30:5": ("Cuánto dura el llanto, según el Salmo treinta.", "Quanto dura o choro, segundo o Salmo trinta."),
 "Psalms 31:15": ("Dónde están tus tiempos, según David.", "Onde estão os teus tempos, segundo Davi."),
 "Psalms 32:8": ("Aquí es Dios quien habla, no David.", "Aqui é Deus quem fala, não Davi."),
 "Psalms 33:20-21": ("Un salmo sin autor, con una espera.", "Um salmo sem autor, com uma espera."),
 "Psalms 34:18": ("A quién está cerca Jehová, según David.", "De quem o Senhor está perto, segundo Davi."),
 "Psalms 37:5": ("Tres verbos: encomienda, confía, y él hará.", "Três verbos: entrega, confia, e ele fará."),
 "Psalms 37:23-24": ("Por qué el que cae no queda tirado.", "Por que quem cai não fica caído."),
 "Psalms 40:1-2": ("De dónde dice David que fue sacado.", "De onde Davi diz que foi tirado."),
 "Psalms 42:11": ("David discute con su propia alma.", "Davi discute com a própria alma."),
 "Psalms 46:1-2": ("El salmo que Lutero convirtió en himno.", "O salmo que Lutero transformou em hino."),
 "Psalms 46:10": ("Dos palabras de Dios para el que no para.", "Duas palavras de Deus para quem não para."),
 "Psalms 51:10": ("Lo que David pidió después de su peor pecado.", "O que Davi pediu depois do seu pior pecado."),
 "Psalms 55:22": ("Qué hacer con la carga, según David.", "O que fazer com a carga, segundo Davi."),
 "Psalms 56:3": ("El día en que temo: la respuesta de David.", "No dia em que temo: a resposta de Davi."),
 "Psalms 57:1": ("David escribió esto escondido en una cueva.", "Davi escreveu isto escondido numa caverna."),
 "Psalms 61:2": ("La oración de David desde el fin de la tierra.", "A oração de Davi desde o fim da terra."),
 "Psalms 62:1-2": ("Por qué David dice que no será movido.", "Por que Davi diz que não será abalado."),
 "Psalms 62:8": ("A quién se le puede decir todo, según David.", "A quem se pode dizer tudo, segundo Davi."),
 "Psalms 63:6-7": ("Lo que David hacía cuando no podía dormir.", "O que Davi fazia quando não conseguia dormir."),
 "Psalms 65:2": ("Un título de Dios: el que oye la oración.", "Um título de Deus: o que ouve a oração."),
 "Psalms 66:20": ("El último versículo del Salmo sesenta y seis.", "O último versículo do Salmo sessenta e seis."),
 "Psalms 67:1": ("Una bendición de tres partes.", "Uma bênção de três partes."),
 "Psalms 71:9": ("La oración para la vejez, en un versículo.", "A oração para a velhice, num versículo."),
 "Psalms 77:11-12": ("Qué hacía Asaf en la noche sin consuelo.", "O que Asafe fazia na noite sem consolo."),
 "Psalms 84:11": ("Lo que Dios no niega, según los hijos de Coré.", "O que Deus não nega, segundo os filhos de Corá."),
 "Psalms 85:8": ("Lo que Dios habla a su pueblo, según este salmo.", "O que Deus fala ao seu povo, segundo este salmo."),
 "Psalms 86:5": ("Tres cosas que David dice de Dios en un versículo.", "Três coisas que Davi diz de Deus num versículo."),
 "Psalms 86:11": ("La oración de David por un corazón sin divisiones.", "A oração de Davi por um coração sem divisões."),
 "Psalms 90:12": ("La oración de Moisés sobre los días.", "A oração de Moisés sobre os dias."),
 "Psalms 90:14": ("Lo que Moisés pide para la mañana.", "O que Moisés pede para a manhã."),
 "Psalms 91:1-2": ("El salmo más leído de noche empieza así.", "O salmo mais lido à noite começa assim."),
 "Psalms 91:4": ("Bajo sus alas: el versículo del amparo.", "Debaixo das suas asas: o versículo do amparo."),
 "Psalms 91:11": ("El versículo que el diablo citó a Jesús.", "O versículo que o diabo citou a Jesus."),
 "Psalms 91:14-15": ("Aquí Dios responde al que lo ama.", "Aqui Deus responde a quem o ama."),
 "Psalms 92:1-2": ("Un salmo para el día de reposo, según la inscripción.", "Um salmo para o dia do descanso, segundo a inscrição."),
 "Psalms 94:19": ("Lo que pasa cuando los pensamientos se multiplican.", "O que acontece quando os pensamentos se multiplicam."),
 "Psalms 95:6-7": ("Una invitación de rodillas.", "Um convite de joelhos."),
 "Psalms 96:1-2": ("Cantad a Jehová canción nueva: el salmo entero llama.", "Cantai ao Senhor um cântico novo: o salmo inteiro chama."),
 "Psalms 97:11": ("Para quién está sembrada la luz.", "Para quem está semeada a luz."),
 "Psalms 100:4-5": ("Cómo entrar, según el Salmo cien.", "Como entrar, segundo o Salmo cem."),
 "Psalms 103:2-4": ("Lo que David manda a su alma no olvidar.", "O que Davi manda a alma não esquecer."),
 "Psalms 103:13": ("Dios comparado con un padre.", "Deus comparado com um pai."),
 "Psalms 104:33-34": ("Una promesa de David para toda la vida.", "Uma promessa de Davi para a vida inteira."),
 "Psalms 107:1": ("Un versículo repetido en toda la Biblia.", "Um versículo repetido em toda a Bíblia."),
 "Psalms 107:29-30": ("Cómo termina la tempestad en el Salmo ciento siete.", "Como termina a tempestade no Salmo cento e sete."),
 "Psalms 108:1": ("David dice que su corazón está listo.", "Davi diz que o seu coração está pronto."),
 "Psalms 111:10": ("Dónde empieza la sabiduría, según el salmo.", "Onde começa a sabedoria, segundo o salmo."),
 "Psalms 112:7": ("Lo que el justo no teme.", "O que o justo não teme."),
 "Psalms 113:7-8": ("Del polvo al trono: un salmo sobre el pobre.", "Do pó ao trono: um salmo sobre o pobre."),
 "Psalms 115:1": ("Un salmo que empieza diciendo: no a nosotros.", "Um salmo que começa dizendo: não a nós."),
 "Psalms 116:1-2": ("Por qué el salmista dice que ama a Jehová.", "Por que o salmista diz que ama o Senhor."),
 "Psalms 116:7": ("Una orden del salmista a su propia alma.", "Uma ordem do salmista à própria alma."),
 "Psalms 118:24": ("El versículo que se canta al despertar.", "O versículo que se canta ao acordar."),
 "Psalms 118:6": ("Lo que el hombre no puede hacerte, según el salmo.", "O que o homem não pode te fazer, segundo o salmo."),
 "Psalms 121:1-2": ("De dónde viene el socorro, según el cántico de las subidas.", "De onde vem o socorro, segundo o cântico das subidas."),
 "Psalms 121:3-4": ("El que te guarda no duerme.", "O que te guarda não dorme."),
 "Psalms 121:7-8": ("El final del salmo del viajero.", "O fim do salmo do viajante."),
 "Psalms 122:1": ("David se alegra por una invitación.", "Davi se alegra por um convite."),
 "Psalms 124:8": ("El último versículo del Salmo ciento veinticuatro.", "O último versículo do Salmo cento e vinte e quatro."),
 "Psalms 125:1-2": ("Los que confían comparados con un monte.", "Os que confiam comparados com um monte."),
 "Psalms 126:5-6": ("Lo que pasa con los que siembran llorando.", "O que acontece com os que semeiam chorando."),
 "Psalms 127:1-2": ("Un salmo de Salomón sobre trabajar de más.", "Um salmo de Salomão sobre trabalhar demais."),
 "Psalms 128:1-2": ("A quién llama bienaventurado el Salmo ciento veintiocho.", "Quem o Salmo cento e vinte e oito chama de bem-aventurado."),
 "Psalms 130:5-6": ("Más que los que esperan la mañana.", "Mais do que os que esperam a manhã."),
 "Psalms 131:2": ("David se compara con un niño destetado.", "Davi se compara com uma criança desmamada."),
 "Psalms 133:1": ("El salmo más corto sobre la familia.", "O salmo mais curto sobre a família."),
 "Psalms 136:1": ("Un salmo que repite la misma frase veintiséis veces.", "Um salmo que repete a mesma frase vinte e seis vezes."),
 "Psalms 138:3": ("El día en que David clamó, y lo que pasó.", "O dia em que Davi clamou, e o que aconteceu."),
 "Psalms 138:8": ("Lo que David dice que Jehová cumplirá.", "O que Davi diz que o Senhor cumprirá."),
 "Psalms 139:9-10": ("Hasta dónde llega la mano de Dios, según David.", "Até onde chega a mão de Deus, segundo Davi."),
 "Psalms 139:14": ("David habla de cómo fue hecho.", "Davi fala de como foi feito."),
 "Psalms 139:23-24": ("La oración con la que termina el Salmo ciento treinta y nueve.", "A oração com que termina o Salmo cento e trinta e nove."),
 "Psalms 141:3": ("Lo que David pide para su boca.", "O que Davi pede para a sua boca."),
 "Psalms 142:5": ("David escribió esto en una cueva, según la inscripción.", "Davi escreveu isto numa caverna, segundo a inscrição."),
 "Psalms 143:8": ("Lo que David quiere oír de mañana.", "O que Davi quer ouvir de manhã."),
 "Psalms 144:1-2": ("Nueve cosas que Dios es para David.", "Nove coisas que Deus é para Davi."),
 "Psalms 145:8-9": ("Cómo es Dios, según David, en dos versículos.", "Como Deus é, segundo Davi, em dois versículos."),
 "Psalms 145:18": ("A quién está cerca Jehová, según el Salmo ciento cuarenta y cinco.", "De quem o Senhor está perto, segundo o Salmo cento e quarenta e cinco."),
 "Psalms 146:5": ("A quién llama bienaventurado el Salmo ciento cuarenta y seis.", "Quem o Salmo cento e quarenta e seis chama de bem-aventurado."),
 "Psalms 147:3": ("Lo que Dios hace con los quebrantados.", "O que Deus faz com os quebrantados."),
 "Psalms 147:4-5": ("Dios cuenta las estrellas, según el salmo.", "Deus conta as estrelas, segundo o salmo."),
 "Psalms 148:3": ("Un salmo en que hasta las estrellas alaban.", "Um salmo em que até as estrelas louvam."),
 "Psalms 149:4": ("Lo que Dios hace con los humildes.", "O que Deus faz com os humildes."),
 "Psalms 150:6": ("El último versículo del libro de los Salmos.", "O último versículo do livro dos Salmos."),
 # Provérbios / Isaías / Romanos / João
 "Proverbs 3:5-6": ("El proverbio más citado de Salomón.", "O provérbio mais citado de Salomão."),
 "Proverbs 3:24": ("Un proverbio sobre acostarse.", "Um provérbio sobre deitar-se."),
 "Proverbs 4:23": ("Qué guardar por encima de todo, según Salomón.", "O que guardar acima de tudo, segundo Salomão."),
 "Proverbs 4:18": ("El camino de los justos comparado con la luz.", "O caminho dos justos comparado com a luz."),
 "Isaiah 40:29": ("A quién da Dios fuerzas, según Isaías.", "A quem Deus dá forças, segundo Isaías."),
 "Isaiah 40:31": ("El versículo de las alas de águila.", "O versículo das asas de águia."),
 "Isaiah 41:10": ("Dios habla en primera persona: no temas.", "Deus fala em primeira pessoa: não temas."),
 "Isaiah 41:13": ("Lo que Dios dice que hace con tu mano.", "O que Deus diz que faz com a tua mão."),
 "Romans 8:28": ("El versículo de Pablo sobre todas las cosas.", "O versículo de Paulo sobre todas as coisas."),
 "Romans 8:31": ("La pregunta de Pablo que nadie puede responder.", "A pergunta de Paulo que ninguém consegue responder."),
 "Romans 8:38-39": ("La lista de Pablo de lo que no puede separarnos.", "A lista de Paulo do que não pode nos separar."),
 "Romans 8:18": ("Cómo compara Pablo el sufrimiento de ahora.", "Como Paulo compara o sofrimento de agora."),
 "John 14:1": ("Lo que Jesús dijo la noche antes de morir.", "O que Jesus disse na noite antes de morrer."),
 "John 14:27": ("La paz que Jesús deja, con sus palabras.", "A paz que Jesus deixa, com as palavras dele."),
 "John 15:5": ("Jesús se compara con una vid.", "Jesus se compara com uma videira."),
 "John 16:33": ("La última frase de Jesús antes de orar.", "A última frase de Jesus antes de orar."),
 # Histórias
 "Genesis 22:7-8": ("La pregunta de Isaac subiendo el monte.", "A pergunta de Isaque subindo o monte."),
 "Genesis 22:11-12": ("El momento en que la voz detiene el cuchillo.", "O momento em que a voz detém a faca."),
 "Genesis 22:13-14": ("El nombre que Abraham le dio a ese lugar.", "O nome que Abraão deu àquele lugar."),
 "Genesis 22:16-17": ("Lo que Dios juró después de la prueba.", "O que Deus jurou depois da prova."),
 "Luke 15:17-19": ("Lo que el hijo pródigo se dijo entre los cerdos.", "O que o filho pródigo disse a si mesmo entre os porcos."),
 "Luke 15:20": ("Lo que hizo el padre cuando lo vio de lejos.", "O que o pai fez quando o viu de longe."),
 "Luke 15:22-24": ("La orden del padre a los siervos.", "A ordem do pai aos servos."),
 "Luke 15:31-32": ("Lo que el padre respondió al hijo mayor.", "O que o pai respondeu ao filho mais velho."),
 "John 11:25-26": ("Jesús dijo esto antes de llegar a la tumba.", "Jesus disse isto antes de chegar ao túmulo."),
 "John 11:35": ("El versículo más corto de la Biblia.", "O versículo mais curto da Bíblia."),
 "John 11:40": ("Lo que Jesús le dijo a Marta frente a la piedra.", "O que Jesus disse a Marta diante da pedra."),
 "John 11:43-44": ("Tres palabras, y el muerto salió.", "Três palavras, e o morto saiu."),
 "Matthew 14:27": ("Lo que Jesús dijo caminando sobre el mar.", "O que Jesus disse andando sobre o mar."),
 "Matthew 14:29-30": ("Pedro caminó sobre el agua hasta que miró el viento.", "Pedro andou sobre a água até olhar para o vento."),
 "Matthew 14:31": ("La pregunta de Jesús a Pedro hundiéndose.", "A pergunta de Jesus a Pedro afundando."),
 "Matthew 14:32-33": ("Lo que pasó cuando subieron a la barca.", "O que aconteceu quando subiram ao barco."),
}

# ---------------------------------------------------------------------------
# Temas
# ---------------------------------------------------------------------------
LIVRO = {"es": {"Psalms": "Salmo", "Proverbs": "Proverbios", "Isaiah": "Isaías",
                "Romans": "Romanos", "John": "Juan", "Luke": "Lucas",
                "Matthew": "Mateo", "Genesis": "Génesis"},
         "pt": {"Psalms": "Salmo", "Proverbs": "Provérbios", "Isaiah": "Isaías",
                "Romans": "Romanos", "John": "João", "Luke": "Lucas",
                "Matthew": "Mateus", "Genesis": "Gênesis"},
         "en": {"Psalms": "Psalm", "Proverbs": "Proverbs", "Isaiah": "Isaiah",
                "Romans": "Romans", "John": "John", "Luke": "Luke",
                "Matthew": "Matthew", "Genesis": "Genesis"}}


def lista(nums: list[int], idioma: str) -> str:
    ext = [G.por_extenso(n, idioma) for n in nums]
    liga = " y " if idioma == "es" else " e "
    return ", ".join(ext[:-1]) + liga + ext[-1] if len(ext) > 1 else ext[0]


def dormir(n: int, salmos: list[int], titulo: dict, thumb: dict, shorts: list[str],
           nota: dict) -> dict:
    nums = ", ".join(str(s) for s in salmos[:-1]) + (" y " if True else "") + str(salmos[-1])
    nums_pt = ", ".join(str(s) for s in salmos[:-1]) + " e " + str(salmos[-1])
    nums_en = ", ".join(str(s) for s in salmos[:-1]) + " and " + str(salmos[-1])
    ab_es = (f"Salmos {lista(salmos, 'es')}, leídos despacio, para escuchar acostado. "
             f"{nota['es']} Sin música alta y sin cortes: solamente el texto de la "
             f"Reina-Valera de mil ochocientos noventa y nueve, de principio a fin.")
    ab_pt = (f"Salmos {lista(salmos, 'pt')}, lidos devagar, para ouvir deitado. "
             f"{nota['pt']} Sem música alta e sem cortes: somente o texto da Bíblia "
             f"Livre, do começo ao fim.")
    return {
        "slug": f"salmos-noche-{n}", "formato": "dormir",
        "longo": {
            "refs": [f"Psalms {s}" for s in salmos],
            "titulo": titulo,
            "thumb_titulo": thumb,
            "thumb_sub": {"es": f"Salmos {nums}", "en": f"Psalms {nums_en}",
                          "pt": f"Salmos {nums_pt}"},
            "consultas_imagens": NOITE[n % len(NOITE)],
            "abertura": {"es": ab_es, "pt": ab_pt},
            "tags_extra": {
                "es": ["salmos para dormir", f"salmo {salmos[0]}", f"salmo {salmos[1]}",
                       "biblia hablada para dormir", "salmos de noche", "salmos narrados"],
                "pt": ["salmos para dormir", f"salmo {salmos[0]}", f"salmo {salmos[1]}",
                       "biblia narrada para dormir", "salmos da noite", "salmos narrados"]},
            "descricao_busca": {
                "es": f"Salmos {nums} seguidos para dormir. Lectura pausada, sin música alta, Reina-Valera 1909.",
                "pt": f"Salmos {nums_pt} seguidos para dormir. Leitura pausada, sem música alta, Bíblia Livre."},
        },
        "shorts": [short(r, NOITE[n % len(NOITE)][k % 3]) for k, r in enumerate(shorts)],
    }


TITULOS_EM_USO: set[str] = set()   # preenchido em main(): acervo + poço


def short(ref: str, img: str) -> dict:
    ges, gpt = V[ref]
    livro, cap, v1, v2 = biblia.analisar_ref(ref)
    vtxt = f"{v1}" if v1 == v2 else f"{v1}-{v2}"
    tit = {}
    for i in ("es", "en", "pt"):
        texto = biblia.carregar_versos(i, ref)[0][1]
        nome = LIVRO[i][livro]
        marca = {"es": "Biblia", "en": "Bible", "pt": "Bíblia"}[i]
        # Título único no acervo: versículo famoso já tem Short publicado com
        # 7 palavras; aqui vai com mais palavras (até 12) até não colidir.
        qtd = 7
        while True:
            palavras = G._aparar(texto.split()[:qtd])
            trecho = " ".join(palavras).rstrip(",;:.")
            t = f"{nome} {cap}:{vtxt} — {trecho} | {marca}"
            if (t not in TITULOS_EM_USO and len(t) <= 100) or qtd >= 12                     or qtd >= len(texto.split()):
                break
            qtd += 1
        trecho = " ".join(palavras).rstrip(",;:.")
        t = f"{nome} {cap}:{vtxt} — {trecho} | {marca}"
        while len(t) > 100 and len(palavras) > 3:
            palavras = G._aparar(palavras[:-1])
            trecho = " ".join(palavras).rstrip(",;:.")
            t = f"{nome} {cap}:{vtxt} — {trecho} | {marca}"
        tit[i] = t[:100].rstrip()
    return {"ref": ref, "tipo": "promesa", "consulta_imagem": img,
            "titulo": tit, "gancho": {"es": ges, "pt": gpt}}


def tema(slug: str, formato: str, refs: list[str], titulo: dict, thumb: dict,
         sub: dict, imgs: list[str], abertura: dict, tags: dict, busca: dict,
         shorts: list[str]) -> dict:
    return {"slug": slug, "formato": formato,
            "longo": {"refs": refs, "titulo": titulo, "thumb_titulo": thumb,
                      "thumb_sub": sub, "consultas_imagens": imgs,
                      "abertura": abertura, "tags_extra": tags,
                      "descricao_busca": busca},
            "shorts": [short(r, imgs[k % len(imgs)]) for k, r in enumerate(shorts)]}


def montar() -> list[dict]:
  return [
 dormir(1, [91, 23, 4], {"es": "Salmos para Dormir — Salmo 91, 23 y 4 | Biblia Hablada Voz Calmada",
                         "en": "Psalms for Sleep — Psalm 91, 23 and 4 | Calm Audio Bible",
                         "pt": "Salmos para Dormir — Salmo 91, 23 e 4 | Bíblia Narrada Voz Calma"},
        {"es": "SALMO 91\nY 23", "en": "PSALM 91\nAND 23", "pt": "SALMO 91\nE 23"},
        ["Psalms 91:1-2", "Psalms 23:4", "Psalms 4:8", "Psalms 91:4"],
        {"es": "El noventa y uno es el salmo del amparo; el veintitrés, el del pastor; el cuatro termina con el versículo de acostarse en paz.",
         "pt": "O noventa e um é o salmo do amparo; o vinte e três, o do pastor; o quatro termina com o versículo de deitar-se em paz."}),
 dormir(2, [121, 127, 131, 3], {"es": "Salmos para Dormir — El Que Te Guarda No Duerme | Salmo 121, 127, 131 y 3",
                                "en": "Psalms for Sleep — He Who Keeps You Will Not Slumber | Psalm 121, 127, 131, 3",
                                "pt": "Salmos para Dormir — Quem Te Guarda Não Dorme | Salmo 121, 127, 131 e 3"},
        {"es": "EL QUE TE\nGUARDA", "en": "HE WHO\nKEEPS YOU", "pt": "QUEM TE\nGUARDA"},
        ["Psalms 121:3-4", "Psalms 127:1-2", "Psalms 131:2", "Psalms 3:5"],
        {"es": "Tres cánticos de las subidas y un salmo de David escrito de noche, huyendo: los cuatro hablan de dormir guardado.",
         "pt": "Três cânticos das subidas e um salmo de Davi escrito de noite, fugindo: os quatro falam de dormir guardado."}),
 dormir(3, [27, 46, 62], {"es": "Salmos para Dormir — Jehová Es Mi Luz | Salmo 27, 46 y 62 Narrados",
                          "en": "Psalms for Sleep — The Lord Is My Light | Psalm 27, 46 and 62",
                          "pt": "Salmos para Dormir — O Senhor É Minha Luz | Salmo 27, 46 e 62 Narrados"},
        {"es": "MI LUZ Y\nMI SALUD", "en": "MY LIGHT\nMY SALVATION", "pt": "MINHA LUZ\nMINHA SALVAÇÃO"},
        ["Psalms 27:1", "Psalms 46:1-2", "Psalms 62:1-2", "Psalms 27:14"],
        {"es": "Tres salmos sobre no temer: el veintisiete empieza con una pregunta, el cuarenta y seis con un refugio, el sesenta y dos con un silencio.",
         "pt": "Três salmos sobre não temer: o vinte e sete começa com uma pergunta, o quarenta e seis com um refúgio, o sessenta e dois com um silêncio."}),
 dormir(4, [34, 37, 40], {"es": "Salmos para Dormir — Cerca Está Jehová | Salmo 34, 37 y 40 Narrados",
                          "en": "Psalms for Sleep — The Lord Is Near | Psalm 34, 37 and 40",
                          "pt": "Salmos para Dormir — Perto Está o Senhor | Salmo 34, 37 e 40 Narrados"},
        {"es": "CERCA ESTÁ\nJEHOVÁ", "en": "THE LORD\nIS NEAR", "pt": "PERTO ESTÁ\nO SENHOR"},
        ["Psalms 34:18", "Psalms 37:5", "Psalms 37:23-24", "Psalms 40:1-2"],
        {"es": "Tres salmos de David sobre esperar: el treinta y cuatro lo escribió fingiéndose loco ante un rey; el cuarenta empieza en un pozo.",
         "pt": "Três salmos de Davi sobre esperar: o trinta e quatro ele escreveu fingindo-se de louco diante de um rei; o quarenta começa num poço."}),
 dormir(5, [63, 143, 130], {"es": "Salmos para Dormir — De Mañana Me Harás Oír | Salmo 63, 143 y 130",
                            "en": "Psalms for Sleep — In the Morning Let Me Hear | Psalm 63, 143 and 130",
                            "pt": "Salmos para Dormir — De Manhã Me Farás Ouvir | Salmo 63, 143 e 130"},
        {"es": "HASTA LA\nMAÑANA", "en": "UNTIL\nMORNING", "pt": "ATÉ A\nMANHÃ"},
        ["Psalms 63:6-7", "Psalms 143:8", "Psalms 130:5-6", "Psalms 116:7"],
        {"es": "Tres salmos para la madrugada: el sesenta y tres habla de meditar en las vigilias de la noche; el ciento treinta, de esperar la mañana.",
         "pt": "Três salmos para a madrugada: o sessenta e três fala de meditar nas vigílias da noite; o cento e trinta, de esperar a manhã."}),
 dormir(6, [103, 145, 146], {"es": "Salmos para Dormir — Bendice, Alma Mía | Salmo 103, 145 y 146 Narrados",
                             "en": "Psalms for Sleep — Bless the Lord, O My Soul | Psalm 103, 145 and 146",
                             "pt": "Salmos para Dormir — Bendize, Ó Minha Alma | Salmo 103, 145 e 146 Narrados"},
        {"es": "BENDICE\nALMA MÍA", "en": "BLESS THE\nLORD", "pt": "BENDIZE\nMINHA ALMA"},
        ["Psalms 103:2-4", "Psalms 103:13", "Psalms 145:8-9", "Psalms 146:5"],
        {"es": "Tres salmos de alabanza para terminar el día: el ciento tres manda al alma no olvidar; el ciento cuarenta y cinco describe cómo es Dios.",
         "pt": "Três salmos de louvor para terminar o dia: o cento e três manda a alma não esquecer; o cento e quarenta e cinco descreve como Deus é."}),
 dormir(7, [139, 16, 18], {"es": "Salmos para Dormir — Tú Me Conoces | Salmo 139, 16 y 18 Narrados",
                           "en": "Psalms for Sleep — You Know Me | Psalm 139, 16 and 18",
                           "pt": "Salmos para Dormir — Tu Me Conheces | Salmo 139, 16 e 18 Narrados"},
        {"es": "TÚ ME\nCONOCES", "en": "YOU\nKNOW ME", "pt": "TU ME\nCONHECES"},
        ["Psalms 139:9-10", "Psalms 139:14", "Psalms 16:8", "Psalms 18:2"],
        {"es": "El ciento treinta y nueve es el salmo del Dios que conoce; el dieciséis y el dieciocho son de David, sobre no ser movido.",
         "pt": "O cento e trinta e nove é o salmo do Deus que conhece; o dezesseis e o dezoito são de Davi, sobre não ser abalado."}),
 dormir(8, [86, 25, 31], {"es": "Salmos para Dormir — En Tu Mano Están Mis Tiempos | Salmo 86, 25 y 31",
                          "en": "Psalms for Sleep — My Times Are in Your Hand | Psalm 86, 25 and 31",
                          "pt": "Salmos para Dormir — Nas Tuas Mãos Estão os Meus Tempos | Salmo 86, 25 e 31"},
        {"es": "EN TU MANO\nMIS TIEMPOS", "en": "MY TIMES\nIN YOUR HAND", "pt": "NAS TUAS MÃOS\nMEUS TEMPOS"},
        ["Psalms 86:5", "Psalms 86:11", "Psalms 25:4-5", "Psalms 31:15"],
        {"es": "Tres oraciones de David: el ochenta y seis pide un corazón sin divisiones; el veinticinco, dirección; el treinta y uno entrega los tiempos.",
         "pt": "Três orações de Davi: o oitenta e seis pede um coração sem divisões; o vinte e cinco, direção; o trinta e um entrega os tempos."}),
 dormir(9, [90, 92, 100], {"es": "Salmos para Dormir — Enséñanos a Contar Nuestros Días | Salmo 90, 92 y 100",
                           "en": "Psalms for Sleep — Teach Us to Number Our Days | Psalm 90, 92 and 100",
                           "pt": "Salmos para Dormir — Ensina-nos a Contar os Nossos Dias | Salmo 90, 92 e 100"},
        {"es": "CONTAR\nLOS DÍAS", "en": "NUMBER\nOUR DAYS", "pt": "CONTAR\nOS DIAS"},
        ["Psalms 90:12", "Psalms 90:14", "Psalms 92:1-2", "Psalms 100:4-5"],
        {"es": "El noventa es la única oración de Moisés en los Salmos; el noventa y dos es para el día de reposo; el cien, para entrar con acción de gracias.",
         "pt": "O noventa é a única oração de Moisés nos Salmos; o noventa e dois é para o dia do descanso; o cem, para entrar com ação de graças."}),
 dormir(10, [107, 116, 118], {"es": "Salmos para Dormir — Para Siempre Es Su Misericordia | Salmo 107, 116 y 118",
                              "en": "Psalms for Sleep — His Mercy Endures Forever | Psalm 107, 116 and 118",
                              "pt": "Psalms para Dormir — Para Sempre É a Sua Misericórdia | Salmo 107, 116 e 118"},
        {"es": "PARA SIEMPRE\nSU MISERICORDIA", "en": "HIS MERCY\nFOREVER", "pt": "PARA SEMPRE\nA MISERICÓRDIA"},
        ["Psalms 107:1", "Psalms 107:29-30", "Psalms 116:1-2", "Psalms 118:6"],
        {"es": "Tres salmos de acción de gracias: el ciento siete cuenta cuatro rescates; el ciento dieciséis, uno solo; el ciento dieciocho es el que Jesús cantó en la última cena.",
         "pt": "Três salmos de ação de graças: o cento e sete conta quatro resgates; o cento e dezesseis, um só; o cento e dezoito é o que Jesus cantou na última ceia."}),
 dormir(11, [121, 124, 125, 126, 128], {"es": "Salmos para Dormir — Cánticos de las Subidas | Salmo 121, 124, 125, 126 y 128",
                                        "en": "Psalms for Sleep — Songs of Ascents | Psalm 121, 124, 125, 126 and 128",
                                        "pt": "Salmos para Dormir — Cânticos das Subidas | Salmo 121, 124, 125, 126 e 128"},
        {"es": "CÁNTICOS DE\nLAS SUBIDAS", "en": "SONGS OF\nASCENTS", "pt": "CÂNTICOS\nDAS SUBIDAS"},
        ["Psalms 121:7-8", "Psalms 124:8", "Psalms 125:1-2", "Psalms 126:5-6"],
        {"es": "Cinco cánticos de las subidas, los que se cantaban en el camino a Jerusalén: cortos, de memoria, uno detrás del otro.",
         "pt": "Cinco cânticos das subidas, os que se cantavam a caminho de Jerusalém: curtos, de cor, um atrás do outro."}),
 dormir(12, [33, 65, 67, 85], {"es": "Salmos para Dormir — Nuestra Alma Esperó a Jehová | Salmo 33, 65, 67 y 85",
                               "en": "Psalms for Sleep — Our Soul Waits for the Lord | Psalm 33, 65, 67 and 85",
                               "pt": "Salmos para Dormir — A Nossa Alma Espera no Senhor | Salmo 33, 65, 67 e 85"},
        {"es": "NUESTRA ALMA\nESPERÓ", "en": "OUR SOUL\nWAITS", "pt": "A NOSSA\nALMA ESPERA"},
        ["Psalms 33:20-21", "Psalms 65:2", "Psalms 67:1", "Psalms 85:8"],
        {"es": "Cuatro salmos de espera y bendición: el sesenta y siete es la bendición sacerdotal vuelta canción; el ochenta y cinco pregunta qué hablará Dios.",
         "pt": "Quatro salmos de espera e bênção: o sessenta e sete é a bênção sacerdotal virada canção; o oitenta e cinco pergunta o que Deus falará."}),
 dormir(13, [42, 55, 56, 57], {"es": "Salmos para Dormir — En el Día Que Temo | Salmo 42, 55, 56 y 57 Narrados",
                               "en": "Psalms for Sleep — When I Am Afraid | Psalm 42, 55, 56 and 57",
                               "pt": "Salmos para Dormir — No Dia em Que Temo | Salmo 42, 55, 56 e 57 Narrados"},
        {"es": "EL DÍA\nQUE TEMO", "en": "WHEN I AM\nAFRAID", "pt": "NO DIA\nEM QUE TEMO"},
        ["Psalms 42:11", "Psalms 55:22", "Psalms 56:3", "Psalms 57:1"],
        {"es": "Cuatro salmos escritos con miedo: el cincuenta y seis, preso por los filisteos; el cincuenta y siete, escondido en una cueva.",
         "pt": "Quatro salmos escritos com medo: o cinquenta e seis, preso pelos filisteus; o cinquenta e sete, escondido numa caverna."}),
 dormir(14, [111, 112, 113, 115], {"es": "Salmos para Dormir — Bienaventurado el Hombre | Salmo 111, 112, 113 y 115",
                                   "en": "Psalms for Sleep — Blessed Is the Man | Psalm 111, 112, 113 and 115",
                                   "pt": "Salmos para Dormir — Bem-aventurado o Homem | Salmo 111, 112, 113 e 115"},
        {"es": "NO TEMERÁ\nMALAS NOTICIAS", "en": "NO FEAR OF\nBAD NEWS", "pt": "NÃO TEMERÁ\nMÁS NOTÍCIAS"},
        ["Psalms 111:10", "Psalms 112:7", "Psalms 113:7-8", "Psalms 115:1"],
        {"es": "Cuatro salmos de aleluya: el ciento doce describe al hombre que no teme malas noticias; el ciento trece levanta al pobre del polvo.",
         "pt": "Quatro salmos de aleluia: o cento e doze descreve o homem que não teme más notícias; o cento e treze levanta o pobre do pó."}),
 dormir(15, [138, 141, 142, 144], {"es": "Salmos para Dormir — Jehová Cumplirá Su Propósito en Mí | Salmo 138, 141, 142 y 144",
                                   "en": "Psalms for Sleep — The Lord Will Fulfill His Purpose | Psalm 138, 141, 142, 144",
                                   "pt": "Salmos para Dormir — O Senhor Cumprirá o Seu Propósito | Salmo 138, 141, 142 e 144"},
        {"es": "JEHOVÁ\nCUMPLIRÁ", "en": "THE LORD\nWILL FULFILL", "pt": "O SENHOR\nCUMPRIRÁ"},
        ["Psalms 138:3", "Psalms 138:8", "Psalms 141:3", "Psalms 142:5"],
        {"es": "Cuatro salmos de David, todos del final del libro: el ciento cuarenta y dos lo escribió en la cueva, sin nadie que lo conociera.",
         "pt": "Quatro salmos de Davi, todos do fim do livro: o cento e quarenta e dois ele escreveu na caverna, sem ninguém que o conhecesse."}),
 dormir(16, [147, 148, 149, 150, 136], {"es": "Salmos para Dormir — Alabad a Jehová | Salmo 147, 148, 149, 150 y 136",
                                        "en": "Psalms for Sleep — Praise the Lord | Psalm 147, 148, 149, 150 and 136",
                                        "pt": "Salmos para Dormir — Louvai ao Senhor | Salmo 147, 148, 149, 150 e 136"},
        {"es": "ALABAD A\nJEHOVÁ", "en": "PRAISE\nTHE LORD", "pt": "LOUVAI AO\nSENHOR"},
        ["Psalms 147:3", "Psalms 147:4-5", "Psalms 148:3", "Psalms 150:6"],
        {"es": "Los cuatro últimos salmos del libro, que empiezan y terminan con aleluya, y el ciento treinta y seis, que repite la misma frase veintiséis veces.",
         "pt": "Os quatro últimos salmos do livro, que começam e terminam com aleluia, e o cento e trinta e seis, que repete a mesma frase vinte e seis vezes."}),
 tema("proverbios-3-4", "tema", ["Proverbs 3", "Proverbs 4"],
      {"es": "Proverbios 3 y 4 — Confía en Jehová con Todo Tu Corazón | Biblia Hablada",
       "en": "Proverbs 3 and 4 — Trust in the Lord with All Your Heart | Audio Bible",
       "pt": "Provérbios 3 e 4 — Confia no Senhor de Todo o Teu Coração | Bíblia Narrada"},
      {"es": "CONFÍA CON\nTODO EL CORAZÓN", "en": "TRUST WITH\nALL YOUR HEART", "pt": "CONFIA DE\nTODO O CORAÇÃO"},
      {"es": "Proverbios 3 y 4 completos", "en": "Proverbs 3 and 4 in full", "pt": "Provérbios 3 e 4 completos"},
      ["clay lamp", "night clouds", "burning candle"],
      {"es": "Dos capítulos de Proverbios, completos: el tres, con el versículo más citado de Salomón, y el cuatro, con la orden de guardar el corazón sobre toda cosa. Sin comentario: solamente el texto de la Reina-Valera de mil ochocientos noventa y nueve.",
       "pt": "Dois capítulos de Provérbios, completos: o três, com o versículo mais citado de Salomão, e o quatro, com a ordem de guardar o coração acima de tudo. Sem comentário: somente o texto da Bíblia Livre."},
      {"es": ["proverbios 3", "proverbios 4", "confia en jehova", "biblia hablada", "sabiduria de salomon"],
       "pt": ["proverbios 3", "proverbios 4", "confia no senhor", "biblia narrada", "sabedoria de salomao"]},
      {"es": "Proverbios 3 y 4 completos, leídos despacio. Reina-Valera 1909.",
       "pt": "Provérbios 3 e 4 completos, lidos devagar. Bíblia Livre."},
      ["Proverbs 3:5-6", "Proverbs 3:24", "Proverbs 4:23", "Proverbs 4:18"]),
 tema("isaias-40-41", "tema", ["Isaiah 40", "Isaiah 41"],
      {"es": "Isaías 40 y 41 — No Temas, Porque Yo Estoy Contigo | Biblia Hablada",
       "en": "Isaiah 40 and 41 — Fear Not, for I Am with You | Audio Bible",
       "pt": "Isaías 40 e 41 — Não Temas, Porque Eu Sou Contigo | Bíblia Narrada"},
      {"es": "NO TEMAS", "en": "FEAR NOT", "pt": "NÃO TEMAS"},
      {"es": "Isaías 40 y 41 completos", "en": "Isaiah 40 and 41 in full", "pt": "Isaías 40 e 41 completos"},
      ["desert night", "starry sky", "moon clouds"],
      {"es": "Dos capítulos de Isaías, completos: el cuarenta, que empieza con consolaos y termina con las alas de águila, y el cuarenta y uno, donde Dios dice no temas en primera persona.",
       "pt": "Dois capítulos de Isaías, completos: o quarenta, que começa com consolai e termina com as asas de águia, e o quarenta e um, onde Deus diz não temas em primeira pessoa."},
      {"es": ["isaias 40", "isaias 41", "no temas", "biblia hablada", "consolaos pueblo mio"],
       "pt": ["isaias 40", "isaias 41", "nao temas", "biblia narrada", "consolai o meu povo"]},
      {"es": "Isaías 40 y 41 completos, leídos despacio. Reina-Valera 1909.",
       "pt": "Isaías 40 e 41 completos, lidos devagar. Bíblia Livre."},
      ["Isaiah 40:29", "Isaiah 40:31", "Isaiah 41:10", "Isaiah 41:13"]),
 tema("romanos-8", "tema", ["Romans 8"],
      {"es": "Romanos 8 — Nada Nos Separará del Amor de Dios | Biblia Hablada",
       "en": "Romans 8 — Nothing Can Separate Us from the Love of God | Audio Bible",
       "pt": "Romanos 8 — Nada Nos Separará do Amor de Deus | Bíblia Narrada"},
      {"es": "NADA NOS\nSEPARARÁ", "en": "NOTHING CAN\nSEPARATE US", "pt": "NADA NOS\nSEPARARÁ"},
      {"es": "Romanos 8 completo", "en": "Romans 8 in full", "pt": "Romanos 8 completo"},
      ["night clouds", "milky way", "moon night"],
      {"es": "El capítulo ocho de la carta a los Romanos, completo: treinta y nueve versículos que empiezan sin condenación y terminan con la lista de lo que no puede separarnos.",
       "pt": "O capítulo oito da carta aos Romanos, completo: trinta e nove versículos que começam sem condenação e terminam com a lista do que não pode nos separar."},
      {"es": ["romanos 8", "nada nos separara", "biblia hablada", "carta a los romanos", "todas las cosas ayudan a bien"],
       "pt": ["romanos 8", "nada nos separara", "biblia narrada", "carta aos romanos", "todas as coisas cooperam"]},
      {"es": "Romanos 8 completo, leído despacio. Reina-Valera 1909.",
       "pt": "Romanos 8 completo, lido devagar. Bíblia Livre."},
      ["Romans 8:28", "Romans 8:31", "Romans 8:38-39", "Romans 8:18"]),
 tema("juan-14-16", "tema", ["John 14", "John 15", "John 16"],
      {"es": "Juan 14, 15 y 16 — No Se Turbe Vuestro Corazón | Biblia Hablada",
       "en": "John 14, 15 and 16 — Let Not Your Heart Be Troubled | Audio Bible",
       "pt": "João 14, 15 e 16 — Não Se Turbe o Vosso Coração | Bíblia Narrada"},
      {"es": "NO SE TURBE\nTU CORAZÓN", "en": "LET NOT YOUR\nHEART BE TROUBLED", "pt": "NÃO SE TURBE\nO CORAÇÃO"},
      {"es": "Juan 14, 15 y 16 completos", "en": "John 14, 15 and 16 in full", "pt": "João 14, 15 e 16 completos"},
      ["burning candle", "night clouds", "clay lamp"],
      {"es": "Tres capítulos de Juan, completos: lo que Jesús dijo a los suyos la noche antes de morir, desde no se turbe vuestro corazón hasta yo he vencido al mundo.",
       "pt": "Três capítulos de João, completos: o que Jesus disse aos seus na noite antes de morrer, de não se turbe o vosso coração até eu venci o mundo."},
      {"es": ["juan 14", "juan 15", "juan 16", "no se turbe vuestro corazon", "biblia hablada", "palabras de jesus"],
       "pt": ["joao 14", "joao 15", "joao 16", "nao se turbe o vosso coracao", "biblia narrada", "palavras de jesus"]},
      {"es": "Juan 14, 15 y 16 completos, leídos despacio. Reina-Valera 1909.",
       "pt": "João 14, 15 e 16 completos, lidos devagar. Bíblia Livre."},
      ["John 14:1", "John 14:27", "John 15:5", "John 16:33"]),
 tema("abraao-isaque", "historia", ["Genesis 22:1-19"],
      {"es": "Abraham e Isaac — Dios Proveerá | Génesis 22 Narrado Completo",
       "en": "Abraham and Isaac — God Will Provide | Genesis 22 Narrated in Full",
       "pt": "Abraão e Isaque — Deus Proverá | Gênesis 22 Narrado Completo"},
      {"es": "DIOS\nPROVEERÁ", "en": "GOD WILL\nPROVIDE", "pt": "DEUS\nPROVERÁ"},
      {"es": "Génesis 22 — historia completa", "en": "Genesis 22 — full story", "pt": "Gênesis 22 — história completa"},
      ["desert night", "bonfire night", "starry sky"],
      {"es": "Génesis veintidós, completo: la prueba de Abraham, la pregunta de Isaac subiendo el monte y el carnero trabado en el zarzal. Solamente el texto, sin comentario.",
       "pt": "Gênesis vinte e dois, completo: a prova de Abraão, a pergunta de Isaque subindo o monte e o carneiro preso no mato. Somente o texto, sem comentário."},
      {"es": ["abraham e isaac", "genesis 22", "historias biblicas", "dios proveera", "biblia narrada"],
       "pt": ["abraao e isaque", "genesis 22", "historias biblicas", "deus provera", "biblia narrada"]},
      {"es": "Génesis 22 completo: Abraham e Isaac en el monte Moriah. Reina-Valera 1909.",
       "pt": "Gênesis 22 completo: Abraão e Isaque no monte Moriá. Bíblia Livre."},
      ["Genesis 22:7-8", "Genesis 22:11-12", "Genesis 22:13-14", "Genesis 22:16-17"]),
 tema("filho-prodigo", "historia", ["Luke 15:11-32"],
      {"es": "El Hijo Pródigo — La Parábola Completa | Lucas 15 Narrado",
       "en": "The Prodigal Son — The Complete Parable | Luke 15 Narrated",
       "pt": "O Filho Pródigo — A Parábola Completa | Lucas 15 Narrado"},
      {"es": "EL HIJO\nPRÓDIGO", "en": "THE PRODIGAL\nSON", "pt": "O FILHO\nPRÓDIGO"},
      {"es": "Lucas 15 — parábola completa", "en": "Luke 15 — full parable", "pt": "Lucas 15 — parábola completa"},
      ["dusk sky", "night clouds", "fireplace fire"],
      {"es": "Lucas quince, del versículo once al treinta y dos: la parábola del hijo que pidió su herencia, la gastó y volvió. Solamente el texto, sin comentario.",
       "pt": "Lucas quinze, do versículo onze ao trinta e dois: a parábola do filho que pediu a herança, gastou tudo e voltou. Somente o texto, sem comentário."},
      {"es": ["hijo prodigo", "lucas 15", "parabolas de jesus", "historias biblicas", "biblia narrada"],
       "pt": ["filho prodigo", "lucas 15", "parabolas de jesus", "historias biblicas", "biblia narrada"]},
      {"es": "Lucas 15:11-32 completo: la parábola del hijo pródigo. Reina-Valera 1909.",
       "pt": "Lucas 15:11-32 completo: a parábola do filho pródigo. Bíblia Livre."},
      ["Luke 15:17-19", "Luke 15:20", "Luke 15:22-24", "Luke 15:31-32"]),
 tema("lazaro", "historia", ["John 11:1-44"],
      {"es": "Lázaro, Ven Fuera — La Resurrección de Lázaro | Juan 11 Narrado",
       "en": "Lazarus, Come Forth — The Raising of Lazarus | John 11 Narrated",
       "pt": "Lázaro, Vem Para Fora — A Ressurreição de Lázaro | João 11 Narrado"},
      {"es": "LÁZARO\nVEN FUERA", "en": "LAZARUS\nCOME FORTH", "pt": "LÁZARO\nVEM PARA FORA"},
      {"es": "Juan 11 — historia completa", "en": "John 11 — full story", "pt": "João 11 — história completa"},
      ["torch fire", "night clouds", "clay lamp"],
      {"es": "Juan once, del versículo uno al cuarenta y cuatro: la enfermedad, los cuatro días, el versículo más corto de la Biblia y la voz frente a la tumba. Solamente el texto.",
       "pt": "João onze, do versículo um ao quarenta e quatro: a doença, os quatro dias, o versículo mais curto da Bíblia e a voz diante do túmulo. Somente o texto."},
      {"es": ["lazaro", "juan 11", "resurreccion de lazaro", "historias biblicas", "biblia narrada"],
       "pt": ["lazaro", "joao 11", "ressurreicao de lazaro", "historias biblicas", "biblia narrada"]},
      {"es": "Juan 11:1-44 completo: la resurrección de Lázaro. Reina-Valera 1909.",
       "pt": "João 11:1-44 completo: a ressurreição de Lázaro. Bíblia Livre."},
      ["John 11:25-26", "John 11:35", "John 11:40", "John 11:43-44"]),
 tema("pedro-sobre-as-aguas", "historia", ["Matthew 14:22-33"],
      {"es": "Pedro Camina Sobre el Mar — Hombre de Poca Fe | Mateo 14 Narrado",
       "en": "Peter Walks on Water — O You of Little Faith | Matthew 14 Narrated",
       "pt": "Pedro Anda Sobre o Mar — Homem de Pouca Fé | Mateus 14 Narrado"},
      {"es": "SOBRE\nEL MAR", "en": "ON THE\nWATER", "pt": "SOBRE\nO MAR"},
      {"es": "Mateo 14 — historia completa", "en": "Matthew 14 — full story", "pt": "Mateus 14 — história completa"},
      ["night sea", "storm clouds", "moon clouds"],
      {"es": "Mateo catorce, del versículo veintidós al treinta y tres: la barca de noche, la cuarta vigilia, Pedro sobre el agua y la mano que lo sostiene. Solamente el texto.",
       "pt": "Mateus catorze, do versículo vinte e dois ao trinta e três: o barco de noite, a quarta vigília, Pedro sobre a água e a mão que o segura. Somente o texto."},
      {"es": ["pedro camina sobre el agua", "mateo 14", "historias biblicas", "hombre de poca fe", "biblia narrada"],
       "pt": ["pedro anda sobre as aguas", "mateus 14", "historias biblicas", "homem de pouca fe", "biblia narrada"]},
      {"es": "Mateo 14:22-33 completo: Pedro camina sobre el mar. Reina-Valera 1909.",
       "pt": "Mateus 14:22-33 completo: Pedro anda sobre o mar. Bíblia Livre."},
      ["Matthew 14:27", "Matthew 14:29-30", "Matthew 14:31", "Matthew 14:32-33"]),
  ]


def main() -> None:
    temas = json.loads(TEMAS.read_text(encoding="utf-8"))
    slugs = {t["slug"] for t in temas}
    titulos = {s["titulo"][i] for t in temas for s in t["shorts"] for i in ("es", "pt")}
    TITULOS_EM_USO.update(titulos)
    refs = set()
    novos = montar()
    for t in novos:
        assert t["slug"] not in slugs, t["slug"]
        for r in t["longo"]["refs"]:
            for i in ("es", "en", "pt"):
                biblia.carregar_versos(i, r)
        for i in ("es", "en", "pt"):
            assert len(t["longo"]["titulo"][i]) <= 100, t["longo"]["titulo"][i]
        for s in t["shorts"]:
            assert s["ref"] not in refs, f"ref repetida: {s['ref']}"
            refs.add(s["ref"])
            n = sum(len(x.split()) for _, x in biblia.carregar_versos("es", s["ref"]))
            assert 2 <= n <= 60, (s["ref"], n)
            for i in ("es", "pt"):
                assert s["titulo"][i] not in titulos, s["titulo"][i]
                titulos.add(s["titulo"][i])
                assert len(s["gancho"][i].split()) <= 13, s["gancho"][i]
        print(f"  {t['slug']}: {[s['ref'] for s in t['shorts']]}")
    print(f"\n{len(novos)} temas, {sum(len(t['shorts']) for t in novos)} Shorts — ok")
    if "--gravar" in sys.argv:
        temas.extend(novos)
        TEMAS.write_text(json.dumps(temas, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
        print("gravado.")


if __name__ == "__main__":
    main()
