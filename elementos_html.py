from datetime import datetime
from enum import StrEnum

import pandas as pd
from dash import dcc, html
import numpy as np
import plotly.express as px  # type: ignore
from dash.dash_table.DataTable import DataTable

from tipos import NOME_VARIAVEIS

NOME_APLICATIVO = "Painel de Gestão do Consumo"
SUBTITULO_APLICATIVO = "DMAE · Gerência de Gestão do Consumo"
TEXTO_SOBRE_APLICATIVO = (
    "Desenvolvido pelo Departamento de Estatística da UFRGS, em projeto de "
    "extensão com alunos do curso. Uso: Gerência de Gestão do Consumo — DMAE."
)

_PLOTLY_CORES_BARRAS = ["#4f80b8", "#2f6db0", "#7fa8d1", "#b0c8e8"]

_PLOTLY_DARK_LAYOUT = dict(
    paper_bgcolor="#ffffff",
    plot_bgcolor="#ffffff",
    font_color="#5d6570",
    xaxis={"gridcolor": "#dde0e5", "linecolor": "#c6cad1"},
    yaxis={"gridcolor": "#dde0e5", "linecolor": "#c6cad1"},
)

# Margem fixa e idêntica para os gráficos de idade/grupo de faturamento
# (lado a lado, Análise Descritiva): sem isso, o Plotly calcula a margem
# superior de cada figura de um jeito diferente dependendo de como o título
# foi definido (direto no px.bar() vs. via update_layout() depois), o que
# fazia os dois gráficos ficarem com título/plotagem em alturas diferentes.
_MARGEM_GRAFICOS_LADO_A_LADO = dict(t=60, b=60, l=60, r=30)

_TABELA_DARK = dict(
    style_cell={
        "textAlign": "left",
        "border": "1px solid #dde0e5",
        "backgroundColor": "#ffffff",
        "color": "#252a31",
        "padding": "9px 15px",
        "fontSize": "12.5px",
        "fontFamily": '"Segoe UI", system-ui, sans-serif',
    },
    style_header={
        "backgroundColor": "#f5f6f8",
        "fontWeight": "600",
        "textTransform": "uppercase",
        "color": "#5d6570",
        "border": "1px solid #dde0e5",
        "letterSpacing": "0.05em",
        "fontSize": "11px",
    },
    style_data_conditional=[
        {
            "if": {"state": "active"},
            "backgroundColor": "rgba(47,109,176,.09)",
            "border": "1px solid #dde0e5",
        },
    ],
)


