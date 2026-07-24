# Palavra Viva Diária — Reels no Instagram (automático)

Mesmo conteúdo bíblico do canal do YouTube, agora como **Reels** no perfil
**@palavravivadiaria.biblia**. Um Reel de versículo (1080×1920, voz TTS,
legenda queimada, fundo da casa) publicado sozinho pelo GitHub Actions, sem PC
e sem intervenção — igual ao pipeline dos 3 canais do YouTube.

Reaproveita o núcleo (`nucleo/`): mesma Bíblia Livre (domínio público), mesma
voz `pt-BR-Antonio`, mesma legenda e os mesmos fundos curados. A regra
editorial é a mesma e inegociável (só texto bíblico em domínio público, sem
pregação, imagem CC0/PD ou gradiente, sem música de terceiros).

## Frequência — por que começa em 3/dia e sobe até 8

A conta é **nova** (perfil reaproveitado, ~14 seguidores). **Volume não é o
gargalo — qualidade é.** O Instagram de 2026 mede engajamento (watch-through,
salvamentos, compartilhamentos), e conta fria postando muito com engajamento
baixo faz o alcance DESPENCAR. Pesquisa (24/07): 3–5 Reels/semana já cresce;
3/dia é o teto seguro de conta nova; **melhor 3–4 Reels BONS que 8 medíocres.**

| Fase | Reels/dia |
|---|---|
| Dias 1–10 | 3 |
| Dia 11+   | 4 |

- **Teto técnico (bloqueio):** a API oficial permite ~**100/24h** (Reels+Stories
  no mesmo balde), com afunilamento relatado a partir de ~50. Como publicamos
  pela API oficial (não por bot de like/follow), risco de *ban* é baixo — o que
  causa shadowban é automação de ENGAJAMENTO, não volume de posts.
- **Teto estratégico:** ~4/dia. Dobrar o volume com Reel fraco divide o alcance,
  não soma seguidores. Ajustável em `config.json` (`agenda_rampa`).

## Qualidade — o gancho é a maior alavanca

50% decidem em 1,7s; o hold dos 3 primeiros segundos separa Reel que alcança
5–10× do que morre. Por isso cada Reel abre com um **GANCHO falado+escrito no
1º segundo** (`GANCHOS_VIDEO` em `reels.py`) ANTES do conteúdo, e **sem abertura
no preto** (`fade_in=0` no `render_short`) — o 1º frame já é o gancho.

**Formatos giram por post** (história e oração puxam save/share mais que
versículo solto — o que mais faz o perfil crescer). Rotação determinística
`TEMPLATE_FORMATOS` no `publicar_ig.py` — 7 slots: 5 versículos, 1 oração,
1 história:

| Formato | Banco | O quê |
|---|---|---|
| versículo | `versiculos.json` | gancho + versículo (Bíblia Livre) |
| história | `historias.json` | gancho narrativo ("Davi era pequeno, Golias um gigante") + passagem do clímax (Bíblia Livre); capa com o nome da história |
| oração | `oracoes.json` | oração curta ORIGINAL nossa (texto próprio, sem copyright — leve relaxamento da regra "só texto bíblico", combinado, para crescer) |

Para adicionar história/oração: editar o JSON (histórias precisam de `ref`
válida na Bíblia Livre — validar como os versículos).

Os posts são espalhados pela **janela 11h–02h UTC** (≈ 08h–23h de Brasília,
quando o público brasileiro está ativo), com intervalo mínimo entre eles.

## Estado: NO AR desde 24/07/2026

App Meta **Palavra Viva Reels** (id 1717198369563451) com "API com login do
Instagram", conta @palavravivadiaria.biblia como Testadora do Instagram,
token de longa duração (60d) com `instagram_business_content_publish`. Secrets
`IG_USER_ID` (28170980895840901, o id de `graph.instagram.com/me`) e
`IG_ACCESS_TOKEN` gravados. 1º Reel publicado no teste: Salmo 23:1-4.

