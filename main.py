import base64
import io

import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, html, dcc, callback, Output, Input, State
from dash.dash_table import DataTable


# Declarações
ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS = {
    "hidrometro": "associacao_col_hidrometro",
    "diametro": "associacao_col_diametro",
    "data_instalacao": "associacao_col_data_instalacao",
    "grupo_leitura": "associacao_col_grupo_leitura",
    "situacao_ligacao_agua": "associacao_col_situacao_ligacao_agua",
    "perfil_imovel": "associacao_col_perfil_imovel",
}


def padronizacao_diametro(diametro: str):
    filtrado = filter(lambda caractere: caractere.isnumeric(), diametro)
    diametro_padronizado_texto = "".join(caractere for caractere in filtrado)
    diametro_padronizado_numero = int(diametro_padronizado_texto)
    return diametro_padronizado_numero


def preparacao_dados(df: pd.DataFrame, relacao_colunas_tabela_inserida_com_dataframe):
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


def calcular_porcentagem_hidrometros_ligados(df: pd.DataFrame):
    apenas_ligados = df[df.situacao_ligacao_agua == "LIGADO"]

    contagem_hidrometros = df.hidrometro.count()

    if contagem_hidrometros > 0:
        porcentagem = (
            apenas_ligados.situacao_ligacao_agua.count() * 100 / contagem_hidrometros
        )
        return porcentagem

    return 0.0


# HTML
def gerar_form_colunas():
    def _label_e_dropdown(
        nome_label: str,
        coluna_necessaria: str,
    ):
        id_select = ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS[
            coluna_necessaria
        ]

        div_html = html.Div(
            children=[
                html.Label(children=nome_label, htmlFor=id_select),
                dcc.Dropdown(id=id_select, options=[]),
            ]
        )
        return div_html

    col_hidrometro = _label_e_dropdown("Hidrômetro", "hidrometro")
    col_diametro = _label_e_dropdown("Diâmetro", "diametro")
    col_data_instalacao = _label_e_dropdown("Data de Instalação", "data_instalacao")
    col_grupo_leitura = _label_e_dropdown("Grupo de Leitura", "grupo_leitura")
    col_situacao_ligacao_agua = _label_e_dropdown(
        "Situação Ligacao Água", "situacao_ligacao_agua"
    )
    col_perfil_imovel = _label_e_dropdown("Perfil do Imóvel", "perfil_imovel")

    return html.Form(
        [
            html.H3("Associar Colunas com Variáveis"),
            html.Div(
                id="dropdowns-associacao-colunas",
                children=[
                    html.Div(
                        children=[
                            col_hidrometro,
                            col_diametro,
                            col_data_instalacao,
                            col_grupo_leitura,
                            col_situacao_ligacao_agua,
                            col_perfil_imovel,
                        ]
                    ),
                    html.Div(
                        html.Button(
                            id="botao_associar_colunas",
                            type="button",
                            disabled=True,
                            children="Associar Colunas",
                        )
                    ),
                ],
            ),
            html.Div(id="dropdowns-associacao-colunas-erro"),
        ]
    )


def gerar_html_filtros(
    opcoes_valores_diametro_filtro,
    valores_unicos_diametro,
    valor_minimo_idade,
    valor_maximo_idade,
    opcoes_valores_situacao_ligacao_agua,
    opcoes_selecionadas_situacao_ligacao_agua,
):
    return [
        html.H2("Filtros"),
        html.Div(
            [
                html.Label("Diâmetro Hidrômetro", htmlFor="filtro-diametro"),
                dcc.Checklist(
                    options=opcoes_valores_diametro_filtro,
                    value=valores_unicos_diametro,
                    inline=True,
                    id="filtro-diametro",
                ),
            ]
        ),
        html.Div(
            [
                html.Label("Idade Hidrômetro", htmlFor="filtro-idade"),
                dcc.RangeSlider(
                    id="filtro-idade",
                    min=valor_minimo_idade,
                    max=valor_maximo_idade,
                    step=2,
                    value=[valor_minimo_idade, valor_maximo_idade],
                ),
            ]
        ),
        html.Div(
            [
                html.Label("Situação Ligação Água", htmlFor="filtro-situacao"),
                dcc.Checklist(
                    id="filtro-situacao",
                    options=opcoes_valores_situacao_ligacao_agua,
                    value=opcoes_selecionadas_situacao_ligacao_agua,
                    inline=True,
                ),
            ]
        ),
        html.Div(
            [
                html.Button(
                    "Filtrar",
                    id="filtro-submit",
                    type="button",
                ),
            ]
        ),
    ]


