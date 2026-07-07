from math import floor
from typing import Literal

from dash import dcc
import plotly.express as px  # type: ignore
import pandas as pd
import numpy as np

from tipos import NOME_VARIAVEIS, ColunasDataframe

SENTINELA_NAO_ASSOCIADA = "Não associada"


# -------------------------------------------------------------
########################
### PREPARAÇÃO DADOS ###
########################
def padronizacao_diametro(diametro: pd.Series) -> pd.Series:
    """Mantém só os dígitos de cada valor (ex: "20MM" -> 20)."""
    return diametro.astype(str).str.replace(r"\D", "", regex=True).astype(int)


def diametro_e_letra_codigo(df: pd.DataFrame) -> pd.Series:
    """
    Monta "<diametro> - <letra>", onde a letra é o primeiro caractere do
    código do hidrômetro (ou "*" se não houver um caractere válido ali).
    `.str[0]` já retorna NaN para valores não-string (int, None), então o
    `fillna` cobre tanto esses casos quanto strings vazias.
    """
    primeira_letra = df[ColunasDataframe.HIDROMETRO].str[0].fillna("*")
    return df[ColunasDataframe.DIAMETRO].astype(str) + " - " + primeira_letra


def calcular_data_referencia(mes_extracao: int, ano_extracao: int):
    data_referencia_1 = f"{ano_extracao}-{mes_extracao}"
    mes_ref_2 = mes_extracao - 1
    ano_ref_2 = ano_extracao
    if mes_ref_2 < 1:
        mes_ref_2 = 12
        ano_ref_2 -= 1

    data_referencia_2 = f"{ano_ref_2}-{mes_ref_2}"

    mes_ref_3 = mes_ref_2 - 1
    ano_ref_3 = ano_ref_2
    if mes_ref_3 < 1:
        mes_ref_3 = 12
        ano_ref_3 -= 1

    data_referencia_3 = f"{ano_ref_3}-{mes_ref_3}"

    return (data_referencia_1, data_referencia_2, data_referencia_3)


def classificar_consumo_ramal(df: pd.DataFrame):
    colunas_consumo = (
        ColunasDataframe.MEDIA_CONSUMO_MES_1,
        ColunasDataframe.MEDIA_CONSUMO_MES_2,
        ColunasDataframe.MEDIA_CONSUMO_MES_3,
    )

    for i, col_consumo in enumerate(colunas_consumo):
        nome_coluna_classificao = ""
        if i == 0:
            nome_coluna_classificao = ColunasDataframe.CONSUMO_MAX_MES_1
        elif i == 1:
            nome_coluna_classificao = ColunasDataframe.CONSUMO_MAX_MES_2
        elif i == 2:
            nome_coluna_classificao = ColunasDataframe.CONSUMO_MAX_MES_3
        else:
            assert False

        df[nome_coluna_classificao] = "Normal"
        df.loc[
            (df[ColunasDataframe.DIAMETRO_LETRA] == "20 - Y") & (df[col_consumo] > 20),
            nome_coluna_classificao,
        ] = "Maior"
        df.loc[
            (df[ColunasDataframe.DIAMETRO_LETRA] == "20 - A") & (df[col_consumo] < 21),
            nome_coluna_classificao,
        ] = "Menor"
        df.loc[
            (df[ColunasDataframe.DIAMETRO_LETRA] == "20 - A") & (df[col_consumo] > 300),
            nome_coluna_classificao,
        ] = "Maior"
        df.loc[
            (df[ColunasDataframe.DIAMETRO] == 25) & (df[col_consumo] < 301),
            nome_coluna_classificao,
        ] = "Menor"
        df.loc[
            (df[ColunasDataframe.DIAMETRO] == 25) & (df[col_consumo] > 750),
            nome_coluna_classificao,
        ] = "Maior"
        df.loc[
            (df[ColunasDataframe.DIAMETRO] == 38) & (df[col_consumo] < 751),
            nome_coluna_classificao,
        ] = "Menor"
        df.loc[
            (df[ColunasDataframe.DIAMETRO] == 38) & (df[col_consumo] > 1500),
            nome_coluna_classificao,
        ] = "Maior"
        df.loc[
            (df[ColunasDataframe.DIAMETRO] == 40) & (df[col_consumo] < 751),
            nome_coluna_classificao,
        ] = "Menor"
        df.loc[
            (df[ColunasDataframe.DIAMETRO] == 40) & (df[col_consumo] > 1500),
            nome_coluna_classificao,
        ] = "Maior"
        df.loc[
            (df[ColunasDataframe.DIAMETRO] == 50) & (df[col_consumo] < 1501),
            nome_coluna_classificao,
        ] = "Menor"
        df.loc[
            (df[ColunasDataframe.DIAMETRO] == 50) & (df[col_consumo] > 2250),
            nome_coluna_classificao,
        ] = "Maior"


