import base64
import io
import sys

import pandas as pd
from dash import Dash, html, dcc, callback, Output, Input, State, ctx, MATCH, no_update

from tipos import NOME_VARIAVEIS, VARIAVEIS_OPCIONAIS
from elementos_html import (
    componente_painel_erros,
    gerar_form_colunas,
    gerar_form_importar_planilha,
    gerar_html_dados,
    gerar_html_dados_consumo_mes,
    gerar_html_filtros,
    gerar_html_titulo_app,
    gerar_html_zero_resultados,
    _ramais_para_tabela,
    ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS,
    ID_ELEMENTOS_HTML,
    EstilosCSS,
)
import calculos

# -------------------------------------------------------------
#########################
### INICIALIZAÇÃO APP ###
#########################
DF = pd.DataFrame()
filtro_html = []
dados_html = []
mes_extracao = None
ano_extracao = None
# Bytes crus da planilha enviada e nomes de colunas disponíveis nela. Guardados
# à parte do DF para adiar a leitura completa (todas as colunas) até o
# usuário associar as colunas necessárias — só nesse momento o arquivo é lido
# de fato, e só com as colunas usadas (usecols), reduzindo a memória do DF
# mantido pelo resto da sessão.
_ARQUIVO_BYTES: bytes | None = None
_COLUNAS_ARQUIVO: list[str] = []
ASSOCIACAO_COLUNAS_VARIAVEIS_PREVIA: dict[NOME_VARIAVEIS, str] | None = None
if len(sys.argv) > 1:

    ASSOCIACAO_COLUNAS_VARIAVEIS_PREVIA = {
        "ramal": "Matricula",
        "diametro": "Diametro",
        "data_instalacao": "Data Instalacao",
        "hidrometro": "Hidrometro",
        "grupo_leitura": "Grupo Leitura",
        "perfil_imovel": "Perfil Imovel",
        "situacao_ligacao_agua": "Situacao Ligacao Agua",
        "tipo_tarifa_esgoto": "tipo Tarifa Esgoto",
        "categoria": "Categoria",
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
        "anormalidade_consumo_mes_1": "Anormalidade Consumo 1",
        "anormalidade_consumo_mes_2": "Anormalidade Consumo 2",
        "anormalidade_consumo_mes_3": "Anormalidade Consumo 3",
        "contas_vencidas_aberto": "Qtd Contas Vencidas em Aberto",
        "divida_total_vencida": "Divida Total Vencida",
    }

    if sys.argv[1] == "-p":
        DF = pd.read_excel("testes/dados_teste/amostra_dados.xlsx", engine="calamine")

        calculos.preparacao_dados(
            DF, ASSOCIACAO_COLUNAS_VARIAVEIS_PREVIA, "2024-10", "2024-09", "2024-08"
        )
        mes_extracao = 10
        ano_extracao = 2024

        _dados_filtro = calculos.calcular_dados_necessarios_do_filtro(DF)
        _dados_filtro.pop("opcoes_valores_anormalidade_leitura", None)
        _dados_filtro.pop("valores_unicos_anormalidade_leitura", None)
        filtro_html = gerar_html_filtros(**_dados_filtro)

        dados = calculos.calcular_todos_os_dados_necessarios(DF)
        dados["datas_referencias"] = calculos.calcular_data_referencia(10, 2024)
        dados_html = gerar_html_dados(**dados)

_meta_registros = str(len(DF)) if not DF.empty else "—"
_meta_referencia = dados["datas_referencias"][0] if not DF.empty else "—"  # type: ignore[possibly-undefined]
_meta_rodape = f"amostra_dados.xlsx · {len(DF)} registros · referência {dados['datas_referencias'][0]}" if not DF.empty else "—"  # type: ignore[possibly-undefined]

app = Dash(suppress_callback_exceptions=True, title="Painel de Gestão do Consumo")

_ESTILO_SECAO_VISIVEL = {
    "display": "flex",
    "flexDirection": "column",
    "gap": "0",
    "gridColumnStart": "span 6",
    "backgroundColor": "#ffffff",
    "border": "1px solid #dde0e5",
    "padding": "20px",
}

_ESTILO_PAINEL_ABERTO = {
    "position": "fixed",
    "top": "0",
    "left": "0",
    "width": "380px",
    "height": "100vh",
    "zIndex": "1001",
    "display": "flex",
    "flexDirection": "column",
    "backgroundColor": "#ffffff",
    "borderRight": "1px solid #dde0e5",
    "boxShadow": "4px 0 24px rgba(0,0,0,0.15)",
}
_ESTILO_PAINEL_FECHADO = {"display": "none"}
_ESTILO_BACKDROP_ABERTO = {
    "position": "fixed",
    "top": "0",
    "left": "0",
    "right": "0",
    "bottom": "0",
    "zIndex": "1000",
    "backgroundColor": "rgba(0,0,0,0.5)",
}
_ESTILO_BACKDROP_FECHADO = {"display": "none"}

