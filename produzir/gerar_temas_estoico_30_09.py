# -*- coding: utf-8 -*-
"""Reabastecimento do poço estoico de 30/09/2026 — 15 temas escritos à mão.

O poço zerou e La Noche Estoica parou de publicar em 28/09 (o alarme do vigia
existia desde 17/09). Este lote foi escrito relendo o PROTOCOLO FANTASMA:

- 1 tema = 1 dia da fila (4 Shorts, 3 publicados + 1 de reserva) e 1 longo.
- Short mais curto: citação de ≤ 30 palavras na maioria (o manual pede 10-20 s;
  o acervo estava em 22-28 s). Gancho de AFIRMAÇÃO/autoridade por Short (no
  estoico faz ~2x o gancho de consolo), escrito depois do trecho, ≤ 10 palavras.
- Título curto (≤ 40 caracteres), segunda pessoa, abre a pergunta sem
  entregar a resposta — o padrão dos campeões do canal ("Cuando todo te sabe
  amargo", "El médico también murió").
- Camada autoral em TODO Short (`aplicacao`) e, no longo, abertura + `cierre`
  falados por nós: é o que separa o canal de "readings of other materials you
  did not originally create" (answer/1311392).
- Longo no formato `libro`: UM livro das Meditaciones ou um terço do
  Enquiridión, inteiro e sem repetição (alvo 0). Os 15 longos usam 15 fontes
  diferentes — nenhum trecho aparece em dois longos deste lote.

    python produzir/gerar_temas_estoico_30_09.py            # valida e mostra
    python produzir/gerar_temas_estoico_30_09.py --gravar   # anexa ao poço
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.stdout.reconfigure(encoding="utf-8")

from nucleo import biblia  # noqa: E402

POCO = RAIZ / "conteudo" / "temas_estoico.json"
DESEMPENHO = RAIZ / "conteudo" / "desempenho.json"


def enq(a: int, b: int) -> list[str]:
    return [f"Enquiridión {c}" for c in range(a, b + 1)]


def med(n: int) -> list[str]:
    return [f"Meditaciones {n}"]


ROMANO = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII",
          8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII"}

# (ref, tipo, imagem, título, gancho, aplicação)
S = tuple[str, str, str, str, str, str]

LOTE: list[dict] = [
 {"slug": "solo-esto-es-tuyo", "refs": enq(1, 26),
  "titulo": "Solo Esto Es Tuyo | Epicteto, Enquiridión I-XXVI",
  "thumb": "SOLO ESTO\nES TUYO", "sub": "Epicteto, Enquiridión I-XXVI",
  "imgs": ["clay lamp", "night clouds", "harbor night"],
  "abertura": "Epicteto nació esclavo. Lo primero que enseñaba a sus alumnos era una división: lo que depende de ti y lo que no. Estos son los primeros veintiséis capítulos de su manual, tal como los tradujo Antonio Brum.",
  "cierre": "Eso fue Epicteto. Si te quedas con una sola idea, que sea esta: antes de preocuparte, pregunta de quién es el problema. Lo tuyo es tu juicio, tu esfuerzo y tu palabra. Lo demás llega y se va, y no te pide permiso.",
  "tags": ["epicteto", "enquiridion", "dicotomia del control", "lo que depende de ti", "estoicismo"],
  "desc": "Epicteto, Enquiridión, capítulos I a XXVI, narrados en español (trad. Antonio Brum).",
  "shorts": [
   ("Enquiridión 1:1/2", "maxim", "harbor night", "Tu reputación no es tuya", "Epicteto puso tu reputación fuera de tu control.", "Cuida lo que haces; lo que dicen de ti lo administra otro."),
   ("Enquiridión 5:1/3", "reframe", "clay lamp", "La pregunta que corta la ansiedad", "Una pregunta de Epicteto para cualquier problema.", "Antes de angustiarte, pregunta de quién es el problema."),
   ("Enquiridión 6:1/3", "maxim", "night clouds", "El único miedo que nunca se cumple", "Hay un miedo que nunca se cumple.", "Teme mentir, no perder: lo primero lo evitas tú."),
   ("Enquiridión 27:1/3", "maxim", "torch fire", "Ni senador ni emperador: libre", "Un exesclavo le dijo esto a la Roma ambiciosa.", "El cargo te lo pueden quitar; la libertad interior, no."),
  ]},
 {"slug": "la-olla-de-barro", "refs": med(10),
  "titulo": "Todo Lo Que Amas Se Puede Romper | Marco Aurelio, Libro X",
  "thumb": "SE PUEDE\nROMPER", "sub": "Marco Aurelio, Meditaciones X",
  "imgs": ["clay lamp", "moon clouds", "dusk sky"],
  "abertura": "El décimo libro de las Meditaciones lo escribió un emperador viejo, en campaña, lejos de Roma. Habla de recibir y de devolver: de tener las cosas sin creer que son para siempre. Este es el libro completo.",
  "cierre": "Marco Aurelio no pedía querer menos, sino querer sabiendo. La olla es de barro, el tiempo es prestado, la gente que amas no es tuya. Saberlo no enfría el cariño: lo prepara para el día en que algo se rompa.",
  "tags": ["marco aurelio", "meditaciones libro 10", "aceptar la perdida", "desapego estoico", "estoicismo"],
  "desc": "El libro X de las Meditaciones de Marco Aurelio, completo, narrado en español.",
  "shorts": [
   ("Enquiridión 8:1/3", "reframe", "clay lamp", "Piensa que se puede romper", "El truco de Epicteto con una olla de barro.", "Lo que amas es frágil; saberlo no te enfría, te prepara."),
   ("Enquiridión 33:1/2", "reframe", "rain window", "Cuando el vaso roto es el tuyo", "Lo que dices cuando el vaso roto es ajeno.", "Repítete el consuelo que regalas a los demás."),
   ("Meditaciones 8:49/1", "maxim", "old clock", "Todo tu tiempo fue un regalo", "Marco Aurelio sobre el tiempo que nadie te debía.", "Lo regalado no se reclama: se agradece mientras dura."),
   ("Meditaciones 10:29/1", "maxim", "moon clouds", "Dame lo que quieras, quítame lo que quieras", "La oración de un emperador a la Naturaleza.", "Recibir sin aferrarse: así se pierde sin romperse."),
  ]},
 {"slug": "nadie-te-ofende", "refs": med(8),
  "titulo": "La Ofensa Necesita Tu Firma | Marco Aurelio, Libro VIII",
  "thumb": "SIN TU\nPERMISO", "sub": "Marco Aurelio, Meditaciones VIII",
  "imgs": ["storm clouds", "night clouds", "bonfire night"],
  "abertura": "El octavo libro de las Meditaciones vuelve una y otra vez a la misma pregunta: qué parte del daño viene de fuera y qué parte pone uno mismo. Lo escuchas completo, en la traducción de Díaz de Miranda.",
  "cierre": "La idea que atraviesa este libro es incómoda: el insulto llega, pero la herida la ponemos nosotros. No significa aguantarlo todo. Significa que quien puede enojarte cuando quiere tiene el mando de tu día, y ese mando se puede recuperar.",
  "tags": ["marco aurelio", "meditaciones libro 8", "como no ofenderse", "insultos estoicismo", "estoicismo"],
  "desc": "El libro VIII de las Meditaciones de Marco Aurelio, completo, narrado en español.",
  "shorts": [
   ("Enquiridión 38:2/1", "maxim", "storm clouds", "La ofensa necesita tu firma", "Epicteto explicó quién decide si te ofenden.", "El insulto llega; la herida la pones tú."),
   ("Meditaciones 8:56/2-3", "reframe", "night clouds", "Te contaron que hablan mal de ti", "Marco Aurelio separa el chisme del daño.", "Te dieron una noticia, no una herida. No la conviertas."),
   ("Meditaciones 8:63/1", "reframe", "dark forest", "¿Quieres el aplauso de quien se odia?", "Antes de buscar su aprobación, oye esto.", "Mira cómo se trata él antes de pedirle que te juzgue."),
   ("Enquiridión 18:2/3", "maxim", "bonfire night", "Quien te enoja cuando quiere, te manda", "Si cualquiera te enciende, tu calma tiene dueño.", "Recupera el mando: que tu humor no dependa del ajeno."),
  ]},
 {"slug": "la-fama-se-olvida", "refs": med(4),
  "titulo": "Todo Nombre Acaba en el Olvido | Marco Aurelio, Libro IV",
  "thumb": "EL\nOLVIDO", "sub": "Marco Aurelio, Meditaciones IV",
  "imgs": ["milky way", "desert night", "night clouds"],
  "abertura": "El cuarto libro de las Meditaciones es el más largo sobre la fama. Marco Aurelio era el hombre más famoso de su mundo y escribió, para sí mismo, que todo nombre acaba olvidado. Este es el libro entero.",
  "cierre": "Lo curioso es que lo escribió alguien a quien todavía recordamos. Y aun así tenía razón: trabajar para que te recuerden es construir sobre arena. Trabajar para hacer el bien deja algo aunque nadie sepa tu nombre.",
  "tags": ["marco aurelio", "meditaciones libro 4", "la fama", "vanidad estoicismo", "estoicismo"],
  "desc": "El libro IV de las Meditaciones de Marco Aurelio, completo, narrado en español.",
  "shorts": [
   ("Meditaciones 6:27/2", "maxim", "desert night", "Quieren el aplauso de quien no verán", "El desatino que Marco Aurelio veía en todos.", "Elogia hoy a quien tienes al lado; el futuro no te aplaude."),
   ("Meditaciones 4:30/5", "reframe", "torch fire", "La esmeralda no necesita aplausos", "Una piedra preciosa contra tu ansia de elogios.", "Si vales, vales en silencio. El elogio no te añade nada."),
   ("Meditaciones 4:50/2", "maxim", "milky way", "Todo acaba siendo leyenda, y luego nada", "Lo que el olvido hace con todos los nombres.", "Trabaja por lo que es bueno, no por lo que se recuerda."),
   ("Meditaciones 8:28/4-5", "maxim", "night clouds", "El que enterró también fue enterrado", "La lista de entierros que escribió un emperador.", "Nadie queda para contar el final. Vive el tuyo con sentido."),
  ]},
 {"slug": "manos-a-la-obra", "refs": med(5),
  "titulo": "Levántate y Haz Tu Trabajo | Marco Aurelio, Libro V",
  "thumb": "MANOS A\nLA OBRA", "sub": "Marco Aurelio, Meditaciones V",
  "imgs": ["dusk sky", "old clock", "torch fire"],
  "abertura": "El quinto libro de las Meditaciones empieza en la cama: un emperador que no quiere levantarse y se discute a sí mismo. Es el libro de la pereza y del deber, completo.",
  "cierre": "Si a un emperador le costaba levantarse, a ti también te va a costar. La diferencia no está en las ganas, que casi nunca llegan, sino en empezar sin ellas. Elige una tarea pequeña y hazla antes de que la duda tenga tiempo de hablar.",
  "tags": ["marco aurelio", "meditaciones libro 5", "pereza", "disciplina estoica", "estoicismo"],
  "desc": "El libro V de las Meditaciones de Marco Aurelio, completo, narrado en español.",
  "shorts": [
   ("Meditaciones 9:44/4", "maxim", "torch fire", "Hazlo aunque nadie lo vea", "Una orden de Marco Aurelio para hoy.", "La obra buena no espera testigos ni el momento perfecto."),
   ("Meditaciones 5:1/4", "reframe", "dusk sky", "¿Naciste para quedarte en la cama?", "Lo que se reprochaba el emperador al despertar.", "La pereza promete descanso y te cobra en culpa."),
   ("Meditaciones 5:1/5", "reframe", "dark forest", "Hasta la hormiga termina su trabajo", "Marco Aurelio se comparó con una hormiga.", "Todo en la naturaleza cumple su tarea. Cumple la tuya."),
   ("Meditaciones 2:4/2", "maxim", "burning candle", "Deja los libros y vive", "Un emperador filósofo se ordenó dejar de leer.", "Leer sobre el cambio también es una forma de no cambiar."),
  ]},
 {"slug": "el-banquete", "refs": enq(27, 52),
  "titulo": "Vive Como en un Banquete | Epicteto, Enquiridión XXVII-LII",
  "thumb": "EL\nBANQUETE", "sub": "Epicteto, Enquiridión XXVII-LII",
  "imgs": ["bonfire night", "clay lamp", "harbor night"],
  "abertura": "La parte central del manual de Epicteto trata del deseo: del placer, del dinero, de lo que otros tienen. Su imagen favorita es un banquete. Escuchas los capítulos veintisiete a cincuenta y dos.",
  "cierre": "La regla del banquete es sencilla: toma tu parte cuando el plato llegue a ti, no lo arrebates, no lo persigas cuando se va. Casi toda la ansiedad por tener más es querer comer antes de que te sirvan.",
  "tags": ["epicteto", "enquiridion", "el deseo", "templanza estoica", "estoicismo"],
  "desc": "Epicteto, Enquiridión, capítulos XXVII a LII, narrados en español (trad. Antonio Brum).",
  "shorts": [
   ("Enquiridión 22:1/1", "maxim", "bonfire night", "Vive como en un banquete", "La regla del banquete de Epicteto.", "Toma tu parte cuando llegue; no arrebates el plato ajeno."),
   ("Enquiridión 56:1/4", "reframe", "burning candle", "El gusto de haber dicho que no", "El placer que Epicteto ponía sobre el placer.", "Decir no también se disfruta, y ese gusto no deja resaca."),
   ("Enquiridión 56:1/3", "reframe", "rain window", "El placer dura menos que la culpa", "La cuenta de Epicteto antes de cada tentación.", "Cuenta los minutos de gusto y las horas de culpa."),
   ("Enquiridión 61:1/4", "maxim", "fireplace fire", "Pasado el límite, ya no hay límite", "Por qué el primer exceso nunca es el último.", "El «solo esta vez» es la puerta, no la excepción."),
  ]},
 {"slug": "el-filosofo-callado", "refs": enq(53, 78),
  "titulo": "No Digas Que Eres Filósofo | Epicteto, Enquiridión LIII-LXXVIII",
  "thumb": "NO LO\nDIGAS", "sub": "Epicteto, Enquiridión LIII-LXXVIII",
  "imgs": ["smoke incense", "clay lamp", "night clouds"],
  "abertura": "El final del manual de Epicteto es una advertencia a sus propios alumnos: saber filosofía no es lo mismo que vivirla. Escuchas los últimos capítulos, del cincuenta y tres al setenta y ocho.",
  "cierre": "Epicteto termina donde empieza la vida real: en lo que haces cuando nadie te pide que expliques. No hace falta citar a los estoicos. Basta con que, mañana, alguien note que ya no reaccionas igual.",
  "tags": ["epicteto", "enquiridion", "practicar la filosofia", "humildad estoica", "estoicismo"],
  "desc": "Epicteto, Enquiridión, capítulos LIII a LXXVIII, narrados en español (trad. Antonio Brum).",
  "shorts": [
   ("Enquiridión 68:1/1", "maxim", "smoke incense", "No digas que eres filósofo", "Epicteto prohibía presumir de lo que lees.", "Que te noten por cómo vives, no por lo que citas."),
   ("Enquiridión 68:2/4", "reframe", "dark forest", "La oveja no devuelve la hierba", "La lección de las ovejas de Epicteto.", "Digiere lo que aprendes; que se vea en lo que das."),
   ("Enquiridión 75:2/3", "maxim", "storm clouds", "Sabemos que mentir es malo, y mentimos", "La acusación de Epicteto contra los que saben mucho.", "Saber la regla no es cumplirla. La prueba es hoy."),
   ("Meditaciones 3:17/4", "maxim", "torch fire", "Que tu palabra baste", "Marco Aurelio y la palabra que no necesita juramento.", "Quien siempre cumple no tiene que jurar nada."),
  ]},
 {"slug": "la-burbuja", "refs": med(7),
  "titulo": "La Burbuja No Pierde Nada al Romperse | Marco Aurelio, Libro VII",
  "thumb": "LA\nBURBUJA", "sub": "Marco Aurelio, Meditaciones VII",
  "imgs": ["night sea", "milky way", "moon clouds"],
  "abertura": "El séptimo libro de las Meditaciones mira el tiempo desde muy lejos: los sabios que ya no están, las ciudades que desaparecieron, la vida como algo breve. No es un libro triste. Es el libro completo.",
  "cierre": "Pensar en lo breve no es para deprimirse, es para dejar de aplazar. Si el tiempo se llevó a Sócrates, se va a llevar también tu excusa de hoy. Lo único que queda en tu mano es qué haces con el día que tienes delante.",
  "tags": ["marco aurelio", "meditaciones libro 7", "memento mori", "la brevedad de la vida", "estoicismo"],
  "desc": "El libro VII de las Meditaciones de Marco Aurelio, completo, narrado en español.",
  "shorts": [
   ("Meditaciones 8:23/2", "reframe", "night sea", "La burbuja no pierde nada al romperse", "Marco Aurelio comparó tu vida con una burbuja.", "No es tristeza: es aprender a no temer el final."),
   ("Meditaciones 4:66/2", "maxim", "old clock", "Mañana o en cien años, casi igual", "La cuenta del tiempo que hacía el emperador.", "No te prometieron más días. Usa bien el que tienes."),
   ("Meditaciones 7:20/2", "maxim", "milky way", "El tiempo se tragó hasta a Sócrates", "Ni los sabios escaparon de esto.", "Si el tiempo no perdonó a los grandes, deja de aplazar."),
   ("Meditaciones 4:67/2", "reframe", "desert night", "Hasta Pompeya murió", "Marco Aurelio nombró ciudades enteras que desaparecieron.", "Si mueren las ciudades, tu problema de hoy también pasará."),
  ]},
 {"slug": "deja-de-culpar", "refs": med(6),
  "titulo": "Deja de Culpar a los Demás | Marco Aurelio, Libro VI",
  "thumb": "DEJA DE\nCULPAR", "sub": "Marco Aurelio, Meditaciones VI",
  "imgs": ["storm clouds", "fireplace fire", "dusk sky"],
  "abertura": "El sexto libro de las Meditaciones es el de la responsabilidad: un emperador que podía culpar a cualquiera y se exigía no hacerlo. Lo escuchas entero, en la traducción de Díaz de Miranda.",
  "cierre": "Culpar a otro alivia un minuto y te deja sin poder el resto del día, porque si la causa está fuera, la solución también. Marco Aurelio y Epicteto proponían el camino inverso: buscar primero en el propio juicio, que es lo único que puedes cambiar hoy.",
  "tags": ["marco aurelio", "meditaciones libro 6", "responsabilidad", "dejar de quejarse", "estoicismo"],
  "desc": "El libro VI de las Meditaciones de Marco Aurelio, completo, narrado en español.",
  "shorts": [
   ("Enquiridión 11:1/1", "maxim", "storm clouds", "Culpar a otros es de ignorantes", "Epicteto no tenía paciencia con esto.", "Mientras el culpable sea otro, tú no puedes cambiar nada."),
   ("Enquiridión 11:1/2", "maxim", "clay lamp", "Los tres pasos de la sabiduría", "Epicteto midió la sabiduría en tres pasos.", "Primero culpas a otros, luego a ti; al final, solo actúas."),
   ("Enquiridión 10:1/4", "reframe", "rain window", "La culpa es de tu opinión", "Dónde buscar la causa cuando todo te molesta.", "Cambia el juicio y cambia el día."),
   ("Meditaciones 8:52/3", "reframe", "fireplace fire", "En vez de lamentarlo, hazlo", "La pregunta de Marco Aurelio a los que se quejan.", "La queja gasta la misma energía que la acción."),
  ]},
 {"slug": "pedir-ayuda-no-es-rendirse", "refs": med(11),
  "titulo": "Pedir Ayuda No Es Rendirse | Marco Aurelio, Libro XI",
  "thumb": "PEDIR\nAYUDA", "sub": "Marco Aurelio, Meditaciones XI",
  "imgs": ["harbor night", "torch fire", "night clouds"],
  "abertura": "El undécimo libro de las Meditaciones habla del alma que no se deja doblar: de la enfermedad, del límite del cuerpo y de la ayuda de otros. Este es el libro completo.",
  "cierre": "Epicteto era cojo y Marco Aurelio estuvo enfermo buena parte de su reinado. Ninguno de los dos confundió el límite del cuerpo con el límite de la voluntad. Y ninguno pensó que llegar con ayuda valiera menos que llegar solo.",
  "tags": ["marco aurelio", "meditaciones libro 11", "resiliencia", "fortaleza estoica", "estoicismo"],
  "desc": "El libro XI de las Meditaciones de Marco Aurelio, completo, narrado en español.",
  "shorts": [
   ("Enquiridión 15:1/1", "maxim", "harbor night", "La enfermedad no toca tu voluntad", "Epicteto era cojo y escribió esto.", "El cuerpo puede caer; la decisión sigue siendo tuya."),
   ("Enquiridión 16:1/1", "reframe", "torch fire", "Para cada golpe tienes una defensa", "Epicteto: no hay ataque sin respuesta interior.", "Busca la virtud que te toca usar hoy; ya la tienes."),
   ("Enquiridión 16:1/4", "maxim", "lightning storm", "Que las cosas no te gobiernen", "El entrenamiento diario que proponía Epicteto.", "Cada molestia pequeña es una repetición en el gimnasio interior."),
   ("Meditaciones 7:7/2", "reframe", "night clouds", "Pedir ayuda no es rendirse", "Marco Aurelio sobre subir la muralla con ayuda.", "Lo importante es llegar. Nadie te pidió llegar solo."),
  ]},
 {"slug": "la-fortaleza-interior", "refs": med(3),
  "titulo": "Tienes una Fortaleza y No Entras | Marco Aurelio, Libro III",
  "thumb": "LA\nFORTALEZA", "sub": "Marco Aurelio, Meditaciones III",
  "imgs": ["fireplace fire", "milky way", "clay lamp"],
  "abertura": "El tercer libro de las Meditaciones fue escrito en la frontera del Danubio, en plena guerra. Habla de la calma que no depende de las circunstancias. Lo escuchas completo.",
  "cierre": "Marco Aurelio no buscaba la calma en un lugar tranquilo; la buscaba en el orden de sus propios pensamientos, en medio de una guerra. Esa fortaleza la tienes también. Entrar en ella es, muchas veces, solo decidir no reaccionar todavía.",
  "tags": ["marco aurelio", "meditaciones libro 3", "paz interior", "tranquilidad estoica", "estoicismo"],
  "desc": "El libro III de las Meditaciones de Marco Aurelio, completo, narrado en español.",
  "shorts": [
   ("Meditaciones 4:4/2", "maxim", "clay lamp", "La calma es orden, no silencio", "Marco Aurelio definió la calma en una línea.", "Ordena lo que piensas y el ruido de fuera baja."),
   ("Meditaciones 8:55/4", "reframe", "fireplace fire", "Tienes una fortaleza y no entras", "El refugio que Marco Aurelio llamaba inexpugnable.", "Entrar en él es decidir no reaccionar todavía."),
   ("Meditaciones 7:18/1", "maxim", "milky way", "La felicidad es una conciencia limpia", "La definición de felicidad de un emperador.", "Nada que compres pesa más que una conciencia tranquila."),
   ("Meditaciones 4:56/1", "reframe", "dark forest", "Tu mal no viene de fuera", "De dónde viene tu sufrimiento, según Marco Aurelio.", "Lo de fuera golpea; lo que duele es lo que concluyes."),
  ]},
 {"slug": "la-higuera-y-la-leche", "refs": med(9),
  "titulo": "Cómo Tratar a la Gente Difícil | Marco Aurelio, Libro IX",
  "thumb": "GENTE\nDIFÍCIL", "sub": "Marco Aurelio, Meditaciones IX",
  "imgs": ["bonfire night", "dusk sky", "storm clouds"],
  "abertura": "El noveno libro de las Meditaciones está lleno de gente difícil: necios, ingratos, envidiosos. Marco Aurelio los conocía de cerca, porque gobernaba con ellos. Este es el libro completo.",
  "cierre": "La enseñanza aquí no es aguantar en silencio. Es esperar de cada uno lo que es, decir la verdad sin rabia, y no convertir cada necedad ajena en una sorpresa propia. Quien deja de sorprenderse deja también de enojarse.",
  "tags": ["marco aurelio", "meditaciones libro 9", "gente toxica", "paciencia estoica", "estoicismo"],
  "desc": "El libro IX de las Meditaciones de Marco Aurelio, completo, narrado en español.",
  "shorts": [
   ("Meditaciones 5:53/1-2", "reframe", "dusk sky", "¿Te enfadas con el que huele mal?", "La comparación más incómoda de Marco Aurelio.", "Cada uno da lo que tiene. Enfadarte no cambia el olor."),
   ("Meditaciones 4:15/1", "maxim", "dark forest", "No le pidas leche a la higuera", "Marco Aurelio y la higuera que da leche.", "Espera de cada uno lo que es; así no te decepciona."),
   ("Meditaciones 9:64/1", "reframe", "storm clouds", "¿Te sorprende que el necio haga necedades?", "La pregunta que desarma cualquier enojo.", "La sorpresa es tuya; él solo hizo lo de siempre."),
   ("Meditaciones 6:36/3", "maxim", "bonfire night", "Díselo, pero sin enojarte", "Marco Aurelio sobre cómo corregir a otro.", "La verdad dicha con rabia se oye como ataque."),
  ]},
 {"slug": "ya-no-eres-joven", "refs": med(2),
  "titulo": "Ya No Eres un Muchacho | Marco Aurelio, Libro II",
  "thumb": "YA NO ERES\nJOVEN", "sub": "Marco Aurelio, Meditaciones II",
  "imgs": ["old clock", "night clouds", "desert night"],
  "abertura": "El segundo libro de las Meditaciones es corto y urgente: el tiempo pasa, y cada día que aplazas es un día que no vuelve. Lo escuchas completo, sin cortes.",
  "cierre": "Epicteto y Marco Aurelio coinciden en algo duro: nadie va a venir a darte permiso para cambiar. No hay maestro que esperar ni lunes perfecto. Hay un día, este, y una versión de ti un poco mejor que la de ayer.",
  "tags": ["marco aurelio", "meditaciones libro 2", "procrastinacion", "el tiempo", "estoicismo"],
  "desc": "El libro II de las Meditaciones de Marco Aurelio, completo, narrado en español.",
  "shorts": [
   ("Enquiridión 74:1/5", "maxim", "old clock", "Ya no eres un muchacho", "Epicteto a los que siguen aplazando su cambio.", "La edad no acepta excusas. Empieza mientras puedes."),
   ("Enquiridión 74:2/1", "maxim", "storm clouds", "Vivirás y morirás como uno más", "La advertencia más dura de Epicteto.", "No es destino: es lo que pasa si no decides hoy."),
   ("Enquiridión 74:2/2", "reframe", "dusk sky", "Elige la vida del que mejora", "La salida que Epicteto daba al que se rinde.", "Un poco mejor que ayer ya es otra vida."),
   ("Enquiridión 74:1/4", "reframe", "desert night", "¿A qué maestro estás esperando?", "Epicteto a los que siempre empiezan el lunes.", "Ya sabes lo que tienes que cambiar. Faltas tú."),
  ]},
 {"slug": "antes-de-empezar", "refs": med(12),
  "titulo": "Por Qué Abandonas Todo Lo Que Empiezas | Marco Aurelio, Libro XII",
  "thumb": "LO DEJAS\nA MEDIAS", "sub": "Marco Aurelio, Meditaciones XII",
  "imgs": ["torch fire", "harbor night", "night clouds"],
  "abertura": "El último libro de las Meditaciones es un balance: qué hacer con lo que queda de vida. Junto a él, Epicteto explica por qué abandonamos lo que empezamos. Escuchas el libro doce completo.",
  "cierre": "El entusiasmo sirve para empezar y casi nunca para terminar. Epicteto pedía mirar antes el precio entero, lo que precede y lo que sigue. Si después de mirarlo todavía lo quieres, entonces sí: ya no es capricho, es decisión.",
  "tags": ["marco aurelio", "meditaciones libro 12", "constancia", "terminar lo que empiezas", "estoicismo"],
  "desc": "El libro XII de las Meditaciones de Marco Aurelio, completo, narrado en español.",
  "shorts": [
   ("Enquiridión 36:3/4", "reframe", "torch fire", "Por qué lo dejas todo a medias", "Epicteto explicó por qué abandonas.", "El entusiasmo empieza; solo el plan termina."),
   ("Enquiridión 36:3/2", "maxim", "dark forest", "Imitas a todos y no acabas nada", "La comparación de Epicteto que nadie quiere oír.", "Copiar el sueño de otro es la forma más rápida de abandonarlo."),
   ("Enquiridión 9:1/1", "maxim", "clay lamp", "Antes de empezar, examina", "La regla de Epicteto antes de cualquier proyecto.", "Cinco minutos de pensar ahorran meses de arrepentirse."),
   ("Enquiridión 4:1/1", "reframe", "harbor night", "Desearlo a medias no basta", "Epicteto sobre el precio de lo que quieres.", "Todo gran sí exige varios no. ¿Cuáles vas a decir?"),
  ]},
 {"slug": "socrates-en-la-carcel", "refs": med(1),
  "titulo": "Lo Que Sócrates Dijo en la Cárcel | Marco Aurelio, Libro I",
  "thumb": "EN LA\nCÁRCEL", "sub": "Marco Aurelio, Meditaciones I",
  "imgs": ["iron chain", "burning candle", "night clouds"],
  "abertura": "El primer libro de las Meditaciones es una lista de gratitud: lo que Marco Aurelio aprendió de cada persona que lo formó. Los estoicos tenían otro maestro común, Sócrates, de quien Epicteto habla en sus Shorts de hoy. Este es el libro primero completo.",
  "cierre": "Marco Aurelio empezó su diario dando las gracias, y Sócrates terminó su vida sin rencor contra quienes lo condenaron. Entre las dos cosas hay una idea: lo que te pueden quitar no es lo que eres. Lo que eres se construye con lo que agradeces y con lo que no traicionas.",
  "tags": ["marco aurelio", "meditaciones libro 1", "socrates", "gratitud estoica", "estoicismo"],
  "desc": "El libro I de las Meditaciones de Marco Aurelio, completo, narrado en español.",
  "shorts": [
   ("Enquiridión 78:1/4", "maxim", "iron chain", "Pueden quitarme la vida, no esto", "Sócrates nombró a los que lo iban a matar.", "Lo que te pueden quitar no es lo que eres."),
   ("Enquiridión 78:1/5", "maxim", "burning candle", "Mi cuerpo obedece, mi espíritu no", "Lo que Sócrates le dijo a Critón en la cárcel.", "Encadenado por fuera, libre por dentro: la única libertad segura."),
   ("Enquiridión 74:2/6", "reframe", "smoke incense", "Cómo llegó Sócrates a ser Sócrates", "El método de Sócrates en una sola línea.", "No es genio: es enfrentar cada cosa con la razón."),
   ("Enquiridión 68:1/4", "maxim", "night clouds", "Nadie aguantó a los demás como él", "Así describió Epicteto la paciencia de Sócrates.", "La paciencia no es debilidad: es fuerza que no se exhibe."),
  ]},
]


def montar() -> list[dict]:
    temas = []
    for t in LOTE:
        temas.append({
            "slug": t["slug"],
            "formato": "libro",
            "longo": {
                "refs": t["refs"],
                "titulo": {"stoic": t["titulo"]},
                "thumb_titulo": {"stoic": t["thumb"]},
                "thumb_sub": {"stoic": t["sub"]},
                "consultas_imagens": t["imgs"],
                "abertura": {"stoic": t["abertura"]},
                "cierre": {"stoic": t["cierre"]},
                "tags_extra": {"stoic": t["tags"]},
                "descricao_busca": {"stoic": t["desc"]},
            },
            "shorts": [{"ref": r, "tipo": tp, "consulta_imagem": im,
                        "titulo": {"stoic": ti}, "gancho": {"stoic": g},
                        "aplicacao": ap}
                       for r, tp, im, ti, g, ap in t["shorts"]],
        })
    return temas


def validar(novos: list[dict], poco: list[dict]) -> list[str]:
    erros = []
    slugs = {t["slug"] for t in poco}
    refs_poco = {s["ref"] for t in poco for s in t["shorts"]}
    publicados = set()
    if DESEMPENHO.exists():
        publicados = {v.get("titulo", "").lower() for v in
                      json.loads(DESEMPENHO.read_text(encoding="utf-8"))
                      if v.get("canal") == "stoic"}
    titulos, refs, longos = set(), set(), []
    for t in novos:
        if t["slug"] in slugs:
            erros.append(f"slug já existe: {t['slug']}")
        longos += t["longo"]["refs"]
        for ref in t["longo"]["refs"]:
            biblia.carregar_versos("stoic", ref)
        if len(t["longo"]["titulo"]["stoic"]) > 100:
            erros.append(f"título longo > 100: {t['slug']}")
        for s in t["shorts"]:
            versos = biblia.carregar_versos("stoic", s["ref"])
            n = sum(len(x.split()) for _, x in versos)
            carga = n + len(s["aplicacao"].split())
            tit = s["titulo"]["stoic"]
            if s["ref"] in refs or s["ref"] in refs_poco:
                erros.append(f"ref repetida: {s['ref']}")
            if tit.lower() in titulos or tit.lower() in publicados:
                erros.append(f"título repetido: {tit}")
            if len(tit) > 45:
                erros.append(f"título > 45: {tit}")
            if len(s["gancho"]["stoic"].split()) > 10:
                erros.append(f"gancho > 10 palavras: {s['gancho']['stoic']}")
            if carga > 56:
                erros.append(f"carga {carga} > 56: {s['ref']}")
            refs.add(s["ref"])
            titulos.add(tit.lower())
    if len(longos) != len(set(longos)):
        erros.append("um trecho aparece em dois longos do lote")
    return erros


def main() -> None:
    poco = json.loads(POCO.read_text(encoding="utf-8"))
    novos = montar()
    erros = validar(novos, poco)
    for t in novos:
        print(f"{t['slug']:28} {t['longo']['refs'][0]:18} "
              f"{len(t['shorts'])} Shorts")
        for s in t["shorts"]:
            n = sum(len(x.split()) for _, x in
                    biblia.carregar_versos("stoic", s["ref"]))
            print(f"    {n:>2}+{len(s['aplicacao'].split()):<2} "
                  f"{s['titulo']['stoic']}")
    if erros:
        print("\nERROS:\n- " + "\n- ".join(erros))
        sys.exit(1)
    print(f"\n{len(novos)} temas válidos.")
    if "--gravar" in sys.argv:
        POCO.write_text(json.dumps(poco + novos, ensure_ascii=False, indent=2)
                        + "\n", encoding="utf-8")
        print(f"Gravado: {POCO.relative_to(RAIZ)} ({len(poco) + len(novos)} temas)")


if __name__ == "__main__":
    main()
