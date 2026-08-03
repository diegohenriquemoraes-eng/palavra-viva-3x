# Dois canais novos em espanhol — pesquisa e recomendação

_Escrito em 03/08/2026, a pedido do Diego ("vamos fazer mais 2 canais em
espanhol; pesquise 2 tipos de conteúdo validado para atingirmos a monetização,
seguindo rigorosamente o Protocolo Fantasma")._

**Nada aqui é opinião.** Todos os números vêm de 28 buscas na YouTube Data API
(`order=viewCount`, `relevanceLanguage=es`), 26 nichos medidos, ~1.200 vídeos
com inscritos do canal cruzados vídeo a vídeo. Dados brutos em
`mercado_es*.json` (scratchpad da sessão). A verificação de domínio público foi
feita obra por obra.

---

## 1. O teste que o manual manda fazer

O Capítulo 6 do PROTOCOLO FANTASMA (pág. 27–30) dá um critério único e frio
para escolher nicho, atribuído ao Calvin:

> "Antes de escolher um nicho, vá procurar um canal PEQUENO, de menos de 50 mil
> inscritos, que JÁ vive daquele nicho. Achou? Bandeira verde."

E completa com a regra que corrige a intuição de todo mundo:

> "Para de procurar o nicho virgem que ninguém faz. Quase sempre, nicho vazio é
> vazio porque não dá dinheiro. (...) Concorrência é prova de que tem dinheiro
> ali."

Então a métrica não é "views do nicho". É **quantos canais abaixo de 60 mil
inscritos já fizeram +300 mil views ali** — chamo de *furadores* na tabela.
Muitos furadores = sala com dinheiro e sem dono. Mediana altíssima e zero
furadores = sala de gigantes, você não entra.

---

## 2. As 26 salas medidas

Ordenado por furadores. Os dois controles são os canais que já temos, para
calibrar a leitura.

| Sala (espanhol) | Views medianas | Dur. mediana | **Furadores** | Veredito |
|---|---|---|---|---|
| sabedoria oriental (Tao/Buda) | 486.987 | 58 min | **13** | ❌ corpus impossível |
| **estoicismo** _(controle — La Noche Estoica)_ | 1.951.364 | 31 min | 12 | já é nosso |
| **psicologia oscura / poder** | 532.090 | 19 min | **11** | ✅ **ESCOLHIDO** |
| finanças / mentalidade milionária | 1.055.188 | 24 min | 9 | ❌ risco de política |
| **Maquiavel / estratégia do poder** | 664.598 | 31 min | **9** | ✅ **ESCOLHIDO** |
| poesia narrada | 48.292 | 4 min | 8 | ❌ demanda é de autor protegido |
| **ler pessoas / astúcia social** | 1.096.609 | 17 min | **5** | ✅ **ESCOLHIDO** |
| audiolivro clássico para dormir | 1.536.459 | 44 min | 5 | ❌ sala é de infantil |
| filosofia narrada | 1.195.066 | 17 min | 5 | ❌ canibaliza o estoico |
| **bíblico ES** _(controle — Palabra Viva)_ | 5.964.624 | 68 min | 6 | já é nosso |
| história antiga narrada | 826.826 | 52 min | 6 | ❌ exige texto autoral |
| motivação / superação | 3.990.922 | 13 min | 4 | ❌ exige texto autoral |
| disciplina / mentalidade guerreira | 330.569 | 16 min | 3 | ⚠️ canibaliza o estoico |
| terror / relatos de medo | 18.463.045 | 49 min | 3 | ❌ sala de gigantes |
| terror clássico (Quiroga/Poe) | 42.922 | 8 min | 2 | ❌ demanda fina demais |
| contos com moral p/ adultos | 1.076.616 | 9 min | 1 | ❌ sala é de infantil |
| mistério / lendas | 8.206.731 | 22 min | 1 | ❌ sala de gigantes |
| **Gracián / arte de la prudencia** | **12.520** | 18 min | **0** | ⚠️ ver §4 |
| **lendas de Bécquer** | **13** | 34 min | **0** | ❌ demanda inexistente |
| cuentos para dormir / audiolivro | 15.946.871 | 34 min | **0** | ❌ sala de gigantes |

### As duas descobertas que mudam a decisão

**A sala com os melhores números do levantamento é juridicamente impossível.**
Sabedoria oriental (Tao Te Ching, budismo) tem 13 furadores, canais de 2 mil e
4,5 mil inscritos fazendo 300–570 mil views. E não existe **nenhuma** tradução
espanhola em domínio público de Tao Te Ching, Dhammapada, Jātaka, contos zen ou
Analectas — todas as que circulam são modernas e protegidas. A única peça com
prova razoável é a Bhagavad Gita de Roviralta Borrell (1896), sem edição digital
limpa. Uma obra só não sustenta seis meses. **Sala descartada por copyright, não
por desempenho.**

**Nome de autor clássico não tem demanda nenhuma.** "Baltasar Gracián / arte de
la prudencia": mediana de **12.520 views, zero furadores**. "Lendas de Bécquer":
a busca inteira devolveu **3 vídeos**, o campeão com 259 views. Isso é o alerta
mais útil de toda a pesquisa: **o corpus é Gracián, mas a embalagem não pode
ser Gracián.** Quem procura é "cómo leer a las personas", "manipulación",
"Maquiavelo", "poder" — nunca o nome do autor do século XVII.

---

## 3. Os 2 tipos de conteúdo validados

Os dois saem da mesma família de sala (a que tem 9–11 furadores medidos duas
vezes em rodadas independentes), com ângulos e públicos separados.

### CANAL 1 — Poder e estratégia (Maquiavel)

**Ângulo:** as regras cruas de poder, liderança e estratégia — o texto de 1532
como fonte, com a nossa leitura aplicada em cima (ver §6: leitura crua não
monetiza).

**Quem já fura essa sala sendo pequeno** (medido, não estimado):

| Canal | Inscritos | Views do vídeo | Duração |
|---|---|---|---|
| Maquiavelo del Poder | 20.000 | 800.312 | 18 min |
| Mentalidad Indomitus | 23.000 | 614.391 | 19 min |
| Maquiavelo Sin Filtros | 23.100 | 500.125 | 58 min |
| Maquiavelo Sin Filtros | 23.100 | 390.596 | **101 min** |
| Ruge En La Oscuridad | 11.100 | 303.548 | 80 min |

E o teto da sala prova o formato longo: **AMA Audiolibros fez 3.675.359 views
com "El Príncipe — Audiolibro Completo", 249 minutos.** É exatamente o nosso
produto: texto em domínio público, narração, fundo escuro parado.

**Corpus (verificado obra a obra):**

| Obra | Situação | Unidades |
|---|---|---|
| *El Príncipe*, trad. anônima, Imprenta Trujillo, **1854** | ✅ PD, Wikisource, transcrição revisada | 26 caps → ~60-80 trechos |
| Gracián, *El Político* (1640) | ✅ PD, original em espanhol | ~10 trechos |
| Gracián, *El Héroe* (1637) | ✅ PD, original em espanhol | 20 "primores" |
| Sun Tzu, *El arte de la guerra* | ❌ **NÃO USAR** | — |

⚠️ **Sun Tzu está proibido em espanhol.** A Wikisource ES apagou a tradução em
julho de 2019 por não existir certeza de nenhuma versão anterior a 1973; a mais
antiga catalogada pela Biblioteca Nacional de España é de 1973 (Enrique Toomey),
protegida. Todo PDF solto que circula é essa ou derivada. Só entraria via
tradução nossa a partir do Lionel Giles (1910), e isso fica fora do escopo.

### CANAL 2 — Astúcia social (ler pessoas / não ser usado)

**Ângulo:** como as pessoas te leem, te usam e te manipulam — e o que o texto
manda fazer. É o *Oráculo Manual* de Gracián (1647), que é literalmente um
manual de leitura de gente escrito 350 anos antes do nicho existir.

**Quem já fura essa sala sendo pequeno:**

| Canal | Inscritos | Views do vídeo | Formato |
|---|---|---|---|
| Dra. Marcela Ré | 31.200 | 2.162.635 | **Short** |
| Daanux | 39.900 | 2.041.219 | **Short** |
| Mejora Diaria | 35.500 | 1.513.460 | 17 min |
| Radiografia Mental | 55.000 | 1.468.705 | 10 min |
| Hector el Geek 12 | 22.100 | 1.299.689 | **Short** |
| La Psicología Oscura real | 10.300 | 645.785 | 35 min |
| El Lado Sombrío | 33.400 | 445.735 | 36 min |
| Estoico Moderno | 25.600 | 308.499 | 35 min |

**Por que este é o canal certo para um lançamento fantasma:** é a única sala
medida onde canais pequenos furam **em Short**, que é a única coisa que o
Protocolo Fantasma publica nos primeiros 30 dias. Três canais entre 22 mil e
40 mil inscritos com Shorts de 1,3 a 2,1 milhões de views.

**Corpus:**

| Obra | Situação | Unidades |
|---|---|---|
| Gracián, *Oráculo manual y arte de prudencia* (1647) | ✅ PD, Wikisource, transcrição revisada, ortografia modernizada | **300 aforismos** |
| Gracián, *El Discreto* (1646) | ✅ PD, original em espanhol | 25 "realces" |
| Quevedo, sonetos | ✅ PD, original em espanhol | 50+ |

**300 aforismos autocontidos = 10 meses de 1 Short/dia com uma obra só.**
Somando tudo, os dois canais têm ~480 unidades curtas — 16 meses a 1/dia.

Vantagem jurídica que nenhum outro candidato tem: **Gracián e Quevedo
escreveram em espanhol.** Não há camada de tradução, então não há a dúvida que
matou o Tao Te Ching e o Sun Tzu.

---

## 4. O que foi descartado e por quê

| Sala | Números | Por que não |
|---|---|---|
| Sabedoria oriental | 13 furadores — os melhores | Zero tradução espanhola em PD. Copyright. |
| Finanças / mentalidade milionária | 9 furadores, maior CPM do manual | Política de conteúdo inautêntico do YouTube corta persona de IA dando **conselho financeiro**. É a categoria (c), a mesma que já mapeamos em `ESTRATEGIA-STOIC-ES.md` §3. Não vale o risco de desmonetização. |
| Poesia narrada | 8 furadores, mediana baixíssima | A demanda é por Neruda e García Márquez — **protegidos**. Bécquer, que é PD, mede 13 views. |
| Terror / mistério | mediana de 18 milhões | Sala de gigantes: 2 e 3 furadores em 50 vídeos. |
| Audiolivro para dormir | **0 furadores** | Dominada por canal infantil de 9 a 31 milhões de inscritos. |
| Disciplina / mentalidade guerreira | 3 furadores, sala mais nova (52% dos vídeos são de 2025+) | O corpus seria Marco Aurélio e Epicteto — **canibalizaria a La Noche Estoica**, que está em janela de teste fechada até 01/09. |
| História antiga narrada | 6 furadores, sala mais fresca | Exige roteiro autoral. Nossa diretriz é texto-fonte, e roteiro autoral em série é exatamente o que a política de conteúdo inautêntico persegue. |

---

## 5. Como os dois nascem — Protocolo Fantasma puro

Idêntico ao regime da La Noche Estoica, que é o que o Diego pediu para seguir
rigorosamente.

| Regra do manual | Aplicação |
|---|---|
| 1 vídeo/dia, mesmo horário, 20–30 dias | `shorts_por_dia: 1` |
| Sem vídeo longo na janela | `hora_longo_utc: null` |
| Short de 10–20s | `max_short_s: 20.0` |
| 2–3 hashtags | 3 por canal |
| Descrição enxuta | `descricao_curta: True` |
| Um canal, um nicho | ângulos separados, sem sobreposição de obra |
| Gancho falado+escrito no 1º frame | `GANCHOS` próprios por canal |
| Loop fechado, sem preto | já é padrão da casa desde 27/07 |

**Uma diferença deliberada em relação à La Noche Estoica:** estes dois canais
**não** narram só a fonte. Levam camada autoral por cima — motivo no §6, e é o
que os furadores medidos de fato fazem.

**Horários escalonados** (nenhum colide com os canais atuais — Palabra Viva,
Palavra Viva Diária e La Noche Estoica às 01 UTC):

| Canal | Hora UTC | Local | Voz |
|---|---|---|---|
| Poder / Maquiavel | **02:00** | 20h CDMX · 21h Bogotá · 23h BsAs | `es-CO-GonzaloNeural` |
| Astúcia social | **03:00** | 21h CDMX · 22h Bogotá · 00h BsAs | `es-AR-TomasNeural` |

Vozes diferentes de propósito, e diferentes das duas já em uso
(`es-MX-Jorge` no Palabra Viva, `es-US-Alonso` na Noche Estoica): mesma voz em
canais da mesma conta é assinatura de fábrica.

**Criação escalonada:** um canal por semana, não os dois no mesmo dia. Vários
canais idênticos nascendo juntos na mesma conta é o padrão que a política de
conteúdo inautêntico procura.

**Réguas de decisão (30 dias após a estreia de cada um):** mediana ≥300
views/Short mantém e escala (2/dia + longo). Repetir a mediana de 1 view do
Living Word Daily mata. Comparar sempre com o ES bíblico no MESMO tempo de vida.
Não mexer em nada durante a janela.

---

## 6. O achado que muda o FORMATO dos dois canais (e cobra os atuais)

A pesquisa de monetização trouxe uma coisa que eu não sabia e que é mais
importante que a escolha de nicho. A política oficial do YouTube
(`support.google.com/youtube/answer/1311392`, conferida por mim na fonte,
não por relato de blog) lista **textualmente**, entre os exemplos de conteúdo
**inelegível para monetização**:

> "Content that exclusively features readings of other materials you did not
> originally create, like text from websites or news feeds"

> "Image slideshows, templated storylines, or scrolling text with minimal or no
> narrative, commentary, or educational value"

> "AI-generated content made with generic or unoriginal templates, giving the
> impression of mass production"

E o critério de aprovação:

> "The substance of each video should be materially varied and deliver creative,
> educational or other value" — e o revisor pergunta se "viewers can tell that
> there's a meaningful difference between the original video and your video".

**Domínio público resolve o problema de COPYRIGHT e não resolve o problema de
MONETIZAÇÃO. São dois trilhos separados.** Um vídeo que é (a) leitura literal de
texto que não escrevemos + (b) fundo estático + (c) sem camada própria bate nos
três exemplos ao mesmo tempo. Isso não é zona cinzenta: é o exemplo que eles
escreveram.

Em julho/2026 a política foi renomeada para "Generic or Repetitive Content" e
ganhou as 3 categorias que já estão mapeadas em `ESTRATEGIA-STOIC-ES.md` §3 —
o que aquela análise não pegou foi este trecho, que é o mais específico contra
o nosso formato.

### A correção: os canais novos levam camada autoral

E aqui a política e o mercado apontam para o **mesmo lugar**, o que torna a
correção fácil. Repare no que os furadores medidos no §3 realmente publicam:

- "8 Lecciones de Maquiavelo Que Te Hacen Peligrosamente Inteligente"
- "48 Leyes Para Seducir, Ser Confiado e Imponer RESPETO"
- "177 ENSEÑANZAS DE MAQUIAVELO (La Guía Más Completa)"

Nenhum é leitura crua da fonte. **Leitura crua na sala do poder é o produto do
AMA Audiolibros — canal de 1,31 milhão de inscritos.** Canal pequeno que fura
ali fura com comentário próprio em cima do texto.

Então o Short dos dois canais novos passa a ser:

```
[gancho]  →  [aforismo/trecho da fonte, citado e creditado]  →  [aplicação própria em 1 frase]
```

A aplicação própria é conteúdo nosso, varia vídeo a vídeo, e é exatamente a
"meaningful difference" que o revisor procura. No longo, vira o mesmo: bloco de
fonte + comentário nosso entre blocos.

⚠️ **Isso NÃO se aplica aos canais bíblicos.** Lá a diretriz editorial nº 4
(sem pregação nem interpretação) é decisão do Diego e não se mexe. Mas a
consequência precisa ser dita com todas as letras: **Palabra Viva, Palavra Viva
Diária e La Noche Estoica estão hoje exatamente no formato que a política
descreve como inelegível**, e nenhum deles foi ainda submetido ao YPP, então
nunca fomos testados. Isso é assunto separado, para o Diego decidir depois da
janela de 01/09 — não mexo em canal em teste. Registrado aqui porque foi
descoberto aqui.

## 7. CPM: o que o dinheiro realmente diz

Pesquisa feita, e o resumo honesto é que **quase tudo que circula sobre CPM é
chute**. O que tem lastro:

- Único estudo com metodologia declarada (22 vídeos, 928 mil views, 2024):
  EUA **€10,26** de CPM mediano · Espanha **€2,69** · México **€1,41**.
  Colômbia, Argentina, Chile e Peru não estão na amostra.
- Razão que interessa: **EUA ≈ 3,8× Espanha ≈ 7× México.**
- Espanhol como língua: CPM estimado em ~$3,00 contra ~$10,26 do inglês — e o
  manual já dizia isso na pág. 32 ("espanhol é a segunda moeda mais valorizada",
  abaixo do inglês).
- Por nicho, só finanças e educação têm número confiável. Psicologia, filosofia
  e história ficam em estimativas de blog na faixa $5–12 de RPM, sem lastro.
  Música/relax é o piso medido: **$0,75 de RPM**.

**A consequência prática que muda decisão:** o que define o RPM não é "estar em
espanhol", é **a fatia de views vinda de EUA e Espanha**. Isso reforça o nicho
de poder/psicologia sobre o devocional — é conteúdo que o hispânico dos EUA
consome — mas não muda o horário de publicação, porque volume ainda está na
LATAM.

## 8. A ressalva honesta sobre "atingir a monetização"

O Diego pediu conteúdo validado **para monetizar**, e o Protocolo Fantasma
monetiza pela porta dos Shorts: 1.000 inscritos + 10 milhões de views de Shorts
em 90 dias. A conta que já está em `ESTRATEGIA-FANTASMA.md` §3 continua valendo:
o Palabra Viva ES, nosso melhor ativo, faz ~1.830 views/dia — precisaria de
111.000/dia. **Fator faltante de 60x.**

Quem entrega monetização é a outra porta: **4.000 horas de exibição**, e quem
entrega hora é o vídeo longo, não o Short.

Isso não invalida o método — o fantasma é o protocolo de **largada** (30 dias a
1/dia para o YouTube não ler o canal como spam, que é a hipótese que explica a
morte do EN). Mas a monetização de verdade vem depois, e por isso as duas salas
escolhidas foram checadas também no formato longo:

- Poder: "El Príncipe — Audiolibro Completo", 249 min, 3,67 milhões de views.
  E um canal de 23,1 mil inscritos com 101 minutos fazendo 390 mil.
- Astúcia: canais de 10 a 33 mil inscritos com vídeos de 35–36 min fazendo
  300–645 mil.

**Ou seja: os dois nichos aguentam o longo de 1h que é o motor das horas de
exibição.** O plano é fantasma por 30 dias e, passada a régua, ligar o longo —
que é onde o AdSense de fato mora.

### Duas correções sobre o longo, vindas da pesquisa

Não existe desconto oficial de hora de exibição por reprodução em segundo plano
ou tela desligada — procurei a regra e ela não existe. Mas dois mecanismos reais
limitam o formato "vídeo de 8 horas para dormir":

1. **Reprodução em segundo plano virou exclusiva do Premium.** Em fevereiro/2026
   o YouTube fechou a última brecha em navegadores móveis de terceiros.
   Espectador não-Premium no celular não consegue dormir com a tela desligada.
2. **O aviso "Vídeo pausado. Continuar assistindo?"** dispara por volta de 30 min
   no app móvel e ~60 min na web, e o Premium não desliga. O espectador dorme, o
   YouTube pausa: um vídeo de 8h não acumula 8h de exibição.

Consequência: manter `ALVO_MIN` em **60 minutos** como já está. Perseguir vídeo
de 3h imitando os campeões do nicho seria renderizar 3x mais para colher a mesma
hora. Vale também para os canais bíblicos quando o assunto voltar.

---

## 9. O que falta para pôr no ar

Tudo é código no repo, exceto quatro cliques que a tela do Google não deixa eu
dar pelo Diego:

1. Criar 2 contas de marca (canais) no Gmail pessoal — **só o Diego**.
2. 2 projetos Google Cloud novos + app OAuth **publicado em produção** (senão o
   refresh token morre em 7 dias) — **1 clique de consentimento cada**.
3. Baixar os `client_secret.json` (o console novo não mostra mais o segredo
   depois de criado — só o download do JSON funciona).
4. País de residência no Studio, se o aviso de monetização aparecer.

Do meu lado, sem depender de ninguém: baixar e normalizar o corpus da
Wikisource, gerar o poço de temas, ganchos/CTA/hashtags em espanhol, config,
render de teste, avatar e banner via canvas, secrets e ativação.

**Cota e infraestrutura não são gargalo:** cada canal ganha projeto Cloud
próprio (10.000 unidades/dia; 1 Short custa ~1.650), e o repo é público, então
os minutos de GitHub Actions são ilimitados.
