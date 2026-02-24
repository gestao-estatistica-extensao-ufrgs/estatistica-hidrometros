import base64
import io
from typing import Literal

import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, callback, Output, Input, State

from elementos_html import (
    gerar_form_colunas,
    gerar_html_dados,
    gerar_html_filtros,
    gerar_html_zero_resultados,
    ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS,
    ID_ELEMENTOS_HTML,
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


# -------------------------------------------------------------
#########################
### INICIALIZAÇÃO APP ###
#########################
DF = pd.DataFrame()
app = Dash(suppress_callback_exceptions=True)

app.layout = [
    html.Section(
        [
            html.Div(
                [
                    html.H2("Abrir Planilha"),
                    dcc.Upload(
                        children=[html.Button("Abrir")],
                        id=ID_ELEMENTOS_HTML.UPLOAD_TABELA,
                    ),
                    dcc.Input(
                        "", readOnly=True, id=ID_ELEMENTOS_HTML.UPLOAD_NOME_ARQUIVO
                    ),
                    html.Div(id=ID_ELEMENTOS_HTML.UPLOAD_TABELA_ERRO, children=""),
                ]
            ),
            gerar_form_colunas(),
        ]
    ),
    html.Hr(),
    html.Section(
        id=ID_ELEMENTOS_HTML.FILTROS,
    ),
    html.Hr(),
    html.Section(
        [],
        id=ID_ELEMENTOS_HTML.SECAO_RESULTADOS,
    ),
]

# -------------------------------------------------------------
#################
### CALLBACKS ###
#################


@callback(
    Output(ID_ELEMENTOS_HTML.UPLOAD_NOME_ARQUIVO, "value"),
    Output(ID_ELEMENTOS_HTML.BOTAO_ASSOCIAR_COLUNAS, "disabled"),
    Output(
        ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS["hidrometro"], "options"
    ),
    Output(ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS["diametro"], "options"),
    Output(
        ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS["data_instalacao"],
        "options",
    ),
    Output(
        ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS["grupo_leitura"], "options"
    ),
    Output(
        ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS["situacao_ligacao_agua"],
        "options",
    ),
    Output(
        ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS["perfil_imovel"],
        "options",
        allow_duplicate=True,
    ),
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
            False,
            opcoes,
            opcoes,
            opcoes,
            opcoes,
            opcoes,
            opcoes,
            "",
            [],
            [],
        )

    return (
        nome_arquivo,
        True,
        [],
        [],
        [],
        [],
        [],
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
    prevent_initial_call=True,
)
def filtrar(
    n_clicks: int,
    limites_diametros: list[int],
    limites_idade: list[int],
    situacoes: list[str],
):
    global DF
    filtrado = DF[
        (DF.diametro.isin(limites_diametros))
        & (DF.idade_hidrometro.between(limites_idade[0], limites_idade[1]))
        & (DF.situacao_ligacao_agua.isin(situacoes))
    ]

    if filtrado.empty:
        return gerar_html_zero_resultados()

    contagem_hidrometros = filtrado.hidrometro.count()

    porcentagem_hidrometros_ligados = calcular_porcentagem_hidrometros_ligados(filtrado)

    idade_media_hidrometros = filtrado.idade_hidrometro.mean()

    idade_media_20MM, idade_desvio_padrao_20MM, grafico_idades_hidrometros_20MM = (
        calcular_dados_hidrometros_segundo_diametro(filtrado, "20")
    )

    idade_media_25MM, idade_desvio_padrao_25MM, grafico_idades_hidrometros_25MM = (
        calcular_dados_hidrometros_segundo_diametro(filtrado, "25")
    )

    (
        idade_media_acima_25MM,
        idade_desvio_padrao_acima_25MM,
        grafico_idades_hidrometros_acima_de_25MM,
    ) = calcular_dados_hidrometros_segundo_diametro(filtrado, "25+")

    freq_perfil_imoveis = calcular_freq_prefil_imoveis(filtrado)

    freq_hidrometros = calcular_freq_hidrometros_por_diametro(filtrado)

    dados_html = gerar_html_dados(
        filtrado,
        contagem_hidrometros,
        porcentagem_hidrometros_ligados,
        idade_media_hidrometros,
        idade_media_20MM,
        idade_desvio_padrao_20MM,
        grafico_idades_hidrometros_20MM,
        idade_media_25MM,
        idade_desvio_padrao_25MM,
        grafico_idades_hidrometros_25MM,
        idade_media_acima_25MM,
        idade_desvio_padrao_acima_25MM,
        grafico_idades_hidrometros_acima_de_25MM,
        freq_perfil_imoveis,
        freq_hidrometros,
    )

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
):
    colunas_associadas_de_cada_variavel: dict[NOME_VARIAVEIS, str] = {
        "hidrometro": hidrometro,
        "situacao_ligacao_agua": situacao_ligacao_agua,
        "diametro": diametro,
        "data_instalacao": data_instalacao,
        "grupo_leitura": grupo_leitura,
        "perfil_imovel": perfil_imovel,
    }

    teste_se_todos_valores_sao_nao_nulos = all(
        map(lambda x: x is not None, colunas_associadas_de_cada_variavel.values())
    )

    if teste_se_todos_valores_sao_nao_nulos:
        global DF
        preparacao_dados(DF, colunas_associadas_de_cada_variavel)

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

        return (
            gerar_html_filtros(
                VALORES_DIAMETRO_FILTRO,
                valores_unicos_diametro,
                VALOR_MINIMO_IDADE,
                VALOR_MAXIMO_IDADE,
                opcoes_valores_situacao_agua,
                valores_unicos_situacao_agua,
            ),
            "",
        )

    return [], "ERRO: Todas as variáveis devem estar associadas a uma coluna da tabela."


if __name__ == "__main__":
    app.run(debug=True)
