import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Relatório SINFO - CEFET/RJ", layout="wide")

# Função para carregar os dados
@st.cache_data
def load_data():
    # Certifique-se que o nome do arquivo no GitHub é EXATAMENTE esse:
    return pd.read_csv('stats-dept-20260303.csv')

# Título do Relatório
st.title("📊 Relatório de Atendimentos e Chamados")
st.markdown("---")

try:
    df = load_data()
    unidade = df['Departamento'].iloc[0]

    # --- SIDEBAR (Barra Lateral) ---
    st.sidebar.header("Configurações")
    st.sidebar.write(f"**Unidade:** {unidade}")
    
    # Se as colunas de data existirem no CSV, ele pega. Se não, usa o que você digitar aqui:
    if 'Data_Inicio' in df.columns and 'Data_Fim' in df.columns:
        data_ini = df['Data_Inicio'].iloc[0]
        data_fim = df['Data_Fim'].iloc[0]
        periodo = f"{data_ini} até {data_fim}"
    else:
        # Se não tiver no CSV, você define o período aqui na mão no site
        periodo = st.sidebar.text_input("Defina o Período do Relatório", "Março / 2026")

    st.subheader(f"Período: {periodo}")

    # --- INDICADORES (KPIs) ---
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Abertos", df['Aberto'].iloc[0])
    with col2:
        taxa = (df['Encerrado'].iloc[0] / df['Aberto'].iloc[0] * 100) if df['Aberto'].iloc[0] > 0 else 0
        st.metric("Encerrados", df['Encerrado'].iloc[0], f"{taxa:.1f}% de eficácia")
    with col3:
        st.metric("Em Atribuição", df['Atribuído'].iloc[0])
    with col4:
        st.metric("Atrasados", df['Atrasado'].iloc[0], delta_color="inverse")

    st.markdown("---")

    # --- GRÁFICOS ---
    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        st.subheader("Distribuição por Status")
        status_cols = ['Aberto', 'Atribuído', 'Atrasado', 'Encerrado', 'Reaberto', 'Deletado']
        # Filtra apenas as colunas que realmente existem no seu CSV para não dar erro
        status_existentes = [c for c in status_cols if c in df.columns]
        
        df_status = pd.DataFrame({
            'Status': status_existentes,
            'Quantidade': df[status_existentes].iloc[0].values
        })
        fig_status = px.bar(df_status, x='Status', y='Quantidade', 
                            color='Status', text_auto=True,
                            color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig_status, use_container_width=True)

    with col_graf2:
        st.subheader("Métricas de Tempo")
        time_cols = ['Tempo de Serviço', 'Tempo de Resposta']
        time_existentes = [c for c in time_cols if c in df.columns]
        
        df_times = pd.DataFrame({
            'Métrica': time_existentes,
            'Valor': df[time_existentes].iloc[0].values
        })
        fig_times = px.bar(df_times, y='Métrica', x='Valor', 
                           orientation='h', text_auto=True,
                           color='Métrica', color_discrete_sequence=['#E67E22', '#1ABC9C'])
        st.plotly_chart(fig_times, use_container_width=True)

    # Tabela de Dados Brutos
    with st.expander("Ver base de dados original"):
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Ocorreu um erro ao carregar o dashboard: {e}")
    st.info("Dica: Verifique se o arquivo 'stats-dept-20260303.csv' está no seu repositório do GitHub.")

st.sidebar.markdown("---")
st.sidebar.info("Dashboard SINFO v1.0")