def gerar_html_area_dados(df: pd.DataFrame):
    if df.empty:
        return html.Div("0 Resultados")

    contagem_hidrometros = df.hidrometro.count()

    porcentagem_hidrometros_ligados = calcular_porcentagem_hidrometros_ligados(df)
    if porcentagem_hidrometros_ligados == 0.0:
        porcentagem_hidrometros_ligados = "-"
    else:
        porcentagem_hidrometros_ligados = f"{porcentagem_hidrometros_ligados:.2f}"

    idade_media_hidrometros = df.idade_hidrometro.mean()
    if idade_media_hidrometros is not np.nan:
        idade_media_hidrometros = f"{idade_media_hidrometros:.2f}"
    else:
        idade_media_hidrometros = "-"

    hidrometros_20MM = df[df.diametro == 20]
    if not hidrometros_20MM.empty:
        idade_media_20MM = hidrometros_20MM.idade_hidrometro.mean()
        idade_desvio_padrao_20MM = hidrometros_20MM.idade_hidrometro.std()
        idade_media_20MM = f"{idade_media_20MM:.2f}"
        idade_desvio_padrao_20MM = f"{idade_desvio_padrao_20MM:.2f}"

        contagem_idades_hidrometros_20MM = (
            hidrometros_20MM.idade_hidrometro.value_counts()
        )

        grafico_idades_hidrometros_20MM = [
            dcc.Graph(
                figure=px.bar(
                    x=contagem_idades_hidrometros_20MM.index,
                    y=contagem_idades_hidrometros_20MM,
                    labels={"y": "Frequência", "x": "idade"},
                    title="Idade Hidrômetros de 20MM",
                )
            )
        ]

    else:
        idade_media_20MM = "-"
        idade_desvio_padrao_20MM = "-"
        contagem_idades_hidrometros_20MM = pd.Series()
        grafico_idades_hidrometros_20MM = []

    hidrometros_25MM = df[df.diametro == 25]
    if not hidrometros_25MM.empty:
        idade_media_25MM = hidrometros_25MM.idade_hidrometro.mean()
        idade_desvio_padrao_25MM = hidrometros_25MM.idade_hidrometro.std()
        idade_media_25MM = f"{idade_media_25MM:.2f}"
        idade_desvio_padrao_25MM = f"{idade_desvio_padrao_25MM:.2f}"

        contagem_idades_hidrometros_25MM = (
            hidrometros_25MM.idade_hidrometro.value_counts()
        )

        grafico_idades_hidrometros_25MM = [
            dcc.Graph(
                figure=px.bar(
                    x=contagem_idades_hidrometros_25MM.index,
                    y=contagem_idades_hidrometros_25MM,
                    labels={"y": "Frequência", "x": "idade"},
                    title="Idade Hidrômetros de 25MM",
                )
            )
        ]

    else:
        idade_media_25MM = "-"
        idade_desvio_padrao_25MM = "-"
        contagem_idades_hidrometros_25MM = pd.Series()
        grafico_idades_hidrometros_25MM = []

    hidrometros_acima_25MM = df[df.diametro > 25]
    if not hidrometros_acima_25MM.empty:
        idade_media_acima_25MM = hidrometros_acima_25MM.idade_hidrometro.mean()
        idade_desvio_padrao_acima_25MM = hidrometros_acima_25MM.idade_hidrometro.std()
        idade_media_acima_25MM = f"{idade_media_acima_25MM:.2f}"
        idade_desvio_padrao_acima_25MM = f"{idade_desvio_padrao_acima_25MM:.2f}"

        contagem_idades_hidrometros_acima_25MM = (
            hidrometros_acima_25MM.idade_hidrometro.value_counts()
        )

        grafico_idades_hidrometros_acima_de_25MM = [
            dcc.Graph(
                figure=px.bar(
                    x=contagem_idades_hidrometros_acima_25MM.index,
                    y=contagem_idades_hidrometros_acima_25MM,
                    labels={"y": "Frequência", "x": "idade"},
                    title="Idade Hidrômetros acima de 25MM",
                )
            )
        ]

    else:
        idade_media_acima_25MM = "-"
        idade_desvio_padrao_acima_25MM = "-"
        contagem_idades_hidrometros_acima_25MM = pd.Series()
        grafico_idades_hidrometros_acima_de_25MM = []

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

    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        contagem_hidrometros,
                        id="contagem-hidrometros",
                        **{"data-dado": ""},
                    ),
                    html.Div("Nº Total de Hidrômetros"),
                ],
                className="quadro-dado",
            ),
            html.Div(
                [
                    html.Div(
                        porcentagem_hidrometros_ligados,
                        id="porcentagem-hidrometros-ligados",
                        **{"data-dado": ""},
                    ),
                    html.Div("Porcentagem de Hidrômetros Ligados"),
                ],
                className="quadro-dado",
            ),
            html.Div(
                [
                    html.Div(
                        idade_media_hidrometros,
                        id="idade-media-hidrometros",
                        **{"data-dado": ""},
                    ),
                    html.Div("Idade Média dos Hidrômetros"),
                ],
                className="quadro-dado",
            ),
            html.Div(
                [
                    dcc.Graph(
                        figure=px.histogram(
                            df,
                            x="idade_hidrometro",
                            nbins=30,  # quantidade de classes
                            labels={
                                "idade_hidrometro": "Idade do Hidrômetro (anos)",
                                "count": "Frequência",
                            },
                            opacity=0.75,
                        ).update_layout(
                            xaxis=dict(
                                tickmode="linear",
                                tick0=0,
                                dtick=2,  # um "tick" a cada 2 anos
                                title="Idade do Hidrômetro (anos)",
                            ),
                            yaxis=dict(
                                title="Frequência",
                            ),
                            bargap=0.05,
                        )
                    )
                ],
                className="grafico",
            ),
            html.Div(
                [
                    dcc.Graph(
                        figure=px.bar(
                            x=df["grupo_leitura"].value_counts().index,
                            y=df["grupo_leitura"].value_counts(),
                            labels={"y": "Frequência", "x": "Grupo de Faturamento"},
                            title="Gráfico de Frequência do Grupo de Faturamento",
                        )
                    )
                ],
                className="grafico",
            ),
            html.Div(
                [
                    html.H3(["Tabela de Frequência de Perfil de Imóvel"]),
                    DataTable(
                        df_freq_perfil_imoveis.to_dict(
                            "records",
                        ),
                        style_cell={"textAlign": "left", "border": "1px solid black"},
                        style_header={
                            "backgroundColor": "azure",
                            "font-weight": "bold",
                            "text-transform": "uppercase",
                        },
                    ),
                ],
                className="tabela",
            ),
            html.Div(
                [
                    html.H3(["Tabela de Frequência de Diâmetro em Hidrômetros"]),
                    DataTable(
                        df_freq_hidrometros.to_dict("records"),
                        style_cell={"textAlign": "left", "border": "1px solid black"},
                        style_header={
                            "backgroundColor": "azure",
                            "font-weight": "bold",
                            "text-transform": "uppercase",
                        },
                    ),
                ],
                className="tabela",
            ),
            html.Div(
                [
                    html.Div(
                        idade_media_20MM,
                        id="idade-media-hidrometros-20MM",
                        **{"data-dado": ""},
                    ),
                    html.Div("Idade Média dos Hidrômetros com 20MM"),
                ],
                className="quadro-dado",
            ),
            html.Div(
                [
                    html.Div(
                        idade_media_25MM,
                        id="idade-media-hidrometros-25MM",
                        **{"data-dado": ""},
                    ),
                    html.Div("Idade Média dos Hidrômetros com 25MM"),
                ],
                className="quadro-dado",
            ),
            html.Div(
                [
                    html.Div(
                        idade_media_acima_25MM,
                        id="idade-media-hidrometros-acima-25MM",
                        **{"data-dado": ""},
                    ),
                    html.Div("Idade Média dos Hidrômetros com mais de 25MM"),
                ],
                className="quadro-dado",
            ),
            html.Div(
                [
                    html.Div(
                        idade_desvio_padrao_20MM,
                        id="idade-desvio-padrao-hidrometros-com-20MM",
                        **{"data-dado": ""},
                    ),
                    html.Div("Desvio Padrão da Idade dos Hidrômetros com 20MM"),
                ],
                className="quadro-dado",
            ),
            html.Div(
                [
                    html.Div(
                        idade_desvio_padrao_25MM,
                        id="idade-desvio-padrao-hidrometros-com-25MM",
                        **{"data-dado": ""},
                    ),
                    html.Div("Desvio Padrão da Idade dos Hidrômetros com 25MM"),
                ],
                className="quadro-dado",
            ),
            html.Div(
                [
                    html.Div(
                        idade_desvio_padrao_acima_25MM,
                        id="idade-desvio-padrao-hidrometros-acima-25MM",
                        **{"data-dado": ""},
                    ),
                    html.Div("Desvio Padrão da Idade dos Hidrômetros com mais de 25MM"),
                ],
                className="quadro-dado",
            ),
            html.Div(
                grafico_idades_hidrometros_20MM,
                className="grafico",
            ),
            html.Div(
                grafico_idades_hidrometros_25MM,
                className="grafico",
            ),
            html.Div(
                grafico_idades_hidrometros_acima_de_25MM,
                className="grafico",
            ),
        ],
        id="area-dados",
    )


