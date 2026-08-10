# Palavra Viva 3x — 1 pipeline, 3 canais bíblicos (ES / EN / PT)

O MESMO conteúdo diário (1 vídeo longo + 4 Shorts) publicado em três canais,
cada um com áudio TTS, legenda queimada, título, descrição e thumbnail no seu
idioma. Custo zero, 100% na nuvem (GitHub Actions), sem PC e sem intervenção.
Sucessor do pipeline do Palabra Viva (repo `palabra-viva`, hoje aposentado).

## A rotina semanal cobre os 5 CANAIS e a MONETIZAÇÃO — decisão do Diego, 10/08/2026

A rotina de segunda-feira (12:00 UTC) analisava só es/pt/Instagram. A partir de
agora tem de cobrir **os 5 canais no ar** — `es`, `pt`, `stoic`, `poder`,
`astucia` (`en` está desligado, não conta) — e **relatar em toda rodada se cada
canal está apto à monetização**, com os dois portões separados:

- **Portão A (VOLUME)**: 1.000 inscritos + 4.000 horas em 12 meses, OU 1.000
  inscritos + 10 mi de views de Shorts em 90 dias. As trilhas não somam. Hora
  de exibição só vem de vídeo LONGO. Canal com `longos_publicados == 0` **não
  tem trilha de horas**, e a de Shorts exige ~111.000 views/dia (o melhor canal
  da casa faz ~1.800/dia). `desempenho_historico.json` traz `inscritos` e
  `longos_publicados` por canal desde 10/08 — é de lá que sai o quadro.
- **Portão B (FORMATO)**: `answer/1311392` lista como inelegível "readings of
  other materials you did not originally create" e slideshow com narrativa
  mínima. `poder` e `astucia` passam (têm camada autoral). Os bíblicos e o
  `stoic` estão hoje no formato que a política descreve como inelegível —
  domínio público resolve COPYRIGHT, não monetização. Ver `ESTRATEGIA-MONETIZACAO.md`.

O relatório tem de dizer, sem rodeio, **quais canais estão aptos e quais não têm
caminho hoje**. Não estimar inscritos: canal sem medição entra como "não medido".

## Canais

| Idioma | Canal | Conta Google | Secrets |
|---|---|---|---|
| es | Palabra Viva Cortes (`UCIh5XGRGc2t4rLmlukHZOgw`) | Gmail pessoal | `YT_CLIENT_SECRET_ES` / `YT_TOKEN_ES` |
| en | Living Word Daily (ex-Corte em Pauta, `UCi0VMppJlwroIUcxUP5L7DQ`) | Gmail pessoal | `YT_CLIENT_SECRET_EN` / `YT_TOKEN_EN` |
| pt | Palavra Viva Diária (channel_id em publicador/config.json quando criado) | Gmail pessoal | `YT_CLIENT_SECRET_PT` / `YT_TOKEN_PT` |

Cada canal tem projeto Google Cloud PRÓPRIO (quota de 10k/dia não é dividida).
App OAuth precisa estar **em produção**, senão o refresh token morre em 7 dias.

## Arquitetura — fila leve, render na hora de publicar

Diferença-chave vs. o pipeline antigo: a fila NÃO guarda MP4. O repo é público
(minutos de Actions ilimitados) e vídeo commitado incharia o Git para sempre.

| Peça | Onde roda | O que faz |
|---|---|---|
| Poço (`conteudo/temas.json`) | Git | Temas: 1 longo + 4 shorts, títulos nos 3 idiomas, consultas de imagem |
| Reabastecedor (`produzir/reabastecer.py`, cron 6h) | Actions | Cria `fila/AAAA-MM-DD-slug/pacote.json` para hoje+2: valida refs nas 3 Bíblias e resolve URLs de imagem CC0 (Openverse) UMA vez — os 3 idiomas usam as MESMAS imagens |
| Publicador (`publicador/publicar.py`, cron horário) | Actions | Por canal: decide o que está devido (longo 1x/dia após hora_longo_utc; Shorts até 4/dia com gap de 270 min), renderiza NA HORA e publica. Máx. 1 item por canal por execução |

## Cota da YouTube API — a conta que define a agenda

