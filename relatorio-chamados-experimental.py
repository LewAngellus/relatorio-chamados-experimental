import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Configurações de layout (Sempre no topo)
st.set_page_config(
    page_title="Relatórios SINFO - CEFET/RJ",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS PARA IMPRESSÃO E RESPONSIVIDADE ---
st.markdown("""
    <style>
    @media print {
        [data-testid="stSidebar"], .stButton, header, [data-testid="stToolbar"], .stDetails, .stCheckbox, .stExpander {
            display: none !important;
        }
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
            margin-bottom: 30px !important;
        }
        .main .block-container {
            max-width: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        h1, h2, h3, h4, p, span { color: black !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Título do Dashboard
st.title("📊 Painel de Controle de Chamados - CEFET/RJ")
st.markdown("---")

# 3. Gerenciamento de Arquivos
arquivos_csv = sorted([f for f in os.listdir('.') if f.endswith('.csv')], reverse=True)

st.sidebar.header("📁 Opções do Relatório")

if arquivos_csv:
    arquivo_selecionado = st.sidebar.selectbox("Selecione o arquivo:", arquivos_csv)
    periodo_input = st.sidebar.text_input("Data do Relatório:", value="03/abr/2025 a 03/jul/2025")

    df = pd.read_csv(arquivo_selecionado)
    unidade = df['Departamento'].iloc[0] if 'Departamento' in df.columns else "SINFO"

    # --- CABEÇALHO COM ÍCONES ---
    st.markdown(f"### 📅 Período: {periodo_input}")
    st.markdown(f"### 📍 Unidade: {unidade}")

    # KPIs
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    abertos = df['Aberto'].iloc[0]
    encerrados = df['Encerrado'].iloc[0]
    taxa = (encerrados / abertos * 100) if abertos > 0 else 0

    c1.metric("Total Chamados", abertos)
    c2.metric("Encerrados", encerrados, f"{taxa:.1f}%")
    c3.metric("Atrasados", df['Atrasado'].iloc[0], delta_color="inverse")
    c4.metric("Atribuídos", df['Atribuído'].iloc[0])

    st.markdown("---")

    # --- GRÁFICOS ---
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.write("#### Distribuição por Status")
        status_cols = ['Aberto', 'Atribuído', 'Atrasado', 'Encerrado']
        df_status = pd.DataFrame({'Status': status_cols, 'Qtd': df[status_cols].iloc[0].values})
        fig1 = px.bar(df_status, x='Status', y='Qtd', color='Status', text_auto=True)
        fig1.update_traces(textposition='outside')
        fig1.update_layout(showlegend=False, height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        st.write("#### Médias de Tempo (Minutos)")
        if 'Tempo de Serviço' in df.columns:
            df_tempo = pd.DataFrame({
                'Métrica': ['Resposta', 'Serviço'],
                'Minutos': [df['Tempo de Resposta'].iloc[0], df['Tempo de Serviço'].iloc[0]]
            })
            fig2 = px.bar(df_tempo, x='Métrica', y='Minutos', text_auto=True, color_discrete_sequence=['#2ecc71'])
            fig2.update_traces(textposition='outside')
            fig2.update_layout(height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig2, use_container_width=True)

    with st.expander("Ver dados brutos"):
        st.dataframe(df, use_container_width=True)

else:
    st.warning("Nenhum CSV encontrado.")

st.sidebar.markdown("---")
st.sidebar.info("💡 **Dica:** Para gerar o PDF, use **Ctrl+P** e marque 'Gráficos de segundo plano'.")
