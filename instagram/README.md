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

A conta é **nova** (perfil reaproveitado, ~14 seguidores). Em conta fria, o
erro clássico é despejar 10 posts/dia logo de cara: o Instagram de 2026 mede
**qualidade de engajamento** (watch-through, salvamentos, compartilhamentos,
comentários), e volume alto com engajamento baixo faz o alcance DESPENCAR — o
oposto de "não flopar". Por isso a conta **aquece**:

| Fase | Reels/dia |
|---|---|
| Dias 1–7   | 3 |
| Dias 8–14  | 5 |
| Dias 15–21 | 7 |
| Dia 22+    | 8 |

- **Teto real da API**: a Graph API permite ~25 publicações/24h por conta
  (Reels contam no mesmo balde). Estamos muito abaixo — o limite aqui é a
  **saúde do algoritmo**, não a cota.
- **8/dia** é o teto recomendado para conta aquecida e sem rosto. Dá para
  chegar a 10, mas acima disso o risco de o feed marcar a conta como
  "produtora de filler" cresce mais que o alcance ganho.
- Tudo é **trivialmente ajustável** em `config.json` (`agenda_rampa`). Para ir
  direto a mais, é só editar e dar push — mas o recomendado é deixar a rampa
  correr.

Os posts são espalhados pela **janela 11h–02h UTC** (≈ 08h–23h de Brasília,
quando o público brasileiro está ativo), com intervalo mínimo entre eles.

## O único passo humano: ligar a API (uma vez)

Igual ao token do YouTube, a publicação automática precisa de credenciais que
só você pode gerar (exigem consentimento e login). Sem elas o pipeline já roda,
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
