import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Configurações de layout (Inicia com barra lateral recolhida)
st.set_page_config(
    page_title="Relatórios SINFO - CEFET/RJ",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS PARA FORMATAÇÃO DE IMPRESSÃO A4 ---
st.markdown("""
    <style>
    @media print {
        /* Esconde elementos do Streamlit na impressão */
        [data-testid="stSidebar"], .stButton, header, [data-testid="stToolbar"], .stDetails {
            display: none !important;
        }
        /* Ajusta margens da folha */
        .main .block-container {
            padding: 0 !important;
            margin: 0 !important;
            width: 100% !important;
        }
        /* Garante fundo branco e texto preto para economizar tinta */
        body, .main {
            background-color: white !important;
            color: black !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Título do Dashboard (Não aparece na impressão se ativado o modo formal)
st.title("📊 Painel de Controle de Chamados - CEFET/RJ")
st.markdown("---")

# 3. Gerenciamento de Arquivos
arquivos_csv = sorted([f for f in os.listdir('.') if f.endswith('.csv')])

st.sidebar.header("📁 Opções de Relatório")

if arquivos_csv:
    # Seleção do arquivo (Ex: 2026-Q1-Jan_a_Mar.csv)
    arquivo_selecionado = st.sidebar.selectbox("Escolha o Período/Trimestre:", arquivos_csv)
    
    # Modo de Impressão
    modo_impressao = st.sidebar.checkbox("Ativar Modo de Impressão (A4)")
    
    # Tratamento do nome para exibição
    nome_exibicao = arquivo_selecionado.replace('.csv', '').replace('-', ' ').replace('_', ' ')
    periodo_final = st.sidebar.text_input("Confirmar Período:", value=nome_exibicao)

    # Carregamento dos dados
    df = pd.read_csv(arquivo_selecionado)
    unidade = df['Departamento'].iloc[0] if 'Departamento' in df.columns else "SINFO"

    # --- CABEÇALHO DO RELATÓRIO (Versão Formal para Impressão) ---
    st.markdown(f"<h2 style='text-align: center;'>CEFET/RJ - Relatório de Gestão de TI</h2>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center;'>Unidade: {unidade}</h4>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'><b>Período:</b> {periodo_final}</p>", unsafe_allow_html=True)
    st.markdown("---")

    # --- KPIs (Indicadores) ---
    c1, c2, c3, c4 = st.columns(4)
    abertos = df['Aberto'].iloc[0]
    encerrados = df['Encerrado'].iloc[0]
    taxa =
