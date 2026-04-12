from typing import Literal, TypeAlias
from enum import StrEnum

import pandas as pd
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
]


class EstilosCSS:
    QUADRO_DADO = {
        "padding": "20px",
        "backgroundColor": "darkblue",
        "color": "white",
        "borderRadius": "12px",
        "textAlign": "center",
        "gridColumnStart": "span 2",
        "border": "1px solid #000080",
    }

    QUADRO_DADO_NUMERO = {
        "fontSize": "3rem",
        "fontWeight": "bold",
        "marginBottom": "5px",
    }

    TABELA = {"gridColumnStart": "span 6"}
    GRAFICO = {"gridColumnStart": "span 6"}

    CHECKLIST = {"display": "flex", "columnGap": "1px", "flex-wrap": "wrap"}
    CHECKLIST_LABEL = {
        "border": "1px solid darkblue",
        "borderRadius": "5px",
        "margin": "2px",
        "backgroundColor": "azure",
        "fontWeight": "bold",
        "cursor": "pointer",
    }

    CONTAINER_FILTROS = {
        "display": "grid",
        "gridTemplateColumns": "repeat(auto-fit, minmax(250px, 1fr))",
        "gap": "20px",
        "padding": "25px",
        "backgroundColor": "#f8f9fa",  # Cinza bem claro profissional
        "borderRadius": "15px",
        "border": "1px solid #e9ecef",
        "boxShadow": "0 4px 6px rgba(0,0,0,0.05)",
    }

    ITEM_FILTRO = {"display": "flex", "flexDirection": "column", "gap": "8px"}

    LABEL_FILTRO = {
        "fontWeight": "bold",
        "fontSize": "0.9rem",
        "color": "#2c3e50",
        "textTransform": "uppercase",
        "letterSpacing": "0.5px",
    }

    BOTAO_FILTRAR = {
        "backgroundColor": "#007bff",
        "color": "white",
        "border": "none",
        "padding": "12px 35px",
        "borderRadius": "8px",
        "fontWeight": "bold",
        "cursor": "pointer",
        "transition": "0.3s",
        "boxShadow": "0 4px 15px rgba(0,123,255,0.3)",
    }

    GRID_AREA_DADOS_CONSUMO = {
        "display": "grid",
        "gridTemplateColumns": "repeat(6, 1fr)",
        "columnGap": "10px",
        "rowGap": "10px",
    }


class ID_ELEMENTOS_HTML(StrEnum):
    LAYOUT = "layout"

    AREA_UPLOAD_TABELA = "area-upload-tabela"
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
    FILTRO_DIAMETRO_LETRA = "filtro-diametro-letra"
    FILTRO_IDADE = "filtro-idade"
    FILTRO_SITUACAO = "filtro-situacao"
    FILTRO_GRUPO_FATURAMENTO = "filtro-grupo-faturamento"
    FILTRO_PERFIL_IMOVEL = "filtro-perfil-imovel"

    AREA_ASSOCIACAO_COLUNAS = "area-associacao-colunas"
    DROPDOWN_ASSOCIACAO_COLUNAS_ERRO = "dropdowns-associacao-colunas-erro"
    DROPDOWN_ASSOCIACAO_COLUNAS = "dropdowns-associacao-colunas"
    BOTAO_ASSOCIAR_COLUNAS = "botao_associar_colunas"

    ESCOLHA_ABA_DADOS_CONSUMO = "escolha-dados-consumo-mes"
    BOTAO_CONCATENAR_CONSUMO = "concatenar-consumo"
    VALOR_LIMITE_CONCATENAR = "valor-limite-concatenar"
    AREA_DADOS_CONSUMO_MES = "area-dados-consumo-mes"
    DADOS_CONSUMO_MES_1 = "dados-consumo-mes-1"
    DADOS_CONSUMO_MES_2 = "dados-consumo-mes-2"
    DADOS_CONSUMO_MES_3 = "dados-consumo-mes-3"


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
    "media_consumo_mes_1": "associacao_media_consumo_mes_1",
    "media_consumo_mes_2": "associacao_media_consumo_mes_2",
    "media_consumo_mes_3": "associacao_media_consumo_mes_3",
    "anormalidade_leitura_mes_1": "associacao_anormalidade_leitura_mes_1",
    "anormalidade_leitura_mes_2": "associacao_anormalidade_leitura_mes_2",
    "anormalidade_leitura_mes_3": "associacao_anormalidade_leitura_mes_3",
    "consumo_medido_mes_1": "associacao_consumo_medido_mes_1",
    "consumo_medido_mes_2": "associacao_consumo_medido_mes_2",
    "consumo_medido_mes_3": "associacao_consumo_medido_mes_3",
    "consumo_faturado_mes_1": "associacao_consumo_faturado_mes_1",
    "consumo_faturado_mes_2": "associacao_consumo_faturado_mes_2",
    "consumo_faturado_mes_3": "associacao_consumo_faturado_mes_3",
    "anormalidade_consumo_mes_1": "associacao_anormalidade_consumo_mes_1",
    "anormalidade_consumo_mes_2": "associacao_anormalidade_consumo_mes_2",
    "anormalidade_consumo_mes_3": "associacao_anormalidade_consumo_mes_3",
}


