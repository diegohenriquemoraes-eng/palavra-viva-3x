# Canais — painel único, estado em 03/09/2026

> Ponto de partida de qualquer sessão sobre canais. Este arquivo diz **o que está no ar, onde
> mora e o que está esperando decisão**. O detalhe técnico de cada motor está no `CLAUDE.md`
> da pasta correspondente — abrir só depois de saber por qual passar.

## O que mudou na madrugada de 02→03/09/2026

**O agendador entregava metade da esteira, e havia sete dias que isso durava.** O ES devia 2
Shorts/dia e publicou 9 de 16 entre 26/08 e 02/09 (em 28/08, zero). Duas causas: `decidir`
devolvia "nada devido" enquanto o 2º longo esperava o gap de 8 h — calando o canal da 01h às
08h UTC todo dia — e o gap entre Shorts era um veto absoluto num cron que o GitHub entrega
**~6 vezes por dia**, não 24. Corrigido, com replay das execuções reais: **es 9 → 13 Shorts,
stoic 20 → 23**. Detalhe do CLAUDE.md que se provou de novo: cron esparso mata a esteira — só
que desta vez o cron ficou esparso sozinho, pelo lado do GitHub.

**A queda do ES não é de retenção.** A coorte por semana de publicação segue entre 95% e 124%
(o limiar de impulso é 70%). O que caiu foi entrega: a mediana por Short foi de 903 (28/07) a
184 (02/09). Nada de mexer em voz, gancho ou teto antes de ver a esteira andar completa por
duas semanas.

**Nada disso apareceu em alarme**, porque o vigia media silêncio e views/dia do canal — dois
números que um canal pela metade não move. Entraram dois alarmes: *publicou menos do que a
config manda* (3 dias fechados) e *mediana da coorte 2-7 d caindo* — este validado contra a
série real: teria tocado em **22/08**, onze dias antes.

**O poço estoico tinha 1 tema livre** e o canal secaria no dia seguinte. Repostos **13 temas
(52 Shorts)**; poço em 14 livres, fila até 15/09. ⚠ O corpus está no fim: sobram ~59 passagens
utilizáveis, uns 14 temas. Corpus novo em domínio público **verificado** é a próxima
necessidade real do canal.

**Existe suíte de testes agora** (`testes/`, 36 casos, 2 s, workflow **Testes** em todo push):
agenda, orçamento de cota, coerência da config e integridade dos poços.

### O que ficou esperando decisão do Diego

1. **Ligar o longo no La Noche Estoica.** É o único canal em crescimento real (mediana 982
   views/Short; 85 inscritos, +5,5/dia contra 1,6 do ES) e tem **39 h/ano projetadas de 4.000**
   porque nunca publicou um longo. Os 13 temas novos já nascem com o longo escrito. Falta só
   `"hora_longo_utc": 12` e `"longos_por_dia": 1` no config — e a janela de medição do canal vai
   até **22/09**, então o certo é ligar depois dela.
2. **O ES não tem margem de cota para reenviar um longo** (8.178/dia normal, 10.354 com um
   reenvio, de 10.000). A conta de 25/08 não incluía o workflow Realinhar nem legenda e playlist
   dos dois longos. Abrir margem custa um Short/dia.
3. **Títulos repetidos no acervo**: 13 Shorts em espanhol e 12 em português têm título idêntico
   a outro do mesmo canal (um saiu 4x). São todos vídeos publicados; consertar custa cota que o
   ES não tem e mexe em vídeo que já ranqueia. O poço livre não repete nenhum, e agora há teste.

## Quem publica hoje

| Canal | Plataforma | Ritmo | Motor (pasta) | Conta |
|---|---|---|---|---|
| **Palabra Viva Cortes** `@PalabraVivaEnAudio` (handle já trocado em 20/08; o NOME ainda é "Cortes" — YouTube recusou por política, ver CLAUDE.md) | YouTube ES | 3 Shorts + 1 longo/dia | `Palavra-Viva-3x` | Gmail pessoal |
| **Palavra Viva Diária** `@PalavraVivaDiária-biblia` | YouTube PT | 1 Short + 1 longo/dia — **canal de LONGO desde 22/08** | `Palavra-Viva-3x` | Gmail pessoal |
| **La Noche Estoica** `@LaNocheEstoica` | YouTube ES | **3 Shorts/dia desde 22/08** (era 1), 01 UTC | `Palavra-Viva-3x` | Gmail pessoal |
| **Sabiduría** (nome a definir) | YouTube ES | ⏳ **preparado, canal ainda não existe** | `Palavra-Viva-3x` | — |
| **Astucia Fría** `@AstuciaFria` | YouTube ES | 1 Short/dia, 01 UTC | `psicologia-fria` ⚠ | Gmail pessoal |
| **@psicologiafria.br** | Instagram | 7 Reels/dia | `psicologia-fria` | — |
| **@VendanaObra** | YouTube PT | manual | — | `diego@perffec.com.br` |

