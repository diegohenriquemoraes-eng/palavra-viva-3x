# -*- coding: utf-8 -*-
"""Orçamento de COTA da YouTube Data API, por canal e por dia.

São 10.000 unidades por dia por projeto Cloud, e cada canal tem projeto
próprio. Estourar não dá erro visível na hora: o canal simplesmente para de
publicar até a virada do dia UTC.

Este teste transforma a conta que hoje vive em prosa no CLAUDE.md em algo que
falha antes do commit — e já achou uma diferença ao ser escrito (03/09/2026):
a conta de 25/08 dava ~7.500 para o canal ES e prometia "margem para um
retry", mas não incluía o workflow **Realinhar** (criado no mesmo dia, 500
unidades diárias) nem a legenda e a playlist dos DOIS longos. O número real
passa de 8.000, e um reenvio de longo estoura o dia. Ver SEM_MARGEM_DE_RETRY.
"""

import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

# Custos oficiais (developers.google.com/youtube/v3/determine_quota_cost),
# os mesmos anotados em nucleo/youtube_api.py.
UPLOAD = 1600
UPDATE = 50            # videos.update — tornar público
THUMBNAIL = 50         # thumbnails.set — só no longo
CAPTION = 400          # captions.insert — a faixa .srt do longo
PLAYLIST_INSERT = 50   # playlistItems.insert — só no longo
CHANNELS_LIST = 1      # validação do channel_id do token, por publicação

# youtube_api.esperar_processamento chama videos().list de 15 em 15 segundos,
# a 1 unidade cada. O caso típico é o vídeo ficar pronto em 2-3 min (Short) e
# 5-6 min (longo); o teto (espera_short_s 900 / espera_longo_s 2400) só é
# alcançado quando o YouTube trava.
POLL_SHORT = 12
POLL_LONGO = 25

LIMITE = 10_000
# Workflow Realinhar, cron 07:10 UTC, `--limite 10` por canal ativo. Pior caso
# do dia: 10 vídeos com algo a mudar, a 50 unidades cada.
REALINHAR_DIARIO = 10 * UPDATE

# Canais em que o dia normal cabe, mas um reenvio de upload não. É uma dívida
# conhecida, não um descuido: o ES roda 2 longos + 2 Shorts desde 25/08/2026
# como teste de funil de horas, com régua em 25/11. Cortar um Short para abrir
# margem é decisão do Diego, não do teste. O que este dicionário garante é que
# a perda de margem seja SEMPRE deliberada: um canal novo que caia aqui sem
# estar na lista faz o teste falhar.
SEM_MARGEM_DE_RETRY = {
    "es": "2 longos + 2 Shorts (teste do funil de horas, régua 25/11/2026)",
}


def custo_short() -> int:
    return UPLOAD + UPDATE + POLL_SHORT + CHANNELS_LIST


def custo_longo() -> int:
    return (UPLOAD + UPDATE + THUMBNAIL + CAPTION + PLAYLIST_INSERT
            + POLL_LONGO + CHANNELS_LIST)


def custo_dia(cfg: dict) -> int:
    shorts = cfg.get("shorts_por_dia", 0) * custo_short()
    longos = (cfg.get("longos_por_dia", 1) * custo_longo()
              if cfg.get("hora_longo_utc") is not None else 0)
    return shorts + longos + REALINHAR_DIARIO


