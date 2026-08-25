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
| es | Palabra Viva Cortes → **rebrand em curso**, ver abaixo (`UCIh5XGRGc2t4rLmlukHZOgw`) | Gmail pessoal | `YT_CLIENT_SECRET_ES` / `YT_TOKEN_ES` |
| en | Living Word Daily (ex-Corte em Pauta, `UCi0VMppJlwroIUcxUP5L7DQ`) | Gmail pessoal | `YT_CLIENT_SECRET_EN` / `YT_TOKEN_EN` |
| pt | Palavra Viva Diária (channel_id em publicador/config.json quando criado) | Gmail pessoal | `YT_CLIENT_SECRET_PT` / `YT_TOKEN_PT` |

Cada canal tem projeto Google Cloud PRÓPRIO (quota de 10k/dia não é dividida).
App OAuth precisa estar **em produção**, senão o refresh token morre em 7 dias.

## Rebrand do canal ES: sai a palavra "Cortes" (19–20/08/2026)

O canal nunca foi de cortes de terceiros (diretriz nº 5 sempre proibiu isso) e
publica vídeo LONGO desde 19/07. O nome "Palabra Viva Cortes" era herança do
Radar Geek e descrevia errado o que o canal faz. Decisão do Diego em 19/08.

**Feito em 19/08**

- **Capa nova** (`marca/banner-es.png`): wordmark passou a ser só
  **PALABRA VIVA**, com a tagline "La Palabra de Dios en audio, cada día".
  Aplicada por API (`channelBanners.insert` + `channels.update`) — essa parte
  tem API e não precisa do Studio.
- `defaultLanguage` do canal corrigido de `en` para `es` (o canal aparecia com
  localização en_US). Efeito colateral: o YouTube criou a localização `es_ES`
  congelando o título atual.
- A **descrição** do canal nunca teve a palavra "cortes"; nada a limpar lá.

**Feito em 20/08 — handle**

Handle trocado para **`@PalabraVivaEnAudio`** pelo Studio (via Chrome MCP,
`javascript_tool`, `authuser=0`). Confirmado por API: `snippet.customUrl` =
`@palabravivaenaudio`. Como o handle é queimado na legenda de todo Short e
longo, os vídeos novos já saem sem "Cortes".

**Continua pendente — o NOME**

Na mesma requisição em que o handle passou, o
`update_channel_page_settings` devolveu **200** com
`titleUpdateStatus.error = TITLE_UPDATE_ERROR_REJECTED_BY_TNS`
(`updateStatus.errorCode: 9`) para "Palabra Viva en Audio" — ou seja, o nome
foi recusado por **política de nome**, não mais por cota (o erro de 19/08 era
`TITLE_UPDATE_ERROR_NAME_CHANGE_QUOTA_EXCEEDED`). Não foi insistido: cada
recusa queima a cota de 24 h.

- Não existe canal chamado "Palabra Viva en Audio" (conferido por
  `search.list`), então a recusa não é duplicidade óbvia — pode ser resíduo do
  bloqueio de 19/08 ou o filtro pegando o "Palabra Viva" cheio de homônimos.
- **Plano B ficou arriscado**: "Palabra Viva Salmos" esbarra em
  "Palabra Viva Salmos Cantados y Música Cristiana", que já existe — é
  exatamente o tipo de colisão que derrubou "Palabra Viva Diaria".
- Sugestão para a próxima tentativa (≥ 21/08): um nome sem homônimo, do tipo
  **"Palabra Viva en Audio Diario"** ou **"Audio Palabra Viva"**; conferir
  antes com `search.list` E com `curl` no handle.
- Como ler o resultado de verdade: patch em `XMLHttpRequest.prototype.open`
  para logar `JSON.parse(responseText).titleUpdateStatus` nas URLs
  `/channel_edit/`. Sem isso a resposta 200 parece sucesso.
- Enquanto o nome não mudar, `titulo_canal` em `publicador/config.json`
  continua "Palabra Viva Cortes" (é o título real) e a localização `es_ES`
  também — mexer só num dos dois cria incoerência.
- `channels.update part=localizations` devolve **400 failedPrecondition**, e
  `part=localizations,brandingSettings` é recusado
  ("branding_settings cannot be used with other parts"): a localização também
  só muda pelo Studio.