10.000 unidades/dia por projeto Cloud, e **cada canal tem projeto próprio**
(os 3 não dividem). Por canal, com 3 Shorts + 1 longo:

| Item | Unidades |
|---|---|
| 4 uploads x 1600 | 6.400 |
| tornar público (4 x 50) | 200 |
| thumbnail do longo | 50 |
| legenda .srt do longo (captions.insert) | 400 |
| playlist, channels.list, polling de processamento | ~90–230 |
| **total** | **~7.200 de 10.000** |

Sobra para **dois envios de reserva** — o que cobre um vídeo que falhe depois
de subir e seja reenviado. Era 4 Shorts + 1 longo (~8.400, folga de um envio
só); reduzido em 19/07 a pedido do Diego, trocando o Short de menor
rendimento por margem de segurança.

Render que falha ANTES do upload não gasta cota nenhuma (foi o caso das
falhas do canal EN em 19/07). Cota só queima no `videos.insert`.

Cada tema tem 4 Shorts e só 3 vão ao ar: o quarto é reserva — se o longo
falhar, o publicador cai para Short e usa esse (ver `publicar.py::montar`).

NUNCA subir para 6 uploads/dia sem aumento de cota aprovado pelo Google.

## Diretriz editorial — inegociável

1. Só texto bíblico de tradução em DOMÍNIO PÚBLICO: RV1909 (es), KJV (en),
   Bíblia Livre (pt). NVI/RVR1960/ARC/NAA são protegidas — nunca.
2. Shorts sem música. Longos só com o pad ambiente PROCEDURAL
   (`nucleo/musica.py`) — sintetizado por nós, zero risco de claim. Nunca
   biblioteca de música de terceiros.
2b. **Longo = fundo escuro PARADO + legenda queimada** (`FUNDO_ESTATICO_LONGO`
   em `fabrica.py`). Conferido em 24/07/2026 nos dois líderes de "salmos para
   dormir" em pt: nenhum anima imagem — um é tela preta pura — e ambos queimam
   o versículo no rodapé. Quem põe para dormir não quer o quarto piscando. Além
   de ser o formato do nicho, é o que libera a duração: a versão com Ken Burns
   renderiza um clipe por imagem (30 numa hora). O mesmo texto também sobe como
   faixa `.srt` — a legenda queimada é pixel, e é a faixa que a busca indexa.
3. Imagens só CC0/domínio público (Openverse), resolvidas no pacote; qualquer
   falha cai no gradiente da casa. Nunca imagem de banco pago/"grátis com
   atribuição obrigatória" sem gravar a atribuição.
3b. **O fundo da biblioteca é sorteado POR CANAL** (o seed inclui o idioma —
   `fabrica.py`, 30/07/2026). Até então os 3 canais da mesma conta publicavam
   no mesmo dia a mesma foto com áudio em idioma diferente, e no longo essa foto
   É a capa: a impressão digital exata de conteúdo produzido em massa. Não voltar
   a compartilhar. Isto não contradiz a regra "os 3 idiomas usam as MESMAS
   imagens" do reabastecedor: aquela vale para as URLs resolvidas no Openverse
   (resolver 3x custaria 3x rede); sortear da biblioteca local não custa nada.
4. Sem pregação/interpretação: só o texto bíblico e a referência.
5. Nada de cortes/vídeos de terceiros (pesquisa de 17/07/2026: zero canais
   bíblicos autorizam cortes; strike derrubaria os 3 canais da mesma conta).
6. Normalização de grafia da RV1909 (`nucleo/biblia.py`) é GRAFIA, não troca
   de tradução. Inscrições de Salmos e "Selah/Selá" saem da narração.

## Rodar local (testes)

```powershell
python produzir\reabastecer.py --dry-run     # o que criaria
python produzir\reabastecer.py               # cria pacotes hoje+2
python publicador\publicar.py --dry-run      # o que publicaria agora
# renderiza sem subir (não precisa de token):
python publicador\publicar.py --canal es --render-apenas --forcar-tipo short
python publicador\publicar.py --canal pt --render-apenas --forcar-tipo longo
```

