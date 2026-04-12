import base64
import io
from typing import Literal
import sys

import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, callback, Output, Input, State

from elementos_html import (
    gerar_form_colunas,
    gerar_html_dados,
    gerar_html_dados_consumo_mes,
    gerar_html_filtros,
    gerar_html_zero_resultados,
    ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS,
    ID_ELEMENTOS_HTML,
    EstilosCSS,
    NOME_VARIAVEIS,
)


# -------------------------------------------------------------
########################
### PREPARAÇÃO DADOS ###
########################
def padronizacao_diametro(diametro: str):
    filtrado = filter(lambda caractere: caractere.isnumeric(), diametro)
    diametro_padronizado_texto = "".join(caractere for caractere in filtrado)
    diametro_padronizado_numero = int(diametro_padronizado_texto)
    return diametro_padronizado_numero


def diametro_e_letra_codigo(linha: pd.Series):
    codigo = linha["hidrometro"]
    if codigo is None:
        primeira_letra = "*"
    elif isinstance(codigo, int):
        primeira_letra = "*"
    elif (len(codigo) < 1) or (not codigo[0].isalpha):
        primeira_letra = "*"
    else:
        primeira_letra = codigo[0]

    return f"{linha["diametro"]} - {primeira_letra}"


def preparacao_dados(
    df: pd.DataFrame,
    relacao_colunas_tabela_inserida_com_dataframe: dict[NOME_VARIAVEIS, str],
):
    df["hidrometro"] = df[relacao_colunas_tabela_inserida_com_dataframe["hidrometro"]]

    df["situacao_ligacao_agua"] = df[
        relacao_colunas_tabela_inserida_com_dataframe["situacao_ligacao_agua"]
    ]

    df["diametro"] = df[
        relacao_colunas_tabela_inserida_com_dataframe["diametro"]
    ].apply(padronizacao_diametro)

    df["diametro_letra"] = df.apply(diametro_e_letra_codigo, axis=1)

    df["data_instalacao"] = df[
        relacao_colunas_tabela_inserida_com_dataframe["data_instalacao"]
    ]
    tempo_instalacao_ate_agora = pd.Timestamp.now() - df["data_instalacao"]
    df["idade_hidrometro"] = tempo_instalacao_ate_agora.apply(
        lambda x: int(round(x.days / 365, 0))
    )

    df["grupo_leitura"] = df[
        relacao_colunas_tabela_inserida_com_dataframe["grupo_leitura"]
    ]
    df["perfil_imovel"] = df[
        relacao_colunas_tabela_inserida_com_dataframe["perfil_imovel"]
    ]

    ### Colunas Consumo
    df["media_consumo_mes_1"] = df[
        relacao_colunas_tabela_inserida_com_dataframe["media_consumo_mes_1"]
    ]
    df["media_consumo_mes_2"] = df[
        relacao_colunas_tabela_inserida_com_dataframe["media_consumo_mes_2"]
    ]
    df["media_consumo_mes_3"] = df[
        relacao_colunas_tabela_inserida_com_dataframe["media_consumo_mes_3"]
    ]

    df["anormalidade_leitura_mes_1"] = df[
        relacao_colunas_tabela_inserida_com_dataframe["anormalidade_leitura_mes_1"]
    ]
    # TODO: Setting an item of incompatible dtype is deprecated and will raise an error in a future version of pandas. Value 'Sem Anormalidade' has dtype incompatible with float64, please explicitly cast to a compatible dtype first.
    df.loc[df["anormalidade_leitura_mes_1"].isna(), "anormalidade_leitura_mes_1"] = (
        "Sem Anormalidade"
    )
    df["anormalidade_leitura_mes_2"] = df[
        relacao_colunas_tabela_inserida_com_dataframe["anormalidade_leitura_mes_2"]
    ]
    df.loc[df["anormalidade_leitura_mes_2"].isna(), "anormalidade_leitura_mes_2"] = (
        "Sem Anormalidade"
    )
    df["anormalidade_leitura_mes_3"] = df[
        relacao_colunas_tabela_inserida_com_dataframe["anormalidade_leitura_mes_3"]
    ]
    df.loc[df["anormalidade_leitura_mes_3"].isna(), "anormalidade_leitura_mes_3"] = (
        "Sem Anormalidade"
    )

    df["consumo_medido_mes_1"] = df[
        relacao_colunas_tabela_inserida_com_dataframe["consumo_medido_mes_1"]
    ]
    df["consumo_medido_mes_2"] = df[
        relacao_colunas_tabela_inserida_com_dataframe["consumo_medido_mes_2"]
    ]
    df["consumo_medido_mes_3"] = df[
        relacao_colunas_tabela_inserida_com_dataframe["consumo_medido_mes_3"]
    ]

    df["consumo_faturado_mes_1"] = df[
        relacao_colunas_tabela_inserida_com_dataframe["consumo_faturado_mes_1"]
    ]
    df["consumo_faturado_mes_2"] = df[
        relacao_colunas_tabela_inserida_com_dataframe["consumo_faturado_mes_2"]
    ]
    df["consumo_faturado_mes_3"] = df[
        relacao_colunas_tabela_inserida_com_dataframe["consumo_faturado_mes_3"]
    ]

    df.drop(
        columns=relacao_colunas_tabela_inserida_com_dataframe.values(),
        inplace=True,
    )


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

    if not hidrometros.empty:
        idade_media = hidrometros.idade_hidrometro.mean()
        idade_desvio_padrao = hidrometros.idade_hidrometro.std()
        idade_media = f"{idade_media:.2f}"
        idade_desvio_padrao = f"{idade_desvio_padrao:.2f}"

        contagem_idades_hidrometros = hidrometros.idade_hidrometro.value_counts()

        titulo = f"Idade Hidrômetros de {diametro}MM"
        if diametro == "25+":
            titulo = f"Idade Hidrômetros acima de 25MM"

        grafico_idades_hidrometros = [
            dcc.Graph(
                figure=px.bar(
                    x=contagem_idades_hidrometros.index,
                    y=contagem_idades_hidrometros,
                    labels={"y": "Frequência", "x": "idade"},
                    title=titulo,
                )
            )
        ]

    else:
        idade_media = "-"
        idade_desvio_padrao = "-"
        grafico_idades_hidrometros = []

    return (idade_media, idade_desvio_padrao, grafico_idades_hidrometros)


