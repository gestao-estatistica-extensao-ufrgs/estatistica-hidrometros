from datetime import datetime
from enum import StrEnum

import pandas as pd
from dash import dcc, html
import numpy as np
import plotly.express as px  # type: ignore
from dash.dash_table.DataTable import DataTable

from tipos import NOME_VARIAVEIS

_PLOTLY_CORES_BARRAS = ["#1e6091", "#2196c4", "#56b4d3", "#a8d8ea"]

_PLOTLY_DARK_LAYOUT = dict(
    paper_bgcolor="#1a2235",
    plot_bgcolor="#1a2235",
    font_color="#8899aa",
    xaxis={"gridcolor": "#2a3f5f", "linecolor": "#2a3f5f"},
    yaxis={"gridcolor": "#2a3f5f", "linecolor": "#2a3f5f"},
)

_TABELA_DARK = dict(
    style_cell={
        "textAlign": "left",
        "border": "1px solid #2a3f5f",
        "backgroundColor": "#1a2235",
        "color": "#ffffff",
        "padding": "8px 12px",
    },
    style_header={
        "backgroundColor": "#212d45",
        "fontWeight": "bold",
        "textTransform": "uppercase",
        "color": "#ffffff",
        "border": "1px solid #2a3f5f",
        "letterSpacing": "0.5px",
        "fontSize": "0.75rem",
    },
    style_data_conditional=[
        {"if": {"row_index": "odd"}, "backgroundColor": "#1e2a40"},
    ],
)