⚠ **Astucia Fría mudou de motor em 15/08**: deixou de publicar Gracián pelo `Palavra-Viva-3x`
(`ativo: false` lá, para sempre) e virou o Psicologia Fria em espanhol, rodando no repo
`psicologia-fria`. É o erro mais fácil de cometer aqui.

## Quem está desligado

| Canal | Desde | Por quê |
|---|---|---|
| **Living Word Daily** `@LivingWordDailyKJV` (EN) | — | mediana de ~1 view; `ativo: false` |
| **El Poder Crudo** `@ElPoderCrudo` | 15/08 | 12 dias, 4 inscritos, mediana 74 contra régua de 300. Canal e vídeos ficam no ar. **Não reativar o formato Maquiavel.** |
| **Corte em Pauta** (cortes do Flow) | 18/07 | Encerrado. O canal virou o Living Word Daily; a pasta é arquivo morto, mas as credenciais em `youtube-api/` seguem em uso como os secrets `YT_*_EN`. |
| **Palabra-Viva** (repo antigo) | 19/07 | Aposentado. O canal é abastecido pelo 3x; a pasta guarda as credenciais `YT_*_ES`. |

## O que foi executado em 22/08 (as 4 decisões do Diego)

Ordem de leitura: o estudo acima diz **por quê**; isto diz **o que mudou**. Regra que valeu para
tudo: **nada tocado no canal ES** — decisão explícita do Diego, e é o canal que sustenta a casa.

1. **O poço estoico estava SECO e ninguém sabia.** A fila terminava em 22/08: a Noche Estoica
   pararia no dia 23. O vigia não avisou porque só olhava `temas.json` — o poço estoico não
   existia para ele. **Corrigido nos dois lugares**: `vigia.py` agora percorre todas as linhas
   (`POCOS`), e o alarme de fila vazia do `publicar.yml` agora olha todas as filas, não só `fila/`.
   Repostos **+14 temas** (56 Shorts) — alcance de 14 dias.
2. **Noche Estoica escalada de 1 para 3 Shorts/dia.** A régua do método já tinha sido cumprida
   com folga: mediana de 782 na coorte 2-7 d contra os 300 exigidos, retenção de 90%, 26 vídeos
   desde 03/08. Detalhe que torna isto barato: **os pacotes já tinham 4 Shorts cada e só o
   short-1 era publicado** — subir para 3 não consome o poço mais rápido, só usa o que já estava
   escrito. Cota: 3 uploads = ~5.150 de 10.000, folga de 3 reenvios. **Medir em 22/09**: se a
   mediana cair abaixo de 300, voltar para 1/dia.
3. **Poço bíblico reposto**: tinha 9 dias, agora tem **21**. +12 temas (48 Shorts), todos com SEO
   por tema, abertura falada no longo e camada autoral no Short. Novos: Rute e Noemi, Zaqueu,
   a tempestade acalmada, os cinco pães, a samaritana, Gideão, os dez leprosos, setenta vezes
   sete, Jeremias 29, e três "salmos para dormir".
4. **Canal PT virou canal de LONGO** e a régua de desligar de 15/09 está **cancelada** —
   ver o estudo acima. Nova régua, **22/11**: horas de exibição dos longos em 12 meses.
   Não medir mais este canal pela mediana de views de Short: é a métrica errada para o que ele é.
5. **Canal ES novo preparado e dormente** (`sabiduria`, Proverbios/Eclesiastés na RV1909, voz
   **feminina** es-MX-Dalia — a primeira da casa). Está tudo pronto menos o que depende do
   YouTube: linha própria no reabastecedor e no vigia, bloco em `idiomas.py`, secrets no
   `publicar.yml`, e poço com 10 temas validados. Com `ativo: false` ele não renderiza nem
   publica nada. **O que falta é só o Diego** — os 6 passos estão em
   `publicador/config.json`, em `sabiduria._o_que_falta_o_diego_fazer`.