# Preparação Dados
DF = pd.DataFrame()

# Inicialização App
app = Dash(suppress_callback_exceptions=True)

app.layout = [
    html.Section(
        [
            html.Div(
                [
                    html.H2("Abrir Planilha"),
                    dcc.Upload(children=[html.Button("Abrir")], id="upload-tabela"),
                    dcc.Input("", readOnly=True, id="upload-nome-arquivo"),
                    html.Div(id="upload-tabela-erro", children=""),
                ]
            ),
            gerar_form_colunas(),
        ]
    ),
    html.Hr(),
    html.Section(
        id="filtros",
    ),
    html.Hr(),
    html.Section(
        [],
        id="secao-resultados",
    ),
]


@callback(
    Output("upload-nome-arquivo", "value"),
    Output("botao_associar_colunas", "disabled"),
    Output("associacao_col_hidrometro", "options"),
    Output("associacao_col_diametro", "options"),
    Output("associacao_col_data_instalacao", "options"),
    Output("associacao_col_grupo_leitura", "options"),
    Output("associacao_col_situacao_ligacao_agua", "options"),
    Output("associacao_col_perfil_imovel", "options", allow_duplicate=True),
    Output("upload-tabela-erro", "children"),
    Output("filtros", "children", allow_duplicate=True),
    Output("secao-resultados", "children"),
    Input("upload-tabela", "contents"),
    State("upload-tabela", "filename"),
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
    Output("secao-resultados", "children", allow_duplicate=True),
    Input("filtro-submit", "n_clicks"),
    State("filtro-diametro", "value"),
    State("filtro-idade", "value"),
    State("filtro-situacao", "value"),
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

    return gerar_html_area_dados(filtrado)


@callback(
    Output("filtros", "children", allow_duplicate=True),
    Output("dropdowns-associacao-colunas-erro", "children"),
    Input("botao_associar_colunas", "n_clicks"),
    State("associacao_col_hidrometro", "value"),
    State("associacao_col_situacao_ligacao_agua", "value"),
    State("associacao_col_diametro", "value"),
    State("associacao_col_data_instalacao", "value"),
    State("associacao_col_grupo_leitura", "value"),
    State("associacao_col_perfil_imovel", "value"),
    prevent_initial_call=True,
)
def associar_colunas(
    n_clicks,
    hidrometro,
    situacao_ligacao_agua,
    diametro,
    data_instalacao,
    grupo_leitura,
    perfil_imovel,
):
    colunas_associadas_de_cada_variavel = {
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
# teste commit github