Saída de teste em `saida/` (gitignorado). Credenciais locais em
`credenciais/{es,en,pt}/` (gitignorado) — nunca no chat, Git ou print.

## Anatomia do Short/Reel — o padrão de 27/07/2026

Pacote único de mudanças aplicado depois de medir os canais e ler o manual do
nicho. Tudo em `nucleo/fabrica.py::montar_short` e `nucleo/render.py::render_short`.
No Short a moeda é **retenção**: o YouTube só impulsiona acima de 70% de view
ratio (80% viraliza) e a retenção só passa de 100% quando o vídeo dá a segunda
passada. As cinco peças servem a isso:

1. **Gancho falado+escrito no 1º frame** (`nucleo/idiomas.GANCHOS`, 12 por
   idioma, os mesmos nos 3 canais na mesma ordem). Até 27/07 só o Reel do
   Instagram tinha gancho; o Short do YouTube entrava direto no versículo.
   O gancho é EMBALAGEM: não interpreta nem acrescenta doutrina (diretriz 4).
2. **Sem preto na abertura** (`fade_in=0`) e **sem fade no fim** (`fade_out=0`).
   Metade da audiência decide em 1,7s e escurecer no fim avisa "acabou".
3. **Fundo em ciclo fechado** (`_zoompan(loop=True)`, cosseno de 0 a 2π): o
   último frame volta ao enquadramento do primeiro, então a emenda do loop não
   tem solavanco. Conferido: diferença média de 0,89/255 entre 1º e último frame.
4. **Teto de 25s** (`MAX_SHORT_S`), cortando em VERSOS INTEIROS e ajustando a
   referência exibida ao que sobrou. Sem teto, o p90 era 41s e o máximo 75s.
   Com teto: mediana 21s, p90 24s. O resto da passagem vive no vídeo longo.
5. **Passagem de até 25 palavras é narrada 2x** (`REPETIR_ATE_PALAVRAS`) —
   formato do nicho (repetição para meditar) e mais loops no mesmo vídeo.

⚠ **Defeito corrigido junto, que saiu em TODOS os Shorts publicados até
27/07/2026**: sem `-framerate 30` na entrada de imagem, o demuxer entrega 25
fps, o zoompan devolve 1 frame por frame de entrada e o `fps=30` do filtro só
carimba a saída — o vídeo saía **17% mais curto que a narração** (23,4s de
áudio com 19,5s de imagem). A narração terminava sobre o último frame parado,
exatamente onde a retenção é decidida. Nunca tirar o `-framerate` da entrada.

## Qualidade do conteúdo — decisões que já custaram um vídeo ruim
- **Imagem fora do assunto**: o Commons devolve muito documento e foto de
  arquivo. `nucleo/imagens.py` reprova por título (blocklist `LIXO`) e exige
  **2 termos da consulta no título** — "green pastures stream" trazia porcos
  de fazenda; "sun rays" trazia peça de museu. Sem imagem boa, o render usa
  o gradiente da casa: melhor liso e limpo que errado.
- Depois de mexer em `conteudo/temas.json`, rodar
  `python produzir/auditar_consultas.py` e reescrever as consultas VAZIA
  (usar substantivos que aparecem em título de foto: "lake sunset",
  "forest path", "eagle soaring").

## Armadilhas já pagas (herdadas dos canais anteriores)

- Cron horário + janela no state, NUNCA cron esparso: disparo do GitHub atrasa
  e combinado com trava de janela pula o slot (o Corte em Pauta pagou com
  publicações de 12h em vez de 6h).
- `state.json` e `fila/` são versionados de propósito: runner é descartado;
  sem commit, o disparo seguinte republicaria o mesmo item.
- Validar `channel_id` do token antes de subir (token errado = vídeo no canal
  errado).
- edge-tts 7.x: `boundary="WordBoundary"` obrigatório no Communicate.
- Fontes do render são as do repo (`marca/fontes` via fontsdir) — nunca
  depender de Arial do sistema (o runner não tem).