class EstilosCSS:
    QUADRO_DADO = {
        "display": "flex",
        "flexDirection": "column",
        "justifyContent": "center",
        "padding": "20px",
        "backgroundColor": "#1a2235",
        "color": "#ffffff",
        "borderRadius": "12px",
        "gridColumn": "span 2",
        "border": "1px solid #2a3f5f",
    }

    QUADRO_DADO_NUMERO = {
        "fontSize": "2rem",
        "fontWeight": "bold",
        "marginBottom": "4px",
        "color": "#ffffff",
    }

    QUADRO_DADO_ICONE = {
        "fontSize": "1.8rem",
        "color": "#2196c4",
        "minWidth": "44px",
        "textAlign": "center",
        "lineHeight": "1",
    }

    QUADRO_DADO_LABEL = {
        "fontSize": "0.75rem",
        "color": "#8899aa",
        "textTransform": "uppercase",
        "letterSpacing": "0.5px",
    }

    TABELA = {"gridColumnStart": "span 6"}
    GRAFICO = {"gridColumnStart": "span 6"}

    CHECKLIST = {"display": "flex", "columnGap": "1px", "flexWrap": "wrap"}
    CHECKLIST_LABEL = {
        "border": "1px solid #2a3f5f",
        "borderRadius": "5px",
        "margin": "2px",
        "backgroundColor": "#212d45",
        "color": "#ffffff",
        "fontWeight": "bold",
        "cursor": "pointer",
    }

    CONTAINER_FILTROS = {
        "display": "grid",
        "gridTemplateColumns": "repeat(auto-fit, minmax(250px, 1fr))",
        "gap": "20px",
        "padding": "25px",
        "backgroundColor": "#151929",
        "borderRadius": "15px",
        "border": "1px solid #2a3f5f",
    }

    ITEM_FILTRO = {"display": "flex", "flexDirection": "column", "gap": "8px"}

    LABEL_FILTRO = {
        "fontWeight": "bold",
        "fontSize": "0.75rem",
        "color": "#8899aa",
        "textTransform": "uppercase",
        "letterSpacing": "0.5px",
    }

    BOTAO_FILTRAR = {
        "backgroundColor": "#2196c4",
        "color": "white",
        "border": "none",
        "padding": "12px",
        "borderRadius": "8px",
        "fontWeight": "bold",
        "cursor": "pointer",
        "width": "100%",
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
    ANO_EXTRACAO = "ano-extracao"
    MES_EXTRACAO = "mes-extracao"
    PROCESSAR_TABELA = "processar-tabela"

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
    FILTRO_CATEGORIA = "filtro-categoria"
    FILTRO_TIPO_TARIFA_ESGOTO = "filtro-tipo-tarifa-esgoto"
    FILTRO_ANORMALIDADE_LEITURA = "filtro-anormalidade-leitura"
    FILTRO_ANORMALIDADE_CONSUMO = "filtro-anormalidade-consumo"

    BOTAO_TOGGLE_FILTROS = "botao-toggle-filtros"
    BOTAO_FECHAR_FILTROS = "botao-fechar-filtros"
    PAINEL_FILTROS = "painel-filtros"
    BACKDROP_FILTROS = "backdrop-filtros"

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

    TABELA_RAMAIS_ANORMALIDADE = "tabela-ramais-anormalidade"
    PESQUISA_RAMAIS_ANORMALIDADE = "pesquisa-ramais-anormalidade"
    PAGINA_RAMAIS_ANORMALIDADE = "pagina-ramais-anormalidade"
    TOTAL_RAMAIS_ANORMALIDADE = "total-ramais-anormalidade"
    BOTAO_DOWNLOAD_SEM_FILTRO = "botao-download-sem-filtro"
    BOTAO_DOWNLOAD_COM_FILTRO = "botao-download-com-filtro"
    DOWNLOAD_RAMAIS = "download-ramais"

    FILTRO_LOCAL_ANORM_LEITURA = "filtro-local-anorm-leitura"

    TABELA_ANORM_LEITURA = "tabela-anorm-leitura"
    PESQUISA_ANORM_LEITURA = "pesquisa-anorm-leitura"
    PAGINA_ANORM_LEITURA = "pagina-anorm-leitura"
    TOTAL_ANORM_LEITURA = "total-anorm-leitura"

    TABELA_ANORM_CONSUMO_FREQ = "tabela-anorm-consumo-freq"
    PESQUISA_ANORM_CONSUMO_FREQ = "pesquisa-anorm-consumo-freq"
    PAGINA_ANORM_CONSUMO_FREQ = "pagina-anorm-consumo-freq"
    TOTAL_ANORM_CONSUMO_FREQ = "total-anorm-consumo-freq"

    TABELA_PERFIL_IMOVEL = "tabela-perfil-imovel"
    PAGINA_PERFIL_IMOVEL = "pagina-perfil-imovel"
    PESQUISA_PERFIL_IMOVEL = "pesquisa-perfil-imovel"
    TABELA_DIAMETRO = "tabela-diametro"
    PAGINA_DIAMETRO = "pagina-diametro"
    PESQUISA_DIAMETRO = "pesquisa-diametro"


ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS: dict[
    NOME_VARIAVEIS,
    str,
] = {
    "ramal": "associacao_col_ramal",
    "hidrometro": "associacao_col_hidrometro",
    "diametro": "associacao_col_diametro",
    "data_instalacao": "associacao_col_data_instalacao",
    "grupo_leitura": "associacao_col_grupo_leitura",
    "situacao_ligacao_agua": "associacao_col_situacao_ligacao_agua",
    "perfil_imovel": "associacao_col_perfil_imovel",
    "contas_vencidas_aberto": "associacao_contas_vencidas_aberto",
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
    "categoria": "associacao_categoria",
    "tipo_tarifa_esgoto": "associacao_tipo_tarifa_esgoto",
    "divida_total_vencida": "associacao_divida_total_vencida",
}


def componente_painel_erros(erros: list[str]):
    if len(erros) < 1:
        return []

    erros_html = [
        html.Div(
            [
                html.Div(
                    e,
                    style={
                        "padding": "0 2px",
                    },
                )
            ],
            style={
                "borderLeft": "solid 1px black",
                "borderRight": "solid 1px black",
                "borderBottom": "solid 1px black",
                "background": "whitesmoke",
                "fontSize": "0.8rem",
            },
        )
        for e in erros
    ]

    return html.Div(
        [
            html.Div(
                "Atenção:",
                style={
                    "border": "solid 1px black",
                    "padding": "0 2px",
                    "background": "yellow",
                    "fontSize": "0.8rem",
                    "fontWeight": "bold",
                },
            ),
            *erros_html,
        ],
        style={"display": "flex", "flexDirection": "column"},
    )


def gerar_form_importar_planilha(
    mes_extracao: int | None = None,
    ano_extracao: int | None = None,
):
    data_padrao = datetime.now()
    if mes_extracao is None:
        mes_extracao = data_padrao.month

    if ano_extracao is None:
        ano_extracao = data_padrao.year

    OPCOES_MESES: list[dict[str, str | int]] = [
        {"value": 1, "label": "Janeiro"},
        {"value": 2, "label": "Fevereiro"},
        {"value": 3, "label": "Março"},
        {"value": 4, "label": "Abril"},
        {"value": 5, "label": "Maio"},
        {"value": 6, "label": "Junho"},
        {"value": 7, "label": "Julho"},
        {"value": 8, "label": "Agosto"},
        {"value": 9, "label": "Setembro"},
        {"value": 10, "label": "Outubro"},
        {"value": 11, "label": "Novembro"},
        {"value": 12, "label": "Dezembro"},
    ]

    return html.Div(
        [
            dcc.Upload(
                id=ID_ELEMENTOS_HTML.UPLOAD_TABELA,
                style={"display": "flex"},
                children=[
                    html.Button("Escolher", type="button"),
                    dcc.Input(
                        None,
                        id=ID_ELEMENTOS_HTML.UPLOAD_NOME_ARQUIVO,
                        readOnly=True,
                        style={"flexGrow": "1"},
                    ),
                ],
            ),
            html.Div(
                [
                    html.Label("Mês da Extração"),
                    dcc.Dropdown(
                        OPCOES_MESES,  # type: ignore
                        id=ID_ELEMENTOS_HTML.MES_EXTRACAO,
                        value=mes_extracao,
                    ),
                    html.Label("Ano da Extração"),
                    dcc.Dropdown(
                        [ano for ano in range(ano_extracao - 20, ano_extracao + 1)],
                        id=ID_ELEMENTOS_HTML.ANO_EXTRACAO,
                        value=ano_extracao,
                    ),
                ]
            ),
            html.Button("Processar Planilha", id=ID_ELEMENTOS_HTML.PROCESSAR_TABELA),
            html.Div(id=ID_ELEMENTOS_HTML.UPLOAD_TABELA_ERRO, children=""),
        ],
        style={
            "display": "flex",
            "flexDirection": "column",
            "gap": "2px",
        },
    )


def gerar_form_colunas(
    data_referencia_1: str,
    data_referencia_2: str,
    data_referencia_3: str,
    opcoes: None | list[str] = None,
    erro="",
    valores_pre_selecionados: dict[NOME_VARIAVEIS, str] | None = None,
):
    opcoes_dropdowns: list[str] = []
    if opcoes is not None:
        opcoes_dropdowns = opcoes

    if valores_pre_selecionados is None:
        valores_pre_selecionados = {}

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
                dcc.Dropdown(
                    id=id_select,
                    options=opcoes_dropdowns,
                    value=valores_pre_selecionados.get(coluna_necessaria, None),
                ),
            ],
            style={"display": "flex", "flexDirection": "column", "gap": "1px"},
        )
        return div_html

    col_ramal = _label_e_dropdown("Ramal", "ramal")
    col_hidrometro = _label_e_dropdown("Hidrômetro", "hidrometro")
    col_diametro = _label_e_dropdown("Diâmetro", "diametro")
    col_data_instalacao = _label_e_dropdown("Data de Instalação", "data_instalacao")
    col_grupo_leitura = _label_e_dropdown("Grupo de Leitura", "grupo_leitura")
    col_situacao_ligacao_agua = _label_e_dropdown(
        "Situação Ligacao Água", "situacao_ligacao_agua"
    )
    col_perfil_imovel = _label_e_dropdown("Perfil do Imóvel", "perfil_imovel")
    col_categoria = _label_e_dropdown("Categoria", "categoria")
    col_divida_total_vencida = _label_e_dropdown(
        "Dívida Total Vencida", "divida_total_vencida"
    )
    col_contas_vencidas_aberto = _label_e_dropdown(
        "Contas Vencidas em Aberto", "contas_vencidas_aberto"
    )
    col_tipo_tarifa_esgoto = _label_e_dropdown(
        "Tipo de Tarifa de Esgoto", "tipo_tarifa_esgoto"
    )
    col_consumo_medio_mes_1 = _label_e_dropdown(
        "Média de Consumo", "media_consumo_mes_1"
    )
    col_consumo_medio_mes_2 = _label_e_dropdown(
        "Média de Consumo", "media_consumo_mes_2"
    )
    col_consumo_medio_mes_3 = _label_e_dropdown(
        "Média de Consumo", "media_consumo_mes_3"
    )
    col_anormalidade_leitura_mes_1 = _label_e_dropdown(
        "Anormalidade de Leitura", "anormalidade_leitura_mes_1"
    )
    col_anormalidade_leitura_mes_2 = _label_e_dropdown(
        "Anormalidade de Leitura", "anormalidade_leitura_mes_2"
    )
    col_anormalidade_leitura_mes_3 = _label_e_dropdown(
        "Anormalidade de Leitura", "anormalidade_leitura_mes_3"
    )
    col_consumo_medido_mes_1 = _label_e_dropdown(
        "Consumo Medido", "consumo_medido_mes_1"
    )
    col_consumo_medido_mes_2 = _label_e_dropdown(
        "Consumo Medido", "consumo_medido_mes_2"
    )
    col_consumo_medido_mes_3 = _label_e_dropdown(
        "Consumo Medido", "consumo_medido_mes_3"
    )

    col_consumo_faturado_mes_1 = _label_e_dropdown(
        "Consumo Faturado", "consumo_faturado_mes_1"
    )
    col_consumo_faturado_mes_2 = _label_e_dropdown(
        "Consumo Faturado", "consumo_faturado_mes_2"
    )
    col_consumo_faturado_mes_3 = _label_e_dropdown(
        "Consumo Faturado", "consumo_faturado_mes_3"
    )

    col_anormalidade_consumo_mes_1 = _label_e_dropdown(
        "Anormalidade de Consumo", "anormalidade_consumo_mes_1"
    )
    col_anormalidade_consumo_mes_2 = _label_e_dropdown(
        "Anormalidade de Consumo", "anormalidade_consumo_mes_2"
    )
    col_anormalidade_consumo_mes_3 = _label_e_dropdown(
        "Anormalidade de Consumo", "anormalidade_consumo_mes_3"
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
                            col_ramal,
                            col_hidrometro,
                            col_diametro,
                            col_data_instalacao,
                            col_grupo_leitura,
                            col_situacao_ligacao_agua,
                            col_perfil_imovel,
                            col_categoria,
                            col_tipo_tarifa_esgoto,
                            col_divida_total_vencida,
                            col_contas_vencidas_aberto,
                            html.Fieldset(
                                [
                                    html.Legend(
                                        f"Dados de {data_referencia_1}",
                                        style={"fontWeight": "bold"},
                                    ),
                                    col_consumo_medio_mes_1,
                                    col_anormalidade_leitura_mes_1,
                                    col_consumo_medido_mes_1,
                                    col_consumo_faturado_mes_1,
                                    col_anormalidade_consumo_mes_1,
                                ],
                            ),
                            html.Fieldset(
                                [
                                    html.Legend(
                                        f"Dados de {data_referencia_2}",
                                        style={"fontWeight": "bold"},
                                    ),
                                    col_consumo_medio_mes_2,
                                    col_anormalidade_leitura_mes_2,
                                    col_consumo_medido_mes_2,
                                    col_consumo_faturado_mes_2,
                                    col_anormalidade_consumo_mes_2,
                                ],
                            ),
                            html.Fieldset(
                                [
                                    html.Legend(
                                        f"Dados de {data_referencia_3}",
                                        style={"fontWeight": "bold"},
                                    ),
                                    col_consumo_medio_mes_3,
                                    col_anormalidade_leitura_mes_3,
                                    col_consumo_medido_mes_3,
                                    col_consumo_faturado_mes_3,
                                    col_anormalidade_consumo_mes_3,
                                ],
                            ),
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
    opcoes_valores_categoria,
    valores_unicos_categoria,
    opcoes_valores_tipo_tarifa_esgoto,
    valores_unicos_tipo_tarifa_esgoto,
    opcoes_valores_anormalidade_consumo,
    valores_unicos_anormalidade_consumo,
):
    estilo_fieldset = {
        "border": "1px solid #2a3f5f",
        "borderRadius": "8px",
        "padding": "12px 16px",
        "backgroundColor": "#1a2235",
    }
    estilo_legend = {
        "fontWeight": "bold",
        "fontSize": "0.75rem",
        "color": "#8899aa",
        "textTransform": "uppercase",
        "letterSpacing": "0.5px",
        "padding": "0 6px",
    }
    estilo_grid_interno = {
        "display": "grid",
        "gridTemplateColumns": "repeat(auto-fit, minmax(180px, 1fr))",
        "gap": "12px",
        "marginTop": "10px",
    }

    return [
        html.Fieldset(
            style=estilo_fieldset,
            children=[
                html.Legend("Hidrômetro", style=estilo_legend),
                html.Div(
                    style=estilo_grid_interno,
                    children=[
                        html.Div([
                            html.Label("Diâmetro", style=EstilosCSS.LABEL_FILTRO),
                            dcc.Dropdown(
                                id=ID_ELEMENTOS_HTML.FILTRO_DIAMETRO,
                                options=opcoes_valores_diametro_filtro,
                                value=valores_unicos_diametro,
                                multi=True,
                                placeholder="Selecione...",
                            ),
                        ], style=EstilosCSS.ITEM_FILTRO),
                        html.Div([
                            html.Label("Diâmetro + Letra", style=EstilosCSS.LABEL_FILTRO),
                            dcc.Dropdown(
                                id=ID_ELEMENTOS_HTML.FILTRO_DIAMETRO_LETRA,
                                options=opcoes_valores_diametro_letra,
                                value=valores_unicos_diametro_letra,
                                multi=True,
                                placeholder="Selecione...",
                            ),
                        ], style=EstilosCSS.ITEM_FILTRO),
                        html.Div([
                            html.Label(
                                f"Idade ({valor_minimo_idade} – {valor_maximo_idade} anos)",
                                style=EstilosCSS.LABEL_FILTRO,
                            ),
                            html.Div(
                                dcc.RangeSlider(
                                    id=ID_ELEMENTOS_HTML.FILTRO_IDADE,
                                    min=valor_minimo_idade,
                                    max=valor_maximo_idade,
                                    step=1,
                                    value=[valor_minimo_idade, valor_maximo_idade],
                                    marks={
                                        str(i): (
                                            str(i)
                                            if i % 5 == 0
                                            or i == valor_minimo_idade
                                            or i == valor_maximo_idade
                                            else ""
                                        )
                                        for i in range(valor_minimo_idade, valor_maximo_idade + 1)
                                    },
                                    tooltip={"placement": "bottom", "always_visible": True},
                                ),
                                style={"marginTop": "15px"},
                            ),
                        ], style=EstilosCSS.ITEM_FILTRO | {"gridColumn": "1 / -1"}),
                    ],
                ),
            ],
        ),
        html.Fieldset(
            style=estilo_fieldset,
            children=[
                html.Legend("Ligação / Imóvel", style=estilo_legend),
                html.Div(
                    style=estilo_grid_interno,
                    children=[
                        html.Div([
                            html.Label("Situação Ligação Água", style=EstilosCSS.LABEL_FILTRO),
                            dcc.Checklist(
                                id=ID_ELEMENTOS_HTML.FILTRO_SITUACAO,
                                options=opcoes_valores_situacao_ligacao_agua,
                                value=opcoes_selecionadas_situacao_ligacao_agua,
                                inline=True,
                                labelStyle={"marginRight": "10px", "cursor": "pointer"},
                            ),
                        ], style=EstilosCSS.ITEM_FILTRO | {"gridColumn": "1 / -1"}),
                        html.Div([
                            html.Label("Grupo de Faturamento", style=EstilosCSS.LABEL_FILTRO),
                            dcc.Dropdown(
                                id=ID_ELEMENTOS_HTML.FILTRO_GRUPO_FATURAMENTO,
                                options=opcoes_valores_grupo_faturamento,
                                value=valores_unicos_grupo_faturamento,
                                multi=True,
                                placeholder="Selecione...",
                            ),
                        ], style=EstilosCSS.ITEM_FILTRO),
                        html.Div([
                            html.Label("Perfil do Imóvel", style=EstilosCSS.LABEL_FILTRO),
                            dcc.Dropdown(
                                id=ID_ELEMENTOS_HTML.FILTRO_PERFIL_IMOVEL,
                                options=opcoes_valores_perfil_imovel,
                                value=valores_unicos_perfil_imovel,
                                multi=True,
                                placeholder="Selecione...",
                            ),
                        ], style=EstilosCSS.ITEM_FILTRO),
                    ],
                ),
            ],
        ),
        html.Fieldset(
            style=estilo_fieldset,
            children=[
                html.Legend("Tarifação", style=estilo_legend),
                html.Div(
                    style=estilo_grid_interno,
                    children=[
                        html.Div([
                            html.Label("Categoria", style=EstilosCSS.LABEL_FILTRO),
                            dcc.Dropdown(
                                id=ID_ELEMENTOS_HTML.FILTRO_CATEGORIA,
                                options=opcoes_valores_categoria,
                                value=valores_unicos_categoria,
                                multi=True,
                                placeholder="Selecione...",
                            ),
                        ], style=EstilosCSS.ITEM_FILTRO),
                        html.Div([
                            html.Label("Tipo de Tarifa de Esgoto", style=EstilosCSS.LABEL_FILTRO),
                            dcc.Dropdown(
                                id=ID_ELEMENTOS_HTML.FILTRO_TIPO_TARIFA_ESGOTO,
                                options=opcoes_valores_tipo_tarifa_esgoto,
                                value=valores_unicos_tipo_tarifa_esgoto,
                                multi=True,
                                placeholder="Selecione...",
                            ),
                        ], style=EstilosCSS.ITEM_FILTRO),
                    ],
                ),
            ],
        ),
        html.Fieldset(
            style=estilo_fieldset,
            children=[
                html.Legend("Anormalidades", style=estilo_legend),
                html.Div(
                    style=estilo_grid_interno,
                    children=[
                        html.Div([
                            html.Label("Anormalidade de Consumo", style=EstilosCSS.LABEL_FILTRO),
                            dcc.Dropdown(
                                id=ID_ELEMENTOS_HTML.FILTRO_ANORMALIDADE_CONSUMO,
                                options=opcoes_valores_anormalidade_consumo,
                                value=valores_unicos_anormalidade_consumo,
                                multi=True,
                                placeholder="Selecione...",
                            ),
                        ], style=EstilosCSS.ITEM_FILTRO),
                    ],
                ),
            ],
        ),
    ]