def _preencher_coluna_opcional_simples(
    df: pd.DataFrame,
    relacao: dict[NOME_VARIAVEIS, str],
    relacao_temp: dict[str, str],
    variavel: NOME_VARIAVEIS,
    coluna: str,
):
    """Copia a coluna associada, ou não cria nada se a variável opcional
    não foi associada a nenhuma coluna do arquivo."""
    if relacao.get(variavel) is None:
        return
    df[coluna] = df[relacao_temp[variavel]]


def _preencher_coluna_opcional_int64(
    df: pd.DataFrame,
    relacao: dict[NOME_VARIAVEIS, str],
    relacao_temp: dict[str, str],
    variavel: NOME_VARIAVEIS,
    coluna: str,
):
    if relacao.get(variavel) is None:
        return
    df[coluna] = df[relacao_temp[variavel]].astype("Int64")


def _preencher_coluna_opcional_anormalidade(
    df: pd.DataFrame,
    relacao: dict[NOME_VARIAVEIS, str],
    relacao_temp: dict[str, str],
    variavel: NOME_VARIAVEIS,
    coluna: str,
):
    """Preenche com SENTINELA_NAO_ASSOCIADA (em vez de simplesmente não criar
    a coluna) porque essas colunas são usadas em filtros (.isin) em vários
    pontos do main.py — precisam existir para esses filtros não quebrarem."""
    if relacao.get(variavel) is None:
        df[coluna] = SENTINELA_NAO_ASSOCIADA
        return
    df[coluna] = df[relacao_temp[variavel]]
    df.loc[df[coluna].isna(), coluna] = "Sem Anormalidade"