class TestOrcamentoDeCota(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(
            (RAIZ / "publicador" / "config.json").read_text(encoding="utf-8"))

    def canais_ativos(self):
        return [(i, c) for i, c in self.config["canais"].items()
                if c.get("ativo")]

    def test_o_dia_normal_cabe_na_cota(self):
        for idioma, cfg in self.canais_ativos():
            with self.subTest(canal=idioma):
                gasto = custo_dia(cfg)
                self.assertLessEqual(
                    gasto, LIMITE,
                    f"{idioma}: {gasto} unidades num dia sem nenhuma falha — "
                    f"passa das {LIMITE} e o canal fica mudo até a virada do "
                    f"dia UTC. Reduza shorts_por_dia ou longos_por_dia.")

    def test_margem_para_um_reenvio(self):
        for idioma, cfg in self.canais_ativos():
            pior = custo_dia(cfg) + max(custo_short(), custo_longo())
            tem_margem = pior <= LIMITE
            with self.subTest(canal=idioma):
                if idioma in SEM_MARGEM_DE_RETRY:
                    self.assertFalse(
                        tem_margem,
                        f"{idioma} ganhou margem de retry ({pior} de "
                        f"{LIMITE}): tirar da lista SEM_MARGEM_DE_RETRY.")
                    continue
                self.assertTrue(
                    tem_margem,
                    f"{idioma}: {custo_dia(cfg)} no dia normal e {pior} com "
                    f"um reenvio de upload — um vídeo que suba e falhe deixa "
                    f"o canal mudo. Reduza a agenda ou registre o motivo em "
                    f"SEM_MARGEM_DE_RETRY.")

    def test_nenhum_canal_passa_de_cinco_uploads_por_dia(self):
        # Teto do CLAUDE.md: "NUNCA subir para 6 uploads/dia sem aumento de
        # cota aprovado pelo Google."
        for idioma, cfg in self.canais_ativos():
            n = cfg.get("shorts_por_dia", 0)
            if cfg.get("hora_longo_utc") is not None:
                n += cfg.get("longos_por_dia", 1)
            with self.subTest(canal=idioma):
                self.assertLessEqual(n, 5, f"{idioma}: {n} uploads por dia")


class TestConfigCoerente(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(
            (RAIZ / "publicador" / "config.json").read_text(encoding="utf-8"))

    def test_canal_ativo_tem_identidade_e_fila(self):
        for idioma, cfg in self.config["canais"].items():
            if not cfg.get("ativo"):
                continue
            with self.subTest(canal=idioma):
                self.assertTrue(cfg.get("channel_id"), "sem channel_id")
                self.assertTrue(cfg.get("handle"), "sem handle")
                fila = RAIZ / cfg.get("fila", "fila")
                self.assertTrue(fila.is_dir(), f"fila ausente: {fila.name}")

    def test_produto_proprio_nao_se_declara_afiliado(self):
        """Dizer "enlace de afiliado" num produto do Diego é declaração falsa.

        Regra do CLAUDE.md (25/08/2026): os e-books da Hotmart 30 Noches con
        la Palabra (X107325587N) e 30 Noches Estoicas (O107325775B) são
        produto PRÓPRIO; a frase de divulgação de afiliado só vale para o
        curso de piano.
        """
        proprios = ("X107325587N", "O107325775B")
        for idioma, cfg in self.config["canais"].items():
            for campo in ("afiliado", "afiliado_short", "bio"):
                texto = cfg.get(campo, "") or ""
                for hotlink in proprios:
                    if hotlink not in texto:
                        continue
                    bloco = texto.split(hotlink, 1)[1].split("\n\n", 1)[0]
                    with self.subTest(canal=idioma, campo=campo):
                        self.assertNotIn(
                            "afiliado", bloco.lower(),
                            f"{idioma}.{campo}: o bloco do produto próprio "
                            f"{hotlink} se declara afiliado")

    def test_todo_link_de_oferta_leva_rastreador(self):
        """Sem ?src= não dá para saber de onde veio a venda (regra de 25/08)."""
        for idioma, cfg in self.config["canais"].items():
            for campo in ("afiliado", "afiliado_short", "bio"):
                texto = cfg.get(campo, "") or ""
                for linha in texto.splitlines():
                    if "hotmart.com" not in linha:
                        continue
                    with self.subTest(canal=idioma, campo=campo):
                        self.assertIn("src=", linha,
                                      f"{idioma}.{campo}: link sem rastreador")


if __name__ == "__main__":
    unittest.main()
