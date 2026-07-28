# Poço de temas — Stoic by Night (`temas_estoico.json`)

Poço inicial do canal novo em inglês de filosofia estoica narrada, reaproveitando
o motor do Palavra Viva 3x. 20 temas = ~20 dias de fila (1 longo + 3 Shorts/dia,
o 4º Short de cada tema é reserva, igual ao canal bíblico).

## Corpus e proveniência

Três obras em domínio público, já preparadas em `fontes/` (ver
`fontes/PROVENIENCIA.md` para a checagem de direitos autoral por arquivo):

| Arquivo | Obra | Tradutor | Estrutura |
|---|---|---|---|
| `marco_aurelio_long.json` | *Meditations* | George Long | 1 book, 12 chapters (= Livros I–XII), 718 verses |
| `seneca_gummere.json` | *Moral Letters to Lucilius* | Richard M. Gummere | 1 book, 124 chapters (= Cartas 1–124), 2.587 verses |
| `epicteto_long.json` | *Discourses* (seleção) + *Encheiridion* | George Long | 2 books, 101 chapters, 709 verses |

Referência no mesmo formato bíblico: `"Meditations 4:55"`, `"Moral Letters 81:5-7"`,
`"Encheiridion 5:1"`. Importante: a numeração de "verse" em Marco Aurélio e
Epicteto é uma renumeração sequencial feita na preparação do corpus (não é a
numeração de parágrafo clássica que aparece em outras edições/citações), e em
Sêneca segue a numeração de seção (§) da edição crítica Loeb. Por isso toda
referência deste arquivo foi validada carregando o texto de verdade via
`nucleo/biblia.carregar_versos`, nunca citada de memória.

## Como os 12 temas do nicho viraram 20 slugs

O Diego pediu os 12 temas centrais do nicho (ansiedade, morte, raiva, tempo,
medo, adversidade, desejo/riqueza, opinião dos outros, amizade, autocontrole,
gratidão, aceitação). A maioria virou 1 slug; os temas com mais material nas
três obras (morte, tempo, adversidade, desejo/riqueza, autocontrole, aceitação)
ganharam uma 2ª variação — mesmo assunto, ângulo e fontes diferentes, sem
repetir nenhuma passagem (ver validação abaixo). Isso espelha o padrão do
`temas.json` bíblico, que também tem múltiplos vídeos de "proteção" ou "salmos
para dormir" com refs diferentes.

| # | Slug | Formato | Tema do nicho | Fonte principal do longo |
|---|---|---|---|---|
| 1 | `anxious-mind-quiet` | dormir | ansiedade/preocupação | Sêneca, Carta 13 *(On groundless fears)* |
| 2 | `things-not-our-own` | dormir | aceitar o que não controlamos | Epicteto, Ench. 1–2/8 + Discourses 1–2 |
| 3 | `no-fear-of-death` | dormir | morte | Sêneca, Carta 24 *(On despising death)* |
| 4 | `the-borrowed-hour` | dormir | morte/impermanência | Marco Aurélio, Livro II inteiro |
| 5 | `memento-mori-short` | tema | morte (variação curta) | Sêneca, Carta 101 *(futility of planning ahead)* |
| 6 | `cooling-the-temper` | dormir | raiva | Epicteto, Disc. 8 + Marco Aurélio 11:34-51 |
| 7 | `stealing-time` | dormir | tempo e pressa | Sêneca, Cartas 1 e 49 |
| 8 | `the-present-hour` | tema | tempo (variação) | Marco Aurélio, Livro III inteiro |
| 9 | `fearless-mind` | dormir | medo | Epicteto, Disc. 45 e 9 (tiranos) |
| 10 | `the-obstacle-is-the-way` | dormir | adversidade/resiliência | Marco Aurélio 5:27-48 (a passagem do "obstáculo") |
| 11 | `enduring-what-comes` | dormir | adversidade (variação) | Sêneca, Cartas 67 e 96 |
| 12 | `grief-and-the-stoic` | tema | luto/perda | Sêneca, Cartas 63 e 99 |
| 13 | `true-wealth` | dormir | desejo e riqueza | Sêneca, Carta 17 + Epicteto Disc. 37 |
| 14 | `fear-of-want` | tema | desejo/riqueza (variação) | Epicteto, Disc. 38 + Sêneca Carta 119 |
| 15 | `the-opinion-of-others` | dormir | opinião dos outros | Sêneca Carta 43 + Epicteto Disc. 44 + Ench. 22-24 |
| 16 | `the-faithful-friend` | dormir | amizade | Sêneca, Cartas 3 e 9 |
| 17 | `the-ruling-self` | dormir | autocontrole | Sêneca, Cartas 116 e 83 |
| 18 | `self-mastery-short` | tema | autocontrole (variação) | Epicteto, Ench. 33/34/41 + Sêneca Carta 123 |
| 19 | `the-grateful-heart` | dormir | gratidão | Sêneca, Carta 81 *(On benefits)* |
| 20 | `the-willing-fate` | tema | aceitar o destino / amor fati | Marco Aurélio, Livro X inteiro |

