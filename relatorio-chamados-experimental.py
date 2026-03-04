import streamlit as st
import pandas as pd
import plotly.express as px
import os
import re

# 1. Configurações de layout
st.set_page_config(
    page_title="Relatórios SINFO - CEFET/RJ",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS: REMOVE SCROLL, ESCONDE "LA" E AJUSTA A4 ---
st.markdown("""
    <style>
    /* Esconde o logo "LA" e o rodapé da interface sempre */
    footer, [data-testid="stStatusWidget"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* AJUSTES PARA IMPRESSÃO (PDF/A4) */
    @media print {
        /* Remove a barra de rolagem (Scroll) no PDF */
        html, body, [data-testid="stAppViewContainer"] {
            overflow: visible !important;
            height: auto !important;
        }
        ::-webkit-scrollbar { display: none !important; }

        header, [data-testid="stSidebar"], .stButton, .stExpander, [data-testid="stToolbar"] {
            display: none !important;
        }
        
        /* Força fundo branco e layout A4 */
        .stApp { background-color: white !important; } 
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
        /* Força textos em preto */
        h1, h2, h3, h4, span, p { color: black !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# Função para interpretar o título
def interpretar_titulo(nome):
    meses_map = {
        'jan': '01', 'fev': '02', 'mar': '03', 'abr': '04', 'mai': '05', 'jun': '06',
        'jul': '07', 'ago': '08', 'set': '09', 'out': '10', 'nov': '11', 'dez': '12'
    }
    txt = re.findall(r'(\d{4})-([a-z]{3})-(\d{2})', nome.lower())
    if len(txt) >= 2:
        d1 = f"{txt[0][2]}/{meses_map.get(txt[0][1], '00')}/{txt[0][0]}"
        d2 = f"{txt[1][2]}/{meses_map.get(txt[1][1], '00')}/{txt[1][0]}"
        return f"{d1} a {d2}"
    return "Data não identificada"

# 2. TÍTULO DO CABEÇALHO (ATUALIZADO)
st.title("📊 Relatório de Controle de Chamados - CEFET/RJ")
st.markdown("---")

# 3. Busca de Arquivos
arquivos_csv = sorted([f for f in os.listdir('.') if f.lower().endswith('.csv')], reverse=True)

if arquivos_csv:
    arquivo_selecionado = st.sidebar.selectbox("Escolha o Trimestre:", arquivos_csv)
    data_auto = interpretar_titulo(arquivo_selecionado)
    periodo_input = st.sidebar.text_input("Data do Relatório:", value=data_auto)
    
    try:
        df = pd.read_csv(arquivo_selecionado)
        unidade = df['Departamento'].iloc[0] if 'Departamento' in df.columns else "SINFO - Maria da Graça"

        # --- CABEÇALHO ---
        st.markdown(f"### 📅 Período: {periodo_input}")
        st.markdown(f"### 📍 Unidade: {unidade}")

        # KPIs (Cálculo da taxa corrigido para evitar o SyntaxError)
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        abertos = int(df['Aberto'].iloc[0])
        encerrados = int(df['Encerrado'].iloc[0])
        
        # CORREÇÃO DA LINHA 83: parêntese fechado e cálculo seguro
        taxa_calc = (encerrados / abertos * 100) if abertos > 0 else 0

        c1.metric("Total", abertos)
        c2.metric("Concluídos", encerrados, f"{taxa_calc:.1f}% Eficiência")
        c3.metric("Atrasados", int(df['Atrasado'].iloc[0]))
        c4.metric("Atribuídos", int(df['Atribuído'].iloc[0]))

        st.markdown("---")

        # --- GRÁFICOS HORIZONTAIS ---
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

        # RODAPÉ (ATUALIZADO)
        st.markdown("---")
        st.caption("Relatório Oficial SINFO/CEFET-RJ | Documento Gerado Automaticamente.")

    except Exception as e:
        st.error(f"Erro: {e}")
else:
    st.warning("Nenhum CSV encontrado.")
