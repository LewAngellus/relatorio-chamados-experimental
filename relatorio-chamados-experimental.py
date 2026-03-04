import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Configurações de layout
st.set_page_config(
    page_title="Relatórios SINFO - CEFET/RJ",
    layout="wide",
    initial_sidebar_state="collapsed" # Começa fechada, mas agora a seta aparece!
)

# --- CSS: ESCONDE O "LA" E LIMPA O PDF, MAS MANTÉM OS MENUS NA TELA ---
st.markdown("""
    <style>
    /* Força fundo branco */
    .stApp { background-color: white !important; color: black !important; }
    
    /* Esconde o rodapé e o widget "LA" (StatusWidget) sempre */
    footer, [data-testid="stStatusWidget"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* Ajustes para a tela (Browser) */
    @media screen {
        /* Mantém o header visível para você acessar Settings e Sidebar */
        header { 
            background-color: rgba(255, 255, 255, 0.8) !important;
        }
    }

    /* AJUSTES EXCLUSIVOS PARA IMPRESSÃO (PDF/A4) */
    @media print {
        /* Aqui sim, escondemos tudo para o Diretor não ver menus */
        header, [data-testid="stSidebar"], .stButton, .stCheckbox, .stExpander, [data-testid="stToolbar"] {
            display: none !important;
        }
        /* Mantém o layout lado a lado no A4 */
        [data-testid="column"] {
            width: 48% !important;
            flex: 1 1 48% !important;
            min-width: 48% !important;
        }
        .main .block-container {
            max-width: 100% !important;
            padding: 5mm !important;
            margin: 0 !important;
        }
        h1, h2, h3, h4, span { color: black !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Título do Painel
st.title("📊 Painel de Controle de Chamados - CEFET/RJ")
st.markdown("---")

# 3. Busca de Arquivos (Melhorada para pegar tudo)
arquivos_csv = sorted([f for f in os.listdir('.') if f.lower().endswith('.csv')], reverse=True)

if arquivos_csv:
    # Sidebar: Agora você verá a setinha ( > ) no topo esquerdo para abrir isto!
    arquivo_selecionado = st.sidebar.selectbox("Escolha o Trimestre:", arquivos_csv)
    periodo_input = st.sidebar.text_input("Data p/ Relatório:", value="03/04/2025 a 03/07/2025")
    
    try:
        df = pd.read_csv(arquivo_selecionado)
        unidade = df['Departamento'].iloc[0] if 'Departamento' in df.columns else "SINFO - Maria da Graça"

        # --- CABEÇALHO CLÁSSICO (O QUE VOCÊ GOSTA) ---
        st.markdown(f"### 📅 Período: {periodo_input}")
        st.markdown(f"### 📍 Unidade: {unidade}")

        # KPIs (Cálculo corrigido para evitar o SyntaxError)
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        
        abertos = int(df['Aberto'].iloc[0])
        encerrados = int(df['Encerrado'].iloc[0])
        
        # Correção da linha 70 que deu erro: taxa_calc agora está completa
        taxa_calc = (encerrados / abertos *
