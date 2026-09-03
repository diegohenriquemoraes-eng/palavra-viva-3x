# -*- coding: utf-8 -*-
"""Testes dos POÇOS de temas — o estoque que alimenta as filas.

Um tema inválido não quebra nada até o dia em que o reabastecedor tenta criar
o pacote; aí a linha inteira para de abastecer e o canal seca dias depois, com
o alarme chegando tarde. Estes testes leem todos os poços de linhas com canal
ativo e reprovam o que o `reabastecer.validar_tema` só descobriria na nuvem.

Sem rede: as Bíblias e os corpora são arquivos do repo.
"""

import json
import sys
import unittest
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from nucleo import biblia  # noqa: E402
from produzir.reabastecer import LINHAS  # noqa: E402


def texto_aplicacao(short: dict, canal: str) -> str:
    """A aplicação é string na maioria dos poços e dict por idioma em alguns."""
    ap = short.get("aplicacao") or ""
    if isinstance(ap, dict):
        ap = ap.get(canal, "") or ""
    return ap.strip()

CONFIG = json.loads(
    (RAIZ / "publicador" / "config.json").read_text(encoding="utf-8"))

# Linhas cujos canais escrevem uma aplicação própria depois do trecho citado.
# É o que separa "leitura de material de terceiros" (inelegível para
# monetização, answer/1311392) de conteúdo com diferença significativa. Nos
# canais bíblicos a diretriz editorial nº 4 proíbe justamente isso.
LINHAS_COM_CAMADA_AUTORAL = {"estoico", "poder", "astucia"}


def linhas_ativas():
    for nome, linha in LINHAS.items():
        if any(CONFIG["canais"].get(c, {}).get("ativo") for c in linha["canais"]):
            yield nome, linha


def carregar(linha):
    dados = json.loads(linha["temas"].read_text(encoding="utf-8"))
    return dados["temas"] if isinstance(dados, dict) else dados


class TestPocos(unittest.TestCase):
    def test_toda_referencia_existe_no_corpus(self):
        for nome, linha in linhas_ativas():
            temas = carregar(linha)
            for tema in temas:
                refs = list(tema["longo"]["refs"]) + [s["ref"]
                                                      for s in tema["shorts"]]
                for canal in linha["canais"]:
                    if not CONFIG["canais"].get(canal, {}).get("ativo"):
                        continue
                    for ref in refs:
                        with self.subTest(poco=nome, tema=tema["slug"],
                                          canal=canal, ref=ref):
                            try:
                                versos = biblia.carregar_versos(canal, ref)
                            except BaseException as exc:   # SystemExit inclusive
                                self.fail(f"{ref}: {exc}")
                            self.assertTrue(versos, f"{ref} não tem texto")

    def test_titulos_cabem_no_limite_do_youtube(self):
        for nome, linha in linhas_ativas():
            for tema in carregar(linha):
                for canal in linha["canais"]:
                    if not CONFIG["canais"].get(canal, {}).get("ativo"):
                        continue
                    with self.subTest(poco=nome, tema=tema["slug"], canal=canal):
                        titulo = tema["longo"]["titulo"].get(canal, "")
                        self.assertTrue(titulo, "longo sem título")
                        self.assertLessEqual(len(titulo), 100)
                        for campo in ("thumb_titulo", "thumb_sub"):
                            self.assertTrue(tema["longo"][campo].get(canal),
                                            f"longo.{campo} vazio")
                        for short in tema["shorts"]:
                            t = short["titulo"].get(canal, "")
                            self.assertTrue(t, f"short {short['ref']} sem título")
                            self.assertLessEqual(len(t), 100)

    def test_slugs_unicos(self):
        for nome, linha in linhas_ativas():
            slugs = Counter(t["slug"] for t in carregar(linha))
            repetidos = [s for s, n in slugs.items() if n > 1]
            with self.subTest(poco=nome):
                self.assertFalse(repetidos, f"slugs repetidos: {repetidos}")

    def test_nenhum_short_repete_passagem_dentro_do_poco(self):
        """Dois Shorts com a mesma passagem são o mesmo vídeo com outra capa —
        exatamente a impressão digital de produção em massa que a análise de
        monetização procura.

        Vale só onde existe camada autoral. Na linha bíblica a repetição é
        deliberada: Salmo 91 e Salmo 23 são a espinha do nicho e voltam em
        temas diferentes, com imagem e recorte próprios (diretriz nº 4 — o
        texto é o produto, e o poço bíblico repete de propósito).
        """
        for nome, linha in linhas_ativas():
            if nome not in LINHAS_COM_CAMADA_AUTORAL:
                continue
            refs = Counter(s["ref"] for t in carregar(linha)
                           for s in t["shorts"])
            repetidas = [r for r, n in refs.items() if n > 1]
            with self.subTest(poco=nome):
                self.assertFalse(repetidas,
                                 f"passagens repetidas: {repetidas[:5]}")

    def test_camada_autoral_presente_onde_a_monetizacao_exige(self):
        for nome, linha in linhas_ativas():
            if nome not in LINHAS_COM_CAMADA_AUTORAL:
                continue
            for tema in carregar(linha):
                for short in tema["shorts"]:
                    canal = linha["canais"][0]
                    with self.subTest(poco=nome, tema=tema["slug"],
                                      ref=short["ref"]):
                        self.assertTrue(
                            texto_aplicacao(short, canal),
                            "sem aplicação própria — o vídeo fica sendo só a "
                            "leitura de um texto de terceiros")

    def test_carga_do_short_na_faixa_que_o_canal_retem(self):
        """Texto citado + aplicação, em palavras.

        O teto por canal (`max_short_s`) limita só o texto CITADO: o gancho e a
        aplicação entram por cima. Na prática o que decide a duração é a soma,
        e o acervo do canal estoico — que retém 90% — tem mediana 42 palavras
        e p90 de 54. O limite aqui é folgado de propósito: reprova o disparate,
        não a variação.

        Só nas linhas com camada autoral: nos canais bíblicos a aplicação não
        existe e `_cortar_ao_teto` já apara a passagem em versos inteiros até
        caber no orçamento, então a carga bruta do poço não diz nada.
        """
        for nome, linha in linhas_ativas():
            if nome not in LINHAS_COM_CAMADA_AUTORAL:
                continue
            canal = linha["canais"][0]
            if not CONFIG["canais"].get(canal, {}).get("ativo"):
                continue
            for tema in carregar(linha):
                for short in tema["shorts"]:
                    versos = biblia.carregar_versos(canal, short["ref"])
                    carga = (sum(len(t.split()) for _, t in versos)
                             + len(texto_aplicacao(short, canal).split()))
                    with self.subTest(poco=nome, tema=tema["slug"],
                                      ref=short["ref"]):
                        self.assertLessEqual(
                            carga, 110,
                            f"{carga} palavras — o Short passaria de um minuto")


if __name__ == "__main__":
    unittest.main()
