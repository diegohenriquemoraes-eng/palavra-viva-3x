# Canal PT — o que o Diego precisa fazer (5 min)

O canal em português é a única peça que eu não consigo criar sozinho: criação
de canal e consentimento OAuth exigem clique humano. Tudo o mais (logo, banner,
projeto Cloud, secrets, automação) eu faço depois.

## Passo 1 — criar o canal (2 min)

1. Chrome logado em **diegohenriquemoraes@gmail.com** (a conta dos outros dois
   canais — não a perffec).
2. Abrir <https://www.youtube.com/account> → **"Crie um canal"**.
3. Nome: **Palavra Viva Diária**
   Identificador: **@PalavraVivaDiaria**
   (se estiver ocupado, tentar `@PalavraVivaDiariaBiblia`; me avisar qual ficou)
4. Pronto. Não precisa mexer em foto nem banner — eu aplico.

## Passo 2 — me avisar

Digo "canal PT criado" e eu sigo com:
- logo e banner (`marca/avatar.png` e `marca/banner-pt.png`, já prontos);
- projeto Google Cloud novo (quota própria de 10.000/dia, separada dos outros);
- app OAuth **publicado em produção** (se ficar em teste, o token morre em 7 dias).

## Passo 3 — clicar o consentimento (1 min)

Vou rodar a autorização e abrir uma tela do Google no navegador. Você:
1. escolhe a conta `diegohenriquemoraes@gmail.com`;
2. seleciona o canal **Palavra Viva Diária** (a tela pergunta qual canal);
3. clica "Continuar" nos avisos de app não verificado (é o nosso próprio app).

Depois disso eu guardo o token nos Secrets do repo, ativo `pt` no
`publicador/config.json` e o canal entra no ar publicando sozinho — 1 vídeo
longo às 18h de Brasília + 4 Shorts espalhados no dia, exatamente o mesmo
conteúdo dos canais ES e EN.

## Por que o canal PT publica em horário diferente

`hora_longo_utc` é 23 (ES), 22 (EN) e 21 (PT) para os três longos não
renderizarem na mesma execução do runner — cada longo leva ~15 min de máquina.
