import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Relatório de Chamados - SINFO", layout="wide")

# Título do Relatório
st.title("📊 Relatório de Atendimentos e Chamados")
st.markdown("---")

# Função para carregar os dados
def load_data():
    df = pd.read_csv('stats-dept-20260303.csv')
    return df

df = load_data()

# --- SIDEBAR (Filtros ou Informações) ---
st.sidebar.header("Configurações")
unidade = df['Departamento'].iloc[0]
st.sidebar.write(f"**Unidade:** {unidade}")

# --- DASHBOARD PRINCIPAL ---

# 1. Indicadores (KPIs) em Colunas
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Abertos", df['Aberto'].iloc[0])
with col2:
    st.metric("Encerrados", df['Encerrado'].iloc[0], delta=f"{(df['Encerrado'].iloc[0]/df['Aberto'].iloc[0]*100):.1f}% taxa")
with col3:
    st.metric("Em Atribuição", df['Atribuído'].iloc[0])
with col4:
    st.metric("Atrasados", df['Atrasado'].iloc[0], delta_color="inverse")
try:
    df = load_data()
    unidade = df['Departamento'].iloc[0]
    
    # PEGAR AS DATAS DO CSV
    data_ini = df['Data_Inicio'].iloc[0]
    data_fim = df['Data_Fim'].iloc[0]

    st.subheader(f"Período do Relatório: {data_ini} até {data_fim}")
    st.info(f"Unidade Responsável: {unidade}")

st.markdown("---")

# 2. Gráficos Interativos
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("Distribuição por Status")
    # Preparando dados para o gráfico de barras
    status_cols = ['Aberto', 'Atribuído', 'Atrasado', 'Encerrado', 'Reaberto', 'Deletado']
    df_status = pd.DataFrame({
        'Status': status_cols,
        'Quantidade': df[status_cols].iloc[0].values
    })
    fig_status = px.bar(df_status, x='Status', y='Quantidade', 
                        color='Status', text_auto=True,
                        color_discrete_sequence=px.colors.qualitative.Safe)
    st.plotly_chart(fig_status, use_container_width=True)

with col_graf2:
    st.subheader("Métricas de Tempo")
    time_cols = ['Tempo de Serviço', 'Tempo de Resposta']
    df_times = pd.DataFrame({
        'Métrica': time_cols,
        'Valor': df[time_cols].iloc[0].values
    })
    fig_times = px.bar(df_times, y='Métrica', x='Valor', 
                       orientation='h', text_auto=True,
                       color='Métrica', color_discrete_sequence=['#E67E22', '#1ABC9C'])
    st.plotly_chart(fig_times, use_container_width=True)

# 3. Tabela de Dados Brutos
with st.expander("Ver dados detalhados"):
    st.dataframe(df, use_container_width=True)

st.sidebar.info("Dashboard atualizado com base nos dados do sistema de chamados.")