app.layout = [
    html.Div(
        id=ID_ELEMENTOS_HTML.LAYOUT,
        children=[
            # Top navigation bar
            html.Div(
                id="topbar",
                children=[
                    gerar_html_titulo_app(),
                    html.Nav(
                        [
                            html.Button(
                                "Análise descritiva",
                                id=ID_ELEMENTOS_HTML.TAB_DESCRITIVA,
                                n_clicks=0,
                                className="nav-tab ativo",
                            ),
                            html.Button(
                                "Análise de consumo",
                                id=ID_ELEMENTOS_HTML.TAB_CONSUMO,
                                n_clicks=0,
                                className="nav-tab",
                            ),
                        ],
                        style={
                            "display": "flex",
                            "alignItems": "stretch",
                            "flex": "1",
                            "padding": "0 4px 0 14px",
                        },
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(
                                        "Registros",
                                        style={
                                            "fontSize": "10px",
                                            "color": "#8b929c",
                                            "lineHeight": "1.3",
                                            "display": "block",
                                        },
                                    ),
                                    html.Span(
                                        _meta_registros,
                                        id=ID_ELEMENTOS_HTML.META_REGISTROS,
                                        style={
                                            "fontSize": "12px",
                                            "lineHeight": "1.3",
                                            "fontVariantNumeric": "tabular-nums",
                                        },
                                    ),
                                ],
                                style={
                                    "padding": "0 15px",
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "justifyContent": "center",
                                    "borderLeft": "1px solid #dde0e5",
                                },
                            ),
                            html.Div(
                                [
                                    html.Span(
                                        "Referência",
                                        style={
                                            "fontSize": "10px",
                                            "color": "#8b929c",
                                            "lineHeight": "1.3",
                                            "display": "block",
                                        },
                                    ),
                                    html.Span(
                                        _meta_referencia,
                                        id=ID_ELEMENTOS_HTML.META_REFERENCIA,
                                        style={
                                            "fontSize": "12px",
                                            "lineHeight": "1.3",
                                            "fontVariantNumeric": "tabular-nums",
                                        },
                                    ),
                                ],
                                style={
                                    "padding": "0 15px",
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "justifyContent": "center",
                                    "borderLeft": "1px solid #dde0e5",
                                },
                            ),
                        ],
                        style={
                            "marginLeft": "auto",
                            "display": "flex",
                            "alignItems": "stretch",
                        },
                    ),
                ],
            ),
            # Sidebar
            html.Div(
                id="sidebar",
                children=[
                    html.Section(
                        id=ID_ELEMENTOS_HTML.AREA_UPLOAD_TABELA,
                        style={"display": "flex", "flexDirection": "column"},
                        children=[
                            html.Div(
                                "ABRIR PLANILHA",
                                style={
                                    "fontSize": "10px",
                                    "fontWeight": "600",
                                    "letterSpacing": "0.12em",
                                    "color": "#5d6570",
                                    "padding": "14px 16px 12px",
                                    "borderBottom": "1px solid #dde0e5",
                                },
                            ),
                            html.Div(
                                gerar_form_importar_planilha(
                                    mes_extracao=mes_extracao, ano_extracao=ano_extracao
                                ),
                                style={"padding": "14px 16px"},
                            ),
                            html.Div(
                                id=ID_ELEMENTOS_HTML.AREA_ASSOCIACAO_COLUNAS,
                                children=[],
                            ),
                        ],
                    ),
                    # Botão de filtros fixo no rodapé da sidebar
                    html.Div(
                        html.Button(
                            "Filtros",
                            id=ID_ELEMENTOS_HTML.BOTAO_TOGGLE_FILTROS,
                            style={
                                "backgroundColor": "#2f6db0",
                                "color": "white",
                                "border": "none",
                                "padding": "14px",
                                "width": "100%",
                                "fontWeight": "500",
                                "cursor": "pointer",
                                "fontSize": "12.5px",
                                "textTransform": "uppercase",
                                "letterSpacing": "0.08em",
                                "fontFamily": '"Segoe UI", system-ui, sans-serif',
                            },
                        ),
                        style={
                            "marginTop": "auto",
                            "borderTop": "1px solid #2a3f5f",
                        },
                    ),
                ],
            ),
            # Área principal
            html.Div(
                id="main-content",
                children=[
                    html.Section(
                        id=ID_ELEMENTOS_HTML.SECAO_RESULTADOS,
                        children=dados_html,
                    ),
                    html.Div(
                        _meta_rodape,
                        id=ID_ELEMENTOS_HTML.RODAPE,
                    ),
                ],
            ),
            # Dummy invisível: alvo do clientside_callback que reseta o
            # scroll ao trocar de aba principal (Descritiva/Consumo).
            dcc.Store(id=ID_ELEMENTOS_HTML.SCROLL_RESET_DUMMY),
            # Backdrop (fecha o painel ao clicar fora)
            html.Div(
                id=ID_ELEMENTOS_HTML.BACKDROP_FILTROS,
                style=_ESTILO_BACKDROP_FECHADO,
                n_clicks=0,
            ),
            # Painel de filtros (drawer lateral)
            html.Div(
                id=ID_ELEMENTOS_HTML.PAINEL_FILTROS,
                style=_ESTILO_PAINEL_FECHADO,
                children=[
                    # Cabeçalho
                    html.Div(
                        [
                            html.Span(
                                "Filtros",
                                style={
                                    "fontWeight": "600",
                                    "fontSize": "13px",
                                    "color": "#252a31",
                                    "textTransform": "uppercase",
                                    "letterSpacing": "0.1em",
                                },
                            ),
                            html.Button(
                                "✕",
                                id=ID_ELEMENTOS_HTML.BOTAO_FECHAR_FILTROS,
                                style={
                                    "background": "none",
                                    "border": "none",
                                    "color": "#8b929c",
                                    "fontSize": "1.2rem",
                                    "cursor": "pointer",
                                    "lineHeight": "1",
                                },
                            ),
                        ],
                        style={
                            "display": "flex",
                            "justifyContent": "space-between",
                            "alignItems": "center",
                            "padding": "16px 24px",
                            "borderBottom": "1px solid #dde0e5",
                            "backgroundColor": "#ffffff",
                        },
                    ),
                    # Conteúdo dos filtros (com scroll)
                    html.Div(
                        html.Section(
                            id=ID_ELEMENTOS_HTML.FILTROS, children=filtro_html
                        ),
                        style={
                            "flex": "1",
                            "overflowY": "auto",
                            "padding": "24px",
                        },
                    ),
                    # Rodapé com botão aplicar
                    html.Div(
                        html.Button(
                            "Aplicar Filtros",
                            id=ID_ELEMENTOS_HTML.FILTRO_SUBMIT,
                            type="button",
                            style={
                                "backgroundColor": "#2f6db0",
                                "color": "white",
                                "border": "none",
                                "padding": "16px",
                                "width": "100%",
                                "fontWeight": "500",
                                "cursor": "pointer",
                                "fontSize": "12.5px",
                                "textTransform": "uppercase",
                                "letterSpacing": "0.08em",
                                "fontFamily": '"Segoe UI", system-ui, sans-serif',
                            },
                        ),
                        style={"borderTop": "1px solid #dde0e5"},
                    ),
                ],
            ),
        ],
    ),
]

