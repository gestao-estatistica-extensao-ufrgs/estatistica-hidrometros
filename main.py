import base64
import io
import sys

import pandas as pd
from dash import Dash, html, callback, Output, Input, State

from tipos import NOME_VARIAVEIS
from elementos_html import (
    componente_painel_erros,
    gerar_form_colunas,
    gerar_form_importar_planilha,
    gerar_html_dados,
    gerar_html_dados_consumo_mes,
    gerar_html_filtros,
    gerar_html_zero_resultados,
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
        "tipo_tarifa_esgoto": "tipo Tarifa Esgoto",
        "categoria": "Categoria",
        "contas_vencidas_aberto": "Qtd Contas Vencidas em Aberto",
        "divida_total_vencida": "Divida Total Vencida",
    }

    if sys.argv[1] == "-p":
        DF = pd.read_excel("testes/dados_teste/amostra_dados.xlsx")

        calculos.preparacao_dados(
            DF, ASSOCIACAO_COLUNAS_VARIAVEIS_PREVIA, "2024-10", "2024-09", "2024-08"
        )
        mes_extracao = 10
        ano_extracao = 2024

        filtro_html = gerar_html_filtros(
            **calculos.calcular_dados_necessarios_do_filtro(DF)
        )

        dados = calculos.calcular_todos_os_dados_necessarios(DF)
        dados["datas_referencias"] = calculos.calcular_data_referencia(10, 2024)
        dados_html = gerar_html_dados(**dados)

app = Dash(suppress_callback_exceptions=True)

app.layout = [
    html.Div(
        id=ID_ELEMENTOS_HTML.LAYOUT,
        children=[
            html.Section(
                id=ID_ELEMENTOS_HTML.AREA_UPLOAD_TABELA,
                style={"display": "flex", "flexDirection": "column", "gap": "5px"},
                children=[
                    html.Div(
                        style={
                            "display": "flex",
                            "flexDirection": "column",
                            "gap": "2px",
                        },
                        children=[
                            html.H2("Abrir Planilha"),
                            gerar_form_importar_planilha(
                                mes_extracao=mes_extracao, ano_extracao=ano_extracao
                            ),
                        ],
                    ),
                    html.Div(
                        id=ID_ELEMENTOS_HTML.AREA_ASSOCIACAO_COLUNAS,
                        children=[],
                    ),
                ],
            ),
            html.Section(id=ID_ELEMENTOS_HTML.FILTROS, children=filtro_html),
            html.Section(
                id=ID_ELEMENTOS_HTML.SECAO_RESULTADOS,
                children=dados_html,
            ),
        ],
    ),
]

# -------------------------------------------------------------
#################
### CALLBACKS ###
#################


@callback(
    Output(ID_ELEMENTOS_HTML.UPLOAD_NOME_ARQUIVO, "value"),
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
    global DF
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

    DF = pd.read_excel(io.BytesIO(base64.b64decode(con)))
    opcoes = list(DF.columns)

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
    Input(ID_ELEMENTOS_HTML.FILTRO_SUBMIT, "n_clicks"),
    State(ID_ELEMENTOS_HTML.FILTRO_DIAMETRO, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_IDADE, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_SITUACAO, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_DIAMETRO_LETRA, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_GRUPO_FATURAMENTO, "value"),
    State(ID_ELEMENTOS_HTML.FILTRO_PERFIL_IMOVEL, "value"),
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
    mes_extracao: int,
    ano_extracao: int,
):
    global DF

    limites_diametros = limites_diametros or []
    situacoes = situacoes or []
    diametro_letra = diametro_letra or []
    grupo_faturamento = grupo_faturamento or []
    perfil_imovel_selecionados = perfil_imovel_selecionados or []

    filtrado = DF[
        (DF.diametro.isin(limites_diametros))
        & (DF.idade_hidrometro.between(limites_idade[0], limites_idade[1]))
        & (DF.situacao_ligacao_agua.isin(situacoes))
        & (DF.diametro_letra.isin(diametro_letra))
        & (DF.grupo_leitura.isin(grupo_faturamento))
        & (DF.perfil_imovel.isin(perfil_imovel_selecionados))
    ]

    if filtrado.empty:
        return gerar_html_zero_resultados()

    dados = calculos.calcular_todos_os_dados_necessarios(filtrado)
    dados["datas_referencias"] = calculos.calcular_data_referencia(
        mes_extracao, ano_extracao
    )
    dados_html = gerar_html_dados(**dados)

    return dados_html


