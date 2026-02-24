from typing import Literal, TypeAlias
from enum import StrEnum

from dash import dcc, html
import numpy as np
import plotly.express as px
from dash.dash_table import DataTable

NOME_VARIAVEIS: TypeAlias = Literal[
    "hidrometro",
    "diametro",
    "data_instalacao",
    "grupo_leitura",
    "situacao_ligacao_agua",
    "perfil_imovel",
]


class ID_ELEMENTOS_HTML(StrEnum):
    UPLOAD_TABELA_ERRO = "upload-tabela-erro"
    UPLOAD_NOME_ARQUIVO = "upload-nome-arquivo"
    UPLOAD_TABELA = "upload-tabela"

    SECAO_RESULTADOS = "secao-resultados"
    CONTAGEM_HIDROMETROS = "contagem-hidrometros"
    PORCENTAGEM_HIDROMETOS_LIGADOS = "porcentagem-hidrometros-ligados"
    IDADE_MEDIA_HIDROMETROS = "idade-media-hidrometros"
    IDADE_HIDROMETRO = "idade_hidrometro"
    IDADE_MEDIA_HIDROMETROS_20MM = "idade-media-hidrometros-20MM"
    IDADE_MEDIA_HIDROMETROS_25MM = "idade-media-hidrometros-25MM"
    IDADE_MEDIA_HIDROMETROS_ACIMA_25MM = "idade-media-hidrometros-acima-25MM"
    IDADE_DESVIO_PADRAO_20MM = "idade-desvio-padrao-hidrometros-com-20MM"
    IDADE_DESVIO_PADRAO_25MM = "idade-desvio-padrao-hidrometros-com-25MM"
    IDADE_DESVIO_PADRAO_ACIMA_25MM = "idade-desvio-padrao-hidrometros-acima-25MM"
    AREA_DADOS = "area-dados"

    FILTROS = "filtros"
    FILTRO_SUBMIT = "filtro-submit"
    FILTRO_DIAMETRO = "filtro-diametro"
    FILTRO_IDADE = "filtro-idade"
    FILTRO_SITUACAO = "filtro-situacao"

    DROPDOWN_ASSOCIACAO_COLUNAS_ERRO = "dropdowns-associacao-colunas-erro"
    DROPDOWN_ASSOCIACAO_COLUNAS = "dropdowns-associacao-colunas"
    BOTAO_ASSOCIAR_COLUNAS = "botao_associar_colunas"


ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS: dict[
    NOME_VARIAVEIS,
    str,
] = {
    "hidrometro": "associacao_col_hidrometro",
    "diametro": "associacao_col_diametro",
    "data_instalacao": "associacao_col_data_instalacao",
    "grupo_leitura": "associacao_col_grupo_leitura",
    "situacao_ligacao_agua": "associacao_col_situacao_ligacao_agua",
    "perfil_imovel": "associacao_col_perfil_imovel",
}


def gerar_form_colunas():
    def _label_e_dropdown(
        nome_label: str,
        coluna_necessaria: NOME_VARIAVEIS,
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
                id=ID_ELEMENTOS_HTML.DROPDOWN_ASSOCIACAO_COLUNAS,
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
                            id=ID_ELEMENTOS_HTML.BOTAO_ASSOCIAR_COLUNAS,
                            type="button",
                            disabled=True,
                            children="Associar Colunas",
                        )
                    ),
                ],
            ),
            html.Div(id=ID_ELEMENTOS_HTML.DROPDOWN_ASSOCIACAO_COLUNAS_ERRO),
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
                html.Label(
                    "Diâmetro Hidrômetro", htmlFor=ID_ELEMENTOS_HTML.FILTRO_DIAMETRO
                ),
                dcc.Checklist(
                    options=opcoes_valores_diametro_filtro,
                    value=valores_unicos_diametro,
                    inline=True,
                    id=ID_ELEMENTOS_HTML.FILTRO_DIAMETRO,
                ),
            ]
        ),
        html.Div(
            [
                html.Label("Idade Hidrômetro", htmlFor=ID_ELEMENTOS_HTML.FILTRO_IDADE),
                dcc.RangeSlider(
                    id=ID_ELEMENTOS_HTML.FILTRO_IDADE,
                    min=valor_minimo_idade,
                    max=valor_maximo_idade,
                    step=2,
                    value=[valor_minimo_idade, valor_maximo_idade],
                ),
            ]
        ),
        html.Div(
            [
                html.Label(
                    "Situação Ligação Água", htmlFor=ID_ELEMENTOS_HTML.FILTRO_SITUACAO
                ),
                dcc.Checklist(
                    id=ID_ELEMENTOS_HTML.FILTRO_SITUACAO,
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
                    id=ID_ELEMENTOS_HTML.FILTRO_SUBMIT,
                    type="button",
                ),
            ]
        ),
    ]