6. **Camada autoral fechada**: 9 Shorts de temas ainda não publicados sairiam como leitura crua
   (é o que a política do YPP lista como inelegível). Hoje **todo tema livre dos três poços está
   coberto**.

⚠ Um alarme falso do vigia deve aparecer no dia 22: com `shorts_por_dia: 3` o limite do canal
estoico cai de 30h para 14h, e o canal só passa a publicar de 7 em 7 h a partir do dia 23.
Some sozinho.

## O que está pedindo mão em 17/08

1. ~~Poço de temas: 4 dias.~~ **Reposto em 17/08**: +10 temas (46 no total, 14 livres = 14
   dias). Os novos: `salmos-dormir-14` a `-17`, `jonas-peixe`, `bom-samaritano`,
   `ester-rainha`, `paulo-silas-prisao`, `cura-e-consolo`, `trabalho-e-proposito`.
   ⚠ O poço é **compartilhado**: quando ele zera, os **três** canais bíblicos param juntos.
   Repor é escrita — 1 longo + 4 Shorts, títulos nos 3 idiomas, consultas de imagem em pares
   concretos de 2 palavras —, e valida com `python produzir/reabastecer.py --dry-run --dias 12`
   (o `--dias` é o que força a validação dos temas novos; sem ele a fila diz "saudável" e não
   valida nada).
2. **pt continua caindo** — mediana da coorte 2-7 d: 41 (10/08) → 15 (17/08), 74 inscritos.
   O corte para 1 Short/dia foi em 15/08 e ainda não teve tempo de aparecer. Régua: 15/09.

Medição de 22/08 (coorte 2-7 dias, `conteudo/desempenho_historico.json`):

| canal | mediana | inscritos | views totais |
|---|---|---|---|
| es (Palabra Viva) | **286** ⚠ ver queda do rebrand | 314 | 79.007 |
| stoic (La Noche Estoica) | **782** | 28 | 15.306 |
| pt (Palavra Viva Diária) | 11 | 76 | 8.621 |
| astucia (Astucia Fría) | — (motor no repo psicologia-fria) | 7 | 652 |

## Estudo de 22/08 — o que separa quem cresce de quem não cresce

Feito com a **Analytics API** (retenção, fonte de tráfego, país, watch time), leitura pura, sem
mexer em canal. Relatório em `Desktop\Analise-Canais-YouTube-22-08-2026.html`.

**A variável é RETENÇÃO, e só ela.** Mesmo código, mesma duração mediana de Short (20,3 s no ES e
no PT), mesmos temas:

| canal | retenção do Short | tempo médio | views medianas |
|---|---|---|---|
| es | **103,5%** (loop) | 22 s | 846 |
| stoic | **90,0%** | 16 s | 486 |
| pt | 53,2% | 11 s | 42 |
| astucia | 29,7% | 6 s | 26 |

Abaixo de ~70% o YouTube não impulsiona. O PT **nasceu** em ~50% — nunca foi punido, nunca decolou.

Três hipóteses caem com dado:
- **Não é o tema.** O pt é a réplica bíblica exata e faz 1/18; o stoic não tem Bíblia e retém 90%.
- **Não é o idioma.** poder e astucia são ES e retiveram 30%.
- **Não é frequência.** O corte do PT de 4/dia para 1/dia (15/08) **não mexeu na retenção**:
  57,8% (sem 32) → 51,0% (sem 33) → 41,9% (sem 34). A régua de 15/09 já pode ser decidida.

O que os dois vencedores têm em comum: **texto clássico contemplativo, narrado em espanhol, sem
interpretação, em ciclo fechado**. Os que falharam em ES tinham camada autoral (citação +
aplicação) — vira conselho, o espectador ouve e sai.

**O achado que muda a decisão do PT:** separando formato, em 60 dias —

| | vídeos | views | horas assistidas | min/view |
|---|---|---|---|---|
| es shorts | 96 | 73.586 | 166,6 h | 0,14 |
| es **longos** | 33 | 1.492 | **171,7 h** | 6,9 |
| pt shorts | 81 | 7.085 | 8,2 h | 0,07 |
| pt **longos** | 30 | 1.374 | **125,8 h** | 5,5 |

**O longo em PT rende quase o mesmo que o longo em ES.** 94% do watch time do canal PT vem dos
longos, e 14,2% do tráfego dele entra por vídeo relacionado com sessão de 5 min. Desligar o PT
seria jogar fora ~765 h/ano de exibição por causa do Short, que é 6% do tempo assistido dele.
O PT também converte MAIS inscrito por view que o ES (9,2 vs 3,9 por mil).