def gerar_form_colunas(
    opcoes: None | list[str] = None,
    erro="",
):
    opcoes_dropdowns: list[str] = []
    if opcoes is not None:
        opcoes_dropdowns = opcoes

    def _label_e_dropdown(
        nome_label: str,
        coluna_necessaria: NOME_VARIAVEIS,
    ):
        id_select = ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS[
            coluna_necessaria
        ]

        div_html = html.Div(
            children=[
                html.Label(
                    style={"fontStyle": "bold"}, children=nome_label, htmlFor=id_select
                ),
                dcc.Dropdown(id=id_select, options=opcoes_dropdowns),
            ],
            style={"display": "flex", "flexDirection": "column", "gap": "1px"},
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
    col_consumo_medio_mes_1 = _label_e_dropdown(
        "Média de Consumo do Mês de Referência 1", "media_consumo_mes_1"
    )
    col_consumo_medio_mes_2 = _label_e_dropdown(
        "Média de Consumo do Mês de Referência 2", "media_consumo_mes_2"
    )
    col_consumo_medio_mes_3 = _label_e_dropdown(
        "Média de Consumo do Mês de Referência 3", "media_consumo_mes_3"
    )
    col_anormalidade_leitura_mes_1 = _label_e_dropdown(
        "Anormalidade de Leitura Mês de Referência 1", "anormalidade_leitura_mes_1"
    )
    col_anormalidade_leitura_mes_2 = _label_e_dropdown(
        "Anormalidade de Leitura Mês de Referência 2", "anormalidade_leitura_mes_2"
    )
    col_anormalidade_leitura_mes_3 = _label_e_dropdown(
        "Anormalidade de Leitura Mês de Referência 3", "anormalidade_leitura_mes_3"
    )
    col_consumo_medido_mes_1 = _label_e_dropdown(
        "Consumo Medido Mês de Referência 1", "consumo_medido_mes_1"
    )
    col_consumo_medido_mes_2 = _label_e_dropdown(
        "Consumo Medido Mês de Referência 2", "consumo_medido_mes_2"
    )
    col_consumo_medido_mes_3 = _label_e_dropdown(
        "Consumo Medido Mês de Referência 3", "consumo_medido_mes_3"
    )

    col_consumo_faturado_mes_1 = _label_e_dropdown(
        "Consumo Faturado Mês de Referência 1", "consumo_faturado_mes_1"
    )
    col_consumo_faturado_mes_2 = _label_e_dropdown(
        "Consumo Faturado Mês de Referência 2", "consumo_faturado_mes_2"
    )
    col_consumo_faturado_mes_3 = _label_e_dropdown(
        "Consumo Faturado Mês de Referência 3", "consumo_faturado_mes_3"
    )

    col_anormalidade_consumo_mes_1 = _label_e_dropdown(
        "Anormalidade de Consumo Mês de Referência 1", "anormalidade_consumo_mes_1"
    )
    col_anormalidade_consumo_mes_2 = _label_e_dropdown(
        "Anormalidade de Consumo Mês de Referência 2", "anormalidade_consumo_mes_2"
    )
    col_anormalidade_consumo_mes_3 = _label_e_dropdown(
        "Anormalidade de Consumo Mês de Referência 3", "anormalidade_consumo_mes_3"
    )

    return html.Form(
        style={
            "display": "flex",
            "flexDirection": "column",
            "gap": "2px",
        },
        children=[
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
                            col_consumo_medio_mes_1,
                            col_consumo_medio_mes_2,
                            col_consumo_medio_mes_3,
                            col_anormalidade_leitura_mes_1,
                            col_anormalidade_leitura_mes_2,
                            col_anormalidade_leitura_mes_3,
                            col_consumo_medido_mes_1,
                            col_consumo_medido_mes_2,
                            col_consumo_medido_mes_3,
                            col_consumo_faturado_mes_1,
                            col_consumo_faturado_mes_2,
                            col_consumo_faturado_mes_3,
                            col_anormalidade_consumo_mes_1,
                            col_anormalidade_consumo_mes_2,
                            col_anormalidade_consumo_mes_3,
                        ]
                    ),
                ],
            ),
            html.Div(
                html.Button(
                    id=ID_ELEMENTOS_HTML.BOTAO_ASSOCIAR_COLUNAS,
                    type="button",
                    children="Associar Colunas",
                )
            ),
            html.Div(
                id=ID_ELEMENTOS_HTML.DROPDOWN_ASSOCIACAO_COLUNAS_ERRO, children=erro
            ),
        ],
    )