# -------------------------------------------------------------
#################
### CALLBACKS ###
#################


@callback(
    Output(ID_ELEMENTOS_HTML.PAINEL_FILTROS, "style"),
    Output(ID_ELEMENTOS_HTML.BACKDROP_FILTROS, "style"),
    Input(ID_ELEMENTOS_HTML.BOTAO_TOGGLE_FILTROS, "n_clicks"),
    Input(ID_ELEMENTOS_HTML.BOTAO_FECHAR_FILTROS, "n_clicks"),
    Input(ID_ELEMENTOS_HTML.BACKDROP_FILTROS, "n_clicks"),
    prevent_initial_call=True,
)
def toggle_painel_filtros(_open, _fechar, _backdrop):
    if ctx.triggered_id == ID_ELEMENTOS_HTML.BOTAO_TOGGLE_FILTROS:
        return _ESTILO_PAINEL_ABERTO, _ESTILO_BACKDROP_ABERTO
    return _ESTILO_PAINEL_FECHADO, _ESTILO_BACKDROP_FECHADO


@callback(
    Output(ID_ELEMENTOS_HTML.PAINEL_SOBRE, "style"),
    Input(ID_ELEMENTOS_HTML.BOTAO_SOBRE, "n_clicks"),
    prevent_initial_call=True,
)
def toggle_painel_sobre(n_clicks: int):
    if n_clicks % 2 == 1:
        return EstilosCSS.ESTILO_SOBRE_ABERTO
    return EstilosCSS.ESTILO_SOBRE_FECHADO


@callback(
    Output(ID_ELEMENTOS_HTML.UPLOAD_NOME_ARQUIVO, "children"),
    Input(ID_ELEMENTOS_HTML.UPLOAD_TABELA, "filename"),
    prevent_initial_call=True,
)
def colocar_nome_arquivo_tabela(nome_arquivo: str):
    return nome_arquivo


@callback(
    Output(ID_ELEMENTOS_HTML.AREA_ASSOCIACAO_COLUNAS, "children"),
    Output(ID_ELEMENTOS_HTML.UPLOAD_TABELA_ERRO, "children"),
    Output(ID_ELEMENTOS_HTML.FILTROS, "children", allow_duplicate=True),
    Output(ID_ELEMENTOS_HTML.SECAO_RESULTADOS, "children"),
    Input(ID_ELEMENTOS_HTML.PROCESSAR_TABELA, "n_clicks"),
    State(ID_ELEMENTOS_HTML.UPLOAD_TABELA, "contents"),
    State(ID_ELEMENTOS_HTML.UPLOAD_TABELA, "filename"),
    State(ID_ELEMENTOS_HTML.MES_EXTRACAO, "value"),
    State(ID_ELEMENTOS_HTML.ANO_EXTRACAO, "value"),
    prevent_initial_call=True,
)
def liberar_associacao_de_colunas(
    n_clicks: int,
    conteudo: str | None,
    nome_arquivo: str,
    mes_extracao: int | None,
    ano_extracao: int | None,
):
    global DF, _ARQUIVO_BYTES, _COLUNAS_ARQUIVO
    DF = pd.DataFrame()

    erros: list[str] = []
    if conteudo is None or nome_arquivo is None:
        erros.append("Arquivo da tabela está vazio ou não foi escolhido.")
    elif len(nome_arquivo) < 4 or nome_arquivo[-4:] != "xlsx":
        erros.append("Arquivo não está no formato '.xlsx'.")

    if mes_extracao is None or ano_extracao is None:
        erros.append("Ano e/ou mês de extração não informado.")

    if len(erros) > 0:
        return (
            [],
            componente_painel_erros(erros),
            [],
            [],
        )

    assert isinstance(conteudo, str)
    _, con = conteudo.split(",")

    _ARQUIVO_BYTES = base64.b64decode(con)
    # Libera as strings base64 (conteúdo original + fatia decodificada) assim
    # que os bytes já foram extraídos, em vez de esperar a função terminar.
    del conteudo, con

    cabecalho = pd.read_excel(io.BytesIO(_ARQUIVO_BYTES), engine="calamine", nrows=0)
    opcoes = list(cabecalho.columns)
    _COLUNAS_ARQUIVO = opcoes

    assert isinstance(mes_extracao, int)
    assert isinstance(ano_extracao, int)
    data_1, data_2, data_3 = calculos.calcular_data_referencia(
        mes_extracao, ano_extracao
    )
    return (
        gerar_form_colunas(
            data_1, data_2, data_3, opcoes, "", ASSOCIACAO_COLUNAS_VARIAVEIS_PREVIA
        ),
        "",
        [],
        [],
    )