Monetização: **Short não conta hora de exibição**. Os 73 mil views de Shorts do ES valem zero no
portão. A trilha real é o longo — ES projeta ~1.045 h/ano contra 4.000 h necessárias, e o que
falta é **views por longo** (capa/título/busca), não mais render. Inscritos do ES: +5,8/dia →
mil por volta de 18/12/2026.

⚠ **Queda do ES em 17-20/08 e o rebrand.** Views/dia: 2.512 (16/08) → 789 → 618 → 510 (19/08),
recuperando para ~1.600 e ~2.300 em 21 e 22. Coincide com a capa nova, o `defaultLanguage` e o
handle (19 e 20/08). A retenção dos vídeos da mesma semana continuou em 116,8% — não foi o
conteúdo. Não é prova de causa, mas **a troca de NOME que ficou pendente deve continuar pendente**:
não há ganho mensurável e há risco medido.

Encaminhamento recomendado (nada foi executado):
1. Escalar a **Noche Estoica** para 2-3 Shorts/dia — retém 90% publicando 1/dia; teste mais barato da casa.
2. Canal ES novo com corpus diferente e o MESMO formato (Provérbios/Eclesiastes, orações narradas).
3. PT vira canal de **longo**; no máximo 1 Short como isca. Não desligar em 15/09.
4. Se ainda quiser insistir no Short em PT, o único teste que ataca a causa é **trocar a voz**
   (`pt-BR-AntonioNeural` está queimada no Brasil) e cortar para ≤15 s — a única faixa em que o
   PT ainda retém 82%.

## O corte de 15/08 — a medição que mandou

Feita pela API, coorte de 2-7 dias:

- **pt**: mediana caiu 95 → 41 → 25 em três semanas com o **mesmo** conteúdo que faz 850 no ES.
  73 views/vídeo publicando 4/dia, contra 438 da Noche Estoica publicando 1/dia. Hipótese:
  saturação de frequência. **Rever em 15/09** — se a mediana não subir, desligar.
- **poder** e **astucia**: abaixo da régua, desligados.

Régua dos canais em Protocolo Fantasma: **mediana ≥ 300 views/Short em 30 dias** mantém e escala.

## Onde o canal ES está para monetizar — conferido em 22/08

Pergunta do Diego: *"o canal está elegível quando atingir o número?"* Ninguém pode **confirmar**
elegibilidade — quem decide é a revisão humana do YouTube, e ela olha o canal inteiro. O que dá
para dizer é onde ele está em cada portão, com número.

**Portão A (volume) — falta, e o gargalo é hora, não inscrito.**

| | hoje | meta | ritmo |
|---|---|---|---|
| Inscritos | 314 | 1.000 | +5,8/dia → **~18/12/2026** |
| Horas (só longos contam) | 171,7 h em 60 d | 4.000 h/12 meses | **~1.045 h/ano — falta 4×** |

Os 73.586 views de Shorts valem **zero** aqui. E a trilha alternativa (10 mi de views de Shorts
em 90 dias) exige 111 mil/dia; o canal faz ~1.800. Está fora.

**Portão B (formato) — coberto no Short, meio coberto no longo.**