def calcular_porcentagem_hidrometros_ligados(df: pd.DataFrame):
    apenas_ligados = df[df.situacao_ligacao_agua == "LIGADO"]

    contagem_hidrometros = df.hidrometro.count()

    if contagem_hidrometros > 0:
        porcentagem = (
            apenas_ligados.situacao_ligacao_agua.count() * 100 / contagem_hidrometros
        )
        return porcentagem

    return 0.0


def calcular_freq_hidrometros_por_diametro(df):
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
            "diametro": "Diâmetro",
            "count": "Frequência",
            "%": "Frequência Relativa (%)",
        },
        inplace=True,
    )

    freq_hidrometros = df_freq_hidrometros.to_dict("records")
    return freq_hidrometros


def calcular_freq_prefil_imoveis(df):
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
            "perfil_imovel": "Perfil Imóvel",
            "count": "Frequência",
            "%": "Frequência Relativa (%)",
        },
        inplace=True,
    )

    freq_perfil_imoveis = df_freq_perfil_imoveis.to_dict(
        "records",
    )

    return freq_perfil_imoveis


def calcular_dados_necessarios_do_filtro(df: pd.DataFrame):
    valores_unicos_diametro = [int(x) for x in DF.diametro.unique()]
    valores_unicos_diametro.sort()
    VALORES_DIAMETRO_FILTRO = [
        {"label": f"{x}MM", "value": int(x)} for x in valores_unicos_diametro
    ]

    valores_unicos_idade = list(DF.idade_hidrometro.unique())
    VALOR_MINIMO_IDADE = min(valores_unicos_idade)
    VALOR_MAXIMO_IDADE = max(valores_unicos_idade)

    valores_unicos_situacao_agua = list(DF.situacao_ligacao_agua.unique())
    opcoes_valores_situacao_agua = [
        {"label": v, "value": v} for v in sorted(valores_unicos_situacao_agua)
    ]

    valores_unicos_diametro_letra = list(DF.diametro_letra.unique())
    opcoes_valores_diametro_letra = [
        {"label": v, "value": v} for v in sorted(valores_unicos_diametro_letra)
    ]

    valores_unicos_grupo_faturamento = list(DF.grupo_leitura.unique())
    opcoes_valores_grupo_faturamento = [
        {"label": v, "value": v} for v in sorted(valores_unicos_grupo_faturamento)
    ]

    valores_unicos_perfil = list(df.perfil_imovel.unique())
    opcoes_perfil = [{"label": v, "value": v} for v in sorted(valores_unicos_perfil)]

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
    }