def preparacao_dados(
    df: pd.DataFrame,
    relacao_colunas_tabela_inserida_com_dataframe: dict[NOME_VARIAVEIS, str],
    data_referencia_1: str,
    data_referencia_2: str,
    data_referencia_3: str,
):
    relacao_temp = {
        var: f"__orig_{var}__" for var in relacao_colunas_tabela_inserida_com_dataframe
    }
    df.rename(
        columns={
            col: relacao_temp[var]
            for var, col in relacao_colunas_tabela_inserida_com_dataframe.items()
        },
        inplace=True,
    )

    df[ColunasDataframe.RAMAL] = df[relacao_temp["ramal"]]
    df[ColunasDataframe.HIDROMETRO] = df[relacao_temp["hidrometro"]]

    df[ColunasDataframe.SITUACAO_LIGACAO_AGUA] = df[
        relacao_temp["situacao_ligacao_agua"]
    ]

    df[ColunasDataframe.DIAMETRO] = padronizacao_diametro(df[relacao_temp["diametro"]])

    df[ColunasDataframe.DIAMETRO_LETRA] = diametro_e_letra_codigo(df)

    df[ColunasDataframe.DATA_INSTALACAO] = df[relacao_temp["data_instalacao"]]
    tempo_instalacao_ate_agora = (
        pd.Timestamp.now() - df[ColunasDataframe.DATA_INSTALACAO]
    )
    df[ColunasDataframe.IDADE_HIDROMETRO] = tempo_instalacao_ate_agora.apply(
        lambda x: floor(x.days / 365.25)
    )

    df[ColunasDataframe.GRUPO_LEITURA] = df[relacao_temp["grupo_leitura"]]
    df[ColunasDataframe.PERFIL_IMOVEL] = df[relacao_temp["perfil_imovel"]]

    if "categoria" in relacao_temp:
        df[ColunasDataframe.CATEGORIA] = df[relacao_temp["categoria"]]
    else:
        df[ColunasDataframe.CATEGORIA] = "-"

    if "tipo_tarifa_esgoto" in relacao_temp:
        df[ColunasDataframe.TIPO_TARIFA_ESGOTO] = df[relacao_temp["tipo_tarifa_esgoto"]]
    else:
        df[ColunasDataframe.TIPO_TARIFA_ESGOTO] = "-"
    df.loc[
        df[ColunasDataframe.TIPO_TARIFA_ESGOTO].isna(),
        ColunasDataframe.TIPO_TARIFA_ESGOTO,
    ] = "-"

    if relacao_colunas_tabela_inserida_com_dataframe.get("divida_total_vencida") is not None:
        df[ColunasDataframe.DIVIDA_TOTAL_VENCIDA] = df[
            relacao_temp["divida_total_vencida"]
        ]
        df[ColunasDataframe.DIVIDA_TOTAL_VENCIDA] = np.where(
            df[ColunasDataframe.DIVIDA_TOTAL_VENCIDA].notna(),
            round(df[ColunasDataframe.DIVIDA_TOTAL_VENCIDA]),
            df[ColunasDataframe.DIVIDA_TOTAL_VENCIDA],
        )
        df[ColunasDataframe.DIVIDA_TOTAL_VENCIDA] = df[
            ColunasDataframe.DIVIDA_TOTAL_VENCIDA
        ].astype("Int64")
    # else: variável opcional não associada, coluna não é criada — os
    # widgets que dependem dela mostram um aviso (ver calcular_todos_os_dados_necessarios)

    if relacao_colunas_tabela_inserida_com_dataframe.get("contas_vencidas_aberto") is not None:
        df[ColunasDataframe.CONTAS_VENCIDAS_ABERTO] = df[
            relacao_temp["contas_vencidas_aberto"]
        ]

    ### Colunas Consumo
    df[ColunasDataframe.DATA_REFERENCIA_1] = data_referencia_1
    df[ColunasDataframe.DATA_REFERENCIA_2] = data_referencia_2
    df[ColunasDataframe.DATA_REFERENCIA_3] = data_referencia_3

    df[ColunasDataframe.MEDIA_CONSUMO_MES_1] = df[relacao_temp["media_consumo_mes_1"]]
    df[ColunasDataframe.MEDIA_CONSUMO_MES_2] = df[relacao_temp["media_consumo_mes_2"]]
    df[ColunasDataframe.MEDIA_CONSUMO_MES_3] = df[relacao_temp["media_consumo_mes_3"]]
    df[ColunasDataframe.MEDIA_CONSUMO_MES_1] = df[
        ColunasDataframe.MEDIA_CONSUMO_MES_1
    ].astype("Int64")
    df[ColunasDataframe.MEDIA_CONSUMO_MES_2] = df[
        ColunasDataframe.MEDIA_CONSUMO_MES_2
    ].astype("Int64")
    df[ColunasDataframe.MEDIA_CONSUMO_MES_3] = df[
        ColunasDataframe.MEDIA_CONSUMO_MES_3
    ].astype("Int64")

    # anormalidade_leitura/anormalidade_consumo/consumo_medido/consumo_faturado
    # são variáveis opcionais (ver tipos.VARIAVEIS_OPCIONAIS): se não forem
    # associadas, os widgets que dependem delas mostram um aviso em vez de
    # obrigar a associação (ver calcular_todos_os_dados_necessarios).
    _relacao = relacao_colunas_tabela_inserida_com_dataframe
    for i in (1, 2, 3):
        _preencher_coluna_opcional_anormalidade(
            df,
            _relacao,
            relacao_temp,
            f"anormalidade_leitura_mes_{i}",
            f"anormalidade_leitura_mes_{i}",
        )
        _preencher_coluna_opcional_int64(
            df,
            _relacao,
            relacao_temp,
            f"consumo_medido_mes_{i}",
            f"consumo_medido_mes_{i}",
        )
        _preencher_coluna_opcional_simples(
            df,
            _relacao,
            relacao_temp,
            f"consumo_faturado_mes_{i}",
            f"consumo_faturado_mes_{i}",
        )
        _preencher_coluna_opcional_anormalidade(
            df,
            _relacao,
            relacao_temp,
            f"anormalidade_consumo_mes_{i}",
            f"anormalidade_consumo_mes_{i}",
        )

    classificar_consumo_ramal(df)

    df.drop(
        columns=[col for col in relacao_temp.values() if col in df.columns],
        inplace=True,
    )

    # Colunas de texto com poucos valores únicos repetidos em todas as
    # linhas: "category" economiza bastante memória frente a "object".
    # Não inclui colunas usadas em groupby/value_counts (ex: perfil_imovel,
    # anormalidade_*), pois category preserva categorias "zeradas" após um
    # filtro e mudaria o resultado dessas contagens.
    colunas_categoricas = (
        ColunasDataframe.SITUACAO_LIGACAO_AGUA,
        ColunasDataframe.DIAMETRO_LETRA,
        ColunasDataframe.GRUPO_LEITURA,
        ColunasDataframe.CATEGORIA,
        ColunasDataframe.TIPO_TARIFA_ESGOTO,
        ColunasDataframe.CONSUMO_MAX_MES_1,
        ColunasDataframe.CONSUMO_MAX_MES_2,
        ColunasDataframe.CONSUMO_MAX_MES_3,
    )
    for coluna in colunas_categoricas:
        df[coluna] = df[coluna].astype("category")


