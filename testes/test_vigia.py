# -*- coding: utf-8 -*-
"""Testes do alarme de ENTREGA — validado contra a série real do projeto.

Um alarme se prova de duas maneiras: tocando quando devia ter tocado e ficando
calado quando o canal só oscilou. Estes testes usam
`conteudo/desempenho_historico.json`, a série de verdade, e travam as duas
pontas:

- o canal ES perdeu 80% da mediana por vídeo entre 28/07 e 02/09/2026 e
  ninguém percebeu por semanas — com esta regra o alarme teria tocado em 22/08;
- o canal estoico teve um -37% isolado em 25/08 enquanto crescia de verdade
  (foi de 12 a 85 inscritos em 23 dias) — não pode virar alarme.
"""

import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from produzir.vigia import (BASE_MINIMA, QUEDA_ALARME,  # noqa: E402
                            alarme_de_entrega, queda_da_coorte)

HIST = json.loads(
    (RAIZ / "conteudo" / "desempenho_historico.json").read_text(encoding="utf-8"))


def serie(canal):
    return [(h["data"], h["canais"][canal]["views_medianas"]) for h in HIST
            if h["canais"].get(canal, {}).get("views_medianas")]


def primeira_data_de_alarme(canal):
    s = serie(canal)
    valores = [v for _, v in s]
    for i in range(len(valores)):
        if alarme_de_entrega(valores[:i + 1]) is not None:
            return s[i][0]
    return None


class TestAlarmeDeEntrega(unittest.TestCase):
    def test_teria_pego_o_colapso_do_es_em_22_08(self):
        data = primeira_data_de_alarme("es")
        self.assertIsNotNone(data, "o alarme nunca tocaria para o ES")
        self.assertLessEqual(
            data, "2026-08-24",
            f"tocaria só em {data}: tarde demais para um canal que caiu de "
            f"903 para 184 views medianos")

    def test_continua_tocando_enquanto_a_queda_dura(self):
        valores = [v for _, v in serie("es")]
        self.assertIsNotNone(alarme_de_entrega(valores),
                             "a queda do ES segue em curso em 02/09")

    def test_nao_toca_para_o_canal_que_estava_crescendo(self):
        # O stoic subiu de 187 (03/08) para 982 (02/09) com um vale no meio.
        valores = [v for _, v in serie("stoic")]
        self.assertIsNone(alarme_de_entrega(valores),
                          "falso positivo no canal que mais cresce")

    def test_uma_leitura_isolada_nao_dispara(self):
        base = [1000] * 10
        self.assertIsNone(alarme_de_entrega(base + [100, 1000, 1000]))

    def test_duas_leituras_seguidas_disparam(self):
        base = [1000] * 10
        self.assertIsNotNone(alarme_de_entrega(base + [300, 300, 300]))

    def test_serie_curta_nao_dispara(self):
        self.assertIsNone(alarme_de_entrega([1000, 900, 100]))

    def test_canal_pequeno_nao_vira_ruido(self):
        pequeno = [BASE_MINIMA - 20] * 10 + [1, 1, 1]
        self.assertIsNone(alarme_de_entrega(pequeno))

    def test_a_queda_medida_bate_com_a_conta(self):
        valores = [100.0] * 7 + [50.0] * 3
        self.assertAlmostEqual(queda_da_coorte(valores, 9), 0.5)
        self.assertGreater(queda_da_coorte(valores, 9), QUEDA_ALARME)


if __name__ == "__main__":
    unittest.main()