14 temas em `"dormir"` (alvo ~60 min, é o que domina a fila) e 6 em `"tema"`
(~30 min), como pedido — "dormir" é o formato dominante do nicho ("Hours of
Stoic Philosophy to Fall Asleep To"), "tema" cobre os ângulos mais curtos e
citáveis (memento mori, o momento presente, autocontrole em regras práticas,
amor fati).

## Lógica dos títulos

Fórmula medida nos líderes do nicho e pedida pelo Diego:
`[DURAÇÃO] of [TEMA] + [PROMESSA] | [palavra-chave]`. Duração varia entre
"3 Hours" (a maioria dos "dormir"), "2 Hours" (uma variação, para não repetir
sempre o mesmo número) e "1 Hour" (todos os "tema"). O sufixo depois do `|`
alterna entre o nome do canal (`Stoic by Night`) e `Stoic Philosophy` /
o autor citado, do mesmo jeito que os exemplos de referência às vezes fecham
com a marca e às vezes com uma palavra-chave de busca.

Todo título de longo ficou ≤100 caracteres (limite validado pelo motor);
o maior tem 90.

Títulos de Short (≤55 caracteres, validado): a regra foi abrir com uma palavra
de impacto nos 3 primeiros termos (verbo de ação, nome próprio famoso — Marco
Aurélio, Sócrates, Zeus — ou uma negação forte tipo "Nothing", "No One") e
nunca entregar a resposta do texto. Exemplos:
- `"The One Thought That Ends Anxiety Instantly"` — promete a resposta, não
  entrega qual é o pensamento.
- `"Marcus Aurelius Escaped Every Trouble Like This"` — nome famoso na abertura,
  "like this" abre curiosidade sem dizer como.
- `"Lead Me, O Zeus, and Thou, O Destiny"` — exceção deliberada: é a citação
  mais famosa do estoicismo (a prece de Cleantes no Encheiridion 52), então o
  próprio verso É o gancho.

Cada short tem um `tipo`:
- **`maxim`** — sentença curta e fechada, already-quotable (ex.: "Not death is
  evil, but a shameful death").
- **`reframe`** — vira a perspectiva do espectador sobre algo que ele já sente
  (ex.: o pastor/curral vs. a metáfora do timoneiro na tempestade).
- **`memento`** — lembrete direto de morte/tempo/impermanência (ex.: "A little
  time, and thou shalt close thy eyes").

## Validação feita (script descartável, não faz parte do repo)

Rodei um validador em `nucleo.biblia.carregar_versos`, apontando
temporariamente `idiomas.CONFIG["en"]["arquivo_fonte"]` para o arquivo certo
de `fontes/` conforme o nome da obra em cada referência (nunca editei
`nucleo/idiomas.py` de verdade — foi um `mock.patch.dict` só durante a
validação). Resultado:

- **517 referências de verso carregadas sem erro** nas 20 refs de longo + 80
  refs de short (4 por tema × 20 temas).
- **Todo título de longo ≤ 100 caracteres**; todo título de Short ≤ 55
  caracteres.
- **Todo Short ≤ 50 palavras** (somando as palavras do(s) verso(s) da própria
  ref).
- **Soma de palavras de cada longo — todas ≥ 1500**, variando de 1.526
  (`true-wealth`) a 2.334 (`the-borrowed-hour`, Livro II inteiro de Marco
  Aurélio):

  | slug | palavras | slug | palavras |
  |---|---:|---|---:|
  | anxious-mind-quiet | 1548 | the-obstacle-is-the-way | 1677 |
  | things-not-our-own | 1719 | enduring-what-comes | 1892 |
  | no-fear-of-death | 1671 | grief-and-the-stoic | 1724 |
  | the-borrowed-hour | 2334 | true-wealth | 1526 |
  | memento-mori-short | 1546 | fear-of-want | 1680 |
  | cooling-the-temper | 2165 | the-opinion-of-others | 1542 |
  | stealing-time | 1774 | the-faithful-friend | 1610 |
  | the-present-hour | 1592 | the-ruling-self | 1864 |
  | fearless-mind | 1904 | self-mastery-short | 1630 |
  | the-obstacle-is-the-way | 1677 | the-grateful-heart | 1542 |
  | | | the-willing-fate | 1546 |

- **Nenhuma passagem repetida entre temas diferentes**, e nenhum tema reaproveita
  a mesma passagem entre o próprio longo e os próprios shorts (checagem por
  `(livro, capítulo, verso)` sobre as 517 referências — 517 combinações
  únicas, zero colisão).

## O que NÃO foi mexido

`conteudo/temas.json` (poço bíblico) e todo o resto do pipeline (`nucleo/`,
`produzir/`, `publicador/`) continuam intocados. Este arquivo novo não está
plugado em `produzir/reabastecer.py` — aquele script hoje lê
`conteudo/temas.json` e valida `("es", "en", "pt")` fixo, e `nucleo/idiomas.py`
só tem as 3 configurações bíblicas. Ligar o canal "Stoic by Night" de verdade
(nova entrada em `idiomas.CONFIG`, canal/credenciais do YouTube, ajuste do
`reabastecer.py` para aceitar um poço por canal) é trabalho à parte, fora do
escopo pedido aqui.