- **Capa personalizada: LIBERADA desde 27/07/2026** (a verificação de identidade
  da conta saiu; antes a API devolvia 403 e o longo ficava com o frame automático
  do YouTube, que num fundo escuro parado é um retângulo preto). Se voltar a dar
  403, é a conta, não o código. Em 30/07 a rodada foi REFEITA nos 31 longos, por
  um defeito de arte e não de permissão: `aplicar_capas.py` passava
  `imagem=None` + `seed=7`, então as capas aplicadas em 27/07 eram todas o MESMO
  gradiente roxo, com só o texto mudando entre 25 vídeos e 3 canais. Agora usa a
  foto da biblioteca, a mesma que o render do longo usaria.

## Poço seco

Workflow abre issue quando `temas.json` esgota. Adicionar temas novos (mesmo
formato: refs canônicas em inglês scrollmapper, títulos ≤100 chars nos 3
idiomas, consultas de imagem em inglês) e dar push. Validar com
`python produzir\reabastecer.py --dry-run` antes.

## La Noche Estoica (@LaNocheEstoica) — o canal estoico agora é ESPANHOL

02/08/2026, decisão do Diego: o 4º canal (parado desde 31/07) foi
transformado para o público hispanohablante. **Mesmo canal, mesmo token,
mesmo projeto Cloud** — renomear não invalida o OAuth; a chave no código
continua sendo `stoic`. Estudo do nicho e plano em `ESTRATEGIA-STOIC-ES.md`.

