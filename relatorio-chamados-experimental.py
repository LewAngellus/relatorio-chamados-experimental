import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Configurações de layout (Primeira linha sempre)
st.set_page_config(
    page_title="Relatórios SINFO - CEFET/RJ",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS PARA RESPONSIVIDADE E IMPRESSÃO A4 ---
st.markdown("""
    <style>
    /* Estilo para a tela (Celular e PC) */
    @media screen {
        .main .block-container { padding-top: 2rem; }
    }

    /* Estilo para Impressão (PDF/A4) */
    @media print {
        [data-testid="stSidebar"], .stButton, header, [data-testid="stToolbar"], .stDetails {
            display: none !important;
        }
        /* Força os gráficos a ocuparem a largura total da folha A4 */
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
            margin-bottom: 50px !important;
        }
        .main .block-container {
            max-width: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        .stPlotlyChart { page-break-inside: avoid !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Título do Dashboard
st.title("📊 Painel de Controle de Chamados - CEFET/RJ")
st.markdown("---")

# 3. Gerenciamento de Arquivos
arquivos_csv = sorted([f for f in os.listdir('.') if f.endswith('.csv')])

st.sidebar.header("📁 Seleção do Período")

if arquivos_csv:
    arquivo_selecionado = st.sidebar.selectbox("Escolha o Trimestre:", arquivos_csv)
    
    # Campo para a data exatamente como você pediu
    periodo_final = st.sidebar.text_input(
        "Confirmar Período:", 
        value="03 abr 2025 a 03 jul 2025"
    )

    # Carrega os dados
    df = pd.read_csv(arquivo_selecionado)
    unidade = df['Departamento'].iloc[0] if 'Departamento' in df.columns else "SINFO - Maria da Graça"

    # --- CABEÇALHO COM O ESTILO ANTIGO (PINO E CALENDÁRIO) ---
    st.markdown(f"### 📅 Período: {periodo_final}")
    st.markdown(f"### 📍 Unidade: {unidade}")

    # KPIs Principais
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    abertos = df['Aberto'].iloc[0]
    encerrados = df['Encerrado'].iloc[0]
    taxa = (encerrados / abertos * 100) if abertos > 0 else 0

    c1.metric("Total de Chamados", abertos)
    c2.metric("Encerrados", encerrados, f"{taxa:.1f}% Eficiência")
    c3.metric("Atrasados", df['Atrasado'].iloc[0], delta_color="inverse")
    c4.metric("Atribuídos", df['Atribuído'].iloc[0])

    st.markdown("---")

    # --- GRÁFICOS (VERTICAIS PARA CABER NO A4) ---
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.write("### Distribuição por Status")
        status_cols = ['Aberto', 'Atribuído', 'Atrasado', 'Encerrado', 'Reaberto', 'Deletado']
        cols_presentes = [c for c in status_cols if c in df.columns]
        df_status = pd.DataFrame({'Status': cols_presentes, 'Qtd': df[cols_presentes].iloc[0].values})
        
        fig1 = px.bar(df_status, x='Status', y='Qtd', color='Status', text_auto=True)
        fig1.update_traces(textposition='outside')
        # Altura maior para o PDF não espremer
        fig1.update_layout(showlegend=False, height=450, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        st.write("### Médias de Tempo (SLA)")
        if 'Tempo de Serviço' in df.columns:
            df_tempo = pd.DataFrame({
                'Métrica': ['Tempo de Resposta', 'Tempo de Serviço'],
                'Minutos': [df['Tempo de Resposta'].iloc[0], df['Tempo de Serviço'].iloc[0]]
            })
            # Gráfico vertical como solicitado
            fig2 = px.bar(df_tempo, x='Métrica', y='Minutos', text_auto=True, color_discrete_sequence=['#2ecc71'])
            fig2.update_traces(textposition='outside')
            fig2.update_layout(height=450, margin=dict(l=10, r=10, t=50, b=10))
            st.plotly_chart(fig2, use_container_width=True)

    # Base de dados (Aparece apenas na tela)
    with st.expander("Ver dados brutos do CSV"):
        st.dataframe(df, use_container_width=True)

else:
    st.warning("Nenhum arquivo CSV encontrado.")

st.sidebar.markdown("---")
st.sidebar.info("Para o PDF: Ative 'Gráficos de segundo plano' no menu de impressão (Ctrl+P).")