class EstilosCSS:
    QUADRO_DADO = {
        "display": "flex",
        "flexDirection": "column",
        "justifyContent": "flex-start",
        "padding": "14px 16px",
        "backgroundColor": "#ffffff",
        "color": "#252a31",
        "gridColumn": "span 2",
        "borderRight": "1px solid #dde0e5",
        "borderBottom": "1px solid #dde0e5",
    }

    QUADRO_DADO_NUMERO = {
        "fontSize": "28px",
        "fontWeight": "500",
        "letterSpacing": "-.02em",
        "lineHeight": "1",
        "marginBottom": "0",
        "color": "#252a31",
        "fontVariantNumeric": "tabular-nums",
    }

    QUADRO_DADO_ICONE = {
        "fontSize": "1.2rem",
        "color": "#2f6db0",
        "minWidth": "32px",
        "textAlign": "center",
        "lineHeight": "1",
    }

    QUADRO_DADO_LABEL = {
        "fontSize": "11.5px",
        "color": "#5d6570",
        "marginBottom": "9px",
    }

    TABELA = {"gridColumnStart": "span 6"}
    TABELA_METADE = {"gridColumnStart": "span 3"}
    GRAFICO = {"gridColumnStart": "span 6"}
    GRAFICO_METADE = {"gridColumnStart": "span 3"}

    CHECKLIST = {"display": "flex", "columnGap": "1px", "flexWrap": "wrap"}
    CHECKLIST_LABEL = {
        "border": "1px solid #dde0e5",
        "borderRadius": "3px",
        "margin": "2px",
        "backgroundColor": "#f7f8fa",
        "color": "#252a31",
        "fontWeight": "500",
        "cursor": "pointer",
    }

    CONTAINER_FILTROS = {
        "display": "grid",
        "gridTemplateColumns": "repeat(auto-fit, minmax(250px, 1fr))",
        "gap": "16px",
        "padding": "18px",
        "backgroundColor": "#f5f6f8",
        "border": "1px solid #dde0e5",
    }

    ITEM_FILTRO = {"display": "flex", "flexDirection": "column", "gap": "6px"}

    LABEL_FILTRO = {
        "fontWeight": "600",
        "fontSize": "11px",
        "color": "#5d6570",
        "textTransform": "uppercase",
        "letterSpacing": "0.1em",
    }

    BOTAO_FILTRAR = {
        "backgroundColor": "#2f6db0",
        "color": "white",
        "border": "none",
        "padding": "10px",
        "fontWeight": "500",
        "cursor": "pointer",
        "width": "100%",
        "fontFamily": '"Segoe UI", system-ui, sans-serif',
        "fontSize": "12.5px",
    }

    GRID_AREA_DADOS_CONSUMO = {
        "display": "grid",
        "gridTemplateColumns": "repeat(6, 1fr)",
        "columnGap": "10px",
        "rowGap": "10px",
    }

    ESTILO_SOBRE_FECHADO = {"display": "none"}
    ESTILO_SOBRE_ABERTO = {
        "display": "block",
        "position": "absolute",
        "top": "100%",
        "left": "0",
        "width": "320px",
        "zIndex": "1002",
        "backgroundColor": "#ffffff",
        "border": "1px solid #dde0e5",
        "boxShadow": "0 4px 16px rgba(0,0,0,0.15)",
        "padding": "12px 14px",
        "fontSize": "12px",
        "color": "#5d6570",
        "lineHeight": "1.4",
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

    BOTAO_DOWNLOAD_TABELA_COMPLETA_FILTRADA = "download-tabela-completa-filtrada"
    DOWNLOADER_TABELA_COMPLETA_FILTRADA = "downloader-tabela-completa-filtrada"

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

    TAB_DESCRITIVA = "tab-descritiva"
    TAB_CONSUMO = "tab-consumo"
    SECAO_DESCRITIVA = "secao-descritiva"
    SECAO_CONSUMO_CARD = "secao-consumo-card"
    META_REGISTROS = "meta-registros"
    META_REFERENCIA = "meta-referencia"
    RODAPE = "rodape"

    BOTAO_SOBRE = "botao-sobre"
    PAINEL_SOBRE = "painel-sobre"

    SCROLL_RESET_DUMMY = "scroll-reset-dummy"


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


def componente_aviso_coluna_nao_associada(nome_variavel: str):
    """
    Substitui um gráfico/tabela quando a coluna que o alimenta não foi
    associada a nenhuma coluna do arquivo importado.
    """
    return html.Div(
        [
            html.Div(
                "Coluna não associada",
                style={
                    "fontSize": "11px",
                    "fontWeight": "600",
                    "textTransform": "uppercase",
                    "letterSpacing": "0.08em",
                    "color": "#8b929c",
                    "marginBottom": "6px",
                },
            ),
            html.Div(
                f'A coluna "{nome_variavel}" não foi associada a nenhuma coluna do arquivo.',
                style={
                    "fontSize": "12.5px",
                    "color": "#5d6570",
                    "maxWidth": "320px",
                },
            ),
        ],
        style={
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "center",
            "alignItems": "center",
            "textAlign": "center",
            "minHeight": "220px",
            "padding": "20px",
            "backgroundColor": "#f7f8fa",
            "border": "1px dashed #dde0e5",
        },
    )


def gerar_html_titulo_app():
    """
    Caixa de identificação do app na topbar: nome do painel, subtítulo com o
    setor do DMAE e um ícone "Sobre" que abre um popover com a autoria
    completa (UFRGS/projeto de extensão). Substitui a antiga caixa "Base de
    dados" — o nome do arquivo carregado continua visível no rodapé.
    """
    return html.Div(
        [
            html.Div(
                [
                    html.Span(
                        NOME_APLICATIVO,
                        style={
                            "fontSize": "13px",
                            "fontWeight": "600",
                            "color": "#252a31",
                            "lineHeight": "1.3",
                        },
                    ),
                    html.Button(
                        "ⓘ",
                        id=ID_ELEMENTOS_HTML.BOTAO_SOBRE,
                        n_clicks=0,
                        title="Sobre este painel",
                        style={
                            "background": "none",
                            "border": "none",
                            "color": "#8b929c",
                            "fontSize": "13px",
                            "cursor": "pointer",
                            "padding": "0",
                            "lineHeight": "1",
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "6px",
                },
            ),
            html.Span(
                SUBTITULO_APLICATIVO,
                style={
                    "fontSize": "10px",
                    "color": "#8b929c",
                    "lineHeight": "1.3",
                    "display": "block",
                    "overflow": "hidden",
                    "textOverflow": "ellipsis",
                    "whiteSpace": "nowrap",
                },
            ),
            html.Div(
                TEXTO_SOBRE_APLICATIVO,
                id=ID_ELEMENTOS_HTML.PAINEL_SOBRE,
                style=EstilosCSS.ESTILO_SOBRE_FECHADO,
            ),
        ],
        style={
            "position": "relative",
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "center",
            "padding": "0 16px",
            "borderRight": "1px solid #dde0e5",
            "width": "280px",
            "minWidth": "280px",
            "overflow": "visible",
        },
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

    _label = {
        "fontSize": "11px",
        "color": "#5d6570",
        "display": "block",
        "marginBottom": "5px",
    }
    _btn_style = {
        "backgroundColor": "#2f6db0",
        "color": "#ffffff",
        "border": "none",
        "padding": "10px",
        "width": "100%",
        "fontWeight": "500",
        "cursor": "pointer",
        "fontSize": "12.5px",
        "borderRadius": "4px",
        "fontFamily": '"Segoe UI", system-ui, sans-serif',
        "letterSpacing": "0.02em",
    }

    return html.Div(
        [
            html.Span("Arquivo de extração", style=_label),
            dcc.Upload(
                id=ID_ELEMENTOS_HTML.UPLOAD_TABELA,
                children=html.Div(
                    [
                        html.Span(
                            "Escolher arquivo .xlsx",
                            style={
                                "color": "#2f6db0",
                                "fontWeight": "500",
                                "fontSize": "12.5px",
                            },
                        ),
                        html.Br(),
                        html.Span(
                            "arraste o arquivo ou clique",
                            style={"color": "#8b929c", "fontSize": "11px"},
                        ),
                    ],
                    style={"textAlign": "center", "padding": "18px 12px"},
                ),
                style={
                    "border": "1.5px dashed #c6cad1",
                    "borderRadius": "4px",
                    "cursor": "pointer",
                    "marginBottom": "3px",
                },
            ),
            html.Span(
                id=ID_ELEMENTOS_HTML.UPLOAD_NOME_ARQUIVO,
                style={
                    "fontSize": "11px",
                    "color": "#2f6db0",
                    "display": "block",
                    "minHeight": "16px",
                    "marginBottom": "10px",
                },
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Mês de extração", style=_label),
                            dcc.Dropdown(
                                OPCOES_MESES,  # type: ignore
                                id=ID_ELEMENTOS_HTML.MES_EXTRACAO,
                                value=mes_extracao,
                                clearable=False,
                            ),
                        ],
                        style={"flex": "2"},
                    ),
                    html.Div(
                        [
                            html.Label("Ano", style=_label),
                            dcc.Dropdown(
                                list(range(ano_extracao - 20, ano_extracao + 1)),
                                id=ID_ELEMENTOS_HTML.ANO_EXTRACAO,
                                value=ano_extracao,
                                clearable=False,
                            ),
                        ],
                        style={"flex": "1"},
                    ),
                ],
                style={
                    "display": "flex",
                    "gap": "8px",
                    "alignItems": "flex-start",
                    "marginBottom": "12px",
                },
            ),
            html.Button(
                "Processar planilha",
                id=ID_ELEMENTOS_HTML.PROCESSAR_TABELA,
                style=_btn_style,
            ),
            html.Div(
                id=ID_ELEMENTOS_HTML.UPLOAD_TABELA_ERRO,
                children="",
                style={"marginTop": "6px"},
            ),
        ],
        style={"display": "flex", "flexDirection": "column"},
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
                    value=(
                        valores_pre_selecionados.get(coluna_necessaria, None)
                        if valores_pre_selecionados.get(coluna_necessaria)
                        in opcoes_dropdowns
                        else None
                    ),
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
    col_divida_total_vencida = _label_e_dropdown(
        "Dívida Total Vencida (opcional)", "divida_total_vencida"
    )
    col_categoria = _label_e_dropdown("Categoria", "categoria")
    col_tipo_tarifa_esgoto = _label_e_dropdown(
        "Tipo Tarifa Esgoto", "tipo_tarifa_esgoto"
    )
    col_contas_vencidas_aberto = _label_e_dropdown(
        "Contas Vencidas em Aberto (opcional)", "contas_vencidas_aberto"
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
        "Anormalidade de Leitura (opcional)", "anormalidade_leitura_mes_1"
    )
    col_anormalidade_leitura_mes_2 = _label_e_dropdown(
        "Anormalidade de Leitura (opcional)", "anormalidade_leitura_mes_2"
    )
    col_anormalidade_leitura_mes_3 = _label_e_dropdown(
        "Anormalidade de Leitura (opcional)", "anormalidade_leitura_mes_3"
    )
    col_consumo_medido_mes_1 = _label_e_dropdown(
        "Consumo Medido (opcional)", "consumo_medido_mes_1"
    )
    col_consumo_medido_mes_2 = _label_e_dropdown(
        "Consumo Medido (opcional)", "consumo_medido_mes_2"
    )
    col_consumo_medido_mes_3 = _label_e_dropdown(
        "Consumo Medido (opcional)", "consumo_medido_mes_3"
    )

    col_consumo_faturado_mes_1 = _label_e_dropdown(
        "Consumo Faturado (opcional)", "consumo_faturado_mes_1"
    )
    col_consumo_faturado_mes_2 = _label_e_dropdown(
        "Consumo Faturado (opcional)", "consumo_faturado_mes_2"
    )
    col_consumo_faturado_mes_3 = _label_e_dropdown(
        "Consumo Faturado (opcional)", "consumo_faturado_mes_3"
    )

    col_anormalidade_consumo_mes_1 = _label_e_dropdown(
        "Anormalidade de Consumo (opcional)", "anormalidade_consumo_mes_1"
    )
    col_anormalidade_consumo_mes_2 = _label_e_dropdown(
        "Anormalidade de Consumo (opcional)", "anormalidade_consumo_mes_2"
    )
    col_anormalidade_consumo_mes_3 = _label_e_dropdown(
        "Anormalidade de Consumo (opcional)", "anormalidade_consumo_mes_3"
    )

    _label = {
        "fontSize": "11px",
        "color": "#5d6570",
        "display": "block",
        "marginBottom": "5px",
    }
    _fieldset = {
        "border": "1px solid #dde0e5",
        "borderRadius": "4px",
        "padding": "10px 12px 12px",
        "display": "flex",
        "flexDirection": "column",
        "gap": "8px",
    }
    _legend = {
        "fontSize": "10px",
        "fontWeight": "600",
        "letterSpacing": "0.08em",
        "color": "#5d6570",
        "textTransform": "uppercase",
        "padding": "0 4px",
    }
    _btn_style = {
        "backgroundColor": "#2f6db0",
        "color": "#ffffff",
        "border": "none",
        "padding": "10px",
        "width": "100%",
        "fontWeight": "500",
        "cursor": "pointer",
        "fontSize": "12.5px",
        "borderRadius": "4px",
        "fontFamily": '"Segoe UI", system-ui, sans-serif',
        "letterSpacing": "0.02em",
    }

    def _styled_label_dropdown(label_dropdown_div):
        label, dropdown = label_dropdown_div.children
        label.style = _label
        return label_dropdown_div

    return html.Form(
        style={"display": "flex", "flexDirection": "column"},
        children=[
            html.Div(
                "ASSOCIAR COLUNAS",
                style={
                    "fontSize": "10px",
                    "fontWeight": "600",
                    "letterSpacing": "0.12em",
                    "color": "#5d6570",
                    "padding": "14px 16px 12px",
                    "borderTop": "1px solid #dde0e5",
                    "borderBottom": "1px solid #dde0e5",
                },
            ),
            html.Div(
                id=ID_ELEMENTOS_HTML.DROPDOWN_ASSOCIACAO_COLUNAS,
                style={
                    "padding": "14px 16px",
                    "display": "flex",
                    "flexDirection": "column",
                    "gap": "8px",
                },
                children=[
                    _styled_label_dropdown(col_ramal),
                    _styled_label_dropdown(col_hidrometro),
                    _styled_label_dropdown(col_diametro),
                    _styled_label_dropdown(col_data_instalacao),
                    _styled_label_dropdown(col_grupo_leitura),
                    _styled_label_dropdown(col_situacao_ligacao_agua),
                    _styled_label_dropdown(col_perfil_imovel),
                    _styled_label_dropdown(col_categoria),
                    _styled_label_dropdown(col_tipo_tarifa_esgoto),
                    _styled_label_dropdown(col_divida_total_vencida),
                    _styled_label_dropdown(col_contas_vencidas_aberto),
                    html.Fieldset(
                        style=_fieldset,
                        children=[
                            html.Legend(f"Dados de {data_referencia_1}", style=_legend),
                            _styled_label_dropdown(col_consumo_medio_mes_1),
                            _styled_label_dropdown(col_anormalidade_leitura_mes_1),
                            _styled_label_dropdown(col_consumo_medido_mes_1),
                            _styled_label_dropdown(col_consumo_faturado_mes_1),
                            _styled_label_dropdown(col_anormalidade_consumo_mes_1),
                        ],
                    ),
                    html.Fieldset(
                        style=_fieldset,
                        children=[
                            html.Legend(f"Dados de {data_referencia_2}", style=_legend),
                            _styled_label_dropdown(col_consumo_medio_mes_2),
                            _styled_label_dropdown(col_anormalidade_leitura_mes_2),
                            _styled_label_dropdown(col_consumo_medido_mes_2),
                            _styled_label_dropdown(col_consumo_faturado_mes_2),
                            _styled_label_dropdown(col_anormalidade_consumo_mes_2),
                        ],
                    ),
                    html.Fieldset(
                        style=_fieldset,
                        children=[
                            html.Legend(f"Dados de {data_referencia_3}", style=_legend),
                            _styled_label_dropdown(col_consumo_medio_mes_3),
                            _styled_label_dropdown(col_anormalidade_leitura_mes_3),
                            _styled_label_dropdown(col_consumo_medido_mes_3),
                            _styled_label_dropdown(col_consumo_faturado_mes_3),
                            _styled_label_dropdown(col_anormalidade_consumo_mes_3),
                        ],
                    ),
                    html.Button(
                        id=ID_ELEMENTOS_HTML.BOTAO_ASSOCIAR_COLUNAS,
                        type="button",
                        children="Associar colunas",
                        style=_btn_style,
                    ),
                    html.Div(
                        id=ID_ELEMENTOS_HTML.DROPDOWN_ASSOCIACAO_COLUNAS_ERRO,
                        children=erro,
                        style={"fontSize": "11px", "color": "#c0392b"},
                    ),
                ],
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
        "border": "1px solid #dde0e5",
        "padding": "12px 16px",
        "backgroundColor": "#f5f6f8",
    }
    estilo_legend = {
        "fontWeight": "600",
        "fontSize": "11px",
        "color": "#5d6570",
        "textTransform": "uppercase",
        "letterSpacing": "0.1em",
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
                        html.Div(
                            [
                                html.Label("Diâmetro", style=EstilosCSS.LABEL_FILTRO),
                                dcc.Dropdown(
                                    id=ID_ELEMENTOS_HTML.FILTRO_DIAMETRO,
                                    options=opcoes_valores_diametro_filtro,
                                    value=valores_unicos_diametro,
                                    multi=True,
                                    placeholder="Selecione...",
                                ),
                            ],
                            style=EstilosCSS.ITEM_FILTRO,
                        ),
                        html.Div(
                            [
                                html.Label(
                                    "Diâmetro + Letra", style=EstilosCSS.LABEL_FILTRO
                                ),
                                dcc.Dropdown(
                                    id=ID_ELEMENTOS_HTML.FILTRO_DIAMETRO_LETRA,
                                    options=opcoes_valores_diametro_letra,
                                    value=valores_unicos_diametro_letra,
                                    multi=True,
                                    placeholder="Selecione...",
                                ),
                            ],
                            style=EstilosCSS.ITEM_FILTRO,
                        ),
                        html.Div(
                            [
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
                                            for i in range(
                                                valor_minimo_idade,
                                                valor_maximo_idade + 1,
                                            )
                                        },
                                        tooltip={
                                            "placement": "bottom",
                                            "always_visible": True,
                                        },
                                    ),
                                    style={"marginTop": "15px"},
                                ),
                            ],
                            style=EstilosCSS.ITEM_FILTRO | {"gridColumn": "1 / -1"},
                        ),
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
                        html.Div(
                            [
                                html.Label(
                                    "Situação Ligação Água",
                                    style=EstilosCSS.LABEL_FILTRO,
                                ),
                                dcc.Checklist(
                                    id=ID_ELEMENTOS_HTML.FILTRO_SITUACAO,
                                    options=opcoes_valores_situacao_ligacao_agua,
                                    value=opcoes_selecionadas_situacao_ligacao_agua,
                                    inline=True,
                                    labelStyle={
                                        "marginRight": "10px",
                                        "cursor": "pointer",
                                    },
                                ),
                            ],
                            style=EstilosCSS.ITEM_FILTRO | {"gridColumn": "1 / -1"},
                        ),
                        html.Div(
                            [
                                html.Label(
                                    "Grupo de Faturamento",
                                    style=EstilosCSS.LABEL_FILTRO,
                                ),
                                dcc.Dropdown(
                                    id=ID_ELEMENTOS_HTML.FILTRO_GRUPO_FATURAMENTO,
                                    options=opcoes_valores_grupo_faturamento,
                                    value=valores_unicos_grupo_faturamento,
                                    multi=True,
                                    placeholder="Selecione...",
                                ),
                            ],
                            style=EstilosCSS.ITEM_FILTRO,
                        ),
                        html.Div(
                            [
                                html.Label(
                                    "Perfil do Imóvel", style=EstilosCSS.LABEL_FILTRO
                                ),
                                dcc.Dropdown(
                                    id=ID_ELEMENTOS_HTML.FILTRO_PERFIL_IMOVEL,
                                    options=opcoes_valores_perfil_imovel,
                                    value=valores_unicos_perfil_imovel,
                                    multi=True,
                                    placeholder="Selecione...",
                                ),
                            ],
                            style=EstilosCSS.ITEM_FILTRO,
                        ),
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
                        html.Div(
                            [
                                html.Label("Categoria", style=EstilosCSS.LABEL_FILTRO),
                                dcc.Dropdown(
                                    id=ID_ELEMENTOS_HTML.FILTRO_CATEGORIA,
                                    options=opcoes_valores_categoria,
                                    value=valores_unicos_categoria,
                                    multi=True,
                                    placeholder="Selecione...",
                                ),
                            ],
                            style=EstilosCSS.ITEM_FILTRO,
                        ),
                        html.Div(
                            [
                                html.Label(
                                    "Tipo de Tarifa de Esgoto",
                                    style=EstilosCSS.LABEL_FILTRO,
                                ),
                                dcc.Dropdown(
                                    id=ID_ELEMENTOS_HTML.FILTRO_TIPO_TARIFA_ESGOTO,
                                    options=opcoes_valores_tipo_tarifa_esgoto,
                                    value=valores_unicos_tipo_tarifa_esgoto,
                                    multi=True,
                                    placeholder="Selecione...",
                                ),
                            ],
                            style=EstilosCSS.ITEM_FILTRO,
                        ),
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
                        html.Div(
                            [
                                html.Label(
                                    "Anormalidade de Consumo",
                                    style=EstilosCSS.LABEL_FILTRO,
                                ),
                                dcc.Dropdown(
                                    id=ID_ELEMENTOS_HTML.FILTRO_ANORMALIDADE_CONSUMO,
                                    options=opcoes_valores_anormalidade_consumo,
                                    value=valores_unicos_anormalidade_consumo,
                                    multi=True,
                                    placeholder="Selecione...",
                                ),
                            ],
                            style=EstilosCSS.ITEM_FILTRO,
                        ),
                    ],
                ),
            ],
        ),
    ]