@callback(
    Output(ID_ELEMENTOS_HTML.FILTROS, "children", allow_duplicate=True),
    Output(ID_ELEMENTOS_HTML.DROPDOWN_ASSOCIACAO_COLUNAS_ERRO, "children"),
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
        ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS["categoria"],
        "value",
    ),
    State(
        ID_HMTL_PARA_OPCOES_FORMULARIO_DE_ASSOCIACAO_COLUNAS["tipo_tarifa_esgoto"],
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
    categoria: str,
    tipo_tarifa_esgoto: str,
    contas_vencidas_aberto: str,
    divida_total_vencida: str,
):
    if n_clicks is None:
        return [], ""

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
        "categoria": categoria,
        "tipo_tarifa_esgoto": tipo_tarifa_esgoto,
        "contas_vencidas_aberto": contas_vencidas_aberto,
        "divida_total_vencida": divida_total_vencida,
    }

    teste_se_todos_valores_sao_nao_nulos = all(
        map(lambda x: x is not None, colunas_associadas_de_cada_variavel.values())
    )

    if teste_se_todos_valores_sao_nao_nulos:
        global DF

        data_referencia_1, data_referencia_2, data_referencia_3 = (
            calculos.calcular_data_referencia(mes_extracao, ano_extracao)
        )

        calculos.preparacao_dados(
            DF,
            colunas_associadas_de_cada_variavel,
            data_referencia_1,
            data_referencia_2,
            data_referencia_3,
        )

        dados = calculos.calcular_dados_necessarios_do_filtro(DF)

        return (
            gerar_html_filtros(**dados),
            "",
        )

    return [], componente_painel_erros(
        ["Todas as variáveis devem estar associadas a uma coluna da tabela"]
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
):
    global DF

    limites_diametros = limites_diametros or []
    situacoes = situacoes or []
    diametro_letra = diametro_letra or []
    grupo_faturamento = grupo_faturamento or []
    perfil_imovel_selecionados = perfil_imovel_selecionados or []

    filtrado = DF[
        (DF.diametro.isin(limites_diametros))
        & (DF.idade_hidrometro.between(limites_idade[0], limites_idade[1]))
        & (DF.situacao_ligacao_agua.isin(situacoes))
        & (DF.diametro_letra.isin(diametro_letra))
        & (DF.grupo_leitura.isin(grupo_faturamento))
        & (DF.perfil_imovel.isin(perfil_imovel_selecionados))
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

    frequencia_total_dividas_vencidas = (
        calculos.calcular_frequencia_total_divida_vencida(filtrado, valor_limite)
    )
    frequencia_contas_vencidas_aberto = (
        calculos.calcular_frequencia_contas_vencidas_aberto(filtrado, valor_limite)
    )

    ramais_com_consumo_maior_ou_menor_que_o_esperado = (
        filtrado[
            ["ramal", "diametro_letra", "consumo_max_mes_1", "media_consumo_mes_1"]
        ],
        filtrado[
            ["ramal", "diametro_letra", "consumo_max_mes_2", "media_consumo_mes_2"]
        ],
        filtrado[
            ["ramal", "diametro_letra", "consumo_max_mes_3", "media_consumo_mes_3"]
        ],
    )

    return [
        gerar_html_dados_consumo_mes(
            media_do_consumo_medio_mes_1,
            desvio_padrao_consumo_medio_mes_1,
            frequencia_consumo_acima_limite_mes_1,
            frequencia_consumos_medios_mes_1,
            anormalidade_leitura_mes_1,
            frequencia_consumos_medidos_mes_1,
            frequencia_consumo_faturado_mes_1,
            frequencia_anormalidade_consumo_1,
            frequencia_contas_vencidas_aberto,
            ramais_com_consumo_maior_ou_menor_que_o_esperado[0],
            frequencia_total_dividas_vencidas,
            "Mês 1",
            ID_ELEMENTOS_HTML.DADOS_CONSUMO_MES_1,
            limite_consumo_utilizado=valor_limite,
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
            frequencia_contas_vencidas_aberto,
            ramais_com_consumo_maior_ou_menor_que_o_esperado[1],
            frequencia_total_dividas_vencidas,
            "Mês 2",
            ID_ELEMENTOS_HTML.DADOS_CONSUMO_MES_2,
            oculto=True,
            limite_consumo_utilizado=valor_limite,
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
            frequencia_contas_vencidas_aberto,
            ramais_com_consumo_maior_ou_menor_que_o_esperado[2],
            frequencia_total_dividas_vencidas,
            "Mês 3",
            ID_ELEMENTOS_HTML.DADOS_CONSUMO_MES_3,
            oculto=True,
            limite_consumo_utilizado=valor_limite,
        ),
    ]


if __name__ == "__main__":
    app.run(debug=True)
