import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- REGRA DE OURO: ESTE DEVE SER O PRIMEIRO COMANDO ST ---
st.set_page_config(
    page_title="Relatórios SINFO - CEFET/RJ",
    layout="wide",
    initial_sidebar_state="collapsed" # Força a barra a começar fechada
)

# 1. Título e Estilo
st.title("📊 Painel de Chamados - CEFET/RJ")
st.markdown("---")

# 2. Busca e Ordenação dos Arquivos
arquivos_csv = sorted([f for f in os.listdir('.') if f.endswith('.csv')], reverse=True)

# 3. Lógica da Barra Lateral (Sidebar)
st.sidebar.header("📁 Configurações")

if arquivos_csv:
    arquivo_selecionado = st.sidebar.selectbox("Escolha o Relatório:", arquivos_csv)
    
    # Limpa o nome para o título (ex: tira o .csv e os traços)
    nome_exibicao = arquivo_selecionado.replace('.csv', '').replace('-', ' ').replace('_', ' ')
    periodo_final = st.sidebar.text_input("Confirmar Nome do Período:", value=nome_exibicao)

    # 4. Carregamento e Exibição
    df = pd.read_csv(arquivo_selecionado)
    unidade = df['Departamento'].iloc[0] if 'Departamento' in df.columns else "SINFO"

    st.header(f"📅 {periodo_final}")
    st.info(f"📍 Unidade: {unidade}")

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    abertos = df['Aberto'].iloc[0]
    encerrados = df['Encerrado'].iloc[0]
    taxa = (encerrados / abertos * 100) if abertos > 0 else 0

    c1.metric("Total Chamados", abertos)
    c2.metric("Encerrados", encerrados, f"{taxa:.1f}% Eficiência")
    c3.metric("Atrasados", df['Atrasado'].iloc[0], delta_color="inverse")
    c4.metric("Atribuídos", df['Atribuído'].iloc[0])

    st.markdown("---")

    # Gráficos
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.write("### Distribuição por Status")
        status_cols = ['Aberto', 'Atribuído', 'Atrasado', 'Encerrado']
        cols_ok = [c for c in status_cols if c in df.columns]
        df_status = pd.DataFrame({'Status': cols_ok, 'Qtd': df[cols_ok].iloc[0].values})
        st.plotly_chart(px.bar(df_status, x='Status', y='Qtd', color='Status', text_auto=True), use_container_width=True)

    with col_b:
        st.write("### Médias de Tempo")
        if 'Tempo de Serviço' in df.columns:
            df_tempo = pd.DataFrame({
                'Métrica': ['Resposta', 'Serviço'],
                'Valor': [df['Tempo de Resposta'].iloc[0], df['Tempo de Serviço'].iloc[0]]
            })
            st.plotly_chart(px.bar(df_tempo, x='Valor', y='Métrica', orientation='h', text_auto=True), color_discrete_sequence=['#2ecc71'], use_container_width=True)

    # Dados Brutos
    with st.expander("Ver base de dados"):
        st.dataframe(df)

else:
    st.warning("Nenhum arquivo CSV encontrado no GitHub.")

st.sidebar.markdown("---")
st.sidebar.info("Clique na setinha ( > ) no topo esquerdo para abrir este menu.")