# -------------------------------------------------------------
#####################
### CÁLCULO DADOS ###
#####################
def calcular_dados_hidrometros_segundo_diametro(
    df: pd.DataFrame, diametro: Literal["20", "25", "25+"]
):
    if diametro == "25+":
        hidrometros = df[df.diametro > 25]
    elif diametro == "20":
        hidrometros = df[df.diametro == 20]
    elif diametro == "25":
        hidrometros = df[df.diametro == 25]
    else:
        assert False, f"Diâmetro fora das categorias '20', '25', '25+'"

    idade_media: Literal["-"] | float = "-"
    idade_desvio_padrao: Literal["-"] | float = "-"
    grafico_idades_hidrometros = []
    if not hidrometros.empty:
        idade_media = round(hidrometros.idade_hidrometro.mean(), 2)
        idade_desvio_padrao = round(hidrometros.idade_hidrometro.std(), 2)

        contagem_idades_hidrometros = (
            hidrometros.idade_hidrometro.value_counts().sort_index()
        )

        titulo = f"Idade Hidrômetros de {diametro}MM"
        if diametro == "25+":
            titulo = f"Idade Hidrômetros acima de 25MM"

        # TODO: separar calculo da produção do gráfico
        grafico_idades_hidrometros = [
            dcc.Graph(
                figure=px.bar(
                    x=contagem_idades_hidrometros.index,
                    y=contagem_idades_hidrometros,
                    labels={"y": "Frequência", "x": "idade"},
                    title=titulo,
                    color_discrete_sequence=[
                        "#4f80b8",
                        "#2f6db0",
                        "#7fa8d1",
                        "#b0c8e8",
                    ],
                ).update_layout(
                    paper_bgcolor="#ffffff",
                    plot_bgcolor="#ffffff",
                    font_color="#5d6570",
                    xaxis={
                        "gridcolor": "#dde0e5",
                        "linecolor": "#c6cad1",
                        "dtick": 1,
                        "tickmode": "linear",
                    },
                    yaxis={"gridcolor": "#dde0e5", "linecolor": "#c6cad1"},
                )
            )
        ]

    return (idade_media, idade_desvio_padrao, grafico_idades_hidrometros)


def calcular_porcentagem_hidrometros_ligados(df: pd.DataFrame):
    apenas_ligados = df[df.situacao_ligacao_agua == "LIGADO"]

    contagem_hidrometros = df.hidrometro.count()

    if contagem_hidrometros > 0:
        porcentagem = round(
            apenas_ligados.situacao_ligacao_agua.count() * 100 / contagem_hidrometros, 2
        )
        return porcentagem

    return 0.0


def calcular_freq_hidrometros_por_diametro(df) -> list[dict]:
    contagem_hidrometros_por_diametro = df.diametro.value_counts()
    df_freq_hidrometros = contagem_hidrometros_por_diametro.to_frame()
    df_freq_hidrometros["%"] = (
        contagem_hidrometros_por_diametro
        * 100
        / contagem_hidrometros_por_diametro.sum()
    )
    df_freq_hidrometros["%"] = df_freq_hidrometros["%"].apply(lambda x: round(x, 2))
    df_freq_hidrometros.reset_index(inplace=True)
    df_freq_hidrometros.rename(
        columns={
            "diametro": "diametro",
            "count": "freq_absoluta",
            "%": "freq_relativa",
        },
        inplace=True,
    )

    freq_hidrometros: list[dict] = df_freq_hidrometros.to_dict("records")
    return freq_hidrometros


def calcular_freq_prefil_imoveis(df) -> list[dict[str, int | float | str]]:
    contagem_perfil_imoveis = df.perfil_imovel.value_counts()
    df_freq_perfil_imoveis = contagem_perfil_imoveis.to_frame()
    df_freq_perfil_imoveis["%"] = (
        contagem_perfil_imoveis * 100 / contagem_perfil_imoveis.sum()
    )
    df_freq_perfil_imoveis["%"] = df_freq_perfil_imoveis["%"].apply(
        lambda x: round(x, 2)
    )
    df_freq_perfil_imoveis.reset_index(inplace=True)
    df_freq_perfil_imoveis.rename(
        columns={
            "perfil_imovel": "perfil_imovel",
            "count": "frequencia_absoluta",
            "%": "frequencia_relativa",
        },
        inplace=True,
    )

    freq_perfil_imoveis = df_freq_perfil_imoveis.to_dict(
        "records",
    )

    return freq_perfil_imoveis