> **Endpoint:** como é *login do Instagram*, o pipeline usa **graph.instagram.com**
> (não graph.facebook.com) e o IG_USER_ID é o id de `/me` (28170...), não o
> número que o painel mostra (17841...). Cota de publicação medida: 100/24h.

## Como foi ligado (referência, caso precise refazer)

Igual ao token do YouTube, a publicação automática precisa de credenciais que
só o dono pode gerar (exigem consentimento e login). Sem elas o pipeline roda
mas **renderiza e não publica** — some os vídeos, sem tocar na conta.

1. **Conta profissional** (pré-requisito da API): no app do Instagram →
   Configurações → Tipo de conta → mudar para **Criador** (ou Empresa).
   *(No perfil @palavravivadiaria.biblia — se ainda não estiver profissional.)*
2. **App na Meta**: em <https://developers.facebook.com/apps> → Criar app →
   tipo **Business** → adicionar o produto **Instagram** → **API com login do
   Instagram** (*Instagram API with Instagram Login* — não precisa de Página do
   Facebook).
3. Em *Instagram → Configuração da API com login do Instagram*, adicione a
   conta como usuária de teste e **gere um token de acesso** com os escopos
   `instagram_business_basic` e `instagram_business_content_publish`. Troque-o
   por um **token de longa duração** (60 dias) — o botão fica na mesma tela, ou
   via `GET /access_token?grant_type=ig_exchange_token`.
4. **Pegue o `IG_USER_ID`** (id numérico da conta): `GET
   https://graph.instagram.com/me?fields=id,username&access_token=SEU_TOKEN`.
5. **Cadastre os secrets** no repositório (Settings → Secrets and variables →
   Actions):
   - `IG_USER_ID` = o id numérico
   - `IG_ACCESS_TOKEN` = o token de longa duração

Pronto: no próximo disparo de hora cheia (dentro da janela) o primeiro Reel sai
sozinho.

### Token expira em 60 dias

Rode a cada ~50 dias, com o token atual no ambiente:

```bash
IG_ACCESS_TOKEN=<token atual> python instagram/refresh_token.py
```

Ele imprime o token novo (ou atualiza o secret sozinho se você definir um PAT
em `REPO_PAT`). **Sem validade**: um token de *System User* de um Portfólio
Comercial nunca expira — se criar um, esqueça esse passo.

## Testar sem esperar o cron

Em **Actions → Instagram Reels → Run workflow**:

- `render_apenas = true` → renderiza um Reel e a caption em `saida/instagram/`
  (não precisa de token; bom para ver o vídeo).
- `forcar = true` → ignora a agenda e **publica agora** (precisa dos secrets).
- `dry_run = true` → só diz o que faria.

Local (sem publicar):

```bash
python instagram/publicar_ig.py --render-apenas --forcar
```

## Como funciona por dentro

| Peça | O quê |
|---|---|
| `versiculos.json` | Banco de 111 referências populares (validadas na Bíblia Livre); giram sem repetir pelo ponteiro no estado |
| `reels.py` | Renderiza o Reel 9:16 (reusa `nucleo/`: TTS, legenda, fundo, render de Short) |
| `legenda.py` | Monta a caption no estilo de canal *dark*: gancho, versículo, micro-CTA de engajamento, ponte para a bio e hashtags que giram |
| `publicar_ig.py` | Decide o que é devido, renderiza, hospeda o MP4 como **asset de Release** (URL pública que o Instagram baixa) e publica pela Graph API (container REELS → espera processar → `media_publish`) |
| `config.json` / `state.json` | Agenda (rampa, janela, intervalo) e memória entre execuções |

O **link de afiliado** (os mesmos produtos da Shopee do canal PT) vive na
**bio** — link em legenda do Instagram não é clicável. A caption sempre aponta
para a bio.
