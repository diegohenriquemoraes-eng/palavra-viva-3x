# Robô de postagem no TikTok — como ligar (Palavra Viva Diária)

Posta 1 Short bíblico por vez, sem link na legenda, 3x/dia, sozinho.
**Só falta 3 passos seus** (o código está pronto). Faça na ordem.

> Aviso honesto: automatizar postagem é contra os termos do TikTok e pode, no
> pior caso, sinalizar/derrubar a conta (que tem 392 seguidores). Cadência baixa
> (3/dia) e legenda “humana” reduzem o risco, mas não zeram. Por isso o 1º teste
> é supervisionado (`--dry-run`) antes de qualquer coisa no automático.

## Passo 1 — Logar 1 vez no navegador do robô
Abre uma janela do Chrome do Playwright para VOCÊ logar (QR pelo celular é o
mais fácil). A sessão fica salva e o robô reusa depois.

```powershell
cd C:\Users\NOTE\Desktop\Projetos\Palavra-Viva-3x
python tiktok\poster\poster.py --login
```
Logou e o feed apareceu? Pode fechar. (Eu não faço esse passo: login/senha e
captcha são coisa sua, não minha.)

## Passo 2 — Teste seguro (NÃO publica)
Faz tudo — abre o upload, joga o vídeo, escreve a legenda, acha o botão — mas
**não clica em Publicar**. É aqui que a gente confere se os seletores do TikTok
ainda batem.

```powershell
python tiktok\poster\poster.py --dry-run
```
Olhe o fim de `tiktok\poster\poster.log`. Se disser `[dry-run] fluxo completo sem
erro`, está pronto. Se aparecer `[ERRO] não achei ...`, me manda a linha que eu
ajusto o seletor.

## Passo 3 — Agendar 3x/dia
```powershell
powershell -ExecutionPolicy Bypass -File tiktok\poster\agendar.ps1
```
Cria as tarefas de 09:00, 14:00 e 19:00. **O PC tem de ficar ligado** nesses
horários. Enquanto não confiar 100%, deixe o `--dry-run` ligado dentro de
`rodar.ps1` (última linha) e olhe os logs por uns dias.

## Peças
- `poster.py` — o robô (login / dry-run / postar 1).
- `rodar.ps1` — reabastece a biblioteca se estiver acabando e posta 1.
- `agendar.ps1` — cria/atualiza as 3 tarefas diárias.
- `perfil_chrome/` — sessão logada (NÃO versionar, NÃO compartilhar).
- `../biblioteca/fila.json` — a fila; `publicado:true` já foi ao ar.

## Link de afiliado (quando quiser)
Nunca vai na legenda. O clicável é o **campo “site” da bio**, que libera ao trocar
a conta para **Comercial** (Configurações → Gerenciar conta) — a qualquer número
de seguidores. Aí aponta para um destino com os links da Shopee.
