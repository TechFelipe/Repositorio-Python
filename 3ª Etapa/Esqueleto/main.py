
import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(
    page_title="Cuidados",
    layout="wide",
    page_icon="🎁"
)


@st.cache_data
def carregar_dados(caminho_arquivo):
    # Carregar todas as abas do Excel
    xls = pd.ExcelFile(caminho_arquivo)

    # Filtrar abas de anos, ignorando as abas de Coeficiente de Variação (CV)
    abas_anos = [
        sheet for sheet in xls.sheet_names
        if "(CV)" not in sheet
    ]

    dados_totais = []

    for ano in abas_anos:
        df_raw = pd.read_excel(xls, sheet_name=ano)

        # Localizar onde começam os dados de localização (Brasil, Regiões, UFs)
        linhas_brasil = df_raw.index[
            df_raw.iloc[:, 0].astype(str).str.strip() == "Brasil"
        ]

        # Ignorar abas que não possuem a linha Brasil
        if linhas_brasil.empty:
            continue

        start_idx = linhas_brasil[0]

        # Selecionar as colunas relevantes: Localidade, Total, Homem, Mulher
        df_ano = df_raw.iloc[
            start_idx:, [0, 1, 2, 3]
        ].copy()

        df_ano.columns = [
            "Localidade",
            "Total",
            "Homem",
            "Mulher"
        ]

        # Limpar linhas nulas ou notas de rodapé
        df_ano = df_ano.dropna(subset=["Localidade"])

        df_ano = df_ano[
            df_ano["Localidade"].astype(str).str.strip() != ""
        ]

        # Converter colunas numéricas
        for col in ["Total", "Homem", "Mulher"]:
            df_ano[col] = pd.to_numeric(
                df_ano[col],
                errors="coerce"
            )

        # Adicionar o ano correspondente à aba
        df_ano["Ano"] = str(ano)

        # Adicionar os dados da aba à lista
        dados_totais.append(df_ano)

    # Verificar se alguma aba foi carregada
    if not dados_totais:
        raise ValueError(
            "Nenhuma aba válida com dados foi encontrada no arquivo Excel."
        )

    # Juntar os dados de todas as abas
    df_completo = pd.concat(
        dados_totais,
        ignore_index=True
    )

    return df_completo


# Caminho do arquivo Excel
caminho_arquivo = r"H:\Python\3ª Etapa\Esqueleto\Tabela 1.1.2.xls"


try:
    # Carregar os dados
    df = carregar_dados(caminho_arquivo)

    # --- BARRA LATERAL (SIDEBAR) ---
    st.sidebar.header("🔍 Filtros")

    # Seleção de ano
    anos_disponiveis = sorted(
        df["Ano"].unique(),
        reverse=True
    )

    ano_selecionado = st.sidebar.selectbox(
        "Selecione o Ano:",
        anos_disponiveis
    )

    # Seleção de localidade
    localidades_disponiveis = df["Localidade"].unique().tolist()

    localidades_padrao = [
        "Brasil",
        "Norte",
        "Nordeste",
        "Sudeste",
        "Sul",
        "Centro-Oeste"
    ]

    # Manter apenas localidades padrão que existem nos dados
    localidades_padrao = [
        localidade
        for localidade in localidades_padrao
        if localidade in localidades_disponiveis
    ]

    localidades_selecionadas = st.sidebar.multiselect(
        "Selecione as Regiões/UFs:",
        options=localidades_disponiveis,
        default=localidades_padrao
    )

    # --- CORPO DA APLICAÇÃO ---
    st.title(
        "📊 Horas Dedicadas a Cuidados e Afazeres Domésticos"
    )

    st.markdown(
        "Análise da média de horas semanais dedicadas por pessoas "
        "ocupadas de 14 anos ou mais, por sexo."
    )

    # Filtrar dados com base nas seleções
    df_filtrado = df[
        (df["Ano"] == ano_selecionado)
        & (df["Localidade"].isin(localidades_selecionadas))
    ]

    if not df_filtrado.empty:

        # --- TABELA DE DADOS ---
        st.subheader(
            f"📑 Dados em Tabela ({ano_selecionado})"
        )

        st.dataframe(
            df_filtrado[
                ["Localidade", "Total", "Homem", "Mulher"]
            ].reset_index(drop=True),
            use_container_width=True
        )

        st.markdown("---")
        st.subheader("📝 Gráficos Comparativos")

        col1, col2 = st.columns(2)

        # --- COLUNA 1: GRÁFICO DE BARRAS ---
        with col1:
            df_melted = df_filtrado.melt(
                id_vars=["Localidade"],
                value_vars=["Homem", "Mulher"],
                var_name="Gênero",
                value_name="Horas Semanais"
            )

            fig_bar = px.bar(
                df_melted,
                x="Localidade",
                y="Horas Semanais",
                color="Gênero",
                barmode="group",
                title=f"Média de Horas por Gênero ({ano_selecionado})",
                color_discrete_sequence=[
                    "#1f77b4",
                    "#e377c2"
                ],
                labels={
                    "Horas Semanais": "Horas/Semana",
                    "Localidade": "Região / UF"
                }
            )

            st.plotly_chart(
                fig_bar,
                use_container_width=True
            )

        # --- COLUNA 2: GRÁFICO DE LINHAS ---
        with col2:
            df_historico = df[
                df["Localidade"].isin(localidades_selecionadas)
            ].copy()

            # Ordenar os anos para exibir a evolução cronológica
            df_historico["Ano_numero"] = pd.to_numeric(
                df_historico["Ano"],
                errors="coerce"
            )

            df_historico = df_historico.sort_values(
                by="Ano_numero"
            )

            fig_line = px.line(
                df_historico,
                x="Ano",
                y="Total",
                color="Localidade",
                markers=True,
                title="Evolução Temporal do Total de Horas Dedicadas",
                labels={
                    "Total": "Horas/Semana",
                    "Ano": "Ano"
                }
            )

            st.plotly_chart(
                fig_line,
                use_container_width=True
            )

    else:
        st.warning(
            "Nenhuma localidade selecionada nos filtros da barra lateral."
        )

except Exception as e:
    st.error(f"Erro ao carregar o arquivo: {e}")

    st.info(
        "Certifique-se de que o arquivo 'Tabela 1.1.2.xls' "
        "está no mesmo diretório do script."
    )