def _ramais_para_tabela(df_ramais: pd.DataFrame, col_anorm: str, col_consumo: str) -> list[dict]:
    return (
        df_ramais
        .rename(columns={"diametro_letra": "diametro", col_anorm: "anormalidade", col_consumo: "consumo_medio"})
        [["ramal", "diametro", "anormalidade", "consumo_medio"]]
        .to_dict("records")
    )


def gerar_html_dados(
    df,
    datas_referencias: tuple[str, str, str],
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
    frequencia_contas_vencidas_aberto,
    ramais_com_consumo_maior_ou_menor_que_o_esperado: tuple[
        pd.DataFrame, pd.DataFrame, pd.DataFrame
    ],
    frequencia_divida_total_vencida: pd.DataFrame,
):
    if idade_media_hidrometros is not np.nan:
        idade_media_hidrometros = f"{idade_media_hidrometros:.2f}"
    else:
        idade_media_hidrometros = "-"

    if porcentagem_hidrometros_ligados == 0.0:
        porcentagem_hidrometros_ligados = "-"
    else:
        porcentagem_hidrometros_ligados = f"{porcentagem_hidrometros_ligados:.2f}"

    _vals_anorm_leitura = sorted(pd.concat([
        df["anormalidade_leitura_mes_1"],
        df["anormalidade_leitura_mes_2"],
        df["anormalidade_leitura_mes_3"],
    ]).dropna().unique().tolist())
    _opcoes_anorm_leitura = [{"label": v, "value": v} for v in _vals_anorm_leitura]

    _ESTILO_CARD_SECAO = {
        "display": "flex",
        "flexDirection": "column",
        "gap": "0",
        "gridColumnStart": "span 6",
        "backgroundColor": "#151929",
        "border": "1px solid #2a3f5f",
        "borderRadius": "12px",
        "padding": "20px",
    }

    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.H3(
                                "Análise Descritiva",
                                style={"color": "#ffffff", "fontSize": "1rem", "margin": "0"},
                            ),
                        ],
                        style={"marginBottom": "16px"},
                    ),
                    html.Div(
                        [
                            gerar_html_quadro_dado(
                                contagem_hidrometros,
                                "Nº Total de Hidrômetros",
                                id_dado_numero=ID_ELEMENTOS_HTML.CONTAGEM_HIDROMETROS,
                                icone="#",
                            ),
                            gerar_html_quadro_dado(
                                porcentagem_hidrometros_ligados,
                                "Hidrômetros Ligados (%)",
                                id_dado_numero=ID_ELEMENTOS_HTML.PORCENTAGEM_HIDROMETOS_LIGADOS,
                                icone="%",
                            ),
                            gerar_html_quadro_dado(
                                idade_media_hidrometros,
                                "Idade Média (anos)",
                                id_dado_numero=ID_ELEMENTOS_HTML.IDADE_MEDIA_HIDROMETROS,
                                icone="⌀",
                            ),
                            html.Div(
                                [
                                    dcc.Graph(
                                        figure=px.bar(
                                            x=df["idade_hidrometro"].value_counts().sort_index().index,
                                            y=df["idade_hidrometro"].value_counts().sort_index(),
                                            labels={"x": "Idade do Hidrômetro (anos)", "y": "Frequência"},
                                            color_discrete_sequence=_PLOTLY_CORES_BARRAS,
                                        ).update_layout(
                                            title="Gráfico de Frequência de Idade dos Hidrômetros",
                                            xaxis=dict(
                                                tickmode="linear",
                                                tick0=0,
                                                dtick=1,
                                                title="Idade do Hidrômetro (anos)",
                                                gridcolor="#2a3f5f",
                                                linecolor="#2a3f5f",
                                            ),
                                            yaxis=dict(title="Frequência", gridcolor="#2a3f5f", linecolor="#2a3f5f"),
                                            bargap=0.05,
                                            paper_bgcolor="#1a2235",
                                            plot_bgcolor="#1a2235",
                                            font_color="#8899aa",
                                        )
                                    )
                                ],
                                style=EstilosCSS.GRAFICO,
                            ),
                            html.Div(
                                [
                                    dcc.Graph(
                                        figure=px.bar(
                                            x=df["grupo_leitura"].value_counts().rename(index=lambda v: v.upper().replace("GRUPO-", "")).sort_index(key=lambda x: x.astype(int)).index,
                                            y=df["grupo_leitura"].value_counts().rename(index=lambda v: v.upper().replace("GRUPO-", "")).sort_index(key=lambda x: x.astype(int)),
                                            labels={"y": "Frequência", "x": "Grupo de Faturamento"},
                                            title="Gráfico de Frequência do Grupo de Faturamento",
                                            color_discrete_sequence=_PLOTLY_CORES_BARRAS,
                                        ).update_layout(**_PLOTLY_DARK_LAYOUT)
                                    )
                                ],
                                style=EstilosCSS.GRAFICO,
                            ),
                            _caixa_tabela(
                                "Tabela de Frequência de Perfil de Imóvel",
                                id_pagina=ID_ELEMENTOS_HTML.PAGINA_PERFIL_IMOVEL,
                                id_pesquisa=ID_ELEMENTOS_HTML.PESQUISA_PERFIL_IMOVEL,
                                id_tabela=ID_ELEMENTOS_HTML.TABELA_PERFIL_IMOVEL,
                                data=freq_perfil_imoveis,
                                columns=[{"name": k, "id": k} for k in freq_perfil_imoveis[0].keys()] if freq_perfil_imoveis else [],
                                page_size_default=5,
                            ),
                            _caixa_tabela(
                                "Tabela de Frequência de Diâmetro em Hidrômetros",
                                id_pagina=ID_ELEMENTOS_HTML.PAGINA_DIAMETRO,
                                id_pesquisa=ID_ELEMENTOS_HTML.PESQUISA_DIAMETRO,
                                id_tabela=ID_ELEMENTOS_HTML.TABELA_DIAMETRO,
                                data=freq_hidrometros,
                                columns=[{"name": k, "id": k} for k in freq_hidrometros[0].keys()] if freq_hidrometros else [],
                                page_size_default=5,
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
                        ],
                        style=EstilosCSS.GRID_AREA_DADOS_CONSUMO,
                    ),
                ],
                style=_ESTILO_CARD_SECAO,
            ),
            html.Div(
                children=[
                    # Cabeçalho da seção
                    html.Div(
                        [
                            html.H3(
                                "Análise de Consumo",
                                style={"color": "#ffffff", "fontSize": "1rem", "margin": "0"},
                            ),
                            html.P(
                                "Estatísticas de consumo por mês de referência.",
                                style={"color": "#8899aa", "fontSize": "0.78rem", "margin": "4px 0 0 0"},
                            ),
                        ],
                        style={"marginBottom": "16px"},
                    ),
                    # Painel de controles locais
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Label("Mês de Referência", style=EstilosCSS.LABEL_FILTRO),
                                    dcc.RadioItems(
                                        {
                                            "1": f"{datas_referencias[0]}",
                                            "2": f"{datas_referencias[1]}",
                                            "3": f"{datas_referencias[2]}",
                                        },
                                        value="1",
                                        inline=True,
                                        id=ID_ELEMENTOS_HTML.ESCOLHA_ABA_DADOS_CONSUMO,
                                        labelStyle={"marginRight": "10px", "cursor": "pointer", "color": "#ffffff"},
                                    ),
                                ],
                                style=EstilosCSS.ITEM_FILTRO,
                            ),
                            html.Div(
                                [
                                    html.Label("Concatenar consumo a partir de:", style=EstilosCSS.LABEL_FILTRO),
                                    html.Div(
                                        [
                                            dcc.Input(
                                                130,
                                                "number",
                                                id=ID_ELEMENTOS_HTML.VALOR_LIMITE_CONCATENAR,
                                                style={"backgroundColor": "#212d45", "color": "#ffffff", "border": "1px solid #2a3f5f", "padding": "6px 10px", "width": "90px"},
                                            ),
                                            html.Button(
                                                "Concatenar",
                                                id=ID_ELEMENTOS_HTML.BOTAO_CONCATENAR_CONSUMO,
                                                style={"backgroundColor": "#2196c4", "color": "white", "border": "none", "padding": "6px 14px", "fontWeight": "bold", "cursor": "pointer"},
                                            ),
                                        ],
                                        style={"display": "flex", "gap": "8px"},
                                    ),
                                ],
                                style=EstilosCSS.ITEM_FILTRO,
                            ),
                            html.Div(
                                [
                                    html.Label("Anormalidade de Leitura (filtro local)", style=EstilosCSS.LABEL_FILTRO),
                                    dcc.Dropdown(
                                        id=ID_ELEMENTOS_HTML.FILTRO_LOCAL_ANORM_LEITURA,
                                        options=_opcoes_anorm_leitura,
                                        value=_vals_anorm_leitura,
                                        multi=True,
                                        placeholder="Selecione...",
                                    ),
                                ],
                                style=EstilosCSS.ITEM_FILTRO | {"gridColumn": "1 / -1"},
                            ),
                        ],
                        style={
                            "display": "grid",
                            "gridTemplateColumns": "1fr 1fr",
                            "gap": "16px",
                            "backgroundColor": "#1a2235",
                            "border": "1px solid #2a3f5f",
                            "borderRadius": "8px",
                            "padding": "16px",
                            "marginBottom": "12px",
                        },
                    ),
                    html.Div(
                        id=ID_ELEMENTOS_HTML.AREA_DADOS_CONSUMO_MES,
                        children=[
                            gerar_html_dados_consumo_mes(
                                media_do_consumo_medio_mes_1,
                                desvio_padrao_consumo_medio_mes_1,
                                frequencia_consumo_acima_limite_mes_1,
                                frequencia_consumos_medios_mes_1,
                                frequencia_consumos_medidos_mes_1,
                                frequencia_consumo_faturado_mes_1,
                                anormalidade_leitura_mes_1,
                                frequencia_anormalidade_consumo_1,
                                ramais_com_consumo_maior_ou_menor_que_o_esperado[0],
                                "consumo_max_mes_1",
                                "media_consumo_mes_1",
                                datas_referencias[0],
                                ID_ELEMENTOS_HTML.DADOS_CONSUMO_MES_1,
                                mes_index="mes-1",
                            ),
                            gerar_html_dados_consumo_mes(
                                media_do_consumo_medio_mes_2,
                                desvio_padrao_consumo_medio_mes_2,
                                frequencia_consumo_acima_limite_mes_2,
                                frequencia_consumos_medios_mes_2,
                                frequencia_consumos_medidos_mes_2,
                                frequencia_consumo_faturado_mes_2,
                                anormalidade_leitura_mes_2,
                                frequencia_anormalidade_consumo_2,
                                ramais_com_consumo_maior_ou_menor_que_o_esperado[1],
                                "consumo_max_mes_2",
                                "media_consumo_mes_2",
                                datas_referencias[1],
                                ID_ELEMENTOS_HTML.DADOS_CONSUMO_MES_2,
                                mes_index="mes-2",
                                oculto=True,
                            ),
                            gerar_html_dados_consumo_mes(
                                media_do_consumo_medio_mes_3,
                                desvio_padrao_consumo_medio_mes_3,
                                frequencia_consumo_acima_limite_mes_3,
                                frequencia_consumos_medios_mes_3,
                                frequencia_consumos_medidos_mes_3,
                                frequencia_consumo_faturado_mes_3,
                                anormalidade_leitura_mes_3,
                                frequencia_anormalidade_consumo_3,
                                ramais_com_consumo_maior_ou_menor_que_o_esperado[2],
                                "consumo_max_mes_3",
                                "media_consumo_mes_3",
                                datas_referencias[2],
                                ID_ELEMENTOS_HTML.DADOS_CONSUMO_MES_3,
                                mes_index="mes-3",
                                oculto=True,
                            ),
                        ],
                    ),
                ],
                style={
                    "display": "flex",
                    "flexDirection": "column",
                    "gap": "0",
                    "gridColumnStart": "span 6",
                    "backgroundColor": "#151929",
                    "border": "1px solid #2a3f5f",
                    "borderRadius": "12px",
                    "padding": "20px",
                },
            ),
        ],
        id=ID_ELEMENTOS_HTML.AREA_DADOS,
    )