def gerar_html_dados(
    df,
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
):
    if idade_media_hidrometros is not np.nan:
        idade_media_hidrometros = f"{idade_media_hidrometros:.2f}"
    else:
        idade_media_hidrometros = "-"

    if porcentagem_hidrometros_ligados == 0.0:
        porcentagem_hidrometros_ligados = "-"
    else:
        porcentagem_hidrometros_ligados = f"{porcentagem_hidrometros_ligados:.2f}"

    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        contagem_hidrometros,
                        id=ID_ELEMENTOS_HTML.CONTAGEM_HIDROMETROS,
                        className="quadro-dado-numero",
                    ),
                    html.Div("Nº Total de Hidrômetros"),
                ],
                className="quadro-dado",
            ),
            html.Div(
                [
                    html.Div(
                        porcentagem_hidrometros_ligados,
                        id=ID_ELEMENTOS_HTML.PORCENTAGEM_HIDROMETOS_LIGADOS,
                        className="quadro-dado-numero",
                    ),
                    html.Div("Porcentagem de Hidrômetros Ligados"),
                ],
                className="quadro-dado",
            ),
            html.Div(
                [
                    html.Div(
                        idade_media_hidrometros,
                        id=ID_ELEMENTOS_HTML.IDADE_MEDIA_HIDROMETROS,
                        className="quadro-dado-numero",
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
                            x=ID_ELEMENTOS_HTML.IDADE_HIDROMETRO,
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
                        freq_perfil_imoveis,
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
                        freq_hidrometros,
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
                        id=ID_ELEMENTOS_HTML.IDADE_MEDIA_HIDROMETROS_20MM,
                        className="quadro-dado-numero",
                    ),
                    html.Div("Idade Média dos Hidrômetros com 20MM"),
                ],
                className="quadro-dado",
            ),
            html.Div(
                [
                    html.Div(
                        idade_media_25MM,
                        id=ID_ELEMENTOS_HTML.IDADE_MEDIA_HIDROMETROS_25MM,
                        className="quadro-dado-numero",
                    ),
                    html.Div("Idade Média dos Hidrômetros com 25MM"),
                ],
                className="quadro-dado",
            ),
            html.Div(
                [
                    html.Div(
                        idade_media_acima_25MM,
                        id=ID_ELEMENTOS_HTML.IDADE_MEDIA_HIDROMETROS_ACIMA_25MM,
                        className="quadro-dado-numero",
                    ),
                    html.Div("Idade Média dos Hidrômetros com mais de 25MM"),
                ],
                className="quadro-dado",
            ),
            html.Div(
                [
                    html.Div(
                        idade_desvio_padrao_20MM,
                        id=ID_ELEMENTOS_HTML.IDADE_DESVIO_PADRAO_20MM,
                        className="quadro-dado-numero",
                    ),
                    html.Div("Desvio Padrão da Idade dos Hidrômetros com 20MM"),
                ],
                className="quadro-dado",
            ),
            html.Div(
                [
                    html.Div(
                        idade_desvio_padrao_25MM,
                        id=ID_ELEMENTOS_HTML.IDADE_DESVIO_PADRAO_25MM,
                        className="quadro-dado-numero",
                    ),
                    html.Div("Desvio Padrão da Idade dos Hidrômetros com 25MM"),
                ],
                className="quadro-dado",
            ),
            html.Div(
                [
                    html.Div(
                        idade_desvio_padrao_acima_25MM,
                        id=ID_ELEMENTOS_HTML.IDADE_DESVIO_PADRAO_ACIMA_25MM,
                        className="quadro-dado-numero",
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
        id=ID_ELEMENTOS_HTML.AREA_DADOS,
    )


def gerar_html_zero_resultados():
    return html.Div("0 Resultados")
