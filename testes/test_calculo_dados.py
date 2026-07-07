from typing import Any
from unittest import TestCase, skip
from pathlib import Path

import pandas as pd

import calculos
import tipos


class TestDadosCalculados(TestCase):
    dados: dict[str, Any] = {}
    df: pd.DataFrame = pd.DataFrame()

    @classmethod
    def setUpClass(cls) -> None:
        ASSOCIACAO_COLUNAS_VARIAVEIS_PREVIA: dict[tipos.NOME_VARIAVEIS, str] = {
            "ramal": "Matricula",
            "diametro": "Diametro",
            "data_instalacao": "Data Instalacao",
            "hidrometro": "Hidrometro",
            "grupo_leitura": "Grupo Leitura",
            "perfil_imovel": "Perfil Imovel",
            "situacao_ligacao_agua": "Situacao Ligacao Agua",
            "media_consumo_mes_1": "Media de Consumo 1",
            "media_consumo_mes_2": "Media de Consumo 2",
            "media_consumo_mes_3": "Media de Consumo 3",
            "anormalidade_leitura_mes_1": "Anormalidade Leitura 1",
            "anormalidade_leitura_mes_2": "Anormalidade Leitura 2",
            "anormalidade_leitura_mes_3": "Anormalidade Leitura 3",
            "consumo_medido_mes_1": "Consumo Medido 1",
            "consumo_medido_mes_2": "Consumo Medido 2",
            "consumo_medido_mes_3": "Consumo Medido 3",
            "consumo_faturado_mes_1": "Consumo Faturado 1",
            "consumo_faturado_mes_2": "Consumo Faturado 2",
            "consumo_faturado_mes_3": "Consumo Faturado 3",
            "anormalidade_consumo_mes_1": "Anormalidade Consumo 1",
            "anormalidade_consumo_mes_2": "Anormalidade Consumo 2",
            "anormalidade_consumo_mes_3": "Anormalidade Consumo 3",
            "tipo_tarifa_esgoto": "tipo Tarifa Esgoto",
            "categoria": "Categoria",
            "contas_vencidas_aberto": "Qtd Contas Vencidas em Aberto",
            "divida_total_vencida": "Divida Total Vencida",
        }

        df = pd.read_excel(Path("testes") / "dados_teste" / "amostra_dados.xlsx")
        cls.df = df
        calculos.preparacao_dados(
            df, ASSOCIACAO_COLUNAS_VARIAVEIS_PREVIA, "2024-10", "2024-09", "2024-08"
        )
        cls.dados = calculos.calcular_todos_os_dados_necessarios(
            df[df[tipos.ColunasDataframe.TIPO_TARIFA_ESGOTO] != "-"]
        )
        return super().setUpClass()

    def test_total_hidrometros(self):
        self.assertEqual(self.dados["contagem_hidrometros"], 12566)

    def test_porcentagem_hidrometros_ligados(self):
        self.assertLess(
            abs(self.dados["porcentagem_hidrometros_ligados"] - 97.14), 0.01
        )

    @skip(
        "Calculo depende da data atual. O valor esperado é obtido com base data anterior."
    )
    def test_idade_media_hidrometro(self):
        obtido = self.dados["idade_media_hidrometros"]
        esperado = 6.39
        diferenca = abs(obtido - esperado)
        self.assertLess(diferenca, 0.01, f"{obtido}, {esperado}, {diferenca}")

    def test_frequencia_perfil_imoveis(self):
        freq = self.dados["freq_perfil_imoveis"]
        valores_esperados = {
            "NORMAL": 7968,
            "IMOVEL DA TECQUA": 3535,
            "TELEMEDIDO C/ ISC": 3,
        }
        for linha in freq:
            perfil = linha["perfil_imovel"]
            absoluta = linha["frequencia_absoluta"]
            if esperado := valores_esperados.get(perfil):
                with self.subTest(perfil=perfil, obtido=absoluta, esperado=esperado):
                    self.assertEqual(absoluta, esperado)

    def test_frequencia_diametro(self):
        freq = self.dados["freq_hidrometros"]
        valores_esperados = {20: 12336, 25: 172}
        for linha in freq:
            diametro = linha["diametro"]
            obtido = linha["freq_absoluta"]
            if esperado := valores_esperados.get(diametro):
                with self.subTest(diametro=diametro, obtido=obtido, esperado=esperado):
                    self.assertEqual(
                        obtido, esperado, f"diametro: {diametro}, {obtido}, {esperado}"
                    )

    @skip(
        "Calculo depende da data atual. O valor esperado é obtido com base data anterior."
    )
    def test_idade_media_hidrometro_20MM(self):
        self.assertLess(abs(self.dados["idade_media_20MM"] - 6.42), 0.01)

    @skip(
        "Calculo depende da data atual. O valor esperado é obtido com base data anterior."
    )
    def test_idade_media_hidrometro_25MM(self):
        obtido = self.dados["idade_media_25MM"]
        esperado = 5.0
        diferenca = abs(obtido - esperado)
        self.assertLess(diferenca, 0.01, f"{obtido}, {esperado}, {diferenca}")

    @skip(
        "Calculo depende da data atual. O valor esperado é obtido com base data anterior."
    )
    def test_idade_media_hidrometro_acima_25MM(self):
        obtido = self.dados["idade_media_acima_25MM"]
        esperado = 4.41
        diferenca = abs(obtido - esperado)
        self.assertLess(diferenca, 0.01, f"{obtido}, {esperado}, {diferenca}")

    @skip(
        "Calculo depende da data atual. O valor esperado é obtido com base data anterior."
    )
    def test_desvio_padrao_idade_hidrometro_20MM(self):
        self.assertLess(abs(self.dados["idade_desvio_padrao_20MM"] - 5.86), 0.01)

    @skip(
        "Calculo depende da data atual. O valor esperado é obtido com base data anterior."
    )
    def test_desvio_padrao_idade_hidrometro_25MM(self):
        obtido = self.dados["idade_desvio_padrao_25MM"]
        esperado = 3.17
        diferenca = abs(obtido - esperado)
        self.assertLess(diferenca, 0.01, f"{obtido}, {esperado}, {diferenca}")

    @skip(
        "Calculo depende da data atual. O valor esperado é obtido com base data anterior."
    )
    def test_desvio_padrao_idade_hidrometro_acima_25MM(self):
        self.assertLess(abs(self.dados["idade_desvio_padrao_acima_25MM"] - 3.22), 0.01)

    def test_consumo_medio_mes_3(self):
        self.assertLess(
            abs(self.dados["media_do_consumo_medio_mes_3"] - 28.02),
            0.01,
            self.dados["media_do_consumo_medio_mes_3"],
        )

    def test_desvio_padrao_consumo_medio_mes_3(self):
        self.assertLess(
            abs(self.dados["desvio_padrao_consumo_medio_mes_3"] - 103.3),
            0.01,
            self.dados["desvio_padrao_consumo_medio_mes_3"],
        )

    def test_frequencia_consumo_maior_que_130_mes_3(self):
        self.assertEqual(
            self.dados["frequencia_consumo_acima_limite_mes_3"],
            480,
        )

    def test_frequencia_consumos_medios_mes_3(self):
        freq = self.dados["frequencia_consumos_medios_mes_3"]
        casos = [
            (freq["0"], 587),
            (freq["1"], 804),
            (freq["2"], 635),
            (freq["7"], 609),
        ]
        for x, y in casos:
            with self.subTest(x=x, esperado=y):
                self.assertEqual(x, y)

    def test_frequencia_consumos_medidos_mes_3(self):
        freq = self.dados["frequencia_consumos_medidos_mes_3"]
        casos = [
            (freq["0"], 13),
            (freq["11"], 7),
            (freq["87"], 2),
            (freq["130+"], 244),
        ]
        for x, y in casos:
            with self.subTest(x=x, esperado=y):
                self.assertEqual(x, y)

    def test_frequencia_consumo_faturado_mes_3(self):
        freq = self.dados["frequencia_consumo_faturado_mes_3"]
        casos = [
            (freq["0"], 583),
            (freq["1"], 798),
            (freq["26"], 137),
            (freq["130+"], 485),
        ]
        for x, y in casos:
            with self.subTest(x=x, resultado_esperado=y):
                self.assertEqual(x, y)

    def test_frequencia_divida_total_vencida(self):
        # Não é mais um dict de faixas concatenadas: dívida (R$) tem amplitude
        # grande demais pra um bucket fixo tipo "130+" fazer sentido (ver
        # calcular_frequencia_total_divida_vencida). Agora é a série bruta
        # de valores, sem nulos, usada num histograma com bins automáticos.
        serie = self.dados["frequencia_divida_total_vencida"]
        self.assertEqual(len(serie), 12198)
        self.assertFalse(serie.isna().any())
        self.assertLess(abs(serie.mean() - 3776.688883), 0.01)

    def test_frequencia_contas_vencidas_aberto(self):
        freq = self.dados["frequencia_contas_vencidas_aberto"]
        casos = [
            (abs(freq["0"] - 39.37609), 0.01),
            (abs(freq["1"] - 14.19704), 0.01),
            (abs(freq["130+"] - 5.44326), 0.01),
        ]
        for x, y in casos:
            with self.subTest(x=x, esperado=y):
                self.assertLess(x, y)
