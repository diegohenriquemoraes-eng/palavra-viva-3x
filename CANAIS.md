# Canais — painel único, estado em 15/08/2026

> Ponto de partida de qualquer sessão sobre canais. Este arquivo diz **o que está no ar, onde
> mora e o que está esperando decisão**. O detalhe técnico de cada motor está no `CLAUDE.md`
> da pasta correspondente — abrir só depois de saber por qual passar.

## Quem publica hoje

| Canal | Plataforma | Ritmo | Motor (pasta) | Conta |
|---|---|---|---|---|
| **Palabra Viva Cortes** `@PalabraVivaCortes` | YouTube ES | 3 Shorts + 1 longo/dia | `Palavra-Viva-3x` | Gmail pessoal |
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