def _caixa_tabela(titulo, id_pagina, id_pesquisa, id_tabela, data, columns, children_extra=None, page_size_default=10):
    _ESTILO_BOX = {
        "gridColumnStart": "span 6",
        "backgroundColor": "#1a2235",
        "border": "1px solid #2a3f5f",
        "borderRadius": "12px",
        "padding": "20px",
    }
    conteudo = [
        html.H5(
            titulo,
            style={"color": "#8899aa", "textTransform": "uppercase", "letterSpacing": "0.5px", "fontSize": "0.82rem", "marginBottom": "10px"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Mostrar", style={"color": "#8899aa", "fontSize": "0.8rem"}),
                        dcc.Dropdown(
                            options=[{"label": str(n), "value": n} for n in [5, 10, 25, 50, 100]],
                            value=page_size_default,
                            id=id_pagina,
                            clearable=False,
                            style={"width": "80px", "display": "inline-block"},
                        ),
                        html.Label("entradas", style={"color": "#8899aa", "fontSize": "0.8rem"}),
                    ],
                    style={"display": "flex", "gap": "8px", "alignItems": "center"},
                ),
                html.Div(
                    [
                        html.Label("Buscar:", style={"color": "#8899aa", "fontSize": "0.8rem"}),
                        dcc.Input(
                            id=id_pesquisa,
                            type="text",
                            debounce=True,
                            placeholder="Filtrar...",
                            style={"backgroundColor": "#212d45", "color": "#ffffff", "border": "1px solid #2a3f5f", "padding": "5px 10px"},
                        ),
                    ],
                    style={"display": "flex", "gap": "8px", "alignItems": "center"},
                ),
            ],
            style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "8px"},
        ),
        DataTable(
            data=data,
            columns=columns,
            id=id_tabela,
            page_size=page_size_default,
            page_action="native",
            sort_action="native",
            filter_action="native",
            **_TABELA_DARK,
        ),
    ]
    if children_extra:
        conteudo.extend(children_extra)

    return html.Div(conteudo, style=_ESTILO_BOX)


