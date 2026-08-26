# Estratégia de monetização dos 5 canais

_Escrito em 04/08/2026, a pedido do Diego ("quero todos os meus canais
elegíveis para monetização"). Políticas conferidas na fonte oficial, não em
blog. Números medidos pela API no mesmo dia._

---

## 1. Os dois portões, que são independentes

O YouTube tem **dois portões separados**, e falhar em qualquer um deles impede
a monetização. A maior parte da confusão vem de tratá-los como um só.

**Portão A — VOLUME.** É o requisito de entrada no YPP
(`support.google.com/youtube/answer/72851`):

- 1.000 inscritos **+ 4.000 horas** públicas válidas em 12 meses, **ou**
- 1.000 inscritos **+ 10 milhões** de views de Shorts em 90 dias.

As duas trilhas **não somam**. Além disso: sem strikes, verificação em duas
etapas ligada e conta AdSense vinculada.

**Portão B — FORMATO.** É a política de monetização
(`support.google.com/youtube/answer/1311392`). Lista como **inelegível**:

> "Content that exclusively features readings of other materials you did not
> originally create" · "Image slideshows, templated storylines, or scrolling
> text with minimal or no narrative, commentary, or educational value"

Critério de aprovação: haver *"meaningful difference"* entre a fonte e o vídeo,
e o conteúdo entregar "creative, educational or other value".

**Domínio público resolve COPYRIGHT. Não resolve nenhum dos dois portões.**

**O que NÃO é problema (conferido, para não gastarmos energia à toa):**
divulgação de IA. A política de conteúdo sintético
(`answer/14328491`) exige a marcação para mídia **realista e enganosa** —
fazer pessoa real dizer o que não disse, alterar evento real. Ela lista
explicitamente **narração com voz sintética como isenta**. Nosso formato não
precisa da etiqueta.

---

## 2. Onde cada canal está hoje (medido em 04/08)

| Canal | Inscritos | Falta p/ 1.000 | Horas (12m) | Falta p/ 4.000h | Portão B |
|---|---|---|---|---|---|
| Palabra Viva Cortes (es) | 205 | 795 | **145** | 3.855 | Shorts ✔ · longo ✗ |
| Palavra Viva Diária (pt) | 65 | 935 | **26** | 3.974 | Shorts ✔ · longo ✗ |
| La Noche Estoica | 5 | 995 | — | — | Shorts ✔ · **sem longo** |
| El Poder Crudo | 2 | 998 | — | — | Shorts ✔ · **sem longo** |
| Astucia Fría | 2 | 998 | — | — | Shorts ✔ · **sem longo** |

---

## 3. A conclusão que reordena tudo

### 3.1 Três dos cinco canais, hoje, NÃO TÊM CAMINHO para monetizar

La Noche Estoica, El Poder Crudo e Astucia Fría rodam o Protocolo Fantasma
puro: **1 Short/dia, sem vídeo longo**. Isso os tranca fora dos dois caminhos:

- **Trilha de horas**: sem vídeo longo, não existe hora de exibição. Short não
  conta para as 4.000 horas.
- **Trilha de Shorts**: exige 10 milhões de views em 90 dias, ou seja
  **111.000 views/dia**. O melhor canal da casa faz ~1.800/dia. Fator 60x.

Não é pessimismo, é aritmética. **Enquanto forem só Shorts, esses três canais
podem crescer para sempre sem nunca monetizar.** O Short é motor de inscritos;
quem entrega hora é o longo.

Isso não invalida o método — o fantasma é protocolo de **largada**, para o
canal não ser lido como spam nos primeiros 30 dias. Mas ele tem data para
acabar, e o que vem depois precisa incluir o longo.

### 3.2 Nos dois bíblicos, o gargalo não é o formato — é ninguém achar o longo

O ES tem 145 horas em 12 meses. Para 4.000 horas seriam necessários ~10.000
views de vídeo de 1h com 40% de retenção. Os longos publicados fazem entre
0 e 41 views cada.

**A duração média de visualização do ES é 34 segundos.** Isso diz tudo: o canal
inteiro é consumido como Short. O longo existe, é publicado todo dia, e não é
encontrado por ninguém.

Short é achado no **feed** — gancho e retenção mandam, SEO é irrelevante.
Longo é achado na **busca** — título, tags e descrição são tudo. Hoje as tags
são **16 fixas por idioma**, iguais para os 26 temas, e o título vem escrito à
mão. Isso é jogar fora a única alavanca que o longo tem. Já estava diagnosticado
em `ESTRATEGIA-FANTASMA.md` §1.6 e nunca foi feito.

---

## 4. O plano, em ordem de impacto

### Passo 1 — Poço bíblico (URGENTE, tem prazo)

Restam **7 temas livres, e os sete são "salmos para dormir"**. Em 7 dias os
dois canais param; antes disso publicam uma semana do mesmo formato, que é
literalmente o que a política chama de repetitivo.

Escrever temas novos com variedade real (`tema` e `historia`, não só `dormir`),
já com nota de contexto nos dois idiomas. O gerador que existe
(`gerar_temas_dormir.py`) só faz mais "dormir" — não serve aqui.

### Passo 2 — Longo orientado à busca (a alavanca das 4.000 horas)

Título, tags e descrição **por tema**, não fixos por idioma. É o que decide se
o vídeo de 1h é encontrado. Sem isso, nenhuma quantidade de longos vira hora.

### Passo 3 — Abertura falada no longo (fecha o Portão B do longo)

20 a 40 segundos de contexto antes do trecho de dormir. Fora do sono, para não
acordar quem o vídeo acabou de fazer dormir. É o formato que os canais grandes
do nicho usam.

⚠ Mexe no render do longo, que é onde o projeto se queimou em 20/07 (MP4 com
DTS quebrado, vídeo rejeitado, 1.600 de cota por tentativa). Vai sozinho, com
render completo testado antes de virar padrão.

### Passo 4 — Ligar o longo nos três canais fantasma, ao fim da janela

Sem isso eles não monetizam nunca. Datas: La Noche Estoica ≈03/09,
El Poder Crudo e Astucia Fría ≈03/09. Formato provado no nicho:
"3 Hours of Stoic Philosophy to Fall Asleep To" — texto de domínio público
narrado sobre fundo escuro parado, que é exatamente o que o motor já faz.

### Passo 5 — Requisitos administrativos do YPP

Verificação em duas etapas ligada e AdSense vinculado, por canal. Não custa
nada e é reprovação boba se faltar na hora de submeter.

⚠ **Medido em 26/08: a conta da La Noche Estoica tem `longUploadsStatus:
eligible`, não `allowed`** — sem verificação por telefone o teto de upload é
15 minutos, e é por isso que os dois testes de longo da era Stoic by Night
("1 Hour of Stoic Wisdom…") morreram no Studio com "Falha no envio: vídeo
muito longo". **O Passo 4 depende disso**: verificar em youtube.com/verify,
logado na conta do canal, ANTES de ≈03/09 — senão cada longo falha e queima
1.600 de cota. Conferir com `python produzir/limpar_uploads_falhos.py --canal
stoic` (workflow "Limpar uploads falhos") até aparecer `allowed`; o mesmo
vale para os outros canais fantasma antes de ligar o longo neles. Os dois
rascunhos falhados NÃO são visíveis pela Data API (varridos os 43 vídeos do
canal: zero com status failed) — apagar é manual, no Studio.

---

## 5. A expectativa honesta de prazo

Com o portão de formato resolvido, o que sobra é volume, e volume é tempo:

- **Inscritos**: o ES ganha ~8/dia. 795 inscritos ≈ **3 meses**.
- **Horas**: é o gargalo real. Depende inteiramente do Passo 2 funcionar. Se os
  longos passarem a ser encontrados, 4.000 horas em 12 meses é plausível. Se
  continuarem invisíveis, não chega — e aí a decisão passa a ser outra
  (mudar formato de longo, ou aceitar que o dinheiro vem de afiliado).

Nenhum canal monetiza em 2026 sem o Passo 2 dar certo. É a aposta que decide.

---

## 6. O que precisa de validação sua

1. **Passo 4 muda o método** que você mandou seguir "rigorosamente": os canais
   fantasma passariam a ter vídeo longo depois dos 30 dias. Sem isso eles não
   têm caminho para monetizar. Precisa do seu ok, mesmo que seja só para 03/09.
2. **Passo 3, a abertura falada** no vídeo de dormir. É mudança de formato num
   produto que hoje funciona pelo silêncio.
3. Os passos 1, 2 e 5 eu faço sem te acionar — são correção de defeito e
   trabalho de SEO, não mudam decisão sua.