@callback(
    Output(ID_ELEMENTOS_HTML.SECAO_RESULTADOS, "children", allow_duplicate=True),
    Output(ID_ELEMENTOS_HTML.PAINEL_FILTROS, "style", allow_duplicate=True),
    Output(ID_ELEMENTOS_HTML.BACKDROP_FILTROS, "style", allow_duplicate=True),
    Output(ID_ELEMENTOS_HTML.META_REGISTROS, "children"),
    Output(ID_ELEMENTOS_HTML.META_REFERENCIA, "children"),
    Output(ID_ELEMENTOS_HTML.RODAPE, "children"),
    Output(ID_ELEMENTOS_HTML.TAB_DESCRITIVA, "className"),
    Output(ID_ELEMENTOS_HTML.TAB_CONSUMO, "className"),
    Input(ID_ELEMENTOS_HTML.FILTRO_SUBMIT, "n_clicks"),
    State(ID_ELEMENTOS_HTML.FILTRO_DIAMETRO, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_IDADE, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_SITUACAO, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_DIAMETRO_LETRA, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_GRUPO_FATURAMENTO, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_PERFIL_IMOVEL, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_CATEGORIA, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_TIPO_TARIFA_ESGOTO, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_ANORMALIDADE_CONSUMO, "value"),
    State(ID_ELEMENTOS_HTML.MES_EXTRACAO, "value"),
    State(ID_ELEMENTOS_HTML.ANO_EXTRACAO, "value"),
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
    categorias: list[str],
    tipos_tarifa_esgoto: list[str],
    anormalidades_consumo: list[str],
    mes_extracao: int,
    ano_extracao: int,
):
    global DF

    limites_diametros = limites_diametros or []
    situacoes = situacoes or []
    diametro_letra = diametro_letra or []
    grupo_faturamento = grupo_faturamento or []
    perfil_imovel_selecionados = perfil_imovel_selecionados or []
    categorias = categorias or []
    tipos_tarifa_esgoto = tipos_tarifa_esgoto or []
    anormalidades_consumo = anormalidades_consumo or []

    filtrado = DF[
        (DF.diametro.isin(limites_diametros))
        & (DF.idade_hidrometro.between(limites_idade[0], limites_idade[1]))
        & (DF.situacao_ligacao_agua.isin(situacoes))
        & (DF.diametro_letra.isin(diametro_letra))
        & (DF.grupo_leitura.isin(grupo_faturamento))
        & (DF.perfil_imovel.isin(perfil_imovel_selecionados))
        & (DF.categoria.isin(categorias))
        & (DF.tipo_tarifa_esgoto.isin(tipos_tarifa_esgoto))
        & (
            DF.anormalidade_consumo_mes_1.isin(anormalidades_consumo)
            | DF.anormalidade_consumo_mes_2.isin(anormalidades_consumo)
            | DF.anormalidade_consumo_mes_3.isin(anormalidades_consumo)
        )
    ]

    if filtrado.empty:
        return (
            gerar_html_zero_resultados(),
            _ESTILO_PAINEL_FECHADO,
            _ESTILO_BACKDROP_FECHADO,
            "0",
            "—",
            "0 registros",
            "nav-tab ativo",
            "nav-tab",
        )

    dados = calculos.calcular_todos_os_dados_necessarios(filtrado)
    dados["datas_referencias"] = calculos.calcular_data_referencia(
        mes_extracao, ano_extracao
    )
    dados_html = gerar_html_dados(**dados)

    ref = dados["datas_referencias"][0]
    n = str(len(filtrado))
    rodape = f"{n} registros · referência {ref}"
    return (
        dados_html,
        _ESTILO_PAINEL_FECHADO,
        _ESTILO_BACKDROP_FECHADO,
        n,
        ref,
        rodape,
        "nav-tab ativo",
        "nav-tab",
    )


