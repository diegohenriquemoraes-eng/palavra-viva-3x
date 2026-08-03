"""Baixa e normaliza o corpus em espanhol dos canais El Poder Crudo e Astucia Fría.

Duas obras, ambas em DOMÍNIO PÚBLICO e ambas com o texto transcrito (não OCR
cru) na es.wikisource:

- **Oráculo manual y arte de prudencia** (Baltasar Gracián, 1647). ORIGINAL em
  espanhol — não há camada de tradução, então não há a dúvida jurídica que
  eliminou o Tao Te Ching e o Sun Tzu. 300 aforismos, cada um com título em
  itálico e corpo. É a espinha dorsal do canal Astucia Fría: cada aforismo é
  uma unidade curta e autocontida, que é exatamente o que um Short de 20s pede.
- **El Príncipe** (Maquiavelo) na tradução ANÔNIMA da ed. Madrid, Imprenta de
  D. José Trujillo, **1854** — domínio público por data de publicação. 26
  capítulos de prosa corrida, fatiados em versos de ~120 palavras como o resto
  do corpus da casa.

O "Anti-Maquiavelo" que acompanha a edição de 1854 fica de fora de propósito:
é texto de Frederico II rebatendo Maquiavel, outro autor e outro produto.

    python produzir/baixar_corpus_es.py            # baixa as duas
    python produzir/baixar_corpus_es.py --obra oraculo
"""

from __future__ import annotations

import argparse
import html as html_lib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.stdout.reconfigure(encoding="utf-8")

FONTES = RAIZ / "fontes"
UA = "PalavraViva3x/1.0 (canal dark ES; contato diego@perffec.com.br)"
API = "https://es.wikisource.org/w/api.php?"

PAGINAS_ORACULO = [f"Oráculo manual y arte de prudencia/Aforismos ({a}-{a + 24})"
                   for a in range(1, 300, 25)]

ROMANOS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI",
           "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX",
           "XXI", "XXII", "XXIII", "XXIV", "XXV", "XXVI"]
PAGINAS_PRINCIPE = [f"El príncipe (1854)/Capítulo {r}" for r in ROMANOS]

PALAVRAS_POR_VERSO = 32     # teto de um verso; o corte real é por frase

# Grafia do século XVII/XIX -> ortografia atual. É GRAFIA, não tradução:
# mesmo critério já usado na RV1909 (nucleo/biblia.py) e no Enquiridión.
GRAFIA = [
    (r"\bagora\b", "ahora"), (r"\bansi\b", "así"), (r"\basi\b", "así"),
    (r"\bdesta\b", "de esta"), (r"\bdeste\b", "de este"),
    (r"\bdestas\b", "de estas"), (r"\bdestos\b", "de estos"),
    (r"\bdesa\b", "de esa"), (r"\bdese\b", "de ese"),
    (r"\bdél\b", "de él"), (r"\bdellos\b", "de ellos"),
    (r"\bdella\b", "de ella"), (r"\bdellas\b", "de ellas"),
    (r"\bhabia\b", "había"), (r"\bpodia\b", "podía"),
    (r"\btenia\b", "tenía"), (r"\bqueria\b", "quería"),
    (r"\bhacia\b(?= )", "hacía"), (r"\bmismo tiempo\b", "mismo tiempo"),
    (r"\bespiritu\b", "espíritu"), (r"\bfacil\b", "fácil"),
    (r"\bdificil\b", "difícil"), (r"\butil\b", "útil"),
    (r"\bjamas\b", "jamás"), (r"\bdemas\b", "demás"),
    (r"\bquiza\b", "quizá"), (r"\btambien\b", "también"),
    (r"\bdespues\b", "después"), (r"\bsegun\b", "según"),
    (r"\bmas bien\b", "más bien"), (r"\bsolo que\b", "solo que"),
    # grafia específica da edição de 1854 (j onde hoje é g, s onde hoje é x)
    (r"\bjéneros?\b", "géneros"), (r"\bjeneral\b", "general"),
    (r"\bestranjeros?\b", "extranjeros"), (r"\bestraordinari",
                                           "extraordinari"),
    (r"\bestremo\b", "extremo"), (r"\besperiencia\b", "experiencia"),
    (r"\bescelente\b", "excelente"), (r"\bescepto\b", "excepto"),
    (r"\besponer\b", "exponer"), (r"\bestinguir\b", "extinguir"),
    (r"\bmuger(es)?\b", r"mujer\1"),
]
GRAFIA = [(re.compile(p, re.IGNORECASE), r) for p, r in GRAFIA]