def gerar_html_filtros(
    opcoes_valores_diametro_filtro,
    valores_unicos_diametro,
    valor_minimo_idade,
    valor_maximo_idade,
    opcoes_valores_situacao_ligacao_agua,
    opcoes_selecionadas_situacao_ligacao_agua,
    opcoes_valores_diametro_letra,
    valores_unicos_diametro_letra,
    opcoes_valores_grupo_faturamento,
    valores_unicos_grupo_faturamento,
    opcoes_valores_perfil_imovel,
    valores_unicos_perfil_imovel,
):
    return [
        html.H2("Filtros", style={"marginBottom": "15px", "color": "#2c3e50"}),
        # Container Principal com Grid
        html.Div(
            style=EstilosCSS.CONTAINER_FILTROS,
            children=[
                # Diâmetro Hidrômetro
                html.Div(
                    [
                        html.Label(
                            "Diâmetro Hidrômetro", style=EstilosCSS.LABEL_FILTRO
                        ),
                        dcc.Dropdown(
                            id=ID_ELEMENTOS_HTML.FILTRO_DIAMETRO,
                            options=opcoes_valores_diametro_filtro,
                            value=valores_unicos_diametro,
                            multi=True,
                            placeholder="Selecione o diâmetro...",
                        ),
                    ],
                    style=EstilosCSS.ITEM_FILTRO,
                ),
                # Diâmetro Hidrômetro + Letra
                html.Div(
                    [
                        html.Label("Diâmetro + Letra", style=EstilosCSS.LABEL_FILTRO),
                        dcc.Dropdown(
                            id=ID_ELEMENTOS_HTML.FILTRO_DIAMETRO_LETRA,
                            options=opcoes_valores_diametro_letra,
                            value=valores_unicos_diametro_letra,
                            multi=True,
                            placeholder="Selecione a combinação...",
                        ),
                    ],
                    style=EstilosCSS.ITEM_FILTRO,
                ),
                # Idade Hidrômetro
                html.Div(
                    [
                        html.Label(
                            f"Idade do Hidrômetro ({valor_minimo_idade} - {valor_maximo_idade} anos)",
                            style=EstilosCSS.LABEL_FILTRO,
                        ),
                        html.Div(
                            dcc.RangeSlider(
                                id=ID_ELEMENTOS_HTML.FILTRO_IDADE,
                                min=valor_minimo_idade,
                                max=valor_maximo_idade,
                                step=1,
                                value=[valor_minimo_idade, valor_maximo_idade],
                                # Gera marcas apenas para múltiplos de 5
                                marks={
                                    str(i): (
                                        str(i)
                                        if i % 5 == 0
                                        or i == valor_minimo_idade
                                        or i == valor_maximo_idade
                                        else ""
                                    )
                                    for i in range(
                                        valor_minimo_idade, valor_maximo_idade + 1
                                    )
                                },
                                tooltip={"placement": "bottom", "always_visible": True},
                            ),
                            style={"marginTop": "15px"},
                        ),
                    ],
                    style=EstilosCSS.ITEM_FILTRO,
                ),
                # Situação Ligação Água
                html.Div(
                    [
                        html.Label(
                            "Situação Ligação Água", style=EstilosCSS.LABEL_FILTRO
                        ),
                        dcc.Checklist(
                            id=ID_ELEMENTOS_HTML.FILTRO_SITUACAO,
                            options=opcoes_valores_situacao_ligacao_agua,
                            value=opcoes_selecionadas_situacao_ligacao_agua,
                            inline=True,
                            labelStyle={"marginRight": "15px", "cursor": "pointer"},
                        ),
                    ],
                    style=EstilosCSS.ITEM_FILTRO,
                ),
                # Grupo de Faturamento
                html.Div(
                    [
                        html.Label(
                            "Grupo de Faturamento", style=EstilosCSS.LABEL_FILTRO
                        ),
                        dcc.Dropdown(
                            id=ID_ELEMENTOS_HTML.FILTRO_GRUPO_FATURAMENTO,
                            options=opcoes_valores_grupo_faturamento,
                            value=valores_unicos_grupo_faturamento,
                            multi=True,
                            placeholder="Selecione os grupos...",
                        ),
                    ],
                    style=EstilosCSS.ITEM_FILTRO,
                ),
                # Perfil do Imóvel
                html.Div(
                    [
                        html.Label("Perfil do Imóvel", style=EstilosCSS.LABEL_FILTRO),
                        dcc.Dropdown(
                            id=ID_ELEMENTOS_HTML.FILTRO_PERFIL_IMOVEL,
                            options=opcoes_valores_perfil_imovel,
                            value=valores_unicos_perfil_imovel,
                            multi=True,
                            placeholder="Selecione os perfis...",
                        ),
                    ],
                    style=EstilosCSS.ITEM_FILTRO,
                ),
            ],
        ),
        html.Div(
            [
                html.Button(
                    "Aplicar Filtros",
                    id=ID_ELEMENTOS_HTML.FILTRO_SUBMIT,
                    type="button",
                    style=EstilosCSS.BOTAO_FILTRAR,
                ),
            ],
            style={"textAlign": "right", "marginTop": "10px"},
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
    media_do_consumo_medio_mes_1,
    media_do_consumo_medio_mes_2,
    media_do_consumo_medio_mes_3,
    desvio_padrao_consumo_medio_mes_1,
    desvio_padrao_consumo_medio_mes_2,
    desvio_padrao_consumo_medio_mes_3,
    frequencia_consumo_acima_limite_mes_1,
    frequencia_consumo_acima_limite_mes_2,
    frequencia_consumo_acima_limite_mes_3,
    frequencia_consumos_medios_mes_1: pd.Series,
    frequencia_consumos_medios_mes_2: pd.Series,
    frequencia_consumos_medios_mes_3: pd.Series,
    anormalidade_leitura_mes_1,
    anormalidade_leitura_mes_2,
    anormalidade_leitura_mes_3,
    frequencia_consumos_medidos_mes_1: pd.Series,
    frequencia_consumos_medidos_mes_2: pd.Series,
    frequencia_consumos_medidos_mes_3: pd.Series,
    frequencia_consumo_faturado_mes_1: pd.Series,
    frequencia_consumo_faturado_mes_2: pd.Series,
    frequencia_consumo_faturado_mes_3: pd.Series,
    frequencia_anormalidade_consumo_1,
    frequencia_anormalidade_consumo_2,
    frequencia_anormalidade_consumo_3,
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
            gerar_html_quadro_dado(
                contagem_hidrometros,
                "Nº Total de Hidrômetros",
                id_dado_numero=ID_ELEMENTOS_HTML.CONTAGEM_HIDROMETROS,
            ),
            gerar_html_quadro_dado(
                porcentagem_hidrometros_ligados,
                "Porcentagem de Hidrômetros Ligados",
                id_dado_numero=ID_ELEMENTOS_HTML.PORCENTAGEM_HIDROMETOS_LIGADOS,
            ),
            gerar_html_quadro_dado(
                idade_media_hidrometros,
                "Idade Média dos Hidrômetros",
                id_dado_numero=ID_ELEMENTOS_HTML.IDADE_MEDIA_HIDROMETROS,
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
                style=EstilosCSS.GRAFICO,
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
                style=EstilosCSS.GRAFICO,
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
                style=EstilosCSS.TABELA,
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
                style=EstilosCSS.TABELA,
            ),
            gerar_html_quadro_dado(
                idade_media_20MM,
                "Idade Média dos Hidrômetros com 20MM",
                id_dado_numero=ID_ELEMENTOS_HTML.IDADE_MEDIA_HIDROMETROS_20MM,
            ),
            gerar_html_quadro_dado(
                idade_media_25MM,
                "Idade Média dos Hidrômetros com 25MM",
                id_dado_numero=ID_ELEMENTOS_HTML.IDADE_MEDIA_HIDROMETROS_25MM,
            ),
            gerar_html_quadro_dado(
                idade_media_acima_25MM,
                "Idade Média dos Hidrômetros com mais de 25MM",
                id_dado_numero=ID_ELEMENTOS_HTML.IDADE_MEDIA_HIDROMETROS_ACIMA_25MM,
            ),
            gerar_html_quadro_dado(
                idade_desvio_padrao_20MM,
                "Desvio Padrão da Idade dos Hidrômetros com 20MM",
                id_dado_numero=ID_ELEMENTOS_HTML.IDADE_DESVIO_PADRAO_20MM,
            ),
            gerar_html_quadro_dado(
                idade_desvio_padrao_25MM,
                "Desvio Padrão da Idade dos Hidrômetros com 25MM",
                id_dado_numero=ID_ELEMENTOS_HTML.IDADE_DESVIO_PADRAO_25MM,
            ),
            gerar_html_quadro_dado(
                idade_desvio_padrao_acima_25MM,
                "Desvio Padrão da Idade dos Hidrômetros com mais de 25MM",
                id_dado_numero=ID_ELEMENTOS_HTML.IDADE_DESVIO_PADRAO_ACIMA_25MM,
            ),
            html.Div(
                grafico_idades_hidrometros_20MM,
                style=EstilosCSS.GRAFICO,
            ),
            html.Div(
                grafico_idades_hidrometros_25MM,
                style=EstilosCSS.GRAFICO,
            ),
            html.Div(
                grafico_idades_hidrometros_acima_de_25MM,
                style=EstilosCSS.GRAFICO,
            ),
            html.Div(
                children=[
                    html.H3("Informações Descritivas de Consumo"),
                    html.Div(
                        children=[
                            dcc.RadioItems(
                                {
                                    "1": "Mês Referência 1",
                                    "2": "Mês Referência 2",
                                    "3": "Mês Referência 3",
                                },
                                value="1",
                                inline=True,
                                id=ID_ELEMENTOS_HTML.ESCOLHA_ABA_DADOS_CONSUMO,
                            ),
                            html.Div(
                                children=[
                                    html.Label("Concatenar Consumo a Partir de: "),
                                    dcc.Input(
                                        130,
                                        "number",
                                        id=ID_ELEMENTOS_HTML.VALOR_LIMITE_CONCATENAR,
                                    ),
                                    html.Button(
                                        "Concatenar",
                                        id=ID_ELEMENTOS_HTML.BOTAO_CONCATENAR_CONSUMO,
                                    ),
                                ]
                            ),
                        ],
                    ),
                    html.Div(
                        id=ID_ELEMENTOS_HTML.AREA_DADOS_CONSUMO_MES,
                        children=[
                            gerar_html_dados_consumo_mes(
                                media_do_consumo_medio_mes_1,
                                desvio_padrao_consumo_medio_mes_1,
                                frequencia_consumo_acima_limite_mes_1,
                                frequencia_consumos_medios_mes_1,
                                anormalidade_leitura_mes_1,
                                frequencia_consumos_medidos_mes_1,
                                frequencia_consumo_faturado_mes_1,
                                frequencia_anormalidade_consumo_1,
                                "Mês 1",
                                ID_ELEMENTOS_HTML.DADOS_CONSUMO_MES_1,
                            ),
                            gerar_html_dados_consumo_mes(
                                media_do_consumo_medio_mes_2,
                                desvio_padrao_consumo_medio_mes_2,
                                frequencia_consumo_acima_limite_mes_2,
                                frequencia_consumos_medios_mes_2,
                                anormalidade_leitura_mes_2,
                                frequencia_consumos_medidos_mes_2,
                                frequencia_consumo_faturado_mes_2,
                                frequencia_anormalidade_consumo_2,
                                "Mês 2",
                                ID_ELEMENTOS_HTML.DADOS_CONSUMO_MES_2,
                                oculto=True,
                            ),
                            gerar_html_dados_consumo_mes(
                                media_do_consumo_medio_mes_3,
                                desvio_padrao_consumo_medio_mes_3,
                                frequencia_consumo_acima_limite_mes_3,
                                frequencia_consumos_medios_mes_3,
                                anormalidade_leitura_mes_3,
                                frequencia_consumos_medidos_mes_3,
                                frequencia_consumo_faturado_mes_3,
                                frequencia_anormalidade_consumo_3,
                                "Mês 3",
                                ID_ELEMENTOS_HTML.DADOS_CONSUMO_MES_3,
                                oculto=True,
                            ),
                        ],
                    ),
                ],
                style={
                    "display": "flex",
                    "flexDirection": "column",
                    "gap": "8px",
                    "gridColumnStart": "span 6",
                },
            ),
        ],
        id=ID_ELEMENTOS_HTML.AREA_DADOS,
    )