def calcular_dados_necessarios_do_filtro(df: pd.DataFrame):
    valores_unicos_diametro = [int(x) for x in df.diametro.unique()]
    valores_unicos_diametro.sort()
    VALORES_DIAMETRO_FILTRO = [
        {"label": f"{x}MM", "value": int(x)} for x in valores_unicos_diametro
    ]

    valores_unicos_idade = list(df.idade_hidrometro.unique())
    VALOR_MINIMO_IDADE = min(valores_unicos_idade)
    VALOR_MAXIMO_IDADE = max(valores_unicos_idade)

    valores_unicos_situacao_agua = list(df.situacao_ligacao_agua.unique())
    opcoes_valores_situacao_agua = [
        {"label": v, "value": v} for v in sorted(valores_unicos_situacao_agua)
    ]

    valores_unicos_diametro_letra = list(df.diametro_letra.unique())
    opcoes_valores_diametro_letra = [
        {"label": v, "value": v} for v in sorted(valores_unicos_diametro_letra)
    ]

    valores_unicos_grupo_faturamento = list(df.grupo_leitura.unique())
    opcoes_valores_grupo_faturamento = [
        {"label": v, "value": v} for v in sorted(valores_unicos_grupo_faturamento)
    ]

    valores_unicos_perfil = list(df.perfil_imovel.unique())
    opcoes_perfil = [{"label": v, "value": v} for v in sorted(valores_unicos_perfil)]

    valores_unicos_categoria = list(df.categoria.unique())
    opcoes_categoria = [
        {"label": v, "value": v} for v in sorted(valores_unicos_categoria)
    ]

    valores_unicos_tipo_tarifa_esgoto = list(df.tipo_tarifa_esgoto.unique())
    opcoes_tipo_tarifa_esgoto = [
        {"label": v, "value": v} for v in sorted(valores_unicos_tipo_tarifa_esgoto)
    ]

    valores_unicos_anormalidade_leitura = list(
        pd.concat(
            [
                df[ColunasDataframe.ANORMALIDADE_LEITURA_MES_1],
                df[ColunasDataframe.ANORMALIDADE_LEITURA_MES_2],
                df[ColunasDataframe.ANORMALIDADE_LEITURA_MES_3],
            ]
        ).unique()
    )
    opcoes_anormalidade_leitura = [
        {"label": v, "value": v} for v in sorted(valores_unicos_anormalidade_leitura)
    ]

    valores_unicos_anormalidade_consumo = list(
        pd.concat(
            [
                df[ColunasDataframe.ANORMALIDADE_CONSUMO_MES_1],
                df[ColunasDataframe.ANORMALIDADE_CONSUMO_MES_2],
                df[ColunasDataframe.ANORMALIDADE_CONSUMO_MES_3],
            ]
        ).unique()
    )
    opcoes_anormalidade_consumo = [
        {"label": v, "value": v} for v in sorted(valores_unicos_anormalidade_consumo)
    ]

    return {
        "opcoes_valores_diametro_filtro": VALORES_DIAMETRO_FILTRO,
        "valores_unicos_diametro": valores_unicos_diametro,
        "valor_minimo_idade": VALOR_MINIMO_IDADE,
        "valor_maximo_idade": VALOR_MAXIMO_IDADE,
        "opcoes_valores_situacao_ligacao_agua": opcoes_valores_situacao_agua,
        "opcoes_selecionadas_situacao_ligacao_agua": valores_unicos_situacao_agua,
        "valores_unicos_diametro_letra": valores_unicos_diametro_letra,
        "opcoes_valores_diametro_letra": opcoes_valores_diametro_letra,
        "opcoes_valores_grupo_faturamento": opcoes_valores_grupo_faturamento,
        "valores_unicos_grupo_faturamento": valores_unicos_grupo_faturamento,
        "opcoes_valores_perfil_imovel": opcoes_perfil,
        "valores_unicos_perfil_imovel": valores_unicos_perfil,
        "opcoes_valores_categoria": opcoes_categoria,
        "valores_unicos_categoria": valores_unicos_categoria,
        "opcoes_valores_tipo_tarifa_esgoto": opcoes_tipo_tarifa_esgoto,
        "valores_unicos_tipo_tarifa_esgoto": valores_unicos_tipo_tarifa_esgoto,
        "opcoes_valores_anormalidade_leitura": opcoes_anormalidade_leitura,
        "valores_unicos_anormalidade_leitura": valores_unicos_anormalidade_leitura,
        "opcoes_valores_anormalidade_consumo": opcoes_anormalidade_consumo,
        "valores_unicos_anormalidade_consumo": valores_unicos_anormalidade_consumo,
    }