def wikitext(titulo: str) -> str:
    u = API + urllib.parse.urlencode({
        "action": "parse", "page": titulo, "prop": "wikitext",
        "format": "json", "formatversion": "2"})
    req = urllib.request.Request(u, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as r:
        d = json.load(r)
    if "parse" not in d:
        raise SystemExit(f"Wikisource recusou '{titulo}': {json.dumps(d)[:200]}")
    return d["parse"]["wikitext"]


def texto_renderizado(titulo: str) -> str:
    """HTML renderizado -> texto. Usado no El Príncipe, que é transclusão de
    <pages index=...> (o wikitext da subpágina não traz o texto)."""
    u = API + urllib.parse.urlencode({
        "action": "parse", "page": titulo, "prop": "text",
        "format": "json", "formatversion": "2"})
    req = urllib.request.Request(u, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as r:
        d = json.load(r)
    if "parse" not in d:
        raise SystemExit(f"Wikisource recusou '{titulo}': {json.dumps(d)[:200]}")
    html = d["parse"]["text"]
    html = re.sub(r"(?is)<(script|style|table|sup|h1|h2|h3).*?</\1>", " ", html)
    html = re.sub(r"(?is)<div class=\"?(ws-noexport|noprint).*?</div>", " ", html)
    html = re.sub(r"(?s)<[^>]+>", " ", html)
    html = html_lib.unescape(html)
    return re.sub(r"[ \t]+", " ", html)


def limpar_wiki(t: str) -> str:
    t = re.sub(r"\{\{[^{}]*\}\}", " ", t)
    t = re.sub(r"\{\{[^{}]*\}\}", " ", t)          # templates aninhados
    t = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", t)
    t = re.sub(r"\[\[([^\]]*)\]\]", r"\1", t)
    t = re.sub(r"(?i)<br\s*/?>", " ", t)
    t = re.sub(r"(?s)<ref.*?</ref>", " ", t)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    t = t.replace("''", "").replace("'''", "")
    t = t.replace("&nbsp;", " ").replace("&#160;", " ")
    return re.sub(r"\s+", " ", t).strip()


def normalizar(t: str) -> str:
    for pat, rep in GRAFIA:
        t = pat.sub(rep, t)
    t = ABRE_ORFA.sub(lambda m: m.group(1), t)
    t = re.sub(r"\s+([.,;:!?»])", r"\1", t)
    t = re.sub(r"([¡¿«])\s+", r"\1", t)
    return re.sub(r"\s+", " ", t).strip()


def em_versos(texto: str) -> list[dict]:
    """Fatia por FRASE, não por contagem fixa de palavras.

    O resto do corpus da casa é bíblico, onde o "verso" já vem curto. Aqui o
    texto é prosa do século XVII/XIX, e o corte de 120 palavras produzia versos
    grandes demais: `fabrica._cortar_ao_teto` corta em versos INTEIROS, então
    um verso de 120 palavras estoura sozinho o teto de 20s do Short e o método
    de canal novo iria por água abaixo. Frase é também a unidade natural do
    aforismo — é onde está o golpe.

    Frases muito curtas ("Sea lección.") são coladas na seguinte até
    `PALAVRAS_POR_VERSO`, para a narração não ficar picotada.
    """
    frases = re.split(r"(?<=[.!?])\s+", texto.strip())
    versos, atual, n = [], "", 0
    for frase in frases:
        frase = frase.strip()
        if not frase:
            continue
        candidato = f"{atual} {frase}".strip()
        if atual and len(candidato.split()) > PALAVRAS_POR_VERSO:
            n += 1
            versos.append({"verse": n, "text": atual})
            atual = frase
        else:
            atual = candidato
    if atual:
        n += 1
        versos.append({"verse": n, "text": atual})
    return versos


def baixar_oraculo() -> dict:
    """300 aforismos. Cada bloco é 'N. ''Título.'' Corpo'."""
    capitulos, titulos = [], {}
    for pagina in PAGINAS_ORACULO:
        bruto = wikitext(pagina)
        bruto = re.sub(r"(?s)\{\{encabezado.*?\n\}\}", "", bruto)
        # O ornamento {{c|🙝🙟}} separa os aforismos — MAS não em todos: entre
        # o 21 e o 22 ele simplesmente não existe na fonte, e cortar por ele
        # engolia o 22. O corte confiável é a própria numeração em início de
        # linha, que a transcrição respeita sempre.
        bruto = re.sub(r"\{\{c\|[^}]*\}\}", "\n", bruto)
        for m in re.finditer(r"(?ms)^(\d+)\.[ \t]+(.*?)(?=^\d+\.[ \t]|\Z)", bruto):
            numero = int(m.group(1))
            resto = m.group(2).strip()
            if not resto:
                continue
            mt = re.match(r"(?s)^''(.+?)''\s*(.*)$", resto)
            if mt:
                titulo = normalizar(limpar_wiki(mt.group(1)))
                corpo = normalizar(limpar_wiki(mt.group(2)))
                # Quando o itálico do título não engloba a pontuação, o corpo
                # começa com ela ("No engañarse en las personas" + ", que es
                # el peor..."). Narrado, isso vira uma pausa sem sentido no
                # primeiro segundo do Short — justo onde se decide a retenção.
                corpo = re.sub(r"^[\s.,;:]+", "", corpo)
                if corpo[:1].islower():
                    corpo = corpo[0].upper() + corpo[1:]
            else:
                titulo, corpo = "", normalizar(limpar_wiki(resto))
            if not corpo:
                continue
            titulos[numero] = titulo
            capitulos.append({"chapter": numero, "verses": em_versos(corpo)})
        print(f"  {pagina.split('/')[-1]}: {len(capitulos)} aforismos acumulados")
        time.sleep(1.0)                      # robot policy da Wikimedia

    capitulos.sort(key=lambda c: c["chapter"])
    faltando = sorted(set(range(1, 301)) - {c["chapter"] for c in capitulos})
    if faltando:
        print(f"  ⚠ faltaram os aforismos: {faltando}")
    (FONTES / "gracian_oraculo_titulos.json").write_text(
        json.dumps({str(k): v for k, v in sorted(titulos.items())},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "translation": ("Baltasar Gracián, 'Oráculo manual y arte de prudencia' "
                        "(1647) - ORIGINAL en español, dominio público - "
                        "es.wikisource.org, transcripción revisada"),
        "books": [{"name": "Oráculo manual", "chapters": capitulos}],
    }


# A página renderizada vem embrulhada em navegação da Wikisource ("otras
# versiones", "metadatos", o aviso de ortografia, o índice do volume e o
# colofão da Imprenta Trujillo). O texto de Maquiavel começa no cabeçalho
# "CAPITULO ..." em caixa alta (grafia de 1854) e termina antes do rodapé.
INICIO_CAP = re.compile(r"CAPITULO\s+(?:PRIMERO|[IVXLC]+)\.?\s*", re.IGNORECASE)
FIM_CAP = re.compile(
    r"(?i)(?:Biografía de Maquiavelo|Cartas sobre el Anti-Maquiavelo"
    r"|Prefacio del Anti-Maquiavelo|Imprenta de D\.|Obtenido de"
    r"|El Pr[íi]ncipe de Maquiavelo\s*,\s*precedido|Índice|Categorías?:)")

# A transcrição de 1854 solta "¿" de abertura em frase que não é pergunta
# (o cap. XVII abre "¿No hay duda en que un príncipe debe ser clemente."). Isso
# faria o TTS subir a entonação numa afirmação. Só cai o "¿" órfão: quando há
# "?" antes do fim da frase, a pergunta é real e fica.
ABRE_ORFA = re.compile(r"¿([^.?¡!]*?)(?=[.]|$)")


def baixar_principe() -> dict:
    capitulos = []
    for i, pagina in enumerate(PAGINAS_PRINCIPE, start=1):
        texto = texto_renderizado(pagina).replace("&#42;", " ")
        inicios = list(INICIO_CAP.finditer(texto))
        if not inicios:
            raise SystemExit(f"{pagina}: não achei o cabeçalho CAPITULO")
        texto = texto[inicios[-1].end():]        # o último é o do corpo
        fim = FIM_CAP.search(texto)
        if fim:
            texto = texto[:fim.start()]
        texto = normalizar(re.sub(r"\s+", " ", texto))
        versos = em_versos(texto)
        capitulos.append({"chapter": i, "verses": versos})
        print(f"  Capítulo {ROMANOS[i-1]}: {len(versos)} versos")
        time.sleep(1.0)
    return {
        "translation": ("Nicolás Maquiavelo, 'El Príncipe' - traducción anónima, "
                        "ed. Madrid, Imprenta de D. José Trujillo, 1854 - "
                        "dominio público - es.wikisource.org"),
        "books": [{"name": "El Príncipe", "chapters": capitulos}],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--obra", choices=["oraculo", "principe"], action="append")
    args = ap.parse_args()
    obras = args.obra or ["oraculo", "principe"]

    if "oraculo" in obras:
        print("Oráculo manual (Gracián, 1647):")
        d = baixar_oraculo()
        alvo = FONTES / "gracian_oraculo.json"
        alvo.write_text(json.dumps(d, ensure_ascii=False, indent=1),
                        encoding="utf-8")
        caps = d["books"][0]["chapters"]
        print(f"  -> {alvo.name}: {len(caps)} aforismos, "
              f"{sum(len(c['verses']) for c in caps)} versos\n")

    if "principe" in obras:
        print("El Príncipe (Maquiavelo, trad. anónima 1854):")
        d = baixar_principe()
        alvo = FONTES / "maquiavelo_principe_1854.json"
        alvo.write_text(json.dumps(d, ensure_ascii=False, indent=1),
                        encoding="utf-8")
        caps = d["books"][0]["chapters"]
        print(f"  -> {alvo.name}: {len(caps)} capítulos, "
              f"{sum(len(c['verses']) for c in caps)} versos")


if __name__ == "__main__":
    main()
