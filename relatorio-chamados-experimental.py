import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Configurações de layout
st.set_page_config(page_title="SINFO - Relatórios Trimestrais", layout="wide", initial_sidebar_state="collapsed" # Isso aqui faz a mágica! )

st.title("📊 Painel de Controle de Chamados - CEFET/RJ")
st.markdown("---")

# 1. Lista os arquivos e ordena (essencial para trimestres)
arquivos_csv = sorted([f for f in os.listdir('.') if f.endswith('.csv')])

st.sidebar.header("📁 Seleção do Período")

if arquivos_csv:
    # O usuário escolhe o arquivo (ex: 2026-Q1-Jan_a_Mar.csv)
    arquivo_selecionado = st.sidebar.selectbox("Escolha o Trimestre:", arquivos_csv)
    
    # TRATAMENTO DO NOME: Transforma "2026-Q1-Jan_a_Mar.csv" em "2026 Q1 - Jan a Mar"
    nome_exibicao = arquivo_selecionado.replace('.csv', '').replace('-', ' ').replace('_', ' ')
    
    # Campo para ajuste fino (caso queira mudar algo na hora de apresentar)
    periodo_final = st.sidebar.text_input("Confirmar Período:", value=nome_exibicao)

    # Carrega os dados
    df = pd.read_csv(arquivo_selecionado)
    unidade = df['Departamento'].iloc[0] if 'Departamento' in df.columns else "SINFO"

    # --- CABEÇALHO ---
    st.header(f"📅 Período: {periodo_final}")
    st.subheader(f"📍 Unidade: {unidade}")

    # KPIs Principais
    c1, c2, c3, c4 = st.columns(4)
    abertos = df['Aberto'].iloc[0]
    encerrados = df['Encerrado'].iloc[0]
    taxa = (encerrados / abertos * 100) if abertos > 0 else 0

    c1.metric("Total de Chamados", abertos)
    c2.metric("Encerrados", encerrados, f"{taxa:.1f}% Eficiência")
    c3.metric("Atrasados", df['Atrasado'].iloc[0], delta_color="inverse")
    c4.metric("Atribuídos", df['Atribuído'].iloc[0])

    st.markdown("---")

    # Gráficos
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.write("### Distribuição por Status")
        status_cols = ['Aberto', 'Atribuído', 'Atrasado', 'Encerrado', 'Reaberto', 'Deletado']
        cols_presentes = [c for c in status_cols if c in df.columns]
        df_status = pd.DataFrame({'Status': cols_presentes, 'Qtd': df[cols_presentes].iloc[0].values})
        st.plotly_chart(px.bar(df_status, x='Status', y='Qtd', color='Status', text_auto=True), use_container_width=True)

    with col_b:
        st.write("### Médias de Tempo (SLA)")
        if 'Tempo de Serviço' in df.columns:
            df_tempo = pd.DataFrame({
                'Métrica': ['Tempo de Resposta', 'Tempo de Serviço'],
                'Minutos': [df['Tempo de Resposta'].iloc[0], df['Tempo de Serviço'].iloc[0]]
            })
            st.plotly_chart(px.bar(df_tempo, x='Minutos', y='Métrica', orientation='h', text_auto=True, color_discrete_sequence=['#2ecc71']), use_container_width=True)

    # Base de dados para conferência
    with st.expander("Ver dados brutos do CSV"):
        st.dataframe(df)

else:
    st.warning("Nenhum arquivo CSV encontrado no repositório GitHub.")

st.sidebar.markdown("---")
st.sidebar.info("Dica: Nomeie seus arquivos como '2026-Q1-Jan_a_Mar.csv' para organização automática.")
