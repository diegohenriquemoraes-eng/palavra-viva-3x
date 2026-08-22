# Canais — painel único, estado em 17/08/2026

> Ponto de partida de qualquer sessão sobre canais. Este arquivo diz **o que está no ar, onde
> mora e o que está esperando decisão**. O detalhe técnico de cada motor está no `CLAUDE.md`
> da pasta correspondente — abrir só depois de saber por qual passar.

## Quem publica hoje

| Canal | Plataforma | Ritmo | Motor (pasta) | Conta |
|---|---|---|---|---|
| **Palabra Viva Cortes** `@PalabraVivaEnAudio` (handle já trocado em 20/08; o NOME ainda é "Cortes" — YouTube recusou por política, ver CLAUDE.md) | YouTube ES | 3 Shorts + 1 longo/dia | `Palavra-Viva-3x` | Gmail pessoal |
| **Palavra Viva Diária** `@PalavraVivaDiária-biblia` | YouTube PT | **1 Short + 1 longo/dia** (cortado 15/08) | `Palavra-Viva-3x` | Gmail pessoal |
| **La Noche Estoica** `@LaNocheEstoica` | YouTube ES | 1 Short/dia, 01 UTC | `Palavra-Viva-3x` | Gmail pessoal |
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