def calcular_todos_os_dados_necessarios(df: pd.DataFrame):
    contagem_hidrometros = df.hidrometro.count()

    porcentagem_hidrometros_ligados = calcular_porcentagem_hidrometros_ligados(df)

    idade_media_hidrometros = df.idade_hidrometro.mean()

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
    }


def calcular_frequencia_consumos_medios(df: pd.DataFrame, valor_concatenar: int):
    resultados = []
    for col in (
        "media_consumo_mes_1",
        "media_consumo_mes_2",
        "media_consumo_mes_3",
    ):
        consumos = df[col][df[col] <= valor_concatenar]
        freq_consumos = consumos.groupby(consumos).count()

        freq_consumos_concatenados = df[col][df[col] > valor_concatenar].count()

        freq_consumos.loc[f"{valor_concatenar}+"] = freq_consumos_concatenados

        resultados.append(freq_consumos)

    return resultados[0], resultados[1], resultados[2]


def calcular_frequencia_anormalidade_leitura(df: pd.DataFrame):
    resultados = []
    for col in (
        "anormalidade_leitura_mes_1",
        "anormalidade_leitura_mes_2",
        "anormalidade_leitura_mes_3",
    ):
        contagem = df.groupby(col)[[col]].count()
        contagem.columns = ["Frequência Absoluta"]
        contagem["Frequência Relativa (%)"] = (
            contagem["Frequência Absoluta"] * 100 / len(df)
        )
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
) -> tuple[pd.Series, pd.Series, pd.Series]:
    resultados = []
    for col in ("consumo_medido_mes_1", "consumo_medido_mes_2", "consumo_medido_mes_3"):
        consumos_medidos = df[col][df[col] <= valor_concatenar]
        freq_consumos_medidos = consumos_medidos.groupby(consumos_medidos).count()

        freq_consumos_medidos_concatenados = df[col][df[col] > valor_concatenar].count()

        freq_consumos_medidos.loc[f"{valor_concatenar}+"] = (
            freq_consumos_medidos_concatenados
        )

        resultados.append(freq_consumos_medidos)

    return resultados[0], resultados[1], resultados[2]


def calcular_frequencia_consumo_faturado(
    df: pd.DataFrame, valor_concatenar: int = 130
) -> tuple[pd.Series, pd.Series, pd.Series]:
    resultados = []
    for col in (
        "consumo_faturado_mes_1",
        "consumo_faturado_mes_2",
        "consumo_faturado_mes_3",
    ):
        consumo_faturado = df[col][df[col] <= valor_concatenar]
        freq_consumo_faturado = consumo_faturado.groupby(consumo_faturado).count()

        freq_consumo_faturado_concatenado = df[col][df[col] > valor_concatenar].count()

        freq_consumo_faturado.loc[f"{valor_concatenar}+"] = (
            freq_consumo_faturado_concatenado
        )

        resultados.append(freq_consumo_faturado)

    return resultados[0], resultados[1], resultados[2]