def calcular_todos_os_dados_necessarios(df: pd.DataFrame):
    contagem_hidrometros = df.hidrometro.count()

    porcentagem_hidrometros_ligados = calcular_porcentagem_hidrometros_ligados(df)

    idade_media_hidrometros = float(df.idade_hidrometro.mean())

    idade_media_20MM, idade_desvio_padrao_20MM, grafico_idades_hidrometros_20MM = (
        calcular_dados_hidrometros_segundo_diametro(df, "20")
    )

    idade_media_25MM, idade_desvio_padrao_25MM, grafico_idades_hidrometros_25MM = (
        calcular_dados_hidrometros_segundo_diametro(df, "25")
    )

    (
        idade_media_acima_25MM,
        idade_desvio_padrao_acima_25MM,
        grafico_idades_hidrometros_acima_de_25MM,
    ) = calcular_dados_hidrometros_segundo_diametro(df, "25+")

    freq_perfil_imoveis = calcular_freq_prefil_imoveis(df)

    freq_hidrometros = calcular_freq_hidrometros_por_diametro(df)

    media_do_consumo_medio_mes_1 = df.media_consumo_mes_1.mean()
    media_do_consumo_medio_mes_2 = df.media_consumo_mes_2.mean()
    media_do_consumo_medio_mes_3 = df.media_consumo_mes_3.mean()

    desvio_padrao_consumo_medio_mes_1 = df.media_consumo_mes_1.std()
    desvio_padrao_consumo_medio_mes_2 = df.media_consumo_mes_2.std()
    desvio_padrao_consumo_medio_mes_3 = df.media_consumo_mes_3.std()

    frequencia_consumo_acima_limite_mes_1 = df.media_consumo_mes_1[
        df.media_consumo_mes_1 > 130
    ].count()
    frequencia_consumo_acima_limite_mes_2 = df.media_consumo_mes_2[
        df.media_consumo_mes_2 > 130
    ].count()
    frequencia_consumo_acima_limite_mes_3 = df.media_consumo_mes_3[
        df.media_consumo_mes_3 > 130
    ].count()

    (
        frequencia_consumos_medios_mes_1,
        frequencia_consumos_medios_mes_2,
        frequencia_consumos_medios_mes_3,
    ) = calcular_frequencia_consumos_medios(df, 130)

    (
        anormalidade_leitura_mes_1,
        anormalidade_leitura_mes_2,
        anormalidade_leitura_mes_3,
    ) = calcular_frequencia_anormalidade_leitura(df)

    (
        frequencia_consumos_medidos_mes_1,
        frequencia_consumos_medidos_mes_2,
        frequencia_consumos_medidos_mes_3,
    ) = calcular_frequencia_consumo_medido(df, 130)

    (
        frequencia_consumo_faturado_mes_1,
        frequencia_consumo_faturado_mes_2,
        frequencia_consumo_faturado_mes_3,
    ) = calcular_frequencia_consumo_faturado(df, 130)

    (
        frequencia_anormalidade_consumo_1,
        frequencia_anormalidade_consumo_2,
        frequencia_anormalidade_consumo_3,
    ) = calcular_frequencia_anormalidade_consumo(df)

    frequencia_divida_total_vencida = calcular_frequencia_total_divida_vencida(df)
    frequencia_contas_vencidas_aberto = calcular_frequencia_contas_vencidas_aberto(df)

    ramais_com_consumo_maior_ou_menor_que_o_esperado = (
        df.loc[
            df[ColunasDataframe.CONSUMO_MAX_MES_1].isin(["Maior", "Menor"]),
            [
                ColunasDataframe.RAMAL,
                ColunasDataframe.DIAMETRO_LETRA,
                ColunasDataframe.CONSUMO_MAX_MES_1,
                ColunasDataframe.MEDIA_CONSUMO_MES_1,
            ],
        ],
        df.loc[
            df[ColunasDataframe.CONSUMO_MAX_MES_2].isin(["Maior", "Menor"]),
            [
                ColunasDataframe.RAMAL,
                ColunasDataframe.DIAMETRO_LETRA,
                ColunasDataframe.CONSUMO_MAX_MES_2,
                ColunasDataframe.MEDIA_CONSUMO_MES_2,
            ],
        ],
        df.loc[
            df[ColunasDataframe.CONSUMO_MAX_MES_3].isin(["Maior", "Menor"]),
            [
                ColunasDataframe.RAMAL,
                ColunasDataframe.DIAMETRO_LETRA,
                ColunasDataframe.CONSUMO_MAX_MES_3,
                ColunasDataframe.MEDIA_CONSUMO_MES_3,
            ],
        ],
    )

    return {
        "df": df,
        "contagem_hidrometros": contagem_hidrometros,
        "porcentagem_hidrometros_ligados": porcentagem_hidrometros_ligados,
        "idade_media_hidrometros": idade_media_hidrometros,
        "idade_media_20MM": idade_media_20MM,
        "idade_desvio_padrao_20MM": idade_desvio_padrao_20MM,
        "grafico_idades_hidrometros_20MM": grafico_idades_hidrometros_20MM,
        "idade_media_25MM": idade_media_25MM,
        "idade_desvio_padrao_25MM": idade_desvio_padrao_25MM,
        "grafico_idades_hidrometros_25MM": grafico_idades_hidrometros_25MM,
        "idade_media_acima_25MM": idade_media_acima_25MM,
        "idade_desvio_padrao_acima_25MM": idade_desvio_padrao_acima_25MM,
        "grafico_idades_hidrometros_acima_de_25MM": grafico_idades_hidrometros_acima_de_25MM,
        "freq_perfil_imoveis": freq_perfil_imoveis,
        "freq_hidrometros": freq_hidrometros,
        "media_do_consumo_medio_mes_1": media_do_consumo_medio_mes_1,
        "media_do_consumo_medio_mes_2": media_do_consumo_medio_mes_2,
        "media_do_consumo_medio_mes_3": media_do_consumo_medio_mes_3,
        "desvio_padrao_consumo_medio_mes_1": desvio_padrao_consumo_medio_mes_1,
        "desvio_padrao_consumo_medio_mes_2": desvio_padrao_consumo_medio_mes_2,
        "desvio_padrao_consumo_medio_mes_3": desvio_padrao_consumo_medio_mes_3,
        "frequencia_consumo_acima_limite_mes_1": frequencia_consumo_acima_limite_mes_1,
        "frequencia_consumo_acima_limite_mes_2": frequencia_consumo_acima_limite_mes_2,
        "frequencia_consumo_acima_limite_mes_3": frequencia_consumo_acima_limite_mes_3,
        "frequencia_consumos_medios_mes_1": frequencia_consumos_medios_mes_1,
        "frequencia_consumos_medios_mes_2": frequencia_consumos_medios_mes_2,
        "frequencia_consumos_medios_mes_3": frequencia_consumos_medios_mes_3,
        "anormalidade_leitura_mes_1": anormalidade_leitura_mes_1,
        "anormalidade_leitura_mes_2": anormalidade_leitura_mes_2,
        "anormalidade_leitura_mes_3": anormalidade_leitura_mes_3,
        "frequencia_consumos_medidos_mes_1": frequencia_consumos_medidos_mes_1,
        "frequencia_consumos_medidos_mes_2": frequencia_consumos_medidos_mes_2,
        "frequencia_consumos_medidos_mes_3": frequencia_consumos_medidos_mes_3,
        "frequencia_consumo_faturado_mes_1": frequencia_consumo_faturado_mes_1,
        "frequencia_consumo_faturado_mes_2": frequencia_consumo_faturado_mes_2,
        "frequencia_consumo_faturado_mes_3": frequencia_consumo_faturado_mes_3,
        "frequencia_anormalidade_consumo_1": frequencia_anormalidade_consumo_1,
        "frequencia_anormalidade_consumo_2": frequencia_anormalidade_consumo_2,
        "frequencia_anormalidade_consumo_3": frequencia_anormalidade_consumo_3,
        "frequencia_contas_vencidas_aberto": frequencia_contas_vencidas_aberto,
        "ramais_com_consumo_maior_ou_menor_que_o_esperado": ramais_com_consumo_maior_ou_menor_que_o_esperado,
        "frequencia_divida_total_vencida": frequencia_divida_total_vencida,
    }


