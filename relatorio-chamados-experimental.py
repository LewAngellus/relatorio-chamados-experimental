import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Configurações de layout (Sempre a primeira linha)
st.set_page_config(
    page_title="SINFO - Relatório CEFET/RJ",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS AVANÇADO PARA FORMATO A4 ---
st.markdown("""
    <style>
    /* Estilo para a tela do computador */
    @media screen {
        .main .block-container { padding-top: 2rem; }
        .print-only { display: none; }
    }

    /* Estilo EXCLUSIVO para Impressão PDF (A4) */
    @media print {
        /* Esconde menus, botões e barras laterais */
        [data-testid="stSidebar"], .stButton, header, [data-testid="stToolbar"], .stDetails, .stCheckbox, .stExpander {
            display: none !important;
        }
        
        /* Força os gráficos a ocuparem 100% da largura da folha A4 */
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
            margin-bottom: 20px !important;
        }

        .main .block-container {
            max-width: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        
        /* Evita cortes no meio dos gráficos */
        .stPlotlyChart { page-break-inside: avoid !important; }
        h1, h2, h3, h4, p { color: black !important; text-align: center !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Título Clássico
st.title("📊 Painel de Controle de Chamados - CEFET/RJ")
st.markdown("---")

# 3. Busca de Arquivos CSV
arquivos_csv = sorted([f for f in os.listdir('.') if f.endswith('.csv')], reverse=True)

st.sidebar.header("📁 Gerenciador de Dados")

if arquivos_csv:
    arquivo_selecionado = st.sidebar.selectbox("Selecione o relatório:", arquivos_csv)
    periodo_custom = st.sidebar.text_input("Confirmar Período:", value="03 abr 2025 a 03 jul 2025")

    try:
        df = pd.read_csv(arquivo_selecionado)
        unidade = df['Departamento'].iloc[0] if 'Departamento' in df.columns else "SINFO - Maria da Graça"

        # --- CABEÇALHO ESTILO SINFO ---
        st.markdown(f"### 📅 Período: {periodo_custom}")
        st.markdown(f"### 📍 Unidade: {unidade}")

        # KPIs (Indicadores)
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        
        abertos = int(df['Aberto'].iloc[0])
        encerrados = int(df['Encerrado'].iloc[0])
        taxa = (encerrados / abertos * 100) if abertos > 0 else 0

        c1.metric("Total de Chamados", abertos)
        c2.metric("Encerrados", encerrados, f"{taxa:.1f}% Eficiência")
        c3.metric("Atrasados", int(df['Atrasado'].iloc[0]), delta_color="inverse")
        c4.metric("Atribuídos", int(df['Atribuído'].iloc[0]))

        st.markdown("---")

        # --- GRÁFICOS ADAPTADOS (EM VERTICAL PARA O A4) ---
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.write("#### Distribuição por Status")
            status_cols = ['Aberto', 'Atribuído', 'Atrasado', 'Encerrado']
            df_status = pd.DataFrame({'Status': status_cols, 'Qtd': df[status_cols].iloc[0].values})
            fig1 = px.bar(df_status, x='Status', y='Qtd', color='Status', text_auto=True)
            fig1.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig1, use_container_width=True)

        with col_b:
            st.write("#### Médias de Tempo - SLA (Minutos)")
            if 'Tempo de Serviço' in df.columns:
                df_tempo = pd.DataFrame({
                    'Métrica': ['Resposta', 'Serviço'],
                    'Minutos': [df['Tempo de Resposta'].iloc[0], df['Tempo de Serviço'].iloc[0]]
                })
                fig2 = px.bar(df_tempo, x='Métrica', y='Minutos', text_auto=True, color_discrete_sequence=['#2ecc71'])
                fig2.update_layout(height=400)
                st.plotly_chart(fig2, use_container_width=True)

        # 4. BOTÃO PARA GERAR RELATÓRIO PDF (Só aparece no site)
        st.markdown("---")
        if st.button("🖨️ Gerar Relatório A4 (PDF)"):
            st.markdown("<script>window.print();</script>", unsafe_allow_html=True)
            st.info("Aguarde o menu de impressão abrir. No destino, escolha 'Salvar como PDF'.")

        with st.expander("Ver base de dados bruta"):
            st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")
else:
    st.warning("Suba seus arquivos .csv para o GitHub primeiro.")