# -------------------------------------------------------------
#########################
### INICIALIZAÇÃO APP ###
#########################
DF = pd.DataFrame()
filtro_html = []
dados_html = []
if len(sys.argv) > 1:
    DF = pd.read_excel("testes/dados_teste/amostra_dados.xlsx")
    colunas_x_variaveis: dict[NOME_VARIAVEIS, str] = {
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
    }
    preparacao_dados(DF, colunas_x_variaveis)

    filtro_html = gerar_html_filtros(**calcular_dados_necessarios_do_filtro(DF))
    dados_html = gerar_html_dados(**calcular_todos_os_dados_necessarios(DF))

app = Dash(suppress_callback_exceptions=True)

app.layout = [
    html.Div(
        id=ID_ELEMENTOS_HTML.LAYOUT,
        children=[
            html.Section(
                id=ID_ELEMENTOS_HTML.AREA_UPLOAD_TABELA,
                style={"display": "flex", "flexDirection": "column", "gap": "5px"},
                children=[
                    html.Div(
                        style={
                            "display": "flex",
                            "flexDirection": "column",
                            "gap": "2px",
                        },
                        children=[
                            html.H2("Abrir Planilha"),
                            dcc.Upload(
                                id=ID_ELEMENTOS_HTML.UPLOAD_TABELA,
                                style={"display": "flex"},
                                children=[
                                    html.Button("Abrir"),
                                    dcc.Input(
                                        "",
                                        id=ID_ELEMENTOS_HTML.UPLOAD_NOME_ARQUIVO,
                                        readOnly=True,
                                        style={"flexGrow": "1"},
                                    ),
                                ],
                            ),
                            html.Div(
                                id=ID_ELEMENTOS_HTML.UPLOAD_TABELA_ERRO, children=""
                            ),
                        ],
                    ),
                    html.Div(
                        id=ID_ELEMENTOS_HTML.AREA_ASSOCIACAO_COLUNAS,
                        children=[],
                    ),
                ],
            ),
            html.Section(id=ID_ELEMENTOS_HTML.FILTROS, children=filtro_html),
            html.Section(
                id=ID_ELEMENTOS_HTML.SECAO_RESULTADOS,
                children=dados_html,
            ),
        ],
    ),
]

# -------------------------------------------------------------
#################
### CALLBACKS ###
#################


@callback(
    Output(ID_ELEMENTOS_HTML.UPLOAD_NOME_ARQUIVO, "value"),
    Output(ID_ELEMENTOS_HTML.AREA_ASSOCIACAO_COLUNAS, "children"),
    Output(ID_ELEMENTOS_HTML.UPLOAD_TABELA_ERRO, "children"),
    Output(ID_ELEMENTOS_HTML.FILTROS, "children", allow_duplicate=True),
    Output(ID_ELEMENTOS_HTML.SECAO_RESULTADOS, "children"),
    Input(ID_ELEMENTOS_HTML.UPLOAD_TABELA, "contents"),
    State(ID_ELEMENTOS_HTML.UPLOAD_TABELA, "filename"),
    prevent_initial_call=True,
)
def liberar_associacao_de_colunas(conteudo: str, nome_arquivo: str):
    global DF
    DF = pd.DataFrame()

    if nome_arquivo[-4:] == "xlsx":
        _, con = conteudo.split(",")

        DF = pd.read_excel(io.BytesIO(base64.b64decode(con)))
        opcoes = list(DF.columns)
        return (
            nome_arquivo,
            gerar_form_colunas(opcoes, ""),
            "",
            [],
            [],
        )

    return (
        nome_arquivo,
        [],
        "Arquivo não está no formato '.xlsx' ",
        [],
        [],
    )


