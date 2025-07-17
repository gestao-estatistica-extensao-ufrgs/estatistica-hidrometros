import pandas as pd
from dash import Dash, html, dash_table, dcc, callback, Output, Input, State


# Declarações
def padronizacao_diametro(diametro: str):
    filtrado = filter(lambda caractere: caractere.isnumeric(), diametro)
    diametro_padronizado_texto = "".join(caractere for caractere in filtrado)
    diametro_padronizado_numero = int(diametro_padronizado_texto)
    return diametro_padronizado_numero


def preparacao_dados(df: pd.DataFrame):
    df["hidrometro"] = df["Hidrometro"]
    df.drop(columns=["Hidrometro"])

    df["diametro"] = df["Diametro"].apply(padronizacao_diametro)
    df.drop(columns=["Diametro"], inplace=True)


# Preparação Dados
df = pd.read_excel(
    "testes/dados_teste/amostra_dados.xlsx",
)
preparacao_dados(df)

# Inicialização App
app = Dash()

VALORES_DIAMETRO_FILTRO = dict([(int(x), str(x)) for x in df.diametro.unique()])
VALOR_MINIMO_DIAMETRO = min(VALORES_DIAMETRO_FILTRO.keys())
VALOR_MAXIMO_DIAMETRO = max(VALORES_DIAMETRO_FILTRO.keys())

app.layout = [
    dash_table.DataTable(data=df.head().to_dict("records")),
    html.Section(
        children=[
            dcc.RangeSlider(
                min=VALOR_MINIMO_DIAMETRO,
                max=VALOR_MAXIMO_DIAMETRO,
                step=5,
                marks=VALORES_DIAMETRO_FILTRO,
                value=[VALOR_MINIMO_DIAMETRO, VALOR_MAXIMO_DIAMETRO],
                included=True,
                id="filtro-diametro",
            ),
            html.Button("Filtrar", id="filtro-submit", type="button"),
        ],
    ),
    html.Section(
        children=[
            html.Div(
                children=[
                    html.Div(children="Nº Total de Hidrômetros:"),
                    html.Div(children=df.hidrometro.count(), id="contagem-hidrometros"),
                ]
            ),
        ],
        id="secao-resultados",
    ),
]


@callback(
    Output("secao-resultados", "children"),
    Input("filtro-submit", "n_clicks"),
    State("filtro-diametro", "value"),
    prevent_initial_call=True,
)
def filtro_diametro(n_clicks: int, limites_diametros: list[int]):
    filtrado = df[
        (df.diametro >= limites_diametros[0]) & (df.diametro <= limites_diametros[1])
    ]

    return html.Div(
        children=[
            html.Div(children="Nº Total de Hidrômetros:"),
            html.Div(children=filtrado.hidrometro.count(), id="contagem-hidrometros"),
        ]
    )


if __name__ == "__main__":
    app.run(debug=True)
