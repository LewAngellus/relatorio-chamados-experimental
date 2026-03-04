import streamlit as st
import pandas as pd
import plotly.express as px
import os
import re

# 1. Configurações de layout
st.set_page_config(
    page_title="Relatório SINFO - CEFET/RJ",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS: LIMPA O PDF, ESCONDE O "LA" E MANTÉM MENUS NA TELA ---
st.markdown("""
    <style>
    .stApp { background-color: white !important; color: black !important; }
    footer, [data-testid="stStatusWidget"] { display: none !important; }
    @media screen { header { visibility: visible !important; } }
    @media print {
        header, [data-testid="stSidebar"], .stButton, .stExpander, [data-testid="stToolbar"] {
            display: none !important;
        }
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

# FUNÇÃO PARA INTERPRETAR O TÍTULO DO ARQUIVO
def interpretar_data_pelo_titulo(nome_arquivo):
    # Dicionário para converter abreviações de meses
    meses_map = {
        'jan': '01', 'fev': '02', 'mar': '03', 'abr': '04', 'mai': '05', 'jun': '06',
        'jul': '07', 'ago': '08', 'set': '09', 'out': '10', 'nov': '11', 'dez': '12'
    }
    
    # 1. Tenta encontrar datas no formato: 2025-abr-03
    padrao_texto = re.findall(r'(\d{4})-([a-zA-Z]{3})-(\d{2})', nome_arquivo)
    if len(padrao_texto) >= 2:
        d1 = f"{padrao_texto[0][2]}/{meses_map.get(padrao_texto[0][1].lower(), '00')}/{padrao_texto[0][0]}"
        d2 = f"{padrao_texto[1][2]}/{meses_map.get(padrao_texto[1][1].lower(), '00')}/{padrao_texto[1][0]}"
        return f"{d1} a {d2}"
    
    # 2. Tenta encontrar datas no formato numérico: 2025-04-03
    padrao_num = re.findall(r'(\d{4})-(\d{2})-(\d{2})', nome_arquivo)
    if len(padrao_num) >= 2:
        d1 = f"{padrao_num[0][2]}/{padrao_num[0][1]}/{padrao_num[0][0]}"
        d2 = f"{padrao_num[1][2]}/{padrao_num[1][1]}/{padrao_num[1][0]}"
        return f"{d1} a {d2}"
    
    # Se não identificar nada, retorna o nome limpo
    return nome_arquivo.replace('.csv', '').replace('_', ' ')

# 2. Título
st.title("📊 Painel de Controle de Chamados - CEFET/RJ")
st.markdown("---")

# 3. Busca de Arquivos
arquivos_csv = sorted([f for f in os.listdir('.') if f.lower().endswith('.csv')], reverse=True)

if arquivos_csv:
    arquivo_selecionado = st.sidebar.selectbox("Escolha o Trimestre:", arquivos_csv)
    
    # INTERPRETAÇÃO AUTOMÁTICA DO TÍTULO
    data_interpretada = interpretar_data_pelo_titulo(arquivo_selecionado)
    periodo_input = st.sidebar.text_input("Data do Relatório:", value=data_interpretada)
    
    try:
        df = pd.read_csv(arquivo_selecionado)
        unidade = df['Departamento'].iloc[0] if 'Departamento' in df.columns else "SINFO"

        # --- CABEÇALHO CLÁSSICO ---
        st.markdown(f"### 📅 Período: {periodo_input}")
        st.markdown(f"### 📍 Unidade: {unidade}")

        # KPIs
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        abertos = int(df['Aberto'].iloc[0])
        encerrados = int(df['Encerrado'].iloc[0])
        # Cálculo seguro da taxa (Fechando todos os parênteses)
        taxa_calc = (encerrados / abertos * 100) if abertos > 0 else 0

        c1.metric("Total", abertos)
        c2.metric("Concluídos", encerrados, f"{taxa_calc:.1f}%")
        c3.metric("Atrasados", int(df['Atrasado'].iloc[0]))
        c4.metric("Atribuídos", int(df['Atribuído'].iloc[0]))

        st.markdown("---")

        # --- GRÁFICOS HORIZONTAIS COM NÚMEROS NA BASE ---
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.write("#### 📈 Distribuição Status")
            status_cols = ['Aberto', 'Atribuído', 'Atrasado', 'Encerrado']
            df_status = pd.DataFrame({'Status': status_cols, 'Qtd': df[status_cols].iloc[0].values})
            fig1 = px.bar(df_status, x='Qtd', y='Status', orientation='h', text_auto=True, color='Status')
            fig1.update_traces(textposition='inside', insidetextanchor='start')
            fig1.update_layout(showlegend=False, height=250, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig1, use_container_width=True)

        with col_b:
            if 'Tempo de Serviço' in df.columns:
                df_tempo = pd.DataFrame({
                    'Métrica': ['Resposta', 'Serviço'],
                    'Minutos': [df['Tempo de Resposta'].iloc[0], df['Tempo de Serviço'].iloc[0]]
                })
                fig2 = px.bar(df_tempo, x='Minutos', y='Métrica', orientation='h', text_auto=True, color_discrete_sequence=['#2ecc71'])
                fig2.update_traces(textposition='inside', insidetextanchor='start')
                fig2.update_layout(height=250, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")
        st.caption("Relatório Oficial SINFO/CEFET-RJ")

    except Exception as e:
        st.error(f"Erro ao ler os dados: {e}")
else:
    st.warning("Nenhum CSV encontrado na raiz.")