@callback(
    Output(ID_ELEMENTOS_HTML.SECAO_RESULTADOS, "children", allow_duplicate=True),
    Input(ID_ELEMENTOS_HTML.FILTRO_SUBMIT, "n_clicks"),
    State(ID_ELEMENTOS_HTML.FILTRO_DIAMETRO, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_IDADE, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_SITUACAO, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_DIAMETRO_LETRA, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_GRUPO_FATURAMENTO, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_PERFIL_IMOVEL, "value"),
    prevent_initial_call=True,
)
def filtrar(
    n_clicks: int,
    limites_diametros: list[int],
    limites_idade: list[int],
    situacoes: list[str],
    diametro_letra: list[str],
    grupo_faturamento: list[str],
    perfil_imovel_selecionados: list[str],
):
    global DF

    limites_diametros = limites_diametros or []
    situacoes = situacoes or []
    diametro_letra = diametro_letra or []
    grupo_faturamento = grupo_faturamento or []
    perfil_imovel_selecionados = perfil_imovel_selecionados or []

    filtrado = DF[
        (DF.diametro.isin(limites_diametros))
        & (DF.idade_hidrometro.between(limites_idade[0], limites_idade[1]))
        & (DF.situacao_ligacao_agua.isin(situacoes))
        & (DF.diametro_letra.isin(diametro_letra))
        & (DF.grupo_leitura.isin(grupo_faturamento))
        & (DF.perfil_imovel.isin(perfil_imovel_selecionados))
    ]

    if filtrado.empty:
        return gerar_html_zero_resultados()

    dados = calcular_todos_os_dados_necessarios(filtrado)
    dados_html = gerar_html_dados(**dados)

    return dados_html


@callback(
    Output(ID_ELEMENTOS_HTML.FILTROS, "children", allow_duplicate=True),
    Output(ID_ELEMENTOS_HTML.DROPDOWN_ASSOCIACAO_COLUNAS_ERRO, "children"),
    Input(ID_ELEMENTOS_HTML.BOTAO_ASSOCIAR_COLUNAS, "n_clicks"),
    State(ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS["hidrometro"], "value"),
    State(
        ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS["situacao_ligacao_agua"],
        "value",
    ),
    State(ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS["diametro"], "value"),
    State(
        ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS["data_instalacao"], "value"
    ),
    State(
        ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS["grupo_leitura"], "value"
    ),
    State(
        ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS["perfil_imovel"], "value"
    ),
    State(
        ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS["media_consumo_mes_1"],
        "value",
    ),
    State(
        ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS["media_consumo_mes_2"],
        "value",
    ),
    State(
        ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS["media_consumo_mes_3"],
        "value",
    ),
    State(
        ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS[
            "anormalidade_leitura_mes_1"
        ],
        "value",
    ),
    State(
        ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS[
            "anormalidade_leitura_mes_2"
        ],
        "value",
    ),
    State(
        ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS[
            "anormalidade_leitura_mes_3"
        ],
        "value",
    ),
    State(
        ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS["consumo_medido_mes_1"],
        "value",
    ),
    State(
        ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS["consumo_medido_mes_2"],
        "value",
    ),
    State(
        ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS["consumo_medido_mes_3"],
        "value",
    ),
    State(
        ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS["consumo_faturado_mes_1"],
        "value",
    ),
    State(
        ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS["consumo_faturado_mes_2"],
        "value",
    ),
    State(
        ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS["consumo_faturado_mes_3"],
        "value",
    ),
    prevent_initial_call=True,
)
def associar_colunas(
    n_clicks,
    hidrometro: str,
    situacao_ligacao_agua: str,
    diametro: str,
    data_instalacao: str,
    grupo_leitura: str,
    perfil_imovel: str,
    media_consumo_mes_1: str,
    media_consumo_mes_2: str,
    media_consumo_mes_3: str,
    anormalidade_leitura_mes_1: str,
    anormalidade_leitura_mes_2: str,
    anormalidade_leitura_mes_3: str,
    consumo_medido_mes_1: str,
    consumo_medido_mes_2: str,
    consumo_medido_mes_3: str,
    consumo_faturado_mes_1: str,
    consumo_faturado_mes_2: str,
    consumo_faturado_mes_3: str,
):
    if n_clicks is None:
        return [], ""

    colunas_associadas_de_cada_variavel: dict[NOME_VARIAVEIS, str] = {
        "hidrometro": hidrometro,
        "situacao_ligacao_agua": situacao_ligacao_agua,
        "diametro": diametro,
        "data_instalacao": data_instalacao,
        "grupo_leitura": grupo_leitura,
        "perfil_imovel": perfil_imovel,
        "media_consumo_mes_1": media_consumo_mes_1,
        "media_consumo_mes_2": media_consumo_mes_2,
        "media_consumo_mes_3": media_consumo_mes_3,
        "anormalidade_leitura_mes_1": anormalidade_leitura_mes_1,
        "anormalidade_leitura_mes_2": anormalidade_leitura_mes_2,
        "anormalidade_leitura_mes_3": anormalidade_leitura_mes_3,
        "consumo_medido_mes_1": consumo_medido_mes_1,
        "consumo_medido_mes_2": consumo_medido_mes_2,
        "consumo_medido_mes_3": consumo_medido_mes_3,
        "consumo_faturado_mes_1": consumo_faturado_mes_1,
        "consumo_faturado_mes_2": consumo_faturado_mes_2,
        "consumo_faturado_mes_3": consumo_faturado_mes_3,
    }

    teste_se_todos_valores_sao_nao_nulos = all(
        map(lambda x: x is not None, colunas_associadas_de_cada_variavel.values())
    )

    if teste_se_todos_valores_sao_nao_nulos:
        global DF
        preparacao_dados(DF, colunas_associadas_de_cada_variavel)

        dados = calcular_dados_necessarios_do_filtro(DF)

        return (
            gerar_html_filtros(**dados),
            "",
        )

    return [], "ERRO: Todas as variáveis devem estar associadas a uma coluna da tabela."


