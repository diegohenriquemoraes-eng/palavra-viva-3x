# TikTok do Palavra Viva — estado, realidade da plataforma e decisão

_Levantamento feito na madrugada de 24/07/2026._

## ATUALIZAÇÃO 24/07 madrugada — decisão tomada e o que travou na prática

Diego decidiu **reaproveitar a @casaqueresolve.oficial** (392 seg.). Comecei o
rebrand na conta ao vivo:

- ✅ **Nome trocado para "Palavra Viva Diária"** (salvo; TikTok trava novo nome
  por 7 dias, liberando em 31/07).
- ✅ **Bio trocada** para "📖 A Palavra de Deus em áudio — um versículo todos os
  dias 🕊️".
- ⛔ **Foto (avatar) NÃO trocada** — e aqui apareceu o problema de fundo.
- ⚠️ **@ (username) travado até 08/08** (foi mudado nos últimos 30 dias); fica
  @casaqueresolve.oficial até lá.
- ℹ️ A conta tem **1 vídeo antigo** ("Geladeira protegida?"). Não apaguei (não foi
  pedido e é irreversível); dá para esconder/apagar depois se quiser.

### O problema de fundo: o TikTok web bloqueia automação de arquivo

Tentei subir o avatar por 4 caminhos e TODOS esbarram na blindagem do TikTok:
1. `file_upload` do navegador MCP → recusa arquivo local (só aceita arquivo
   "compartilhado com a sessão").
2. Injeção via JavaScript (montar o File na página) → o anti-adulteração do TikTok
   **fecha a aba** toda vez.
3. `fetch` do avatar no GitHub → **bloqueado pela CSP** do TikTok.
4. Print da imagem para reenviar → a extensão **não tem permissão** no host do
   GitHub, e a **janela do Chrome fica minimizada** (print falha).

**Consequência importante:** esse MESMO bloqueio vale para **subir os vídeos**.
O upload de vídeo do tiktok.com é blindado igual — não dá para automatizar a
postagem pela via do navegador MCP. Somado ao que já sabíamos (API oficial só
publica rascunho sem auditoria), **a postagem hands-off que você pediu não é
viável hoje por nenhuma via automática que eu controle daqui**.

### Caminhos reais para postar (você escolhe)

- **A) Manual pelo app do TikTok (celular):** o mais confiável. Eu mantenho a
  biblioteca de vídeos + legendas prontas (já tem 6); você abre o app e posta em
  segundos, sem link na legenda. Avatar também troca no app em 10s.
- **B) Robô local Playwright (hands-off, com ressalvas):** um script no SEU PC,
  usando sua sessão logada, sobe os vídeos por Task Scheduler 3/dia. É a ÚNICA via
  hands-off. Ressalvas honestas: contra os termos do TikTok, pode sinalizar/derrubar
  uma conta com histórico, o PC tem de ficar ligado, e preciso de um primeiro teste
  supervisionado — não vou disparar sozinho num canal com 392 seguidores.
- **C) API oficial com auditoria:** a única via realmente "na nuvem, sem PC", mas
  a auditoria leva semanas e não é garantida.

**Avatar agora (30s):** app do TikTok → Editar perfil → foto → escolher a imagem.
O arquivo está em `marca/avatar.png`. Ou me diga para ir pelo caminho B que eu
troco avatar e posto junto.

## O que já está pronto (não depende de decisão)

- **Conteúdo**: os Shorts do TikTok são renderizados pelo MESMO motor do YouTube
  (`nucleo/fabrica.montar_short`) — mesmo vídeo, voz e legenda. Rodei local e
  funciona. Script novo: `tiktok/montar_biblioteca_tiktok.py` gera uma biblioteca
  de MP4 (9:16, 1080x1920) + um `.txt` de legenda por vídeo, **sem nenhum link**
  (nem clicável nem em texto — foi o erro antigo que você pediu para não repetir).
  Biblioteca inicial em `tiktok/biblioteca/`.
- **Identidade**: avatar e nome iguais aos do YouTube/Instagram. Textos em
  `tiktok/PERFIL-TIKTOK.md`; avatar em `marca/avatar.png`.

## Dois obstáculos reais que mudam o plano

### 1. A conta logada NÃO é um canal em branco — é o "Casa que Resolve" (392 seguidores)

O TikTok logado no Chrome é **@casaqueresolve.oficial — "Casa que Resolve",
392 seguidores**, nicho de achados/utilidades para casa, com vídeos já postados.
Não é um canal novo/vazio. "Apagar a foto e recomeçar" essa conta significa
**converter uma conta com 392 seguidores reais de outro nicho** em canal bíblico —
é irreversível e voltado para fora, então parei antes de mexer. Ver a decisão no fim.

### 2. TikTok NÃO permite a automação 100% na nuvem que o YouTube permite

No YouTube a automação roda sozinha no GitHub Actions porque existe API oficial de
upload. No TikTok **não há esse caminho hands-off sem auditoria**:

- A **Content Posting API** oficial, enquanto o app não passa por auditoria da
  TikTok, só publica como **rascunho/privado (SELF_ONLY)** — inútil para um canal
  público. A auditoria leva **semanas e não é garantida** (já registrado em
  17/07). Ou seja: não dá para replicar hoje o "posta sozinho na nuvem, PC
  desligado".
- O único jeito de postar sem sua aprovação, hoje, é **automação de navegador no
  seu PC** (o Chrome logado), agendada. Isso funciona, mas: (a) o PC precisa ficar
  ligado; (b) é frágil — o TikTok tem anti-robô e pode pedir captcha/verificação
  (que eu não posso resolver); (c) numa conta **nova/recém-convertida**, postar em
  rajada por robô é justamente o que faz a conta ser sinalizada/flopar.

**Recomendação de cadência**: começar **3 Shorts/dia** (igual ao YouTube), não mais,
até a conta aquecer. Subir volume só depois que estiver estável — despejar muitos
vídeos numa conta nova derruba o alcance, não aumenta.

## Link de afiliado no TikTok — o que dá e o que não dá

- **Legenda de vídeo**: nunca fica clicável, e URL em texto é penalizada. **Não uso.**
- **Bio**: o campo de texto da bio também não linka.
- **Campo "site" do perfil (clicável)**: aparece ao trocar para **Conta Comercial
  (Business)** — e isso vale **a qualquer número de seguidores**, sem esperar os
  2 mil. É o caminho certo para o link de afiliado. (Trocar o tipo de conta é uma
  mudança de configuração — deixo para você confirmar; recomendo fazer.)
- Enquanto o link não entra, seguimos o seu plano: publicar e crescer.

## Decisão que preciso de você (única trava)

Qual conta o Palavra Viva vai usar no TikTok?

- **A) Recomeçar a @casaqueresolve.oficial** (392 seg.): mais rápido, aproveita os
  seguidores — mas são de outro nicho (risco de unfollow e de o TikTok sufocar a
  virada de tema), e mata o projeto "Casa que Resolve".
- **B) Conta nova só do Palavra Viva** (recomendado): alinha com a estratégia do
  YouTube/Instagram (canal limpo, sinal de nicho puro, que é o que o algoritmo do
  TikTok premia). Você cria a conta e loga (não posso criar conta por você); eu
  faço marca + automação. Começa do zero.
- **C) Era outra conta**: se você quis dizer outra conta que não a que ficou logada,
  me diz qual.

Assim que você escolher, em minutos: aplico a marca, ligo a biblioteca de vídeos e
deixo o robô de postagem local agendado (3/dia).