def _ramais_para_tabela(
    df_ramais: pd.DataFrame, col_anorm: str, col_consumo: str
) -> list[dict]:
    return df_ramais.rename(
        columns={
            "diametro_letra": "diametro",
            col_anorm: "anormalidade",
            col_consumo: "consumo_medio",
        }
    )[["ramal", "diametro", "anormalidade", "consumo_medio"]].to_dict("records")


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
    freq_perfil_imoveis: list[dict[str, int | float | str]],
    freq_hidrometros: list[dict],
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
    frequencia_consumos_medidos_mes_1: dict[str, int],
    frequencia_consumos_medidos_mes_2: dict[str, int],
    frequencia_consumos_medidos_mes_3: dict[str, int],
    frequencia_consumo_faturado_mes_1: dict[str, int],
    frequencia_consumo_faturado_mes_2: dict[str, int],
    frequencia_consumo_faturado_mes_3: dict[str, int],
    frequencia_anormalidade_consumo_1,
    frequencia_anormalidade_consumo_2,
    frequencia_anormalidade_consumo_3,
    frequencia_contas_vencidas_aberto: dict[str, float],
    ramais_com_consumo_maior_ou_menor_que_o_esperado: tuple[
        pd.DataFrame, pd.DataFrame, pd.DataFrame
    ],
    frequencia_divida_total_vencida: pd.Series | None,
):
    if idade_media_hidrometros is not np.nan:
        idade_media_hidrometros = f"{idade_media_hidrometros:.2f}"
    else:
        idade_media_hidrometros = "-"

    if porcentagem_hidrometros_ligados == 0.0:
        porcentagem_hidrometros_ligados = "-"
    else:
        porcentagem_hidrometros_ligados = f"{porcentagem_hidrometros_ligados:.2f}"

    _vals_anorm_leitura = sorted(
        pd.concat(
            [
                df["anormalidade_leitura_mes_1"],
                df["anormalidade_leitura_mes_2"],
                df["anormalidade_leitura_mes_3"],
            ]
        )
        .dropna()
        .unique()
        .tolist()
    )
    _opcoes_anorm_leitura = [{"label": v, "value": v} for v in _vals_anorm_leitura]

    _ESTILO_CARD_SECAO = {
        "display": "flex",
        "flexDirection": "column",
        "gap": "0",
        "gridColumnStart": "span 6",
        "backgroundColor": "#ffffff",
        "border": "1px solid #dde0e5",
        "padding": "20px",
    }

    return html.Div(
        [
            html.Div(
                id=ID_ELEMENTOS_HTML.SECAO_DESCRITIVA,
                children=[
                    html.Div(
                        [
                            html.Div(
                                "Diagnóstico dos hidrômetros",
                                style={
                                    "fontSize": "11px",
                                    "letterSpacing": ".13em",
                                    "textTransform": "uppercase",
                                    "color": "#8b929c",
                                    "marginBottom": "5px",
                                },
                            ),
                            html.H3(
                                "Análise Descritiva",
                                style={
                                    "color": "#252a31",
                                    "fontSize": "19px",
                                    "fontWeight": "600",
                                    "letterSpacing": "-.01em",
                                    "margin": "0",
                                },
                            ),
                            html.P(
                                "Caracterização dos hidrômetros instalados por idade, perfil de imóvel e diâmetro. Dívida total vencida e contas vencidas em aberto.",
                                style={
                                    "color": "#5d6570",
                                    "fontSize": "12px",
                                    "margin": "5px 0 0 0",
                                },
                            ),
                        ],
                        style={
                            "marginBottom": "20px",
                            "paddingBottom": "16px",
                            "borderBottom": "1px solid #dde0e5",
                        },
                    ),
                    html.Div(
                        [
                            # KPI strip — 3 colunas horizontais
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                "Total de hidrômetros",
                                                style=EstilosCSS.QUADRO_DADO_LABEL,
                                            ),
                                            html.Div(
                                                contagem_hidrometros,
                                                id=ID_ELEMENTOS_HTML.CONTAGEM_HIDROMETROS,
                                                style=EstilosCSS.QUADRO_DADO_NUMERO,
                                            ),
                                        ],
                                        style={
                                            "padding": "14px 16px",
                                            "borderRight": "1px solid #dde0e5",
                                        },
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                "Hidrômetros ligados",
                                                style=EstilosCSS.QUADRO_DADO_LABEL,
                                            ),
                                            html.Div(
                                                [
                                                    html.Span(
                                                        porcentagem_hidrometros_ligados,
                                                        id=ID_ELEMENTOS_HTML.PORCENTAGEM_HIDROMETOS_LIGADOS,
                                                        style=EstilosCSS.QUADRO_DADO_NUMERO,
                                                    ),
                                                    html.Span(
                                                        "%",
                                                        style={
                                                            "fontSize": "15px",
                                                            "color": "#5d6570",
                                                            "marginLeft": "4px",
                                                            "fontWeight": "400",
                                                        },
                                                    ),
                                                ],
                                                style={
                                                    "display": "flex",
                                                    "alignItems": "baseline",
                                                    "gap": "0",
                                                },
                                            ),
                                        ],
                                        style={
                                            "padding": "14px 16px",
                                            "borderRight": "1px solid #dde0e5",
                                        },
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                "Idade média dos hidrômetros",
                                                style=EstilosCSS.QUADRO_DADO_LABEL,
                                            ),
                                            html.Div(
                                                [
                                                    html.Span(
                                                        idade_media_hidrometros,
                                                        id=ID_ELEMENTOS_HTML.IDADE_MEDIA_HIDROMETROS,
                                                        style=EstilosCSS.QUADRO_DADO_NUMERO,
                                                    ),
                                                    html.Span(
                                                        "anos",
                                                        style={
                                                            "fontSize": "15px",
                                                            "color": "#5d6570",
                                                            "marginLeft": "4px",
                                                            "fontWeight": "400",
                                                        },
                                                    ),
                                                ],
                                                style={
                                                    "display": "flex",
                                                    "alignItems": "baseline",
                                                },
                                            ),
                                        ],
                                        style={"padding": "14px 16px"},
                                    ),
                                ],
                                style={
                                    "display": "grid",
                                    "gridTemplateColumns": "repeat(3, 1fr)",
                                    "border": "1px solid #dde0e5",
                                    "backgroundColor": "#ffffff",
                                    "gridColumnStart": "span 6",
                                    "marginBottom": "16px",
                                },
                            ),
                            html.Div(
                                [
                                    dcc.Graph(
                                        style={"height": "420px"},
                                        figure=px.bar(
                                            x=df["idade_hidrometro"]
                                            .value_counts()
                                            .sort_index()
                                            .index,
                                            y=df["idade_hidrometro"]
                                            .value_counts()
                                            .sort_index(),
                                            labels={
                                                "x": "Idade do Hidrômetro (anos)",
                                                "y": "Frequência",
                                            },
                                            color_discrete_sequence=_PLOTLY_CORES_BARRAS,
                                        ).update_layout(
                                            **{
                                                **_PLOTLY_DARK_LAYOUT,
                                                "title": "Frequência de idade dos hidrômetros",
                                                "xaxis": {
                                                    **_PLOTLY_DARK_LAYOUT["xaxis"],
                                                    "tickmode": "linear",
                                                    "tick0": 0,
                                                    "dtick": 5,
                                                    "title": "Idade do Hidrômetro (anos)",
                                                },
                                                "yaxis": {
                                                    **_PLOTLY_DARK_LAYOUT["yaxis"],
                                                    "title": "Frequência",
                                                },
                                                "bargap": 0.05,
                                                "height": 420,
                                                "margin": _MARGEM_GRAFICOS_LADO_A_LADO,
                                            }
                                        )
                                    )
                                ],
                                style={"gridColumnStart": "span 3"},
                            ),
                            html.Div(
                                [
                                    dcc.Graph(
                                        style={"height": "420px"},
                                        figure=px.bar(
                                            x=df["grupo_leitura"]
                                            .value_counts()
                                            .rename(
                                                index=lambda v: str(v)
                                                .upper()
                                                .replace("GRUPO-", "")
                                            )
                                            .sort_index(key=lambda x: x.astype(int))
                                            .index,
                                            y=df["grupo_leitura"]
                                            .value_counts()
                                            .rename(
                                                index=lambda v: str(v)
                                                .upper()
                                                .replace("GRUPO-", "")
                                            )
                                            .sort_index(key=lambda x: x.astype(int)),
                                            labels={
                                                "y": "Frequência",
                                                "x": "Grupo de Faturamento",
                                            },
                                            title="Frequência do grupo de faturamento",
                                            color_discrete_sequence=_PLOTLY_CORES_BARRAS,
                                        ).update_layout(
                                            **_PLOTLY_DARK_LAYOUT,
                                            height=420,
                                            margin=_MARGEM_GRAFICOS_LADO_A_LADO,
                                        )
                                    )
                                ],
                                style={"gridColumnStart": "span 3"},
                            ),
                            _caixa_tabela(
                                "Tabela de Frequência de Perfil de Imóvel",
                                id_pagina=ID_ELEMENTOS_HTML.PAGINA_PERFIL_IMOVEL,
                                id_pesquisa=ID_ELEMENTOS_HTML.PESQUISA_PERFIL_IMOVEL,
                                id_tabela=ID_ELEMENTOS_HTML.TABELA_PERFIL_IMOVEL,
                                data=freq_perfil_imoveis,
                                columns=(
                                    [
                                        {"name": k, "id": k}
                                        for k in freq_perfil_imoveis[0].keys()
                                    ]
                                    if freq_perfil_imoveis
                                    else []
                                ),
                                page_size_default=5,
                            ),
                            _caixa_tabela(
                                "Tabela de Frequência de Diâmetro em Hidrômetros",
                                id_pagina=ID_ELEMENTOS_HTML.PAGINA_DIAMETRO,
                                id_pesquisa=ID_ELEMENTOS_HTML.PESQUISA_DIAMETRO,
                                id_tabela=ID_ELEMENTOS_HTML.TABELA_DIAMETRO,
                                data=freq_hidrometros,
                                columns=(
                                    [
                                        {"name": k, "id": k}
                                        for k in freq_hidrometros[0].keys()
                                    ]
                                    if freq_hidrometros
                                    else []
                                ),
                                page_size_default=5,
                            ),
                            # Stats grid — idade por faixa de diâmetro
                            html.Div(
                                [
                                    html.Div(
                                        "Idade por faixa de diâmetro — média / desvio padrão",
                                        style={
                                            "gridColumn": "1 / -1",
                                            "fontSize": "11px",
                                            "letterSpacing": ".1em",
                                            "textTransform": "uppercase",
                                            "color": "#8b929c",
                                            "padding": "11px 15px 9px",
                                            "borderBottom": "1px solid #dde0e5",
                                        },
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Span(
                                                        idade_media_20MM,
                                                        id=ID_ELEMENTOS_HTML.IDADE_MEDIA_HIDROMETROS_20MM,
                                                        style={
                                                            "fontSize": "22px",
                                                            "fontWeight": "500",
                                                            "fontVariantNumeric": "tabular-nums",
                                                        },
                                                    ),
                                                    html.Span(
                                                        "anos",
                                                        style={
                                                            "fontSize": "12px",
                                                            "color": "#5d6570",
                                                            "marginLeft": "4px",
                                                        },
                                                    ),
                                                ],
                                                style={
                                                    "display": "flex",
                                                    "alignItems": "baseline",
                                                },
                                            ),
                                            html.Div(
                                                "Idade média · 20 mm",
                                                style={
                                                    "fontSize": "11.5px",
                                                    "color": "#5d6570",
                                                    "marginTop": "6px",
                                                },
                                            ),
                                        ],
                                        style={
                                            "padding": "14px 15px",
                                            "borderRight": "1px solid #dde0e5",
                                            "borderBottom": "1px solid #dde0e5",
                                        },
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Span(
                                                        idade_media_25MM,
                                                        id=ID_ELEMENTOS_HTML.IDADE_MEDIA_HIDROMETROS_25MM,
                                                        style={
                                                            "fontSize": "22px",
                                                            "fontWeight": "500",
                                                            "fontVariantNumeric": "tabular-nums",
                                                        },
                                                    ),
                                                    html.Span(
                                                        "anos",
                                                        style={
                                                            "fontSize": "12px",
                                                            "color": "#5d6570",
                                                            "marginLeft": "4px",
                                                        },
                                                    ),
                                                ],
                                                style={
                                                    "display": "flex",
                                                    "alignItems": "baseline",
                                                },
                                            ),
                                            html.Div(
                                                "Idade média · 25 mm",
                                                style={
                                                    "fontSize": "11.5px",
                                                    "color": "#5d6570",
                                                    "marginTop": "6px",
                                                },
                                            ),
                                        ],
                                        style={
                                            "padding": "14px 15px",
                                            "borderRight": "1px solid #dde0e5",
                                            "borderBottom": "1px solid #dde0e5",
                                        },
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Span(
                                                        idade_media_acima_25MM,
                                                        id=ID_ELEMENTOS_HTML.IDADE_MEDIA_HIDROMETROS_ACIMA_25MM,
                                                        style={
                                                            "fontSize": "22px",
                                                            "fontWeight": "500",
                                                            "fontVariantNumeric": "tabular-nums",
                                                        },
                                                    ),
                                                    html.Span(
                                                        "anos",
                                                        style={
                                                            "fontSize": "12px",
                                                            "color": "#5d6570",
                                                            "marginLeft": "4px",
                                                        },
                                                    ),
                                                ],
                                                style={
                                                    "display": "flex",
                                                    "alignItems": "baseline",
                                                },
                                            ),
                                            html.Div(
                                                "Idade média · acima de 25 mm",
                                                style={
                                                    "fontSize": "11.5px",
                                                    "color": "#5d6570",
                                                    "marginTop": "6px",
                                                },
                                            ),
                                        ],
                                        style={
                                            "padding": "14px 15px",
                                            "borderBottom": "1px solid #dde0e5",
                                        },
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Span(
                                                        idade_desvio_padrao_20MM,
                                                        id=ID_ELEMENTOS_HTML.IDADE_DESVIO_PADRAO_20MM,
                                                        style={
                                                            "fontSize": "22px",
                                                            "fontWeight": "500",
                                                            "fontVariantNumeric": "tabular-nums",
                                                        },
                                                    ),
                                                    html.Span(
                                                        "anos",
                                                        style={
                                                            "fontSize": "12px",
                                                            "color": "#5d6570",
                                                            "marginLeft": "4px",
                                                        },
                                                    ),
                                                ],
                                                style={
                                                    "display": "flex",
                                                    "alignItems": "baseline",
                                                },
                                            ),
                                            html.Div(
                                                "Desvio padrão · 20 mm",
                                                style={
                                                    "fontSize": "11.5px",
                                                    "color": "#5d6570",
                                                    "marginTop": "6px",
                                                },
                                            ),
                                        ],
                                        style={
                                            "padding": "14px 15px",
                                            "borderRight": "1px solid #dde0e5",
                                        },
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Span(
                                                        idade_desvio_padrao_25MM,
                                                        id=ID_ELEMENTOS_HTML.IDADE_DESVIO_PADRAO_25MM,
                                                        style={
                                                            "fontSize": "22px",
                                                            "fontWeight": "500",
                                                            "fontVariantNumeric": "tabular-nums",
                                                        },
                                                    ),
                                                    html.Span(
                                                        "anos",
                                                        style={
                                                            "fontSize": "12px",
                                                            "color": "#5d6570",
                                                            "marginLeft": "4px",
                                                        },
                                                    ),
                                                ],
                                                style={
                                                    "display": "flex",
                                                    "alignItems": "baseline",
                                                },
                                            ),
                                            html.Div(
                                                "Desvio padrão · 25 mm",
                                                style={
                                                    "fontSize": "11.5px",
                                                    "color": "#5d6570",
                                                    "marginTop": "6px",
                                                },
                                            ),
                                        ],
                                        style={
                                            "padding": "14px 15px",
                                            "borderRight": "1px solid #dde0e5",
                                        },
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Span(
                                                        idade_desvio_padrao_acima_25MM,
                                                        id=ID_ELEMENTOS_HTML.IDADE_DESVIO_PADRAO_ACIMA_25MM,
                                                        style={
                                                            "fontSize": "22px",
                                                            "fontWeight": "500",
                                                            "fontVariantNumeric": "tabular-nums",
                                                        },
                                                    ),
                                                    html.Span(
                                                        "anos",
                                                        style={
                                                            "fontSize": "12px",
                                                            "color": "#5d6570",
                                                            "marginLeft": "4px",
                                                        },
                                                    ),
                                                ],
                                                style={
                                                    "display": "flex",
                                                    "alignItems": "baseline",
                                                },
                                            ),
                                            html.Div(
                                                "Desvio padrão · acima de 25 mm",
                                                style={
                                                    "fontSize": "11.5px",
                                                    "color": "#5d6570",
                                                    "marginTop": "6px",
                                                },
                                            ),
                                        ],
                                        style={"padding": "14px 15px"},
                                    ),
                                ],
                                style={
                                    "display": "grid",
                                    "gridTemplateColumns": "repeat(3, 1fr)",
                                    "border": "1px solid #dde0e5",
                                    "backgroundColor": "#ffffff",
                                    "gridColumnStart": "span 6",
                                },
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
                                [
                                    html.Button(
                                        "⬇ Download Tabela Filtrada",
                                        id=ID_ELEMENTOS_HTML.BOTAO_DOWNLOAD_TABELA_COMPLETA_FILTRADA,
                                        style={
                                            "backgroundColor": "#2f6db0",
                                            "color": "white",
                                            "border": "1px solid #2f6db0",
                                            "padding": "7px 15px",
                                            "fontWeight": "500",
                                            "cursor": "pointer",
                                            "fontSize": "12.5px",
                                            "display": "flex",
                                            "alignItems": "center",
                                            "gap": "7px",
                                        },
                                    ),
                                    dcc.Download(
                                        ID_ELEMENTOS_HTML.DOWNLOADER_TABELA_COMPLETA_FILTRADA
                                    ),
                                ],
                                style={
                                    "display": "flex",
                                    "gap": "10px",
                                    "gridColumnStart": "span 6",
                                },
                            ),
                        ],
                        style=EstilosCSS.GRID_AREA_DADOS_CONSUMO,
                    ),
                ],
                style=_ESTILO_CARD_SECAO,
            ),
            html.Div(
                id=ID_ELEMENTOS_HTML.SECAO_CONSUMO_CARD,
                children=[
                    # Cabeçalho da seção
                    html.Div(
                        [
                            html.Div(
                                "Comportamento de consumo",
                                style={
                                    "fontSize": "11px",
                                    "letterSpacing": ".13em",
                                    "textTransform": "uppercase",
                                    "color": "#8b929c",
                                    "marginBottom": "5px",
                                },
                            ),
                            html.H3(
                                "Análise de Consumo",
                                style={
                                    "color": "#252a31",
                                    "fontSize": "19px",
                                    "fontWeight": "600",
                                    "letterSpacing": "-.01em",
                                    "margin": "0",
                                },
                            ),
                            html.P(
                                "Estatísticas de consumo por mês de referência.",
                                style={
                                    "color": "#5d6570",
                                    "fontSize": "12px",
                                    "margin": "5px 0 0 0",
                                },
                            ),
                        ],
                        style={
                            "marginBottom": "20px",
                            "paddingBottom": "16px",
                            "borderBottom": "1px solid #dde0e5",
                        },
                    ),
                    # Painel de controles locais
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Label(
                                        "Mês de Referência",
                                        style=EstilosCSS.LABEL_FILTRO,
                                    ),
                                    dcc.RadioItems(
                                        {
                                            "1": f"{datas_referencias[0]}",
                                            "2": f"{datas_referencias[1]}",
                                            "3": f"{datas_referencias[2]}",
                                        },
                                        value="1",
                                        inline=True,
                                        id=ID_ELEMENTOS_HTML.ESCOLHA_ABA_DADOS_CONSUMO,
                                        labelStyle={
                                            "marginRight": "10px",
                                            "cursor": "pointer",
                                            "color": "#252a31",
                                        },
                                    ),
                                ],
                                style=EstilosCSS.ITEM_FILTRO,
                            ),
                            html.Div(
                                [
                                    html.Label(
                                        "Concatenar consumo a partir de:",
                                        style=EstilosCSS.LABEL_FILTRO,
                                    ),
                                    html.Div(
                                        [
                                            dcc.Input(
                                                130,
                                                "number",
                                                id=ID_ELEMENTOS_HTML.VALOR_LIMITE_CONCATENAR,
                                                style={
                                                    "backgroundColor": "#f7f8fa",
                                                    "color": "#252a31",
                                                    "border": "1px solid #dde0e5",
                                                    "padding": "6px 10px",
                                                    "width": "90px",
                                                },
                                            ),
                                            html.Button(
                                                "Concatenar",
                                                id=ID_ELEMENTOS_HTML.BOTAO_CONCATENAR_CONSUMO,
                                                style={
                                                    "backgroundColor": "#2f6db0",
                                                    "color": "white",
                                                    "border": "none",
                                                    "padding": "6px 14px",
                                                    "fontWeight": "500",
                                                    "cursor": "pointer",
                                                    "fontFamily": '"Segoe UI", system-ui, sans-serif',
                                                },
                                            ),
                                        ],
                                        style={"display": "flex", "gap": "8px"},
                                    ),
                                ],
                                style=EstilosCSS.ITEM_FILTRO,
                            ),
                            html.Div(
                                [
                                    html.Label(
                                        "Anormalidade de Leitura (filtro local)",
                                        style=EstilosCSS.LABEL_FILTRO,
                                    ),
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
                            "backgroundColor": "#f5f6f8",
                            "border": "1px solid #dde0e5",
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
                                frequencia_divida_total_vencida=frequencia_divida_total_vencida,
                                frequencia_contas_vencidas_aberto=frequencia_contas_vencidas_aberto,
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
                                frequencia_divida_total_vencida=frequencia_divida_total_vencida,
                                frequencia_contas_vencidas_aberto=frequencia_contas_vencidas_aberto,
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
                                frequencia_divida_total_vencida=frequencia_divida_total_vencida,
                                frequencia_contas_vencidas_aberto=frequencia_contas_vencidas_aberto,
                            ),
                        ],
                    ),
                ],
                style={
                    "display": "none",
                    "flexDirection": "column",
                    "gap": "0",
                    "gridColumnStart": "span 6",
                    "backgroundColor": "#ffffff",
                    "border": "1px solid #dde0e5",
                    "padding": "20px",
                },
            ),
        ],
        id=ID_ELEMENTOS_HTML.AREA_DADOS,
    )