@callback(
    Output(ID_ELEMENTOS_HTML.DADOS_CONSUMO_MES_1, "style"),
    Output(ID_ELEMENTOS_HTML.DADOS_CONSUMO_MES_2, "style"),
    Output(ID_ELEMENTOS_HTML.DADOS_CONSUMO_MES_3, "style"),
    Input(ID_ELEMENTOS_HTML.ESCOLHA_ABA_DADOS_CONSUMO, "value"),
    prevent_initial_call=True,
)
def escolher_aba_consumo_mes(mes_referencia: str):
    if mes_referencia == "1":
        return (
            EstilosCSS.GRID_AREA_DADOS_CONSUMO,
            {"display": "none"},
            {"display": "none"},
        )
    elif mes_referencia == "2":
        return (
            {"display": "none"},
            EstilosCSS.GRID_AREA_DADOS_CONSUMO,
            {"display": "none"},
        )
    else:
        return (
            {"display": "none"},
            {"display": "none"},
            EstilosCSS.GRID_AREA_DADOS_CONSUMO,
        )


@callback(
    Output(ID_ELEMENTOS_HTML.AREA_DADOS_CONSUMO_MES, "children"),
    Input(ID_ELEMENTOS_HTML.BOTAO_CONCATENAR_CONSUMO, "n_clicks"),
    State(ID_ELEMENTOS_HTML.VALOR_LIMITE_CONCATENAR, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_DIAMETRO, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_IDADE, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_SITUACAO, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_DIAMETRO_LETRA, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_GRUPO_FATURAMENTO, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_PERFIL_IMOVEL, "value"),
    prevent_initial_call=True,
)
def concatenar_dados_consumo_mes(
    n_clicks,
    valor_limite: int,
    limites_diametros: list[int],
    limites_idade: list[int],
    situacoes: list[str],
    diametro_letra: list[str],
    grupo_faturamento: list[str],
    perfil_imovel_selecionados: list[str],
):
    global DF

    limites_diametros = limites_diametros or []
    situacoes = situacoes or []
    diametro_letra = diametro_letra or []
    grupo_faturamento = grupo_faturamento or []
    perfil_imovel_selecionados = perfil_imovel_selecionados or []

    filtrado = DF[
        (DF.diametro.isin(limites_diametros))
        & (DF.idade_hidrometro.between(limites_idade[0], limites_idade[1]))
        & (DF.situacao_ligacao_agua.isin(situacoes))
        & (DF.diametro_letra.isin(diametro_letra))
        & (DF.grupo_leitura.isin(grupo_faturamento))
        & (DF.perfil_imovel.isin(perfil_imovel_selecionados))
    ]

    media_do_consumo_medio_mes_1 = filtrado.media_consumo_mes_1.mean()
    media_do_consumo_medio_mes_2 = filtrado.media_consumo_mes_2.mean()
    media_do_consumo_medio_mes_3 = filtrado.media_consumo_mes_3.mean()

    desvio_padrao_consumo_medio_mes_1 = filtrado.media_consumo_mes_1.std()
    desvio_padrao_consumo_medio_mes_2 = filtrado.media_consumo_mes_2.std()
    desvio_padrao_consumo_medio_mes_3 = filtrado.media_consumo_mes_3.std()

    frequencia_consumo_acima_limite_mes_1 = filtrado.media_consumo_mes_1[
        filtrado.media_consumo_mes_1 > valor_limite
    ].count()
    frequencia_consumo_acima_limite_mes_2 = filtrado.media_consumo_mes_2[
        filtrado.media_consumo_mes_2 > valor_limite
    ].count()
    frequencia_consumo_acima_limite_mes_3 = filtrado.media_consumo_mes_3[
        filtrado.media_consumo_mes_3 > valor_limite
    ].count()

    (
        frequencia_consumos_medios_mes_1,
        frequencia_consumos_medios_mes_2,
        frequencia_consumos_medios_mes_3,
    ) = calcular_frequencia_consumos_medios(filtrado, valor_limite)

    (
        anormalidade_leitura_mes_1,
        anormalidade_leitura_mes_2,
        anormalidade_leitura_mes_3,
    ) = calcular_frequencia_anormalidade_leitura(filtrado)

    (
        frequencia_consumos_medidos_mes_1,
        frequencia_consumos_medidos_mes_2,
        frequencia_consumos_medidos_mes_3,
    ) = calcular_frequencia_consumo_medido(filtrado, valor_limite)

    (
        frequencia_consumo_faturado_mes_1,
        frequencia_consumo_faturado_mes_2,
        frequencia_consumo_faturado_mes_3,
    ) = calcular_frequencia_consumo_faturado(filtrado, valor_limite)

    return [
        gerar_html_dados_consumo_mes(
            media_do_consumo_medio_mes_1,
            desvio_padrao_consumo_medio_mes_1,
            frequencia_consumo_acima_limite_mes_1,
            frequencia_consumos_medios_mes_1,
            anormalidade_leitura_mes_1,
            frequencia_consumos_medidos_mes_1,
            frequencia_consumo_faturado_mes_1,
            "Mês 1",
            ID_ELEMENTOS_HTML.DADOS_CONSUMO_MES_1,
            limite_consumo_utilizado=valor_limite,
        ),
        gerar_html_dados_consumo_mes(
            media_do_consumo_medio_mes_2,
            desvio_padrao_consumo_medio_mes_2,
            frequencia_consumo_acima_limite_mes_2,
            frequencia_consumos_medios_mes_2,
            anormalidade_leitura_mes_2,
            frequencia_consumos_medidos_mes_2,
            frequencia_consumo_faturado_mes_2,
            "Mês 2",
            ID_ELEMENTOS_HTML.DADOS_CONSUMO_MES_2,
            oculto=True,
            limite_consumo_utilizado=valor_limite,
        ),
        gerar_html_dados_consumo_mes(
            media_do_consumo_medio_mes_3,
            desvio_padrao_consumo_medio_mes_3,
            frequencia_consumo_acima_limite_mes_3,
            frequencia_consumos_medios_mes_3,
            anormalidade_leitura_mes_3,
            frequencia_consumos_medidos_mes_3,
            frequencia_consumo_faturado_mes_3,
            "Mês 3",
            ID_ELEMENTOS_HTML.DADOS_CONSUMO_MES_3,
            oculto=True,
            limite_consumo_utilizado=valor_limite,
        ),
    ]


if __name__ == "__main__":
    app.run(debug=True)
