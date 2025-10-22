import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, html, dcc, callback, Output, Input, State
from dash.dash_table import DataTable


# Declarações
def padronizacao_diametro(diametro: str):
    filtrado = filter(lambda caractere: caractere.isnumeric(), diametro)
    diametro_padronizado_texto = "".join(caractere for caractere in filtrado)
    diametro_padronizado_numero = int(diametro_padronizado_texto)
    return diametro_padronizado_numero


def preparacao_dados(df: pd.DataFrame):
    df["hidrometro"] = df["Hidrometro"]

    df["situacao_ligacao_agua"] = df["Situacao Ligacao Agua"]

    df["diametro"] = df["Diametro"].apply(padronizacao_diametro)

    df["data_instalacao"] = df["Data Instalacao"]
    tempo_instalacao_ate_agora = pd.Timestamp.now() - df["data_instalacao"]
    df["idade_hidrometro"] = tempo_instalacao_ate_agora.apply(
        lambda x: int(round(x.days / 365, 0))
    )

    df["grupo_leitura"] = df["Grupo Leitura"]
    df["perfil_imovel"] = df["Perfil Imovel"]

    df.drop(
        columns=[
            "Diametro",
            "Situacao Ligacao Agua",
            "Hidrometro",
            "Idade Hidrometro",
            "Data Instalacao",
            "Grupo Leitura",
            "Perfil Imovel",
        ],
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

    idade_media_20MM = df[df.diametro == 20].idade_hidrometro.mean()
    if idade_media_20MM is not np.nan:
        idade_media_20MM = f"{idade_media_20MM:.2f}"
    else:
        idade_media_20MM = "-"

    idade_media_25MM = df[df.diametro == 25].idade_hidrometro.mean()
    if idade_media_25MM is not np.nan:
        idade_media_25MM = f"{idade_media_25MM:.2f}"
    else:
        idade_media_25MM = "-"

    idade_media_acima_25MM = df[df.diametro > 25].idade_hidrometro.mean()
    if idade_media_acima_25MM is not np.nan:
        idade_media_acima_25MM = f"{idade_media_acima_25MM:.2f}"
    else:
        idade_media_acima_25MM = "-"

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
                            nbins=10,
                            labels={
                                "idade_hidrometro": "Idade Hidrômetro",
                            },
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
        ],
        id="area-dados",
    )


# Preparação Dados
df = pd.read_excel(
    "testes/dados_teste/amostra_dados.xlsx",
)
preparacao_dados(df)

# Inicialização App
app = Dash()

valores_unicos_diametro = [int(x) for x in df.diametro.unique()]
valores_unicos_diametro.sort()
VALORES_DIAMETRO_FILTRO = [
    dict([["label", f"{x}MM"], ["value", int(x)]]) for x in valores_unicos_diametro
]
VALOR_MINIMO_DIAMETRO = min(valores_unicos_diametro)
VALOR_MAXIMO_DIAMETRO = max(valores_unicos_diametro)

valores_unicos_idade = list(df.idade_hidrometro.unique())
VALOR_MINIMO_IDADE = min(valores_unicos_idade)
VALOR_MAXIMO_IDADE = max(valores_unicos_idade)

app.layout = [
    html.Section(
        [
            html.H2("Filtros"),
            html.Div(
                [
                    html.Label("Diâmetro Hidrômetro", htmlFor="filtro-diametro"),
                    dcc.Checklist(
                        options=VALORES_DIAMETRO_FILTRO,
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
                        min=VALOR_MINIMO_IDADE,
                        max=VALOR_MAXIMO_IDADE,
                        step=2,
                        value=[VALOR_MINIMO_IDADE, VALOR_MAXIMO_IDADE],
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
        ],
        id="filtros",
    ),
    html.Hr(),
    html.Section(
        [gerar_html_area_dados(df)],
        id="secao-resultados",
    ),
]


@callback(
    Output("secao-resultados", "children"),
    Input("filtro-submit", "n_clicks"),
    State("filtro-diametro", "value"),
    State("filtro-idade", "value"),
    prevent_initial_call=True,
)
def filtrar(n_clicks: int, limites_diametros: list[int], limites_idade: list[int]):
    filtrado = df[
        (df.diametro.isin(limites_diametros))
        & (df.idade_hidrometro.between(limites_idade[0], limites_idade[1]))
    ]

    return gerar_html_area_dados(filtrado)


if __name__ == "__main__":
    app.run(debug=True)