@callback(
    Output(ID_ELEMENTOS_HTML.FILTROS, "children", allow_duplicate=True),
    Output(ID_ELEMENTOS_HTML.DROPDOWN_ASSOCIACAO_COLUNAS_ERRO, "children"),
    Output(ID_ELEMENTOS_HTML.SECAO_RESULTADOS, "children", allow_duplicate=True),
    Output(ID_ELEMENTOS_HTML.META_REGISTROS, "children", allow_duplicate=True),
    Output(ID_ELEMENTOS_HTML.META_REFERENCIA, "children", allow_duplicate=True),
    Output(ID_ELEMENTOS_HTML.RODAPE, "children", allow_duplicate=True),
    Output(ID_ELEMENTOS_HTML.TAB_DESCRITIVA, "className", allow_duplicate=True),
    Output(ID_ELEMENTOS_HTML.TAB_CONSUMO, "className", allow_duplicate=True),
    Input(ID_ELEMENTOS_HTML.BOTAO_ASSOCIAR_COLUNAS, "n_clicks"),
    State(ID_ELEMENTOS_HTML.MES_EXTRACAO, "value"),
    State(ID_ELEMENTOS_HTML.ANO_EXTRACAO, "value"),
    State(ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS["ramal"], "value"),
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
    State(
        ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS[
            "anormalidade_consumo_mes_1"
        ],
        "value",
    ),
    State(
        ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS[
            "anormalidade_consumo_mes_2"
        ],
        "value",
    ),
    State(
        ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS[
            "anormalidade_consumo_mes_3"
        ],
        "value",
    ),
    State(
        ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS["contas_vencidas_aberto"],
        "value",
    ),
    State(
        ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS["divida_total_vencida"],
        "value",
    ),
    State(ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS["categoria"], "value"),
    State(
        ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS["tipo_tarifa_esgoto"],
        "value",
    ),
    prevent_initial_call=True,
)
def associar_colunas(
    n_clicks,
    mes_extracao: int,
    ano_extracao: int,
    ramal: str,
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
    anormalidade_consumo_mes_1: str,
    anormalidade_consumo_mes_2: str,
    anormalidade_consumo_mes_3: str,
    contas_vencidas_aberto: str,
    divida_total_vencida: str,
    categoria: str,
    tipo_tarifa_esgoto: str,
):
    _sem_alteracao = (no_update,) * 6

    if n_clicks is None:
        return [], "", *_sem_alteracao

    colunas_associadas_de_cada_variavel: dict[NOME_VARIAVEIS, str] = {
        "ramal": ramal,
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
        "anormalidade_consumo_mes_1": anormalidade_consumo_mes_1,
        "anormalidade_consumo_mes_2": anormalidade_consumo_mes_2,
        "anormalidade_consumo_mes_3": anormalidade_consumo_mes_3,
        "contas_vencidas_aberto": contas_vencidas_aberto,
        "divida_total_vencida": divida_total_vencida,
        "categoria": categoria,
        "tipo_tarifa_esgoto": tipo_tarifa_esgoto,
    }

    # Variáveis opcionais (ver tipos.VARIAVEIS_OPCIONAIS) podem ficar sem
    # associação — só as demais (estruturais) são obrigatórias.
    teste_se_todos_valores_sao_nao_nulos = all(
        valor is not None
        for variavel, valor in colunas_associadas_de_cada_variavel.items()
        if variavel not in VARIAVEIS_OPCIONAIS
    )

    if teste_se_todos_valores_sao_nao_nulos:
        global DF

        data_referencia_1, data_referencia_2, data_referencia_3 = (
            calculos.calcular_data_referencia(mes_extracao, ano_extracao)
        )

        colunas_para_ler = [
            col
            for col in colunas_associadas_de_cada_variavel.values()
            if col is not None
        ]

        try:
            # Só agora o arquivo é lido de fato, e só com as colunas
            # associadas (não as ~todas da planilha original) — reduz a
            # memória do DF mantido pelo resto da sessão.
            DF = pd.read_excel(
                io.BytesIO(_ARQUIVO_BYTES),
                engine="calamine",
                usecols=colunas_para_ler,
            )
            calculos.preparacao_dados(
                DF,
                colunas_associadas_de_cada_variavel,
                data_referencia_1,
                data_referencia_2,
                data_referencia_3,
            )
        except (KeyError, ValueError) as e:
            return (
                [],
                componente_painel_erros(
                    [
                        f"Coluna não encontrada: {e}. Colunas disponíveis: {_COLUNAS_ARQUIVO}"
                    ]
                ),
                *_sem_alteracao,
            )

        dados_filtro = calculos.calcular_dados_necessarios_do_filtro(DF)
        dados_filtro.pop("opcoes_valores_anormalidade_leitura", None)
        dados_filtro.pop("valores_unicos_anormalidade_leitura", None)

        dados = calculos.calcular_todos_os_dados_necessarios(DF)
        dados["datas_referencias"] = calculos.calcular_data_referencia(
            mes_extracao, ano_extracao
        )
        dados_html = gerar_html_dados(**dados)

        ref = dados["datas_referencias"][0]
        n = str(len(DF))
        rodape = f"{n} registros · referência {ref}"

        return (
            gerar_html_filtros(**dados_filtro),
            "",
            dados_html,
            n,
            ref,
            rodape,
            "nav-tab ativo",
            "nav-tab",
        )

    return (
        [],
        componente_painel_erros(
            ["Todas as variáveis devem estar associadas a uma coluna da tabela"]
        ),
        *_sem_alteracao,
    )


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
    State(ID_ELEMENTOS_HTML.FILTRO_CATEGORIA, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_TIPO_TARIFA_ESGOTO, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_LOCAL_ANORM_LEITURA, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_ANORMALIDADE_CONSUMO, "value"),
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
    categorias: list[str],
    tipos_tarifa_esgoto: list[str],
    anorm_leitura_local: list[str],
    anormalidades_consumo: list[str],
):
    global DF

    limites_diametros = limites_diametros or []
    situacoes = situacoes or []
    diametro_letra = diametro_letra or []
    grupo_faturamento = grupo_faturamento or []
    perfil_imovel_selecionados = perfil_imovel_selecionados or []
    categorias = categorias or []
    tipos_tarifa_esgoto = tipos_tarifa_esgoto or []
    anorm_leitura_local = anorm_leitura_local or []
    anormalidades_consumo = anormalidades_consumo or []

    filtrado = DF[
        (DF.diametro.isin(limites_diametros))
        & (DF.idade_hidrometro.between(limites_idade[0], limites_idade[1]))
        & (DF.situacao_ligacao_agua.isin(situacoes))
        & (DF.diametro_letra.isin(diametro_letra))
        & (DF.grupo_leitura.isin(grupo_faturamento))
        & (DF.perfil_imovel.isin(perfil_imovel_selecionados))
        & (DF.categoria.isin(categorias))
        & (DF.tipo_tarifa_esgoto.isin(tipos_tarifa_esgoto))
        & (
            DF.anormalidade_leitura_mes_1.isin(anorm_leitura_local)
            | DF.anormalidade_leitura_mes_2.isin(anorm_leitura_local)
            | DF.anormalidade_leitura_mes_3.isin(anorm_leitura_local)
        )
        & (
            DF.anormalidade_consumo_mes_1.isin(anormalidades_consumo)
            | DF.anormalidade_consumo_mes_2.isin(anormalidades_consumo)
            | DF.anormalidade_consumo_mes_3.isin(anormalidades_consumo)
        )
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
    ) = calculos.calcular_frequencia_consumos_medios(filtrado, valor_limite)

    (
        anormalidade_leitura_mes_1,
        anormalidade_leitura_mes_2,
        anormalidade_leitura_mes_3,
    ) = calculos.calcular_frequencia_anormalidade_leitura(filtrado)

    (
        frequencia_consumos_medidos_mes_1,
        frequencia_consumos_medidos_mes_2,
        frequencia_consumos_medidos_mes_3,
    ) = calculos.calcular_frequencia_consumo_medido(filtrado, valor_limite)

    (
        frequencia_consumo_faturado_mes_1,
        frequencia_consumo_faturado_mes_2,
        frequencia_consumo_faturado_mes_3,
    ) = calculos.calcular_frequencia_consumo_faturado(filtrado, valor_limite)

    (
        frequencia_anormalidade_consumo_1,
        frequencia_anormalidade_consumo_2,
        frequencia_anormalidade_consumo_3,
    ) = calculos.calcular_frequencia_anormalidade_consumo(filtrado)

    ramais_mes_1 = filtrado.loc[
        filtrado.consumo_max_mes_1.isin(["Maior", "Menor"]),
        ["ramal", "diametro_letra", "consumo_max_mes_1", "media_consumo_mes_1"],
    ]
    ramais_mes_2 = filtrado.loc[
        filtrado.consumo_max_mes_2.isin(["Maior", "Menor"]),
        ["ramal", "diametro_letra", "consumo_max_mes_2", "media_consumo_mes_2"],
    ]
    ramais_mes_3 = filtrado.loc[
        filtrado.consumo_max_mes_3.isin(["Maior", "Menor"]),
        ["ramal", "diametro_letra", "consumo_max_mes_3", "media_consumo_mes_3"],
    ]

    # "Concatenar Consumo a partir de" é especificamente sobre consumo (m³);
    # contas vencidas (contagem) e dívida total (R$) são unidades diferentes
    # e não devem usar esse mesmo limite — mantêm o padrão de calculos.py.
    frequencia_contas_vencidas_aberto = (
        calculos.calcular_frequencia_contas_vencidas_aberto(filtrado)
    )
    frequencia_divida_total_vencida = calculos.calcular_frequencia_total_divida_vencida(
        filtrado
    )

    return [
        gerar_html_dados_consumo_mes(
            media_do_consumo_medio_mes_1,
            desvio_padrao_consumo_medio_mes_1,
            frequencia_consumo_acima_limite_mes_1,
            frequencia_consumos_medios_mes_1,
            frequencia_consumos_medidos_mes_1,
            frequencia_consumo_faturado_mes_1,
            anormalidade_leitura_mes_1,
            frequencia_anormalidade_consumo_1,
            ramais_mes_1,
            "consumo_max_mes_1",
            "media_consumo_mes_1",
            "Mês 1",
            ID_ELEMENTOS_HTML.DADOS_CONSUMO_MES_1,
            mes_index="mes-1",
            limite_consumo_utilizado=valor_limite,
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
            ramais_mes_2,
            "consumo_max_mes_2",
            "media_consumo_mes_2",
            "Mês 2",
            ID_ELEMENTOS_HTML.DADOS_CONSUMO_MES_2,
            mes_index="mes-2",
            oculto=True,
            limite_consumo_utilizado=valor_limite,
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
            ramais_mes_3,
            "consumo_max_mes_3",
            "media_consumo_mes_3",
            "Mês 3",
            ID_ELEMENTOS_HTML.DADOS_CONSUMO_MES_3,
            mes_index="mes-3",
            oculto=True,
            limite_consumo_utilizado=valor_limite,
            frequencia_divida_total_vencida=frequencia_divida_total_vencida,
            frequencia_contas_vencidas_aberto=frequencia_contas_vencidas_aberto,
        ),
    ]


