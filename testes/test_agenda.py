# -*- coding: utf-8 -*-
"""Testes da AGENDA — quem decide o que sai em cada execução do cron.

Existem por causa de um defeito que ficou sete dias no ar (26/08 a 02/09/2026)
sem que nenhum alarme tocasse: com `hora_longo_utc: 0`, `longos_por_dia: 2` e
`gap_longos_min: 480`, a função `decidir` devolvia None enquanto o segundo
longo esperava o gap — e o Short devido nessas 8 horas simplesmente não saía.
O canal ES publicou 9 Shorts de 16 nesse período.

Rodar: python -m unittest discover -s testes -v
"""

import json
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from publicador.publicar import PISO_GAP_SHORT_MIN, decidir, gap_efetivo  # noqa: E402

UTC = timezone.utc


def estado(hoje, n_longos=0, n_shorts=0, ultimo_longo=None, ultimo_short=None):
    return {
        "publicados": [],
        "ultimo_short": ultimo_short,
        "ultimo_longo": ultimo_longo,
        "shorts_dia": {"data": hoje, "n": n_shorts},
        "longos_dia": {"data": hoje, "n": n_longos},
        "longo_data": hoje if n_longos else "",
    }


CFG_ES = {"hora_longo_utc": 0, "longos_por_dia": 2, "gap_longos_min": 480,
          "shorts_por_dia": 2, "gap_shorts_min": 420}
CFG_STOIC = {"hora_longo_utc": None, "shorts_por_dia": 3,
             "gap_shorts_min": 420, "hora_short_utc": 1}


class TestGapDoLongoNaoCalaOCanal(unittest.TestCase):
    """O defeito de 26/08 a 02/09/2026, em forma de teste."""

    def test_short_sai_enquanto_o_segundo_longo_espera_o_gap(self):
        # 06:54 UTC: o 1º longo saiu à 01:59, o gap de 480 min ainda não venceu
        # (295 min). O 2º longo tem de esperar — mas o Short está devido.
        agora = datetime(2026, 9, 2, 6, 54, tzinfo=UTC)
        ec = estado("2026-09-02", n_longos=1,
                    ultimo_longo="2026-09-02T01:59:00+00:00",
                    ultimo_short="2026-09-01T23:40:00+00:00")
        self.assertEqual(decidir(CFG_ES, ec, agora), "short")

    def test_longo_sai_quando_o_gap_vence(self):
        agora = datetime(2026, 9, 2, 11, 51, tzinfo=UTC)
        ec = estado("2026-09-02", n_longos=1,
                    ultimo_longo="2026-09-02T01:59:00+00:00")
        self.assertEqual(decidir(CFG_ES, ec, agora), "longo")

    def test_primeiro_longo_tem_prioridade_sobre_o_short(self):
        agora = datetime(2026, 9, 2, 1, 59, tzinfo=UTC)
        ec = estado("2026-09-02")
        self.assertEqual(decidir(CFG_ES, ec, agora), "longo")

    def test_nada_devido_quando_o_dia_esta_completo(self):
        agora = datetime(2026, 9, 2, 23, 0, tzinfo=UTC)
        ec = estado("2026-09-02", n_longos=2, n_shorts=2,
                    ultimo_longo="2026-09-02T11:51:00+00:00",
                    ultimo_short="2026-09-02T20:00:00+00:00")
        self.assertIsNone(decidir(CFG_ES, ec, agora))


class TestGapEfetivo(unittest.TestCase):
    """O gap é alvo de espaçamento, não veto: tem de caber no dia."""

    def test_gap_cheio_quando_o_dia_ainda_e_longo(self):
        agora = datetime(2026, 9, 2, 9, 0, tzinfo=UTC)   # restam 900 min
        self.assertEqual(gap_efetivo(420, 2, agora), 420)

    def test_gap_encolhe_quando_o_dia_acaba(self):
        agora = datetime(2026, 9, 2, 22, 8, tzinfo=UTC)  # restam 112 min
        self.assertEqual(gap_efetivo(420, 1, agora), 112)

    def test_nunca_abaixo_do_piso(self):
        agora = datetime(2026, 9, 2, 23, 40, tzinfo=UTC)  # restam 20 min
        self.assertEqual(gap_efetivo(420, 2, agora), PISO_GAP_SHORT_MIN)

    def test_o_short_perdido_de_02_09_agora_sai(self):
        # Caso real: 22:08 UTC, um Short de dois publicado, o último às 15:37.
        # Decorrido 391 min contra gap de 420 — perdido por 29 minutos.
        agora = datetime(2026, 9, 2, 22, 8, tzinfo=UTC)
        ec = estado("2026-09-02", n_longos=2, n_shorts=1,
                    ultimo_longo="2026-09-02T11:51:00+00:00",
                    ultimo_short="2026-09-02T15:37:00+00:00")
        self.assertEqual(decidir(CFG_ES, ec, agora), "short")

    def test_nao_publica_dois_shorts_colados(self):
        agora = datetime(2026, 9, 2, 23, 0, tzinfo=UTC)
        ec = estado("2026-09-02", n_longos=2, n_shorts=1,
                    ultimo_short="2026-09-02T22:30:00+00:00")
        self.assertIsNone(decidir(CFG_ES, ec, agora))


