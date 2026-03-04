import streamlit as st
import pandas as pd
import plotly.express as px
import os
import re

# 1. Configurações de layout (Sempre no topo)
st.set_page_config(
    page_title="Relatórios SINFO - CEFET/RJ",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS: LIBERA MENUS, LIMPA O PDF E ESCONDE O "LA" ---
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

# Função para extrair e formatar a data do nome do arquivo
def extrair_data_arquivo(nome_arquivo):
    # Procura datas no formato YYYY-MM-DD no nome do arquivo
    datas = re.findall(r'(\d{4})-(\d{2})-(\d{2})', nome_arquivo)
    if len(datas) >= 2:
        # Converte de YYYY-MM-DD para DD/MM/YYYY
        d1 = f"{datas[0][2]}/{datas[0][1]}/{datas[0][0]}"
        d2 = f"{datas[1][2]}/{datas[1][1]}/{datas[1][0]}"
        return f"{d1} a {d2}"
    return "Data não identificada"

# 2. Título Principal
st.title("📊 Painel de Controle de Chamados - CEFET/RJ")
st.markdown("---")

# 3. Busca de Arquivos CSV
arquivos_csv = sorted([f for f in os.listdir('.') if f.lower().endswith('.csv')], reverse=True)

if arquivos_csv:
    arquivo_selecionado = st.sidebar.selectbox("Escolha o Trimestre:", arquivos_csv)
    
    # LÓGICA AUTOMÁTICA: Extrai a data do nome do arquivo selecionado
    data_automatica = extrair_data_arquivo(arquivo_selecionado)
    periodo_input = st.sidebar.text_input("Período do Relatório:", value=data_automatica)
    
    try:
        df = pd.read_csv(arquivo_selecionado)
        unidade = df['Departamento'].iloc[0] if 'Departamento' in df.columns else "SINFO - Maria da Graça"

        # --- CABEÇALHO CLÁSSICO COM PINO E CALENDÁRIO ---
        st.markdown(f"### 📅 Período: {periodo_input}")
        st.markdown(f"### 📍 Unidade: {unidade}")

        # KPIs (Métricas corrigidas - Sem erro de sintaxe)
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        abertos = int(df['Aberto'].iloc[0])
        encerrados = int(df['Encerrado'].iloc[0])
        
        # CORREÇÃO DA LINHA 83 (image_394b77): Cálculo fechado corretamente
        taxa_calc = (encerrados / abertos * 100) if abertos > 0 else 0

        c1.metric("Total", abertos)
        c2.metric("Concluídos", encerrados, f"{taxa_calc:.1f}% Eficiência")
        c3.metric("Atrasados", int(df['Atrasado'].iloc[0]))
        c4.metric("Atribuídos", int(df['Atribuído'].iloc[0]))

        st.markdown("---")

        # --- GRÁFICOS HORIZONTAIS PARA A4 ---
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.write("#### 📈 Distribuição por Status")
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
        st.caption("Relatório Oficial SINFO/CEFET-RJ | Documento Gerado Automaticamente")

    except Exception as e:
        st.error(f"Erro ao processar dados: {e}")
else:
    st.warning("⚠️ Nenhum arquivo CSV encontrado.")