def _filtrar_df(
    limites_diametros,
    limites_idade,
    situacoes,
    diametro_letra,
    grupo_faturamento,
    perfil_imovel_selecionados,
    categorias,
    tipos_tarifa_esgoto,
    anormalidades_consumo,
):
    global DF
    return DF[
        (DF.diametro.isin(limites_diametros or []))
        & (DF.idade_hidrometro.between(limites_idade[0], limites_idade[1]))
        & (DF.situacao_ligacao_agua.isin(situacoes or []))
        & (DF.diametro_letra.isin(diametro_letra or []))
        & (DF.grupo_leitura.isin(grupo_faturamento or []))
        & (DF.perfil_imovel.isin(perfil_imovel_selecionados or []))
        & (DF.categoria.isin(categorias or []))
        & (DF.tipo_tarifa_esgoto.isin(tipos_tarifa_esgoto or []))
        & (
            DF.anormalidade_consumo_mes_1.isin(anormalidades_consumo or [])
            | DF.anormalidade_consumo_mes_2.isin(anormalidades_consumo or [])
            | DF.anormalidade_consumo_mes_3.isin(anormalidades_consumo or [])
        )
    ]


@callback(
    Output(ID_ELEMENTOS_HTML.TABELA_RAMAIS_ANORMALIDADE, "data"),
    Output(ID_ELEMENTOS_HTML.TOTAL_RAMAIS_ANORMALIDADE, "children"),
    Input(ID_ELEMENTOS_HTML.ESCOLHA_ABA_DADOS_CONSUMO, "value"),
    Input(ID_ELEMENTOS_HTML.PESQUISA_RAMAIS_ANORMALIDADE, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_DIAMETRO, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_IDADE, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_SITUACAO, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_DIAMETRO_LETRA, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_GRUPO_FATURAMENTO, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_PERFIL_IMOVEL, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_CATEGORIA, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_TIPO_TARIFA_ESGOTO, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_ANORMALIDADE_CONSUMO, "value"),
    prevent_initial_call=True,
)
def atualizar_tabela_ramais_anormalidade(
    mes,
    termo,
    limites_diametros,
    limites_idade,
    situacoes,
    diametro_letra,
    grupo_faturamento,
    perfil_imovel_selecionados,
    categorias,
    tipos_tarifa_esgoto,
    anormalidades_consumo,
):
    if limites_idade is None:
        return [], ""

    filtrado = _filtrar_df(
        limites_diametros,
        limites_idade,
        situacoes,
        diametro_letra,
        grupo_faturamento,
        perfil_imovel_selecionados,
        categorias,
        tipos_tarifa_esgoto,
        anormalidades_consumo,
    )

    mes = mes or "1"
    col_anorm = f"consumo_max_mes_{mes}"
    col_consumo = f"media_consumo_mes_{mes}"

    ramais = filtrado.loc[filtrado[col_anorm].isin(["Maior", "Menor"])].copy()

    if termo:
        mask = ramais.ramal.astype(str).str.contains(
            termo, case=False, na=False
        ) | ramais.diametro_letra.astype(str).str.contains(termo, case=False, na=False)
        ramais = ramais[mask]

    dados = _ramais_para_tabela(
        ramais[["ramal", "diametro_letra", col_anorm, col_consumo]],
        col_anorm,
        col_consumo,
    )
    total = f"Total: {len(dados)} ramais"
    return dados, total


