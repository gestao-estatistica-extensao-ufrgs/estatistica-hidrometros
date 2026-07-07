"""
Módulo com algumas definições de tipos e nomes de colunas/variáveis
"""

from typing import TypeAlias, Literal
from enum import StrEnum

NOME_VARIAVEIS: TypeAlias = Literal[
    "ramal",
    "hidrometro",
    "diametro",
    "data_instalacao",
    "grupo_leitura",
    "situacao_ligacao_agua",
    "perfil_imovel",
    "divida_total_vencida",
    "contas_vencidas_aberto",
    "media_consumo_mes_1",
    "media_consumo_mes_2",
    "media_consumo_mes_3",
    "anormalidade_leitura_mes_1",
    "anormalidade_leitura_mes_2",
    "anormalidade_leitura_mes_3",
    "consumo_medido_mes_1",
    "consumo_medido_mes_2",
    "consumo_medido_mes_3",
    "consumo_faturado_mes_1",
    "consumo_faturado_mes_2",
    "consumo_faturado_mes_3",
    "anormalidade_consumo_mes_1",
    "anormalidade_consumo_mes_2",
    "anormalidade_consumo_mes_3",
    "categoria",
    "tipo_tarifa_esgoto",
]

# Variáveis "isoladas": cada uma alimenta só um gráfico/tabela específico, então
# se não forem associadas a nenhuma coluna do arquivo, o app mostra um aviso no
# lugar daquela visualização em vez de obrigar a associação. As demais variáveis
# (ex: ramal, diâmetro, situação, média de consumo) sustentam quase todo o resto
# do app (filtros, classificação de consumo, idade do hidrômetro) e continuam
# obrigatórias.
VARIAVEIS_OPCIONAIS: frozenset[NOME_VARIAVEIS] = frozenset(
    {
        "divida_total_vencida",
        "contas_vencidas_aberto",
        "anormalidade_leitura_mes_1",
        "anormalidade_leitura_mes_2",
        "anormalidade_leitura_mes_3",
        "anormalidade_consumo_mes_1",
        "anormalidade_consumo_mes_2",
        "anormalidade_consumo_mes_3",
        "consumo_medido_mes_1",
        "consumo_medido_mes_2",
        "consumo_medido_mes_3",
        "consumo_faturado_mes_1",
        "consumo_faturado_mes_2",
        "consumo_faturado_mes_3",
    }
)


class ColunasDataframe(StrEnum):
    """
    Enum com todas as colunas presentes no dataframe para facilitar acesso e controle
    """

    RAMAL = "ramal"
    HIDROMETRO = "hidrometro"
    SITUACAO_LIGACAO_AGUA = "situacao_ligacao_agua"
    DIAMETRO = "diametro"
    DIAMETRO_LETRA = "diametro_letra"
    DATA_INSTALACAO = "data_instalacao"
    IDADE_HIDROMETRO = "idade_hidrometro"
    GRUPO_LEITURA = "grupo_leitura"
    PERFIL_IMOVEL = "perfil_imovel"
    CATEGORIA = "categoria"
    TIPO_TARIFA_ESGOTO = "tipo_tarifa_esgoto"
    DIVIDA_TOTAL_VENCIDA = "divida_total_vencida"
    CONTAS_VENCIDAS_ABERTO = "contas_vencidas_aberto"

    DATA_REFERENCIA_1 = "data_referencia_1"
    DATA_REFERENCIA_2 = "data_referencia_2"
    DATA_REFERENCIA_3 = "data_referencia_3"

    MEDIA_CONSUMO_MES_1 = "media_consumo_mes_1"
    MEDIA_CONSUMO_MES_2 = "media_consumo_mes_2"
    MEDIA_CONSUMO_MES_3 = "media_consumo_mes_3"

    ANORMALIDADE_LEITURA_MES_1 = "anormalidade_leitura_mes_1"
    ANORMALIDADE_LEITURA_MES_2 = "anormalidade_leitura_mes_2"
    ANORMALIDADE_LEITURA_MES_3 = "anormalidade_leitura_mes_3"

    CONSUMO_MEDIDO_MES_1 = "consumo_medido_mes_1"
    CONSUMO_MEDIDO_MES_2 = "consumo_medido_mes_2"
    CONSUMO_MEDIDO_MES_3 = "consumo_medido_mes_3"

    CONSUMO_FATURADO_MES_1 = "consumo_faturado_mes_1"
    CONSUMO_FATURADO_MES_2 = "consumo_faturado_mes_2"
    CONSUMO_FATURADO_MES_3 = "consumo_faturado_mes_3"

    ANORMALIDADE_CONSUMO_MES_1 = "anormalidade_consumo_mes_1"
    ANORMALIDADE_CONSUMO_MES_2 = "anormalidade_consumo_mes_2"
    ANORMALIDADE_CONSUMO_MES_3 = "anormalidade_consumo_mes_3"

    CONSUMO_MAX_MES_1 = "consumo_max_mes_1"
    CONSUMO_MAX_MES_2 = "consumo_max_mes_2"
    CONSUMO_MAX_MES_3 = "consumo_max_mes_3"