**Não adianta rodar "Realinhar descrições" por causa do rebrand.** `handle` e
`titulo_canal` NUNCA entram na descrição do vídeo: o handle só é usado em
`fabrica.montar_short/montar_longo` → `legendas.ass_*`, ou seja, é **queimado no
pixel** do vídeo. Os vídeos já publicados vão continuar estampando
@PalabraVivaCortes na imagem para sempre (só re-upload mudaria) e o realinhar
gastaria 50 unidades de cota por vídeo sem alterar nada.

⚠ Chrome: o Studio deste canal está na conta pessoal, que neste perfil do Chrome
é **authuser=0** (o padrão do YouTube abre em diego@perffec.com.br). URL certa:
`studio.youtube.com/channel/UCIh5XGRGc2t4rLmlukHZOgw/editing/profile?authuser=0`.
A aba fica hidden: screenshot dá timeout, então operar por `javascript_tool`
percorrendo shadow DOM e escrevendo com o setter nativo de `value`.

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

## Funil de HORAS: playlist + ponte do Short (25/08/2026)

Pergunta do Diego: "seguidores crescem, horas de exibição não — publico 2 longos
por dia?". **Não.** Dobrar a esteira não move a agulha e cobra caro: os longos
respondem por 1,6% das views do ES (o gargalo é distribuição, não estoque), o
canal já gasta ~7.200 dos 10.000 de cota (um 2º longo levaria a ~9.600, sem
margem de retry), o poço secaria 2x mais rápido e o Portão B de monetização
piora — vídeo de 1h idêntico duas vezes ao dia é a impressão digital de produção
em massa. O que rende hora é **encadear sessão** no que já existe:

- **Playlist por formato com autoplay**: acabando um longo, o YouTube emenda o
  próximo da lista em vez de mandar o espectador embora. Os 83 longos publicados
  (es 38, en 9, pt 36) estão nas 9 playlists dos 3 canais desde 25/08 —
  `produzir/preencher_playlists.py` é a auditoria idempotente disso (workflow
  manual **Preencher playlists**). O publicador já inseria o longo na hora de
  publicar, mas "playlist falhou; seguindo" nunca derrubou publicação: 8 longos
  estavam fora da lista e ninguém sabia.
- **Ponte do Short com `&list=`**: a descrição do Short aponta o longo do dia
  como `watch?v=...&list=...`, ou seja, abre DENTRO da playlist. Se o longo do
  dia falhou, cai no último longo do mesmo formato — link de ontem é melhor que
  Short sem ponte. 95% das views do canal vêm do feed de Shorts e esse tráfego
  morria ali.
- **Link da lista na descrição do longo** (`fabrica.bloco_playlist`), que é
  quem recebe a busca — o espectador de horas.
- Os ids das playlists ficam em `publicador/playlists.json`
  (`nucleo/playlists.py`), versionado como o `state.json`: o RENDER precisa
  deles e roda sem token, e descobrir por API custaria uma chamada por
  publicação.

**O que NÃO foi feito, de propósito:** comentário fixado no Short apontando o
longo — **fixar comentário não tem API** (só o Studio, vídeo a vídeo), e
comentário do dono sem fixar se perde. E realinhar os 86 Shorts antigos para
incluir a ponte: 4.300 de cota para uma descrição que quase ninguém abre no
feed. Se um dia valer, é `realinhar_publicados.py --tudo`.

⚠ `realinhar_publicados.py` ficou **idempotente e retomável**: compara o que já
está no ar e só gasta as 50 unidades do update quando algo mudou de verdade;
`--limite N` teta as atualizações por rodada. A comparação de **tags é por
CONJUNTO** — a API devolve as tags em ordem alfabética, então comparar as listas
posição a posição dava "diferente" sempre e reescrevia o acervo inteiro a cada
rodada. Com isso o workflow Realinhar ganhou **schedule diário às 07:10 UTC**
(logo após a virada da cota, antes do Short das ~07:30), teto de 19 vídeos por
canal ativo: em dia sem mudança gasta ~40 unidades e não toca em nada; quando o
padrão muda, o acervo se realinha sozinho em rodadas de 19/dia. O ES leva dois
dias para os 38 longos — de propósito, estourar a cota deixaria o canal mudo.