@callback(
    Output(ID_ELEMENTOS_HTML.TABELA_RAMAIS_ANORMALIDADE, "page_size"),
    Input(ID_ELEMENTOS_HTML.PAGINA_RAMAIS_ANORMALIDADE, "value"),
    prevent_initial_call=True,
)
def atualizar_pagina_tabela_ramais(value):
    return value or 10


@callback(
    Output({"type": "tabela-anorm-leitura", "index": MATCH}, "page_size"),
    Input({"type": "pagina-anorm-leitura", "index": MATCH}, "value"),
    prevent_initial_call=True,
)
def pagina_anorm_leitura(value):
    return value or 10


@callback(
    Output({"type": "tabela-anorm-leitura", "index": MATCH}, "filter_query"),
    Input({"type": "pesquisa-anorm-leitura", "index": MATCH}, "value"),
    prevent_initial_call=True,
)
def buscar_anorm_leitura(termo):
    return f'{{Anormalidade}} icontains "{termo}"' if termo else ""


@callback(
    Output({"type": "tabela-anorm-consumo", "index": MATCH}, "page_size"),
    Input({"type": "pagina-anorm-consumo", "index": MATCH}, "value"),
    prevent_initial_call=True,
)
def pagina_anorm_consumo(value):
    return value or 10


@callback(
    Output({"type": "tabela-anorm-consumo", "index": MATCH}, "filter_query"),
    Input({"type": "pesquisa-anorm-consumo", "index": MATCH}, "value"),
    prevent_initial_call=True,
)
def buscar_anorm_consumo(termo):
    return f'{{Anormalidade}} icontains "{termo}"' if termo else ""


@callback(
    Output({"type": "tabela-ramais-mes", "index": MATCH}, "page_size"),
    Input({"type": "pagina-ramais-mes", "index": MATCH}, "value"),
    prevent_initial_call=True,
)
def pagina_ramais_mes(value):
    return value or 10


@callback(
    Output({"type": "tabela-ramais-mes", "index": MATCH}, "filter_query"),
    Input({"type": "pesquisa-ramais-mes", "index": MATCH}, "value"),
    prevent_initial_call=True,
)
def buscar_ramais_mes(termo):
    if not termo:
        return ""
    return f'{{ramal}} icontains "{termo}" || {{diametro}} icontains "{termo}"'


@callback(
    Output({"type": "download-mes", "index": MATCH}, "data"),
    Input({"type": "btn-dl-sem", "index": MATCH}, "n_clicks"),
    Input({"type": "btn-dl-com", "index": MATCH}, "n_clicks"),
    State(ID_ELEMENTOS_HTML.FILTRO_DIAMETRO, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_IDADE, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_SITUACAO, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_DIAMETRO_LETRA, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_GRUPO_FATURAMENTO, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_PERFIL_IMOVEL, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_CATEGORIA, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_TIPO_TARIFA_ESGOTO, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_ANORMALIDADE_CONSUMO, "value"),
    prevent_initial_call=True,
)
def download_ramais_mes(
    _n_sem,
    _n_com,
    limites_diametros,
    limites_idade,
    situacoes,
    diametro_letra,
    grupo_faturamento,
    perfil_imovel_selecionados,
    categorias,
    tipos_tarifa_esgoto,
    anormalidades_consumo,
):
    global DF
    triggered = ctx.triggered_id
    mes_index = (
        triggered.get("index", "mes-1") if isinstance(triggered, dict) else "mes-1"
    )
    mes = mes_index.split("-")[1]
    sem_filtro = isinstance(triggered, dict) and triggered.get("type") == "btn-dl-sem"

    col_anorm = f"consumo_max_mes_{mes}"
    col_consumo = f"media_consumo_mes_{mes}"

    df_base = (
        DF
        if sem_filtro
        else _filtrar_df(
            limites_diametros,
            limites_idade,
            situacoes,
            diametro_letra,
            grupo_faturamento,
            perfil_imovel_selecionados,
            categorias,
            tipos_tarifa_esgoto,
            anormalidades_consumo,
        )
    )

    df_export = df_base.loc[
        df_base[col_anorm].isin(["Maior", "Menor"]),
        ["ramal", "diametro_letra", col_anorm, col_consumo],
    ].rename(
        columns={
            "ramal": "Ramal",
            "diametro_letra": "Diâmetro",
            col_anorm: "Anormalidade de Consumo",
            col_consumo: "Consumo Médio",
        }
    )
    return dcc.send_data_frame(
        df_export.to_excel, f"ramais_anormalidade_mes{mes}.xlsx", index=False
    )