def gerar_html_dados_consumo_mes(
    media_consumo_medio: float,
    desvio_padrao: float,
    frequencia_consumo_acima_limite: int,
    frequencia_consumos_medios: pd.Series,
    anormalidade_de_leitura: pd.DataFrame,
    frequencia_consumos_medidos: pd.Series,
    frequencia_consumo_faturado: pd.Series,
    frequencia_anormalidade_consumo,
    titulo: str,
    id_html_elemento: str,
    limite_consumo_utilizado: int = 130,
    oculto: bool = False,
):
    estilo = EstilosCSS.GRID_AREA_DADOS_CONSUMO
    if oculto:
        estilo = {"display": "none"}

    return html.Div(
        id=id_html_elemento,
        children=[
            html.H4(titulo, style={"gridColumnStart": "1", "gridColumnEnd": "-1"}),
            gerar_html_quadro_dado(
                f"{media_consumo_medio:.2f}",
                "Média dos Consumos Médios",
            ),
            gerar_html_quadro_dado(
                f"{desvio_padrao:.2f}",
                "Desvio Padrão dos Consumos Médios",
            ),
            gerar_html_quadro_dado(
                frequencia_consumo_acima_limite,
                f"Frequência de Consumo maior que {limite_consumo_utilizado}",
            ),
            html.Div(
                [
                    dcc.Graph(
                        figure=px.bar(
                            x=[str(x) for x in frequencia_consumos_medios.index],
                            y=frequencia_consumos_medios,
                            labels={"y": "Frequência", "x": "Consumo Médio"},
                            title="Gráfico de Consumo Médio",
                        )
                    )
                ],
                style=EstilosCSS.GRAFICO,
            ),
            DataTable(
                anormalidade_de_leitura.to_dict("records"),
                style_cell={"textAlign": "left", "border": "1px solid black"},
                style_header={
                    "backgroundColor": "azure",
                    "font-weight": "bold",
                    "text-transform": "uppercase",
                },
            ),
            html.Div(
                [
                    dcc.Graph(
                        figure=px.bar(
                            x=[str(x) for x in frequencia_consumos_medidos.index],
                            y=frequencia_consumos_medidos,
                            labels={"y": "Frequência", "x": "Consumo Medido"},
                            title="Gráfico de Consumo Medido",
                        )
                    )
                ],
                style=EstilosCSS.GRAFICO,
            ),
            html.Div(
                [
                    dcc.Graph(
                        figure=px.bar(
                            x=[str(x) for x in frequencia_consumo_faturado.index],
                            y=frequencia_consumo_faturado,
                            labels={"y": "Frequência", "x": "Consumo Faturado"},
                            title="Gráfico de Consumo Faturado",
                        )
                    )
                ],
                style=EstilosCSS.GRAFICO,
            ),
            DataTable(
                frequencia_anormalidade_consumo.to_dict("records"),
                style_cell={"textAlign": "left", "border": "1px solid black"},
                style_header={
                    "backgroundColor": "azure",
                    "font-weight": "bold",
                    "text-transform": "uppercase",
                },
            ),
        ],
        style=estilo,
    )


def gerar_html_quadro_dado(
    dado,
    titulo: str,
    estilo_extra: dict[str, str] | None = None,
    id_dado_numero: str = "",
    hidden: bool = False,
):
    if estilo_extra is None:
        estilo_extra = {}

    return html.Div(
        [
            html.Div(dado, style=EstilosCSS.QUADRO_DADO_NUMERO, id=id_dado_numero),
            html.Div(titulo),
        ],
        style=EstilosCSS.QUADRO_DADO | estilo_extra,
        hidden=hidden,
    )


def gerar_html_zero_resultados():
    return html.Div("0 Resultados")