def calcular_frequencia_consumos_medios(
    df: pd.DataFrame, valor_concatenar: int
) -> tuple[dict[str, int], dict[str, int], dict[str, int]]:
    resultados: list[dict[str, int]] = []
    for col in (
        ColunasDataframe.MEDIA_CONSUMO_MES_1,
        ColunasDataframe.MEDIA_CONSUMO_MES_2,
        ColunasDataframe.MEDIA_CONSUMO_MES_3,
    ):
        consumos = df[col][df[col] <= valor_concatenar]
        freq_consumos = consumos.groupby(consumos).count()

        frequencia = {str(k): v for k, v in freq_consumos.to_dict().items()}
        frequencia[f"{valor_concatenar}+"] = df[col][df[col] > valor_concatenar].count()

        resultados.append(frequencia)

    return resultados[0], resultados[1], resultados[2]


def calcular_frequencia_anormalidade_leitura(df: pd.DataFrame):
    resultados = []
    for col in (
        ColunasDataframe.ANORMALIDADE_LEITURA_MES_1,
        ColunasDataframe.ANORMALIDADE_LEITURA_MES_2,
        ColunasDataframe.ANORMALIDADE_LEITURA_MES_3,
    ):
        if (df[col] == SENTINELA_NAO_ASSOCIADA).all():
            resultados.append(None)
            continue

        contagem = df.groupby(col)[[col]].count()
        contagem.columns = ["Frequência Absoluta"]
        contagem["Frequência Relativa (%)"] = (
            contagem["Frequência Absoluta"] * 100 / len(df)
        ).round(2)
        contagem.reset_index(inplace=True)

        contagem.columns = [
            "Anormalidade",
            "Frequência Absoluta",
            "Frequência Relativa (%)",
        ]

        resultados.append(contagem)

    return resultados[0], resultados[1], resultados[2]


def calcular_frequencia_consumo_medido(
    df: pd.DataFrame, valor_concatenar: int = 130
) -> tuple[dict[str, int], dict[str, int], dict[str, int]]:
    resultados = []
    for col in (
        ColunasDataframe.CONSUMO_MEDIDO_MES_1,
        ColunasDataframe.CONSUMO_MEDIDO_MES_2,
        ColunasDataframe.CONSUMO_MEDIDO_MES_3,
    ):
        if col not in df.columns:
            resultados.append(None)
            continue

        consumos_medidos = df[col][df[col] <= valor_concatenar]
        freq_consumos_medidos = consumos_medidos.groupby(consumos_medidos).count()

        frequencia = {str(k): v for k, v in freq_consumos_medidos.to_dict().items()}
        frequencia[f"{valor_concatenar}+"] = df[col][df[col] > valor_concatenar].count()

        resultados.append(frequencia)

    return resultados[0], resultados[1], resultados[2]