- **Nome**: o YouTube RECUSOU "Noche Estoica" ("Esse nome não pode ser usado
  no seu canal") e o handle @NocheEstoica já estava tomado. Ficou
  **La Noche Estoica / @LaNocheEstoica**.
- **Corpus** (`fontes/PROVENIENCIA.md` §6 e §7): Meditaciones na tradução
  Díaz de Miranda (1785/1888) e Enquiridión na de Antonio Brum (1669/1888),
  ambas em domínio público. **Sêneca ficou de fora**: a tradução PD
  (Navarro y Calvo, 1884) não está transcrita e as Cartas do es.wikisource
  são tradução comunitária moderna, protegida. Não usar.
- **Voz** `es-US-AlonsoNeural` — diferente do es-MX-Jorge do Palabra Viva de
  propósito: dois canais da mesma conta com a mesma voz é assinatura de
  fábrica.
- **CTA pede SAVE**, não inscrição ("Guárdalo para cuando lo necesites"):
  em 2026 o "guardar" é o sinal nº 1 do algoritmo de Reels/Shorts.
- **Imagens só NOTURNAS**. O filtro do Commons exige 2 termos da consulta no
  título, então consulta de 3+ palavras ("candle night desk") reprova e cai
  no gradiente — o poço inteiro foi reescrito com pares concretos validados
  ("moon clouds", "milky way", "bonfire night", "clay lamp"...). E o canal se
  chama "La Noche": foto diurna verde destoa da marca.

## El Poder Crudo e Astucia Fría — 2 canais ES novos (03/08/2026)

Decisão do Diego depois do teste de mercado de **26 salas em espanhol** medidas
pela YouTube Data API (critério do manual: canais <60k inscritos com +300k
views). Estudo completo em `ESTRATEGIA-2-CANALES-ES.md`.

| chave | canal | channel_id | hora | voz | corpus |
|---|---|---|---|---|---|
| `poder` | El Poder Crudo `@ElPoderCrudo` | `UC9m5fvEqQZ_J34oQzczgFoQ` | 02 UTC | es-CO-Gonzalo | El Príncipe, trad. anônima 1854 |
| `astucia` | Astucia Fría `@AstuciaFria` | `UCNyr1A0MN3rQT1Oa5LBjLUA` | 03 UTC | es-AR-Tomas | Oráculo manual de Gracián (1647) |

Ambos rodam **Protocolo Fantasma puro** (1 Short/dia, sem longo, teto 20s,
3 hashtags, descrição enxuta, 30 dias sem mexer). Régua ≈03/09: mediana ≥300
views/Short mantém e escala.

### A diferença que NÃO se copia dos canais bíblicos: camada autoral

O Short destes dois é **gancho → trecho citado → aplicação própria**, narrada.
Motivo não é estético. A política oficial de monetização do YouTube
(`support.google.com/youtube/answer/1311392`, conferida na fonte em 03/08)
lista como **inelegível**:

> "Content that exclusively features readings of other materials you did not
> originally create" · "Image slideshows, templated storylines, or scrolling
> text with minimal or no narrative, commentary, or educational value"

E o critério de aprovação é haver *"meaningful difference"* entre a fonte e o
vídeo. **Domínio público resolve COPYRIGHT, não MONETIZAÇÃO — são dois
trilhos.** A aplicação vive no poço (`aplicacao` por short) e é narrada por
`fabrica.montar_short`; ela também desconta do orçamento de duração, senão o
Short estoura os 20s.

⚠ Isso **não** vale para os bíblicos: lá a diretriz nº 4 (sem interpretação) é
decisão do Diego. Mas os 3 canais bíblicos estão hoje exatamente no formato
que a política descreve como inelegível, e nenhum foi submetido ao YPP —
assunto para depois de 01/09.

### Armadilhas pagas nestes dois (03/08)

- **Corpus fatiado por FRASE, não por 120 palavras.** `_cortar_ao_teto` corta
  em versos inteiros; verso de 120 palavras estoura sozinho o teto de 20s.
- **Consulta de imagem tem de ser NOTURNA.** A primeira rodada trouxe muro de
  castelo japonês ao meio-dia, com grama verde e céu azul, num canal chamado
  "El Poder Crudo" — o mesmo erro que a Noche Estoica já tinha pago. Pares
  concretos com `night`/`dark`; falhar e cair no gradiente da casa é melhor
  que acertar uma foto diurna.
- **O workflow Reabastecer só commitava `fila/`** — as filas próprias
  (`fila_stoic`, e agora `fila_poder`/`fila_astucia`) nunca subiam da nuvem.
  A Noche Estoica ia secar sem aviso. Corrigido em 03/08.
- **Studio de canal novo responde "Ops" por horas** — avatar e banner ficaram
  gerados (`marca/gerar_marca_es2.py`) e commitados, mas não aplicados.

## Regime do "método de canal novo" no canal estoico (retomado em 02/08)

O canal `stoic` roda **100% pelo método do PROTOCOLO FANTASMA** (PDF em
`Desktop\Venda na Obra`). Estreou assim em 28/07 (em inglês), foi abortado em
31/07 e **retomado em 02/08 já em espanhol** — o Diego pediu explicitamente
"seguir rigorosamente a estratégia do protocolo fantasma". É um teste
deliberado: os canais bíblicos nasceram em 4 uploads/dia e o manual diz que
canal novo tem de fazer 1/dia por 20-30 dias, senão o YouTube lê como spam e
estrangula a entrega.

O que muda SÓ neste canal (os bíblicos seguem como estavam):

| Regra do método | Como está implementado |
|---|---|
| 1 vídeo/dia, mesmo horário | `shorts_por_dia: 1` + `hora_short_utc: 1` (01 UTC = 19h CDMX / 20h Bogotá / 22h Buenos Aires) |
| Sem vídeo longo | `hora_longo_utc: null` (suportado em `decidir`) |
| Short de 10-20s | `max_short_s: 20.0` no CONFIG do idioma |
| 2-3 hashtags, não 5 | `hashtags` com 3 |
| Descrição enxuta | `descricao_curta: True` (pula o texto citado e o CTA escrito) |

O horário mira a LATAM, não a Espanha: México + Colômbia + Argentina somam
umas 4x a população espanhola, e 01 UTC é noite lá e madrugada em Madri.

Consequência aceita: abre mão das 4.000 horas de exibição neste canal durante
o teste. O método monetiza pela via de Shorts (1.000 inscritos + 10 mi de
views em 90 dias), que não depende de vídeo longo.

**Revisar 30 dias depois da retomada (≈01/09/2026)**: mediana ≥300 views por
Short mantém e escala (2/dia + longo de dormir, que é o motor de horas);
repetir a mediana de 1 view do EN mata de vez. Comparar sempre com o ES
bíblico no MESMO tempo de vida. Não mexer em nada durante a janela — foi
mudar duas variáveis ao mesmo tempo que derrubou o pipeline em 20/07.
