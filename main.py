import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, html, dcc, callback, Output, Input, State


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
        lambda x: round(x.days / 365, 2)
    )

    df.drop(
        columns=[
            "Diametro",
            "Situacao Ligacao Agua",
            "Hidrometro",
            "Idade Hidrometro",
            "Data Instalacao",
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
    prevent_initial_call=True,
)
def filtrar(n_clicks: int, limites_diametros: list[int]):
    filtrado = df[df.diametro.isin(limites_diametros)]

    return gerar_html_area_dados(filtrado)


if __name__ == "__main__":
    app.run(debug=True)
