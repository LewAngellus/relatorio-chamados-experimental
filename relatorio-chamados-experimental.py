import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Configurações de layout
st.set_page_config(
    page_title="Relatório SINFO - CEFET/RJ",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS PARA FORÇAR TUDO EM 1 PÁGINA A4 ---
st.markdown("""
    <style>
    /* Força modo claro na tela */
    .stApp { background-color: white !important; color: black !important; }
    
    @media print {
        [data-testid="stSidebar"], .stButton, header, [data-testid="stToolbar"], .stDetails, .stCheckbox, .stExpander {
            display: none !important;
        }
        /* Ajuste fino de margens para caber em 1 folha */
        .main .block-container {
            max-width: 100% !important;
            padding: 10mm !important; /* Margem padrão de documento */
            margin: 0 !important;
        }
        /* Mantém as colunas lado a lado na impressão para economizar altura */
        [data-testid="column"] {
            width: 48% !important;
            flex: 1 1 48% !important;
            min-width: 48% !important;
        }
        h1 { font-size: 20pt !important; }
        h3, h4 { font-size: 14pt !important; margin-bottom: 5px !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Título do Painel
st.title("📊 Painel de Controle de Chamados - CEFET/RJ")

# 3. Busca de Arquivos
arquivos_csv = sorted([f for f in os.listdir('.') if f.endswith('.csv')], reverse=True)

if arquivos_csv:
    arquivo_selecionado = st.sidebar.selectbox("Escolha o Trimestre:", arquivos_csv)
    periodo_input = st.sidebar.text_input("Data do Relatório:", value="03/abr/2025 a 03/jul/2025")

    try:
        df = pd.read_csv(arquivo_selecionado)
        unidade = df['Departamento'].iloc[0] if 'Departamento' in df.columns else "SINFO - Maria da Graça"

        # --- CABEÇALHO COMPACTO ---
        st.markdown(f"**📅 Período:** {periodo_input} | **📍 Unidade:** {unidade}")
        st.markdown("---")

        # KPIs (Métricas em linha única)
        c1, c2, c3, c4 = st.columns(4)
        abertos = int(df['Aberto'].iloc[0])
        encerrados = int(df['Encerrado'].iloc[0])
        taxa = (encerrados / abertos * 100) if abertos > 0 else 0

        c1.metric("Total", abertos)
        c2.metric("Concluídos", encerrados, f"{taxa:.1f}%")
        c3.metric("Atrasados", int(df['Atrasado'].iloc[0]))
        c4.metric("Atribuídos", int(df['Atribuído'].iloc[0]))

        # --- GRÁFICOS HORIZONTAIS (ESCALÁVEIS) ---
        # Aqui está a mágica: gráficos horizontais ocupam menos altura
        st.write("#### 📈 Distribuição de Status e Tempos (SLA)")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            status_cols = ['Aberto', 'Atribuído', 'Atrasado', 'Encerrado']
            df_status = pd.DataFrame({'Status': status_cols, 'Qtd': df[status_cols].iloc[0].values})
            
            # Gráfico Horizontal para Status
            fig1 = px.bar(df_status, x='Qtd', y='Status', orientation='h', text_auto=True, color='Status')
            fig1.update_layout(showlegend=False, height=250, margin=dict(l=10, r=30, t=10, b=10))
            st.plotly_chart(fig1, use_container_width=True)

        with col_b:
            if 'Tempo de Serviço' in df.columns:
                df_tempo = pd.DataFrame({
                    'Métrica': ['Resposta', 'Serviço'],
                    'Minutos': [df['Tempo de Resposta'].iloc[0], df['Tempo de Serviço'].iloc[0]]
                })
                # Gráfico Horizontal para SLA
                fig2 = px.bar(df_tempo, x='Minutos', y='Métrica', orientation='h', text_auto=True, color_discrete_sequence=['#2ecc71'])
                fig2.update_layout(height=250, margin=dict(l=10, r=30, t=10, b=10))
                st.plotly_chart(fig2, use_container_width=True)

        # Rodapé Institucional
        st.markdown("---")
        st.caption("Relatório gerado automaticamente pelo Sistema de Gestão SINFO/CEFET-RJ")

    except Exception as e:
        st.error(f"Erro: {e}")

else:
    st.warning("Nenhum arquivo encontrado.")