- **Shorts: 103 de 103 têm camada autoral** (nota factual sobre o texto). Cobertos.
- **Longos: 18 de 35 têm abertura falada**, e todos os 18 são de 05/08 em diante. Os **17
  anteriores são leitura crua sobre fundo estático** — exatamente o que a política descreve como
  inelegível ("readings of other materials you did not originally create", "image slideshows...
  with minimal or no narrative").

⚠ **E aqui está a decisão desagradável, com o número medido**: os 17 longos de leitura crua valem
**50% de todas as horas de longo do canal** (86,6 h contra 85,0 h dos novos). Deixá-los não
listados antes de submeter limpa o acervo — e **corta metade da trilha de horas**. Não há como
ter as duas coisas. No canal PT o mesmo cálculo dá 27%, bem mais barato de limpar.

Nada foi feito quanto a isso em 22/08: é decisão do Diego, e mexer no acervo do ES contraria a
ordem de não tocar no canal.

## O muro que vale para todos: monetização tem dois portões

- **Portão A (volume)**: 1.000 inscritos + 4.000 h em 12 meses **OU** 1.000 inscritos + 10 mi
  de views de Shorts em 90 dias. As trilhas não somam. **Hora de exibição só vem de vídeo
  longo** — canal sem longo não tem essa trilha, e a de Shorts exige ~111 mil views/dia (o
  melhor canal da casa faz ~1.800/dia).
- **Portão B (formato)**: a política lista como inelegível *"readings of other materials you
  did not originally create"*. **Domínio público resolve copyright, não monetização.** Os
  bíblicos e o estoico estão hoje nesse formato. `poder` e `astucia` passavam por causa da
  camada autoral.

Detalhe em `Palavra-Viva-3x/ESTRATEGIA-MONETIZACAO.md`.

## O motor tem prazo de validade? — resposta de 22/08

Não pára sozinho por desgaste, mas **também não é perpétuo**. São cinco relógios, e só um deles
é realmente curto:

| Relógio | Estado em 22/08 | Quem resolve |
|---|---|---|
| **Poço de temas** ⏳ | bíblico **21 dias**, estoico **14 dias** | escrita à mão — é o único que **acaba de verdade** |
| Token OAuth | precisa do app **em produção**; fora dela o refresh morre em 7 dias | uma vez, no Cloud |
| Cota da API | ES ~7.200/10.000; estoico ~5.150/10.000 com 3 Shorts | teto, não relógio |
| Actions | repo público = minutos ilimitados | — |
| edge-tts e Wikimedia | dependências externas sem contrato | risco, não prazo |

**O poço é o prazo de validade.** Cada tema é um dia; escrevê-los é trabalho de escrita humana
(refs válidas, títulos nos idiomas do canal, consultas de imagem em pares concretos, camada
autoral, abertura do longo). Um canal com poço vazio para no dia seguinte, em silêncio —
foi o que quase aconteceu com a Noche Estoica em 23/08.

Regra prática: **repor quando o vigia avisar (5 dias), não quando zerar.** O aviso dá 5 dias e
encher leva uma sessão. Chegar a 4 dias, como em 17/08, é tarde demais para uma semana ruim.

As duas correções de 22/08 (vigia por linha + alarme de fila por linha) existem para que esse
aviso chegue de **todos** os poços, e não só do bíblico.

## As vozes — uma por canal, de propósito

Nenhum canal usa a voz de outro: duas vozes iguais na mesma conta é assinatura de fábrica.

| Canal | Voz (edge-tts) |
|---|---|
| Palabra Viva (ES) | `es-MX-JorgeNeural` |
| La Noche Estoica (ES) | `es-US-AlonsoNeural` |
| El Poder Crudo (ES, desligado) | `es-CO-GonzaloNeural` |
| Astucia Fría (ES, migrado) | `es-AR-TomasNeural` |
| Palavra Viva Diária (PT) | `pt-BR-AntonioNeural` |
| Living Word Daily (EN, desligado) | `en-US-ChristopherNeural` |
| Sabiduría (ES, preparado) | **`es-MX-DaliaNeural` — feminina** |

Todas as seis em uso são masculinas. A do canal novo é a primeira feminina da casa, e serve
também como o teste de voz que ficou pendente no canal PT — onde `pt-BR-Antonio` é a voz que o
Diego já reprovou no Psicologia Fria e que o brasileiro ouve em toda parte.

## Armadilhas que já custaram caro

- **O cron "horário" do GitHub não é horário** — medido: intervalos de 2 a 2,5 h.
  `hora_short_utc` garante "não antes de", não horário fixo.
- **Nunca cron esparso**: cron horário + janela no `state.json`, senão o atraso do GitHub pula
  o slot (o Corte em Pauta postava de 12 em 12 h achando que era 6).
- **`state.json` e `fila/` são versionados de propósito** — o runner é descartável.
- **App OAuth tem de estar em produção**, senão o refresh token morre em 7 dias.
- Cada canal tem projeto Google Cloud **próprio** (quota de 10 mil/dia não é dividida).
- **Sêneca em ES é proibido**: a única tradução em domínio público não está transcrita, e as
  Cartas do Wikisource são tradução moderna. **Sun Tzu em ES também não existe** limpo.
- Nome de autor clássico não tem demanda: o corpus é Gracián, a embalagem é "cómo leer a las
  personas". Nunca embalar pelo autor.

## Ao terminar a sessão

Atualizar este arquivo (o que ligou, o que desligou, que medição mandou) e o `CLAUDE.md` da
pasta que foi mexida. Commitar e dar push no repo do projeto.