@callback(
    Output(ID_ELEMENTOS_HTML.TABELA_PERFIL_IMOVEL, "page_size"),
    Input(ID_ELEMENTOS_HTML.PAGINA_PERFIL_IMOVEL, "value"),
    prevent_initial_call=True,
)
def pagina_perfil_imovel(value):
    return value or 5


@callback(
    Output(ID_ELEMENTOS_HTML.TABELA_PERFIL_IMOVEL, "filter_query"),
    Input(ID_ELEMENTOS_HTML.PESQUISA_PERFIL_IMOVEL, "value"),
    prevent_initial_call=True,
)
def buscar_perfil_imovel(termo):
    return f'{{"Perfil Imóvel"}} icontains "{termo}"' if termo else ""


@callback(
    Output(ID_ELEMENTOS_HTML.TABELA_DIAMETRO, "page_size"),
    Input(ID_ELEMENTOS_HTML.PAGINA_DIAMETRO, "value"),
    prevent_initial_call=True,
)
def pagina_diametro(value):
    return value or 5


@callback(
    Output(ID_ELEMENTOS_HTML.TABELA_DIAMETRO, "filter_query"),
    Input(ID_ELEMENTOS_HTML.PESQUISA_DIAMETRO, "value"),
    prevent_initial_call=True,
)
def buscar_diametro(termo):
    return f'{{"Diâmetro"}} icontains "{termo}"' if termo else ""


@callback(
    Output(ID_ELEMENTOS_HTML.SECAO_DESCRITIVA, "style"),
    Output(ID_ELEMENTOS_HTML.SECAO_CONSUMO_CARD, "style"),
    Output(ID_ELEMENTOS_HTML.TAB_DESCRITIVA, "className", allow_duplicate=True),
    Output(ID_ELEMENTOS_HTML.TAB_CONSUMO, "className", allow_duplicate=True),
    Input(ID_ELEMENTOS_HTML.TAB_DESCRITIVA, "n_clicks"),
    Input(ID_ELEMENTOS_HTML.TAB_CONSUMO, "n_clicks"),
    prevent_initial_call=True,
)
def alternar_abas_principais(_d, _c):
    if ctx.triggered_id == ID_ELEMENTOS_HTML.TAB_CONSUMO:
        return {"display": "none"}, _ESTILO_SECAO_VISIVEL, "nav-tab", "nav-tab ativo"
    return _ESTILO_SECAO_VISIVEL, {"display": "none"}, "nav-tab ativo", "nav-tab"


app.clientside_callback(
    """
    function(classeDescritiva, classeConsumo) {
        var el = document.getElementById('main-content');
        if (el) { el.scrollTop = 0; }
        return '';
    }
    """,
    Output(ID_ELEMENTOS_HTML.SCROLL_RESET_DUMMY, "data"),
    Input(ID_ELEMENTOS_HTML.TAB_DESCRITIVA, "className"),
    Input(ID_ELEMENTOS_HTML.TAB_CONSUMO, "className"),
    prevent_initial_call=True,
)


@callback(
    Output(ID_ELEMENTOS_HTML.DOWNLOADER_TABELA_COMPLETA_FILTRADA, "data"),
    Input(ID_ELEMENTOS_HTML.BOTAO_DOWNLOAD_TABELA_COMPLETA_FILTRADA, "n_clicks"),
    State(ID_ELEMENTOS_HTML.FILTRO_DIAMETRO, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_IDADE, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_SITUACAO, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_DIAMETRO_LETRA, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_GRUPO_FATURAMENTO, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_PERFIL_IMOVEL, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_CATEGORIA, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_TIPO_TARIFA_ESGOTO, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_ANORMALIDADE_CONSUMO, "value"),
    prevent_initial_call=True,
)
def download_tabela_completa_filtrada(
    n_clicks: int,
    limites_diametros: list[int],
    limites_idade: list[int],
    situacoes: list[str],
    diametro_letra: list[str],
    grupo_faturamento: list[str],
    perfil_imovel_selecionados: list[str],
    categorias: list[str],
    tipos_tarifa_esgoto: list[str],
    anormalidades_consumo: list[str],
):
    global DF

    limites_diametros = limites_diametros or []
    situacoes = situacoes or []
    diametro_letra = diametro_letra or []
    grupo_faturamento = grupo_faturamento or []
    perfil_imovel_selecionados = perfil_imovel_selecionados or []
    categorias = categorias or []
    tipos_tarifa_esgoto = tipos_tarifa_esgoto or []
    anormalidades_consumo = anormalidades_consumo or []

    filtrado = DF[
        (DF.diametro.isin(limites_diametros))
        & (DF.idade_hidrometro.between(limites_idade[0], limites_idade[1]))
        & (DF.situacao_ligacao_agua.isin(situacoes))
        & (DF.diametro_letra.isin(diametro_letra))
        & (DF.grupo_leitura.isin(grupo_faturamento))
        & (DF.perfil_imovel.isin(perfil_imovel_selecionados))
        & (DF.categoria.isin(categorias))
        & (DF.tipo_tarifa_esgoto.isin(tipos_tarifa_esgoto))
        & (
            DF.anormalidade_consumo_mes_1.isin(anormalidades_consumo)
            | DF.anormalidade_consumo_mes_2.isin(anormalidades_consumo)
            | DF.anormalidade_consumo_mes_3.isin(anormalidades_consumo)
        )
    ]

    return dcc.send_data_frame(
        filtrado.to_excel,
        "filtrado.xlsx",
        sheet_name="planilha1",
        index=False,
    )


if __name__ == "__main__":
    app.run(debug=True)