class TestCanalSoDeShorts(unittest.TestCase):
    """Protocolo Fantasma: hora_longo_utc = null nunca pode gerar longo."""

    def test_nunca_devolve_longo(self):
        for hora in range(24):
            agora = datetime(2026, 9, 2, hora, 30, tzinfo=UTC)
            ec = estado("2026-09-02")
            self.assertNotEqual(decidir(CFG_STOIC, ec, agora), "longo",
                                f"devolveu longo às {hora}h")

    def test_respeita_hora_short_utc(self):
        ec = estado("2026-09-02")
        self.assertIsNone(decidir(CFG_STOIC, ec,
                                  datetime(2026, 9, 2, 0, 30, tzinfo=UTC)))
        self.assertEqual(decidir(CFG_STOIC, ec,
                                 datetime(2026, 9, 2, 1, 30, tzinfo=UTC)),
                         "short")

    def test_respeita_o_teto_diario(self):
        ec = estado("2026-09-02", n_shorts=3,
                    ultimo_short="2026-09-02T18:00:00+00:00")
        self.assertIsNone(decidir(CFG_STOIC, ec,
                                  datetime(2026, 9, 2, 23, 0, tzinfo=UTC)))


class TestEsteiraCompleta(unittest.TestCase):
    """Replay: com as execuções que o cron entrega de verdade, o canal fecha
    o dia? Medido na API do repo em 03/09/2026, o workflow Publicar roda ~6
    vezes por dia, em intervalos de 2 a 7 horas."""

    EXECUCOES_REAIS = ["01:59", "06:54", "11:51", "15:37", "19:05", "22:08"]

    def _replay(self, cfg, horas, dias=3):
        ec = estado("", 0, 0)
        saiu = {}
        for d in range(dias):
            dia = datetime(2026, 9, 1, tzinfo=UTC) + timedelta(days=d)
            for hhmm in horas:
                h, m = (int(x) for x in hhmm.split(":"))
                agora = dia.replace(hour=h, minute=m)
                hoje = agora.date().isoformat()
                tipo = decidir(cfg, ec, agora)
                if tipo is None:
                    continue
                chave = "longos_dia" if tipo == "longo" else "shorts_dia"
                if ec[chave]["data"] != hoje:
                    ec[chave] = {"data": hoje, "n": 0}
                ec[chave]["n"] += 1
                ec["ultimo_longo" if tipo == "longo" else "ultimo_short"] = \
                    agora.isoformat()
                saiu.setdefault(hoje, {"longo": 0, "short": 0})[tipo] += 1
        return saiu

    def test_es_fecha_a_cota_com_as_execucoes_reais(self):
        saiu = self._replay(CFG_ES, self.EXECUCOES_REAIS)
        for dia in list(saiu)[1:]:      # o 1º dia começa com estado vazio
            self.assertEqual(saiu[dia]["longo"], 2, f"{dia}: longos")
            self.assertEqual(saiu[dia]["short"], 2, f"{dia}: shorts")

    def test_stoic_fecha_a_cota_com_as_execucoes_reais(self):
        saiu = self._replay(CFG_STOIC, self.EXECUCOES_REAIS)
        for dia in list(saiu)[1:]:
            self.assertEqual(saiu[dia]["short"], 3, f"{dia}: shorts")


class TestConfigReal(unittest.TestCase):
    """A config em produção tem de fechar a esteira com o cron que existe."""

    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(
            (RAIZ / "publicador" / "config.json").read_text(encoding="utf-8"))

    def test_todo_canal_ativo_fecha_o_dia(self):
        horas = TestEsteiraCompleta.EXECUCOES_REAIS
        replay = TestEsteiraCompleta()._replay
        for idioma, cfg in self.config["canais"].items():
            if not cfg.get("ativo"):
                continue
            with self.subTest(canal=idioma):
                saiu = replay(cfg, horas)
                ultimo = list(saiu)[-1]
                self.assertEqual(saiu[ultimo]["short"],
                                 cfg["shorts_por_dia"],
                                 f"{idioma}: Shorts não fecharam")
                if cfg.get("hora_longo_utc") is not None:
                    self.assertEqual(saiu[ultimo]["longo"],
                                     cfg.get("longos_por_dia", 1),
                                     f"{idioma}: longos não fecharam")


if __name__ == "__main__":
    unittest.main()