def _caixa_tabela(
    titulo,
    id_pagina,
    id_pesquisa,
    id_tabela,
    data,
    columns,
    children_extra=None,
    page_size_default=10,
):
    _ESTILO_BOX = {
        "gridColumnStart": "span 6",
        "backgroundColor": "#ffffff",
        "border": "1px solid #dde0e5",
        "padding": "0",
    }
    conteudo = [
        html.Div(
            titulo,
            style={
                "fontWeight": "600",
                "fontSize": "13px",
                "color": "#252a31",
                "padding": "12px 15px 11px",
                "borderBottom": "1px solid #dde0e5",
            },
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Label(
                            "Mostrar", style={"color": "#5d6570", "fontSize": "11.5px"}
                        ),
                        dcc.Dropdown(
                            options=[
                                {"label": str(n), "value": n}
                                for n in [5, 10, 25, 50, 100]
                            ],
                            value=page_size_default,
                            id=id_pagina,
                            clearable=False,
                            style={"width": "80px", "display": "inline-block"},
                        ),
                        html.Label(
                            "entradas", style={"color": "#5d6570", "fontSize": "11.5px"}
                        ),
                    ],
                    style={"display": "flex", "gap": "8px", "alignItems": "center"},
                ),
                html.Div(
                    [
                        html.Label(
                            "Buscar:", style={"color": "#5d6570", "fontSize": "11.5px"}
                        ),
                        dcc.Input(
                            id=id_pesquisa,
                            type="text",
                            debounce=True,
                            placeholder="Filtrar...",
                            style={
                                "backgroundColor": "#f7f8fa",
                                "color": "#252a31",
                                "border": "1px solid #dde0e5",
                                "padding": "4px 10px",
                                "fontSize": "11.5px",
                            },
                        ),
                    ],
                    style={"display": "flex", "gap": "8px", "alignItems": "center"},
                ),
            ],
            style={
                "display": "flex",
                "justifyContent": "space-between",
                "alignItems": "center",
                "padding": "10px 15px",
                "borderBottom": "1px solid #dde0e5",
            },
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
    frequencia_consumos_medios: dict,
    frequencia_consumos_medidos: dict | None,
    frequencia_consumo_faturado: dict | None,
    anormalidade_de_leitura: pd.DataFrame | None,
    frequencia_anormalidade_consumo: pd.DataFrame | None,
    ramais_df: pd.DataFrame,
    col_anorm_ramais: str,
    col_consumo_ramais: str,
    titulo: str,
    id_html_elemento: str,
    mes_index: str,
    frequencia_divida_total_vencida: pd.Series | None,
    frequencia_contas_vencidas_aberto: dict | None,
    limite_consumo_utilizado: int = 130,
    oculto: bool = False,
):
    estilo = EstilosCSS.GRID_AREA_DADOS_CONSUMO
    if oculto:
        estilo = {"display": "none"}

    _COLS_ANORM = (
        [{"name": c, "id": c} for c in anormalidade_de_leitura.columns]
        if anormalidade_de_leitura is not None
        else []
    )
    _COLS_CONSUMO = (
        [{"name": c, "id": c} for c in frequencia_anormalidade_consumo.columns]
        if frequencia_anormalidade_consumo is not None
        else []
    )
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
                    style={
                        "backgroundColor": "#ffffff",
                        "color": "#252a31",
                        "border": "1px solid #dde0e5",
                        "padding": "7px 15px",
                        "fontWeight": "400",
                        "cursor": "pointer",
                        "fontSize": "12.5px",
                        "display": "flex",
                        "alignItems": "center",
                        "gap": "7px",
                    },
                ),
                html.Button(
                    "⬇ Download com filtros",
                    id={"type": "btn-dl-com", "index": mes_index},
                    style={
                        "backgroundColor": "#2f6db0",
                        "color": "white",
                        "border": "1px solid #2f6db0",
                        "padding": "7px 15px",
                        "fontWeight": "500",
                        "cursor": "pointer",
                        "fontSize": "12.5px",
                        "display": "flex",
                        "alignItems": "center",
                        "gap": "7px",
                    },
                ),
                dcc.Download(id={"type": "download-mes", "index": mes_index}),
            ],
            style={
                "display": "flex",
                "gap": "10px",
                "padding": "12px 15px",
                "borderTop": "1px solid #dde0e5",
            },
        ),
    ]

    return html.Div(
        id=id_html_elemento,
        children=[
            html.H4(
                titulo,
                style={
                    "gridColumnStart": "1",
                    "gridColumnEnd": "-1",
                    "color": "#252a31",
                    "fontSize": "14px",
                    "fontWeight": "600",
                },
            ),
            # KPI strip consumo
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                "Consumo Médio", style=EstilosCSS.QUADRO_DADO_LABEL
                            ),
                            html.Div(
                                [
                                    html.Span(
                                        f"{media_consumo_medio:.2f}",
                                        style=EstilosCSS.QUADRO_DADO_NUMERO,
                                    ),
                                    html.Span(
                                        "m³",
                                        style={
                                            "fontSize": "15px",
                                            "color": "#5d6570",
                                            "marginLeft": "4px",
                                            "fontWeight": "400",
                                        },
                                    ),
                                ],
                                style={"display": "flex", "alignItems": "baseline"},
                            ),
                        ],
                        style={
                            "padding": "14px 16px",
                            "borderRight": "1px solid #dde0e5",
                        },
                    ),
                    html.Div(
                        [
                            html.Div(
                                "Desvio Padrão do Consumo Médio",
                                style=EstilosCSS.QUADRO_DADO_LABEL,
                            ),
                            html.Div(
                                [
                                    html.Span(
                                        f"{desvio_padrao:.2f}",
                                        style=EstilosCSS.QUADRO_DADO_NUMERO,
                                    ),
                                    html.Span(
                                        "m³",
                                        style={
                                            "fontSize": "15px",
                                            "color": "#5d6570",
                                            "marginLeft": "4px",
                                            "fontWeight": "400",
                                        },
                                    ),
                                ],
                                style={"display": "flex", "alignItems": "baseline"},
                            ),
                        ],
                        style={
                            "padding": "14px 16px",
                            "borderRight": "1px solid #dde0e5",
                        },
                    ),
                    html.Div(
                        [
                            html.Div(
                                f"Consumo maior que {limite_consumo_utilizado} m³",
                                style=EstilosCSS.QUADRO_DADO_LABEL,
                            ),
                            html.Div(
                                [
                                    html.Span(
                                        frequencia_consumo_acima_limite,
                                        style=EstilosCSS.QUADRO_DADO_NUMERO,
                                    ),
                                    html.Span(
                                        "ramais",
                                        style={
                                            "fontSize": "15px",
                                            "color": "#5d6570",
                                            "marginLeft": "4px",
                                            "fontWeight": "400",
                                        },
                                    ),
                                ],
                                style={"display": "flex", "alignItems": "baseline"},
                            ),
                        ],
                        style={"padding": "14px 16px"},
                    ),
                ],
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(3, 1fr)",
                    "border": "1px solid #dde0e5",
                    "backgroundColor": "#ffffff",
                    "gridColumnStart": "span 6",
                },
            ),
            # Gráfico de Consumo Médio
            html.Div(
                [
                    dcc.Graph(
                        figure=px.bar(
                            x=[x for x in frequencia_consumos_medios.keys()],
                            y=frequencia_consumos_medios.values(),
                            labels={"y": "Frequência", "x": "Consumo Médio"},
                            title="Gráfico de Consumo Médio",
                            color_discrete_sequence=_PLOTLY_CORES_BARRAS,
                        ).update_layout(**_PLOTLY_DARK_LAYOUT)
                    )
                ],
                style=EstilosCSS.GRAFICO,
            ),
            # Box: Anorm Leitura
            (
                _caixa_tabela(
                    "Tabela de Frequência de Anormalidade de Leitura",
                    id_pagina={"type": "pagina-anorm-leitura", "index": mes_index},
                    id_pesquisa={"type": "pesquisa-anorm-leitura", "index": mes_index},
                    id_tabela={"type": "tabela-anorm-leitura", "index": mes_index},
                    data=anormalidade_de_leitura.to_dict("records"),
                    columns=_COLS_ANORM,
                )
                if anormalidade_de_leitura is not None
                else html.Div(
                    componente_aviso_coluna_nao_associada("Anormalidade de Leitura"),
                    style=EstilosCSS.TABELA,
                )
            ),
            # Box: Anorm Consumo
            (
                _caixa_tabela(
                    "Tabela de Frequência de Anormalidade de Consumo",
                    id_pagina={"type": "pagina-anorm-consumo", "index": mes_index},
                    id_pesquisa={"type": "pesquisa-anorm-consumo", "index": mes_index},
                    id_tabela={"type": "tabela-anorm-consumo", "index": mes_index},
                    data=frequencia_anormalidade_consumo.to_dict("records"),
                    columns=_COLS_CONSUMO,
                )
                if frequencia_anormalidade_consumo is not None
                else html.Div(
                    componente_aviso_coluna_nao_associada("Anormalidade de Consumo"),
                    style=EstilosCSS.TABELA,
                )
            ),
            # Gráficos lado a lado: Consumo Medido e Consumo Faturado
            html.Div(
                (
                    dcc.Graph(
                        figure=px.bar(
                            x=[x for x in frequencia_consumos_medidos.keys()],
                            y=frequencia_consumos_medidos.values(),
                            labels={"y": "Frequência", "x": "Consumo Medido"},
                            title="Gráfico de Consumo Medido",
                            color_discrete_sequence=_PLOTLY_CORES_BARRAS,
                        ).update_layout(**_PLOTLY_DARK_LAYOUT)
                    )
                    if frequencia_consumos_medidos is not None
                    else componente_aviso_coluna_nao_associada("Consumo Medido")
                ),
                style={"gridColumnStart": "span 3"},
            ),
            html.Div(
                (
                    dcc.Graph(
                        figure=px.bar(
                            x=[x for x in frequencia_consumo_faturado.keys()],
                            y=frequencia_consumo_faturado.values(),
                            labels={"y": "Frequência", "x": "Consumo Faturado"},
                            title="Gráfico de Consumo Faturado",
                            color_discrete_sequence=_PLOTLY_CORES_BARRAS,
                        ).update_layout(**_PLOTLY_DARK_LAYOUT)
                    )
                    if frequencia_consumo_faturado is not None
                    else componente_aviso_coluna_nao_associada("Consumo Faturado")
                ),
                style={"gridColumnStart": "span 3"},
            ),
            # Box: Ramais com consumo fora do esperado + downloads
            _caixa_tabela(
                "Tabela de Ramais com Consumo Menor ou Maior do que o Esperado",
                id_pagina={"type": "pagina-ramais-mes", "index": mes_index},
                id_pesquisa={"type": "pesquisa-ramais-mes", "index": mes_index},
                id_tabela={"type": "tabela-ramais-mes", "index": mes_index},
                data=_ramais_para_tabela(
                    ramais_df, col_anorm_ramais, col_consumo_ramais
                ),
                columns=_COLS_RAMAIS,
                children_extra=_botoes_download,
            ),
            html.Div(
                (
                    dcc.Graph(
                        figure=px.histogram(
                            x=frequencia_divida_total_vencida,
                            title="Frequência de Divida Total Vencida",
                            labels={"x": "Valor da Conta Vencida"},
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
                            yaxis_title="Frequência",
                            xaxis={
                                # sem dtick/tickmode fixos: dívida (R$) tem
                                # amplitude bem maior e variável que consumo
                                # (m³), então os bins e os rótulos do eixo X
                                # se ajustam automaticamente à escala dos dados
                                "gridcolor": "#dde0e5",
                                "linecolor": "#c6cad1",
                            },
                            yaxis={
                                "gridcolor": "#dde0e5",
                                "linecolor": "#c6cad1",
                            },
                        )
                    )
                    if frequencia_divida_total_vencida is not None
                    else componente_aviso_coluna_nao_associada("Dívida Total Vencida")
                ),
                style=EstilosCSS.GRAFICO,
            ),
            html.Div(
                (
                    dcc.Graph(
                        figure=px.bar(
                            title="Frequência de Contas Vencidas em Aberto",
                            x=frequencia_contas_vencidas_aberto.keys(),
                            y=frequencia_contas_vencidas_aberto.values(),
                            labels={
                                "x": "Qtd. Contas Vencidas",
                                "y": "Frequência",
                            },
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
                                "dtick": 10,
                                "tickmode": "linear",
                            },
                            yaxis={
                                "gridcolor": "#dde0e5",
                                "linecolor": "#c6cad1",
                            },
                        )
                    )
                    if frequencia_contas_vencidas_aberto is not None
                    else componente_aviso_coluna_nao_associada(
                        "Contas Vencidas em Aberto"
                    )
                ),
                style=EstilosCSS.GRAFICO,
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
    return html.Div(
        [
            html.Div("0 Resultados", id=ID_ELEMENTOS_HTML.SECAO_DESCRITIVA),
            html.Div(
                "0 Resultados",
                id=ID_ELEMENTOS_HTML.SECAO_CONSUMO_CARD,
                style={"display": "none"},
            ),
        ],
    )