def calcular_frequencia_consumo_faturado(
    df: pd.DataFrame, valor_concatenar: int = 130
) -> tuple[dict[str, int], dict[str, int], dict[str, int]]:
    resultados: list[dict[str, int] | None] = []
    for col in (
        ColunasDataframe.CONSUMO_FATURADO_MES_1,
        ColunasDataframe.CONSUMO_FATURADO_MES_2,
        ColunasDataframe.CONSUMO_FATURADO_MES_3,
    ):
        if col not in df.columns:
            resultados.append(None)
            continue

        dados_sem_na = df[df[col].notna()]

        consumo_faturado = dados_sem_na[col][dados_sem_na[col] <= valor_concatenar]
        consumo_faturado = consumo_faturado.astype("Int64")
        freq_consumo_faturado = consumo_faturado.groupby(consumo_faturado).count()

        freq_consumo_faturado_concatenado = dados_sem_na[col][
            dados_sem_na[col] > valor_concatenar
        ].count()

        frequencia = {str(k): v for k, v in freq_consumo_faturado.to_dict().items()}

        frequencia[f"{valor_concatenar}+"] = freq_consumo_faturado_concatenado

        resultados.append(frequencia)

    return resultados[0], resultados[1], resultados[2]


def calcular_frequencia_anormalidade_consumo(df: pd.DataFrame):
    resultados = []
    for col in (
        ColunasDataframe.ANORMALIDADE_CONSUMO_MES_1,
        ColunasDataframe.ANORMALIDADE_CONSUMO_MES_2,
        ColunasDataframe.ANORMALIDADE_CONSUMO_MES_3,
    ):
        if (df[col] == SENTINELA_NAO_ASSOCIADA).all():
            resultados.append(None)
            continue

        contagem = df.groupby(col)[[col]].count()
        contagem.columns = ["Frequência Absoluta"]
        contagem["Frequência Relativa (%)"] = (
            contagem["Frequência Absoluta"] * 100 / len(df)
        ).round(2)
        contagem.reset_index(inplace=True)

        contagem.columns = [
            "Anormalidade",
            "Frequência Absoluta",
            "Frequência Relativa (%)",
        ]

        resultados.append(contagem)

    return resultados[0], resultados[1], resultados[2]


def calcular_frequencia_contas_vencidas_aberto(
    df: pd.DataFrame, valor_concatenar: int = 130
) -> dict[str, float] | None:
    col = ColunasDataframe.CONTAS_VENCIDAS_ABERTO
    if col not in df.columns:
        return None

    registros_com_valor_menor_igual_a_concatenacao = df[df[col] <= valor_concatenar]
    frequencia = registros_com_valor_menor_igual_a_concatenacao.groupby(col)[
        [col]
    ].count()
    frequencia.columns = ["freq_abs"]

    freq_registros_a_concatenar = df[col][df[col] > valor_concatenar].count()
    frequencia.loc[f"{valor_concatenar}+", "freq_abs"] = freq_registros_a_concatenar

    total = len(df)

    frequencia["freq_rel"] = frequencia["freq_abs"] * 100 / total

    resultado: dict[str, float] = {
        str(k): v for k, v in frequencia["freq_rel"].to_dict().items()
    }

    return resultado


def calcular_frequencia_total_divida_vencida(
    df: pd.DataFrame, valor_concatenar: int = 130
) -> dict[str, float] | None:
    col = ColunasDataframe.DIVIDA_TOTAL_VENCIDA
    if col not in df.columns:
        return None

    sem_valores_na = df[df[col].notna()]

    registros_com_valor_menor_igual_a_concatenacao = sem_valores_na[
        sem_valores_na[col] <= valor_concatenar
    ]
    frequencia = registros_com_valor_menor_igual_a_concatenacao.groupby(col)[
        [col]
    ].count()
    frequencia.columns = ["freq_abs"]

    freq_registros_a_concatenar = sem_valores_na[col][
        sem_valores_na[col] > valor_concatenar
    ].count()
    frequencia.loc[f"{valor_concatenar}+", "freq_abs"] = freq_registros_a_concatenar

    total = len(sem_valores_na)

    frequencia["freq_rel"] = frequencia["freq_abs"] * 100 / total

    resultado: dict[str, float] = {
        str(k): v for k, v in frequencia["freq_rel"].to_dict().items()
    }

    return resultado