## A ESTRATÉGIA DE MONETIZAÇÃO em vigor (25/08/2026) — ler antes de mexer

O Diego perguntou o que eu faria "se a decisão fosse minha e quisesse
monetizar". A resposta, e o que está implementado:

**O YPP não é o prêmio que parece.** Nos últimos 60 dias o ES entregou 87.590
views de Shorts e 1.566 de longo. Com os RPM reais do formato (Shorts pagam
~US$0,10/mil; longo devocional em espanhol, US$2-4/mil), o canal aprovado hoje
renderia **R$30 a 60 por mês** — e o PT, menos de R$10. Uma única venda do
afiliado (US$40) paga seis meses disso. Perseguir as 4.000 h como objetivo
econômico é meta de vaidade **no volume atual**.

**O que muda de patamar é uma variável só: views de vídeo LONGO.** Uma view de
longo vinda de recomendação vale 7,2 minutos; uma de Short, 0,13 — **55x**. E o
canal recebe ~37 views por longo publicado. O longo já converte bem; ele só não
é visto. Toda a economia do projeto está aí, e o Short é motor de vaidade —
views que não pagam nem convertem (mas ainda contam para o portão de inscritos).

Decisões que saíram disso, todas no ar:

1. **2 longos/dia no ES** (`longos_por_dia: 2`, gap de 480 min), com o Short
   caindo de 3 para 2/dia — a cota manda: 2 longos (2×2.100) + 2 Shorts
   (2×1.650) = ~7.500 de 10.000, sobrando margem para um retry. Com 3 Shorts
   daria 9.150 e um único retry derrubaria o dia.
2. **O 2º longo sai do 2º pacote da data**, nunca do mesmo tema do 1º, e o
   reabastecedor dá **preferência ao formato "dormir"** para essa vaga (60 min
   contra 30 do "tema"): a vaga extra existe para gerar HORA.
3. **`gerar_temas_salmo.py` acabou com o gargalo humano do poço.** Cada salmo é
   um tema natural ("Salmo N completo" — e "salmo 103" é termo de busca real,
   medido na Analytics). Título, abertura falada, tags e descrição saem de
   FATOS do próprio salmo: quantos versículos tem, o que diz a inscrição, como
   começa. Não interpreta (diretriz nº 4) e **não afirma autoria** — a inscrição
   é citada como inscrição ("leva por inscrição: Salmo de Davi"), nunca como
   autoria, que é disputada. Os 55 salmos que ainda não eram tema viraram tema:
   o poço foi de 18 para **70 livres** (~35 dias a 2/dia).
   ⚠ A **capa** desses temas leva uma CITAÇÃO do salmo no subtítulo, não "Salmo
   N completo". A primeira versão repetia o título e as 55 capas ficavam
   idênticas mudando só o número — sem motivo para clicar e com a cara de
   produção em massa que a análise de monetização procura. Conferido na capa
   renderizada, inclusive no subtítulo mais longo.
4. **Régua automática**: `medir_horas.py` roda junto do medir diário e compara
   com `conteudo/baseline_funil_horas.json` (a foto de 25/08, antes da mudança).
   Os tokens de Analytics viraram secrets (`YT_TOKEN_ANALYTICS_*`) — antes só
   existiam no PC do Diego e a régua dependia de alguém lembrar de rodar.
5. **`&src=yt_largo_es` no link de afiliado**: sem rastreio não dá para saber se
   a oferta gerou um clique sequer em dois meses, e trocar de oferta viraria
   achismo.

**A régua, combinada com o Diego: 25/11/2026.** Se as horas contáveis do ES não
tiverem dobrado (de ~1.100 para ~2.200 h/ano), o teste falhou: volta para 1
longo/dia e o projeto vira ativo dormente, sem mais horas humanas. E vale dizer
o desconfortável: **mesmo dando certo, isto é um projeto de algumas centenas de
reais por mês**. Ele se justifica por rodar sozinho e por ser uma opção, não por
ser renda.

**A oferta em espanhol deixou de ser pendência em 25/08** — e é PRODUTO PRÓPRIO,
não afiliado. Dois e-books de US$ 4,90 na Hotmart, feitos no projeto
`Desktop\Projetos\Productos-Canales`, com KYC aprovado e checkout testado:

| Canal | Produto | ID | Hotlink |
|---|---|---|---|
| `es` | 30 Noches con la Palabra | 8389798 | `pay.hotmart.com/X107325587N` |
| `stoic` | 30 Noches Estoicas | 8389879 | `pay.hotmart.com/O107325775B` |

- No ES o devocional entra **acima** do piano (que continua como segunda oferta
  por ser o produto mais quente do nicho no marketplace), e o **Short voltou a
  ter oferta**: o piano tinha saído de lá em 28/07 por ser descasado do público,
  e o devocional é do mesmo público do vídeo — era exatamente o critério que
  faltava.
- Todo link leva `?src=` por origem (`yt_largo_es`, `yt_short_es`,
  `yt_largo_stoic`, `yt_short_stoic`): é o rastreador nativo da Hotmart e é o
  que vai dizer se o Short converte.
- ⚠ **Nunca escrever "link de afiliado" nesses blocos** — o produto é do Diego;
  a frase de divulgação de afiliado só vale para o piano.
- O acervo antigo recebe o link pelo workflow Realinhar (07:10 UTC, 10/dia).

O que eu NÃO faria e por quê: abrir o canal `sabiduria` agora (o problema não é
falta de canal, é falta de views de longo, e canal novo divide o único recurso
escasso); otimizar Short (retém 103%, não há upside); e limpar o acervo dos 17
longos crus antes de haver motivo real para submeter ao YPP — eles valem 50% das
horas de longo do ES.

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

## Reel do Instagram: modo CINE (13/08/2026) — o formato antigo não engajava

Medição de 13/08/2026 no @psicologiafria.br, 10 dias no ar: **18 seguidores e
Reels com 6 a 118 views**. Estudo de 3 perfis sem rosto do mesmo nicho
(@omanualdomanipulador 149 mil / 4-13 mil views por Reel, @estoicodiario 329 mil
/ 21-58 mil, @estoicismopratico 187 mil / 8-43 mil) e do que saía daqui:

| O que saía | O que mudou (`modo: "cine"` em instagram/config.json) |
|---|---|
| Foto da biblioteca (floresta VERDE ensolarada num perfil "gelado") | Fundo **procedural** escuro em movimento (`render.fundo_cine`): nuvens à deriva + feixe de luz + grão, paleta sorteada por seed |
| Voz TTS pt-BR-Antonio | **Sem narração**: texto grande + trilha procedural (`musica.gerar_trilha_fria`) |
| Legenda 86 px, tempos vindos do TTS | 96-112 px, 3 estilos (Gancho/Verso/**Fecho** em azul-gelo) e tempos de LEITURA (`instagram/roteiro.py`) |
| ~28 s narrando o item inteiro | ~19-21 s: premissa + o que couber + **a última frase inteira**, que fica mais tempo na tela |
| Rampa subindo para 4/dia | **Congelada em 2/dia** até a mediana passar de 1.000 views/Reel |

`instagram/reels.py` tem as duas funções: `montar_reel_cine` (padrão) e
`montar_reel` (o modo antigo, mantido para comparar sem reescrever nada).

Armadilhas pagas neste pacote:

- **`blend` sem `format=gbrp` mistura os planos em YUV e o azul-gelo sai ROXO.**
  Cada camada entra em RGB planar e só o resultado vira yuv420p.
- **`zoompan` está proibido neste caminho.** No ffmpeg 8 o idioma `d=1` +
  `fps=30` devolve 1/3 dos frames: um render local saiu com **7,8 s de imagem
  para 28 s de áudio**. (Os Reels publicados até 13/08 estão íntegros — o
  runner ainda usa ffmpeg 6 —, mas o defeito chega quando o runner atualizar.)
  Movimento vem das fontes `gradients`, que se comportam igual em toda versão.
- **`gblur` vai ANTES do `scale`**: borrar 120x213 e ampliar dá a mesma névoa
  por uma fração do custo (o runner tem 2 núcleos).
- **A trilha tem de viver acima de ~200 Hz.** A primeira versão foi escrita em
  55-82 Hz e no alto-falante do celular seria vídeo mudo.
- **Blocar por FRASE, não por texto corrido**: blocando corrido saíam legendas
  como "emocional. Mais tarde, quando" — fim de uma frase colado no começo da
  outra. E o fecho é reservado ANTES do miolo, senão chega picado.

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