def gerar_html_dados_consumo_mes(
    media_consumo_medio: float,
    desvio_padrao: float,
    frequencia_consumo_acima_limite: int,
    frequencia_consumos_medios: pd.Series,
    frequencia_consumos_medidos: pd.Series,
    frequencia_consumo_faturado: pd.Series,
    anormalidade_de_leitura: pd.DataFrame,
    frequencia_anormalidade_consumo: pd.DataFrame,
    ramais_df: pd.DataFrame,
    col_anorm_ramais: str,
    col_consumo_ramais: str,
    titulo: str,
    id_html_elemento: str,
    mes_index: str,
    limite_consumo_utilizado: int = 130,
    oculto: bool = False,
):
    estilo = EstilosCSS.GRID_AREA_DADOS_CONSUMO
    if oculto:
        estilo = {"display": "none"}

    _COLS_ANORM = [{"name": c, "id": c} for c in anormalidade_de_leitura.columns]
    _COLS_CONSUMO = [{"name": c, "id": c} for c in frequencia_anormalidade_consumo.columns]
    _COLS_RAMAIS = [
        {"name": "Ramal", "id": "ramal"},
        {"name": "Diâmetro", "id": "diametro"},
        {"name": "Anormalidade", "id": "anormalidade"},
        {"name": "Consumo Médio", "id": "consumo_medio", "type": "numeric"},
    ]

    _botoes_download = [
        html.Div(
            [
                html.Button(
                    "⬇ Download sem filtros",
                    id={"type": "btn-dl-sem", "index": mes_index},
                    style={"backgroundColor": "#2196c4", "color": "white", "border": "none", "padding": "8px 16px", "borderRadius": "6px", "fontWeight": "bold", "cursor": "pointer", "fontSize": "0.8rem"},
                ),
                html.Button(
                    "⬇ Download com filtros",
                    id={"type": "btn-dl-com", "index": mes_index},
                    style={"backgroundColor": "#2196c4", "color": "white", "border": "none", "padding": "8px 16px", "borderRadius": "6px", "fontWeight": "bold", "cursor": "pointer", "fontSize": "0.8rem"},
                ),
                dcc.Download(id={"type": "download-mes", "index": mes_index}),
            ],
            style={"display": "flex", "gap": "12px", "marginTop": "14px"},
        ),
    ]

    return html.Div(
        id=id_html_elemento,
        children=[
            html.H4(titulo, style={"gridColumnStart": "1", "gridColumnEnd": "-1"}),
            # 3 cards
            gerar_html_quadro_dado(f"{media_consumo_medio:.2f}", "Consumo Médio"),
            gerar_html_quadro_dado(f"{desvio_padrao:.2f}", "Desvio Padrão do Consumo Médio"),
            gerar_html_quadro_dado(frequencia_consumo_acima_limite, f"Frequência de Consumo maior que {limite_consumo_utilizado}"),
            # Gráfico de Consumo Médio
            html.Div(
                [dcc.Graph(
                    figure=px.bar(
                        x=[str(x) for x in frequencia_consumos_medios.index],
                        y=frequencia_consumos_medios,
                        labels={"y": "Frequência", "x": "Consumo Médio"},
                        title="Gráfico de Consumo Médio",
                        color_discrete_sequence=_PLOTLY_CORES_BARRAS,
                    ).update_layout(**_PLOTLY_DARK_LAYOUT)
                )],
                style=EstilosCSS.GRAFICO,
            ),
            # Box: Anorm Leitura
            _caixa_tabela(
                "Tabela de Frequência de Anormalidade de Leitura",
                id_pagina={"type": "pagina-anorm-leitura", "index": mes_index},
                id_pesquisa={"type": "pesquisa-anorm-leitura", "index": mes_index},
                id_tabela={"type": "tabela-anorm-leitura", "index": mes_index},
                data=anormalidade_de_leitura.to_dict("records"),
                columns=_COLS_ANORM,
            ),
            # Box: Anorm Consumo
            _caixa_tabela(
                "Tabela de Frequência de Anormalidade de Consumo",
                id_pagina={"type": "pagina-anorm-consumo", "index": mes_index},
                id_pesquisa={"type": "pesquisa-anorm-consumo", "index": mes_index},
                id_tabela={"type": "tabela-anorm-consumo", "index": mes_index},
                data=frequencia_anormalidade_consumo.to_dict("records"),
                columns=_COLS_CONSUMO,
            ),
            # Gráficos lado a lado: Consumo Medido e Consumo Faturado
            html.Div(
                [dcc.Graph(
                    figure=px.bar(
                        x=[str(x) for x in frequencia_consumos_medidos.index],
                        y=frequencia_consumos_medidos,
                        labels={"y": "Frequência", "x": "Consumo Medido"},
                        title="Gráfico de Consumo Medido",
                        color_discrete_sequence=_PLOTLY_CORES_BARRAS,
                    ).update_layout(**_PLOTLY_DARK_LAYOUT)
                )],
                style={"gridColumnStart": "span 3"},
            ),
            html.Div(
                [dcc.Graph(
                    figure=px.bar(
                        x=[str(x) for x in frequencia_consumo_faturado.index],
                        y=frequencia_consumo_faturado,
                        labels={"y": "Frequência", "x": "Consumo Faturado"},
                        title="Gráfico de Consumo Faturado",
                        color_discrete_sequence=_PLOTLY_CORES_BARRAS,
                    ).update_layout(**_PLOTLY_DARK_LAYOUT)
                )],
                style={"gridColumnStart": "span 3"},
            ),
            # Box: Ramais com consumo fora do esperado + downloads
            _caixa_tabela(
                "Tabela de Ramais com Consumo Menor ou Maior do que o Esperado",
                id_pagina={"type": "pagina-ramais-mes", "index": mes_index},
                id_pesquisa={"type": "pesquisa-ramais-mes", "index": mes_index},
                id_tabela={"type": "tabela-ramais-mes", "index": mes_index},
                data=_ramais_para_tabela(ramais_df, col_anorm_ramais, col_consumo_ramais),
                columns=_COLS_RAMAIS,
                children_extra=_botoes_download,
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
    icone: str = "",
):
    if estilo_extra is None:
        estilo_extra = {}

    return html.Div(
        [
            html.Div(dado, style=EstilosCSS.QUADRO_DADO_NUMERO, id=id_dado_numero),
            html.Div(titulo, style=EstilosCSS.QUADRO_DADO_LABEL),
        ],
        style=EstilosCSS.QUADRO_DADO | estilo_extra,
        hidden=hidden,
    )


def gerar_html_zero_resultados():
    return html.Div("0 Resultados")
