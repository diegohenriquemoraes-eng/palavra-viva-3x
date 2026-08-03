# Proveniência dos textos estoicos (fontes/)

Preparado para alimentar o canal dark de filosofia estoica narrada ("3 Hours
of Stoic Philosophy to Fall Asleep To"), no mesmo molde do pipeline
Palavra Viva 3x. Regra seguida: **só texto em domínio público comprovado**,
verificando tradutor + evidência textual em cada arquivo do Project
Gutenberg — a obra ser antiga não basta, a tradução tem direito autoral
próprio.

## 1. Marco Aurélio — *Meditations* (Thoughts of Marcus Aurelius Antoninus)

- **Tradutor**: George Long (1800–1879).
- **Fonte**: Project Gutenberg eBook **#15877**,
  `https://www.gutenberg.org/ebooks/15877` (texto puro:
  `https://www.gutenberg.org/ebooks/15877.txt.utf-8`).
- **Evidência textual encontrada no próprio arquivo**:
  - Cabeçalho: `Title: Thoughts of Marcus Aurelius Antoninus` /
    `Author: Emperor of Rome Marcus Aurelius` / `Translator: George Long`.
  - Página bibliográfica do Gutenberg (`/ebooks/15877`) declara
    `Copyright: Public domain in the USA.`
  - Boilerplate padrão do Gutenberg no topo/rodapé do .txt: *"This eBook is
    for the use of anyone anywhere in the United States and most other
    parts of the world at no cost and with almost no restrictions
    whatsoever."*
  - Nenhum aviso de copyright de terceiros aparece em nenhum lugar do
    arquivo (nem editora, nem ano de reimpressão) — é uma digitalização
    "limpa" de uma edição do séc. XIX/XX antiga.
- **Observação sobre o ano**: o arquivo do Gutenberg não imprime o ano de
  1862 (data usualmente citada para a 1ª publicação da tradução de Long)
  em nenhum lugar do próprio texto — não fabriquei essa data a partir do
  arquivo, ela vem de conhecimento externo. O que o arquivo comprova
  diretamente é o tradutor (George Long, m. 1879) e a classificação de
  domínio público nos EUA feita pelo próprio Gutenberg.
- **Status**: DOMÍNIO PÚBLICO — usado.
- **Limpeza aplicada**: removida a "Biographical Sketch" e o ensaio
  "Philosophy of Marcus Aurelius Antoninus" (aparato do tradutor, antes do
  texto de fato), os índices finais ("INDEXES." / "INDEX OF TERMS." /
  "GENERAL INDEX."), todas as notas de rodapé numeradas por letra
  (`[A]`, `[B]`...) e os termos gregos transliterados entre colchetes
  (`[Greek: ...]`). Colchetes de interpolação editorial do próprio Long
  (ex.: `[I learned]`) tiveram só o colchete removido, mantendo a palavra —
  mesma convenção já usada em `nucleo/biblia.py` para o KJV.
- **Estrutura**: 1 "book" (`Meditations`) com 12 "chapters" (Livros I–XII
  do original) e a numeração de parágrafo do Long dentro de cada livro foi
  descartada em favor de uma numeração sequencial de "verse".
- **Saída**: `marco_aurelio_long.json` — 1 book, 12 chapters, 718 verses.

## 2. Epicteto — *Discourses* (seleção) + *Encheiridion*

- **Tradutor**: George Long (1800–1879) — o mesmo tradutor de Marco
  Aurélio, o que dá uma voz de narração consistente entre as duas obras.
- **Fonte**: Project Gutenberg eBook **#10661**, *"A Selection from the
  Discourses of Epictetus with the Encheiridion"*,
  `https://www.gutenberg.org/ebooks/10661` (texto puro:
  `https://www.gutenberg.org/ebooks/10661.txt.utf-8`).
- **Evidência textual encontrada no próprio arquivo**:
  - Cabeçalho: `Title: A Selection from the Discourses of Epictetus with
    the Encheiridion` / `Author: Epictetus` / `Translator: George Long`.
  - Página bibliográfica do Gutenberg declara
    `Copyright: Public domain in the USA.`
  - Rodapé padrão do Gutenberg: *"Creating the works from print editions
    not protected by U.S. copyright law means that no one owns a United
    States copyright in these works"* / *"all of which are confirmed as
    not protected by copyright in the U.S. unless a copyright notice is
    included"* — e **não há nenhum aviso de copyright em nenhum lugar do
    corpo do texto** (só nesse boilerplate jurídico do próprio Gutenberg).
    Isso diferencia esta edição da do Enchiridion por Higginson (ver
    seção 4, descartada) — aqui não existe nenhuma editora/ano de
    reimpressão moderna reivindicando direitos.
- **Status**: DOMÍNIO PÚBLICO — usado.
- **Limpeza aplicada**: removida a nota biográfica sobre Epicteto (aparato
  do tradutor), os termos gregos transliterados entre colchetes
  (`[Greek: ...]`, inclusive quando deixavam parênteses vazios do tipo
  "opinion ()" — removidos também), e o catálogo de outros títulos da
  coleção que vem colado no fim do arquivo.
- **Estrutura**: 2 "books" dentro do mesmo JSON —
  1. `Discourses of Epictetus (a Selection)`: os discursos vêm divididos
     por subtítulos temáticos em caixa alta no próprio texto do Long
     (ex.: "OF THE THINGS WHICH ARE IN OUR POWER AND NOT IN OUR POWER",
     "OF PROVIDENCE", "HOW WE SHOULD BEHAVE TO TYRANTS"...). Cada
     subtítulo virou um "chapter".
  2. `The Encheiridion, or Manual`: os 52 capítulos numerados em algarismo
     romano no original viraram "chapter" 1–52.
- **Saída**: `epicteto_long.json` — 2 books (49 + 52 = 101 chapters),
  709 verses.
- **Nota**: existe também no Gutenberg uma tradução do *Enchiridion* só
  (sem os Discourses) por **Thomas Wentworth Higginson**, eBook #45109 —
  ver seção 4: foi **descartada** por precaução, apesar de o Gutenberg
  também a marcar como domínio público nos EUA.

## 3. Sêneca — *Moral Letters to Lucilius* (Epistulae Morales) — NÃO ENCONTRADO

- **Candidata**: tradução de Richard Mott Gummere (Loeb Classical Library,
  1917–1925).
- **Busca feita**: `gutenberg.org/ebooks/search` com as queries "seneca
  moral letters lucilius", "seneca gummere", "seneca epistles", "seneca
  moral epistles", "seneca lucilius" e uma busca ampla por "seneca"
  (24 resultados revisados um a um), além do índice oficial
  *"Index of the Project Gutenberg Works of Lucius Annaeus Seneca"*
  (eBook #59025).
- **Resultado**: o Project Gutenberg **não tem** as *Moral Letters to
  Lucilius* / *Epistulae Morales* em nenhuma tradução — nem a de Gummere,
  nem qualquer outra. As únicas obras de Sêneca disponíveis são: *Seneca's
  Morals of a Happy Life, Benefits, Anger and Clemency* (paráfrase livre
  de Roger L'Estrange, 1678 — uma reorganização temática/abreviada, não
  uma tradução direta das cartas), *Minor Dialogues*, *On Benefits*, as
  tragédias, o *Apocolocyntosis* e o tratado científico
  *Quaestiones Naturales*.
- **Decisão**: DESCARTADO — não por falta de domínio público (a tradução
  de Gummere provavelmente É de domínio público hoje: o Volume I dos Loeb
  saiu em 1917 e o prazo de proteção de obras americanas pré-1929 já
  expirou), mas porque **não está no Project Gutenberg**, que era a fonte
  definida para esta tarefa. Não usei o texto de L'Estrange como
  substituto porque é uma obra estruturalmente diferente (paráfrase por
  tema, não as cartas), o que quebraria a promessa de "Moral Letters to
  Lucilius" ao público do canal.
- Não foi gerado `seneca_gummere.json` **nesta tentativa**. Se quiser Sêneca no canal, os
  caminhos possíveis (fora do escopo desta tarefa, quero seu ok antes de
  seguir por qualquer um deles) seriam: (a) usar a tradução de Gummere via
  Wikisource, que também a hospeda como domínio público, com verificação
  própria; ou (b) usar *Seneca's Morals* de L'Estrange do próprio
  Gutenberg como uma terceira obra estoica separada (é raiz clássica
  igualmente boa, só que não são as "cartas a Lucílio").
- **Atualização**: o caminho (a) foi seguido numa tentativa seguinte — ver
  seção 5 abaixo. `seneca_gummere.json` **existe** hoje, vindo do
  Wikisource, não do Project Gutenberg.

## 4. Epicteto — *The Enchiridion*, trad. Higginson (eBook #45109) — DESCARTADO por precaução

- **Tradutor**: Thomas Wentworth Higginson (1823–1911), tradução de 1865.
- **Fonte avaliada**: Project Gutenberg eBook **#45109**,
  `https://www.gutenberg.org/ebooks/45109`.
- **Por que foi descartado apesar de o Gutenberg marcar "Public domain in
  the USA"**: o próprio corpo do arquivo traz um aviso de copyright que a
  ficha bibliográfica do Gutenberg não deixa óbvio à primeira vista:
  ```
  COPYRIGHT, 1948
  THE LIBERAL ARTS PRESS, INC.

  First Edition, October, 1948
  Reprinted December, 1950; August, 1954
  Second Edition, November, 1955
  ```
  Essa edição de 1948/1955 (The Library of Liberal Arts, nº 8) inclui uma
  introdução autoral de Albert Salomon (claramente protegida, sem qualquer
  indício de domínio público) e notas editoriais marcadas "—Ed." acrescidas
  pela equipe da editora. O próprio arquivo diz que o texto da tradução
  em si é "a reprint of the first edition except for a few minor
  corrections in style, punctuation, and spelling", então a tradução de
  Higginson (1865) provavelmente segue sendo a mesma no fundo — mas dado
  que o arquivo carrega uma reivindicação de copyright de 1948 em texto
  claro, e a regra desta tarefa é não confiar só na obra original ser
  antiga, decidi não usar essa edição. A classificação "public domain in
  the USA" do Gutenberg aqui provavelmente reflete não renovação do
  copyright de 1948 (o que era comum em livros americanos pré-1964), mas
  isso não está comprovado dentro do próprio arquivo — só a American
  Copyright Office confirmaria.
- **Resultado prático**: sem perda de conteúdo, porque a tradução de Long
  do mesmo Enchiridion (dentro do eBook #10661, seção 2 acima) cobre o
  mesmo texto com proveniência muito mais limpa (nenhum aviso de copyright
  em lugar nenhum do arquivo).

## 5. Sêneca — *Moral Letters to Lucilius* (Epistulae Morales ad Lucilium), trad. Gummere — ENCONTRADO no Wikisource

- **Tradutor**: Richard Mott Gummere, Ph.D., Haverford College (1883–1969).
  Correção em relação à tarefa que originou esta seção: a tarefa partiu da
  premissa "Gummere morreu em 1941"; isso está **errado** — confirmado por
  busca externa (Online Books Page / Penn, Rutgers DBCS, Harvard UP): ele
  viveu **1883–1969**. Isso não muda a conclusão de domínio público nos
  EUA, que depende da **data de publicação**, não da data de morte do
  tradutor (ver abaixo) — só corrijo o dado para não propagar o erro.
- **Fonte**: `en.wikisource.org/wiki/Moral_letters_to_Lucilius`, uma página
  por carta (`.../Letter_1` a `.../Letter_124`), texto transcluído da
  digitalização proofread da edição Loeb Classical Library (William
  Heinemann/Londres e G. P. Putnam's Sons/Nova York): Volume I publicado em
  1917, Volume II em 1920, Volume III em 1925 (segundo o próprio cabeçalho
  `{{header}}` de cada página wiki e a nota da página-índice).
- **Evidência de domínio público, capturada diretamente do rodapé de
  licença da página-índice** (`action=parse` na página
  `Moral letters to Lucilius`, que carrega o template `{{PD/US|1969}}`):
  - *"This work is in the public domain in the United States because it
    was published before January 1, 1931."* — a regra usada é "publicado
    há mais de 95 anos"; hoje (2026) o corte cai em 1931, e os três volumes
    Loeb (1917/1920/1925) ficam todos abaixo dele. Esse critério **não
    depende de quando o tradutor morreu**, só da data de publicação —
    então mesmo a data errada de 1941 na tarefa original não teria
    comprometido a conclusão de domínio público nos EUA.
  - Segunda frase do mesmo aviso: *"The longest-living author of this work
    died in 1969, so this work is in the public domain in countries and
    areas where the copyright term is the author's life plus 56 years or
    less."* — é o próprio Wikisource confirmando 1969 como o ano de morte
    de Gummere (o "autor" mais recente entre Sêneca e o tradutor), o que
    bate com a busca externa acima.
  - Nenhum aviso de copyright de terceiros (nem editora reimpressora, nem
    ano de reimpressão posterior reivindicando direitos) aparece em
    nenhuma das 124 páginas de carta — diferente do caso do Enchiridion de
    Higginson (seção 4 acima), que foi descartado justamente por carregar
    um aviso `COPYRIGHT, 1948` dentro do próprio corpo do texto.
- **Status**: DOMÍNIO PÚBLICO nos EUA — usado.
- **Como o texto foi obtido**: API MediaWiki do Wikisource
  (`action=parse&prop=text`) para cada uma das 124 páginas
  `Moral letters to Lucilius/Letter N` (N=1..124), pedindo o HTML
  renderizado (não o wikitext bruto) porque o corpo de cada carta é
  transcluído a partir do namespace `Page:` via `<pages index=... />` — o
  wikitext da página da carta em si só contém a tag de transclusão, sem o
  texto. Script local em Python (com o monkeypatch de `socket.getaddrinfo`
  para IPv4, por causa do blackhole de IPv6 desta máquina).
- **Limpeza aplicada** (parser dedicado ao HTML do Wikisource,
  `fetch_seneca.py`, mantido só no scratchpad da sessão — não faz parte do
  repo):
  - Removido o cabeçalho de navegação do Wikisource (`ws-header`, links
    "anterior/próxima carta", ícone de irmãos-projeto).
  - Removido o título centralizado da carta e a fórmula de saudação
    ("Greetings from Seneca to his friend Lucilius") que abre a Carta 1 —
    tudo que vem *antes* do primeiro marcador de seção numerada (`§1.`) foi
    tratado como aparato editorial e descartado, o mesmo critério já usado
    para a "Biographical Sketch" de Marco Aurélio.
  - Removidas as chamadas de nota de rodapé (`<sup class="reference">…</sup>`,
    numeradas `[1]`, `[2]`...) e a lista de notas no fim de cada carta
    (`<div class="reflist">`) — são aparato do editor/tradutor da Loeb,
    não texto de Sêneca.
  - Removidos os marcadores de número de página do fac-símile
    (`<span class="pagenum">`, invisíveis, só indicam onde a digitalização
    trocou de página física) e os separadores decorativos entre trechos de
    página (`wst-dhr`).
  - Cada seção numerada da Loeb (`§1`, `§2`, ...) virou um "verse" —
    numeração da própria edição crítica, mais fina que os parágrafos soltos
    usados em Marco Aurélio/Epicteto.
  - Parágrafos com mais de 120 palavras foram quebrados em ponto final de
    frase; quando a seção inteira era uma única frase longa (sem ponto
    final interno), a quebra caiu em ponto-e-vírgula e, na falta dele, em
    vírgula — nunca no meio de uma locução sem pontuação alguma. Só restam
    3 passagens (de 2.587) levemente acima de 120 palavras (135–142), por
    serem frases únicas de Sêneca sem nenhuma pontuação forte interna.
  - Aspas e travessões tipográficos (`’ ‘ “ ” – — …`) normalizados para o
    equivalente ASCII reto (`' " -- ...`), para bater com o estilo simples
    dos dois arquivos já existentes (herdados do Gutenberg em texto puro).
  - Verificação automática pós-limpeza: zero resíduo de marcação
    (`wst-`, tags HTML, entidades `&...;`, `{{...}}`, `cite_note`), zero
    número de seção vazado no início de um "verse", zero espaço duplo,
    zero fragmento com menos de 3 palavras.
- **Introdução do tradutor**: existe uma página
  `Moral letters to Lucilius/Introduction` (linkada como "anterior" da
  Carta 1) — **não foi incluída**, é aparato do tradutor, mesmo critério
  usado para descartar a "Philosophy of Marcus Aurelius Antoninus" de Long.
- **Estrutura**: 1 book (`Moral Letters to Lucilius (Epistulae Morales ad
  Lucilium)`) com 124 "chapters" (Cartas 1–124, cada uma com `titulo` =
  o subtítulo da carta em inglês, ex. "On saving time", "On being"), e
  dentro de cada chapter os "verses" seguem a numeração de seção da
  própria edição Loeb (quebrada por sentença quando passa de 120 palavras).
- **Saída**: `seneca_gummere.json` — 1 book, 124 chapters, 2.587 verses.

## 6. Marco Aurélio — *Meditaciones* em ESPANHOL, trad. Díaz de Miranda

Preparado em 02/08/2026 para o canal estoico em espanhol (ex-Stoic by Night).

- **Tradutor**: Jacinto Díaz de Miranda, 1785 ("Los doce libros del emperador
  Marco Aurelio"), revisão de 1888 na Biblioteca Clásica ("Obras de los
  moralistas griegos: Marco Aurelio-Teofrasto-Epicteto-Cebes"). Tradução do
  séc. XVIII, tradutor morto há mais de dois séculos — DOMÍNIO PÚBLICO.
- **Fonte do texto**: `textos.info/marco-aurelio/meditaciones-2` (biblioteca
  digital de obras livres), que credita explicitamente a tradução a Díaz de
  Miranda e declara: "Actualmente esta edición se encuentra en dominio
  público". A MESMA tradução existe no es.wikisource ("Soliloquios", da
  edição de 1888, template PD 100 anos p.m.a.), o que confirma tradutor e
  status — mas a transcrição do Wikisource é OCR não revisado (notas do
  tradutor coladas no corpo, cabeçalhos de página "M. AURELIO.-SOLILOQUIOS"
  no meio do texto, palavras partidas), imprestável para narração. O
  incipit do Libro I é idêntico nas duas fontes ("Aprendí de mi abuelo Vero
  el ser de honestas costumbres y no enojarme con facilidad."), provando que
  é o mesmo texto; usei a cópia limpa do textos.info.
- **Limpeza aplicada**: removido o rodapé editorial do site (parágrafo
  "Traducción realizada por..."); grafia pré-reforma normalizada (mesma
  política da RV1909 em `nucleo/biblia.py`: "á"→"a", "fué"→"fue" etc. —
  GRAFIA, não tradução); parágrafos >120 palavras quebrados em ponto final
  (fallback ";" e ","), como no seneca_gummere.
- **Estrutura**: 1 book (`Meditaciones`) com 12 chapters (Libros I–XII) e
  numeração sequencial de verse por livro.
- **Saída**: `marco_aurelio_diaz.json` — 1 book, 12 chapters, 746 verses.

## 7. Epicteto — *Enquiridión* em ESPANHOL, trad. Antonio Brum

- **Tradutor**: Antonio Brum (tradução seiscentista, 1ª ed. Bruxelas 1669),
  reimpressa no mesmo volume de 1888 da Biblioteca Clásica. DOMÍNIO PÚBLICO
  (tradução com mais de 350 anos; a página do Wikisource carrega o template
  de PD na Espanha).
- **Fonte do texto**: `es.wikisource.org/wiki/Enquiridión/Máximas` (API
  MediaWiki `action=parse`, HTML renderizado), com IPv4 forçado pelo
  monkeypatch de `socket.getaddrinfo` (blackhole de IPv6 desta máquina).
- **Limpeza aplicada** — a transcrição é OCR não revisado; foi lida NA
  ÍNTEGRA (130 passagens) e cada defeito corrigido um a um
  (`finalize_enquiridion.py`, no scratchpad da sessão de 02/08/2026):
  - Cabeçalhos/nº de página vazados no corpo: "52 MORALISTAS GRIEGOS.",
    "BPICTETO.-MÁXIMAS. 387", "23"/"24"/"25" soltos no meio da frase.
  - **As "máximas perdidas"**: a transcrição traz 70 parágrafos numerados,
    mas 8 numerais de máxima (VII, XI, XIII, XXVIII, XXXVII, LIV, LXIX,
    LXXV) ficaram no MEIO do texto em vez de abrir parágrafo. As fronteiras
    foram restauradas → **78 máximas**, batendo com o índice do Wikisource.
  - ~35 erros de OCR corrigidos por lista explícita ("yoluntad"→"voluntad",
    "comola"→"como la", "Eea"→"Sea", "fir.ne"→"firme", "euerpo"→"cuerpo",
    "compañfa"→"compañía" etc.) e uma transposição de linhas na máxima do
    banho (61 na numeração antiga) reordenada para o texto fazer sentido.
    Política: restauração de erro de impressão/OCR, nunca reescrita.
  - Grafia: "tí"→"ti", "asi"→"así", "espiritu"→"espíritu" + lista padrão.
- **Estrutura**: 1 book (`Enquiridión`) com 78 chapters (uma máxima por
  chapter) e verses = quebra de 120 palavras.
- **Saída**: `epicteto_brum.json` — 1 book, 78 chapters, 115 verses.
- **Nota**: as "Cartas a Lucilio" avulsas do es.wikisource NÃO podem ser
  usadas — são tradução comunitária moderna (Antonius Djacnov, 2009), não
  domínio público. A tradução PD de Navarro y Calvo (1884) existe só como
  scan não transcrito; Sêneca em espanhol fica de fora até haver OCR próprio
  verificado.

## Resumo dos arquivos gerados

| Arquivo | Obra(s) | Tradutor | Fonte | Books | Chapters | Verses |
|---|---|---|---|---|---|---|
| `marco_aurelio_long.json` | Meditations | George Long | Project Gutenberg #15877 | 1 | 12 | 718 |
| `epicteto_long.json` | Discourses (seleção) + Encheiridion | George Long | Project Gutenberg #10661 | 2 | 101 | 709 |
| `seneca_gummere.json` | Moral Letters to Lucilius | Richard Mott Gummere | Wikisource (`en.wikisource.org`) | 1 | 124 | 2.587 |
| `marco_aurelio_diaz.json` | Meditaciones (ES) | Jacinto Díaz de Miranda | textos.info (verif. es.wikisource) | 1 | 12 | 746 |
| `epicteto_brum.json` | Enquiridión (ES) | Antonio Brum | Wikisource (`es.wikisource.org`) | 1 | 78 | 115 |

Nenhum arquivo do repo fora de `fontes/` foi alterado.
