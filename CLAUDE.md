# Palavra Viva 3x — 1 pipeline, 3 canais bíblicos (ES / EN / PT)

O MESMO conteúdo diário (1 vídeo longo + 4 Shorts) publicado em três canais,
cada um com áudio TTS, legenda queimada, título, descrição e thumbnail no seu
idioma. Custo zero, 100% na nuvem (GitHub Actions), sem PC e sem intervenção.
Sucessor do pipeline do Palabra Viva (repo `palabra-viva`, hoje aposentado).

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
| playlist, channels.list, polling de processamento | ~90–230 |
| **total** | **~6.800 de 10.000** |

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
3. Imagens só CC0/domínio público (Openverse), resolvidas no pacote; qualquer
   falha cai no gradiente da casa. Nunca imagem de banco pago/"grátis com
   atribuição obrigatória" sem gravar a atribuição.
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

## Qualidade do conteúdo — decisões que já custaram um vídeo ruim

- **Short curto demais**: versículo único (Salmo 4:8) rendia 9s, fino para
  reter. Abaixo de `MIN_SHORT_S` (15s) o texto é narrado **duas vezes** com
  pausa — formato consagrado do nicho (repetição para meditar), não
  enchimento. Ver `nucleo/fabrica.py::montar_short`.
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

## Poço seco

Workflow abre issue quando `temas.json` esgota. Adicionar temas novos (mesmo
formato: refs canônicas em inglês scrollmapper, títulos ≤100 chars nos 3
idiomas, consultas de imagem em inglês) e dar push. Validar com
`python produzir\reabastecer.py --dry-run` antes.
