# Licenças do conteúdo

## Texto bíblico (domínio público)

| Idioma | Tradução | Origem do JSON |
|---|---|---|
| es | Reina-Valera 1909 | scrollmapper/bible_databases |
| en | King James Version (1769) | scrollmapper/bible_databases (`KJV.json`) |
| pt | Bíblia Livre (PorBLivre) | scrollmapper/bible_databases (`PorBLivre.json`) |

As três traduções estão em domínio público. A normalização aplicada em
`nucleo/biblia.py` (grafia arcaica da RV1909, remoção de inscrições de
Salmos e de "Selah") é ortográfica/editorial e não altera a tradução.

## Imagens

Somente imagens com licença **CC0 / Public Domain Mark**, buscadas via
Openverse (api.openverse.org) com filtro `license=cc0,pdm`. A URL de origem
de cada imagem fica gravada no `pacote.json` do dia (campo `origem`).
Fallback: gradientes gerados pelo próprio pipeline.

## Música

Nenhuma faixa de terceiros. O pad ambiente dos vídeos longos é sintetizado
por `nucleo/musica.py` (senos em camadas, determinístico por seed) — obra
gerada pelo próprio projeto.

## Fontes tipográficas

- Bebas Neue — SIL Open Font License 1.1
- Montserrat — SIL Open Font License 1.1
