import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Configurações de layout (Sempre a primeira linha)
st.set_page_config(
    page_title="Relatórios SINFO - CEFET/RJ",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS: MÁGICA PARA PDF A4 E MOBILE ---
st.markdown("""
    <style>
    /* ESTILO PARA IMPRESSÃO (PDF/A4) */
    @media print {
        /* Esconde menus e barras laterais */
        [data-testid="stSidebar"], .stButton, header, [data-testid="stToolbar"], .stDetails, .stCheckbox {
            display: none !important;
        }
        /* FORÇA EMPILHAMENTO: Faz os gráficos ocuparem a largura total da folha A4 */
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
        /* Evita que gráficos sejam cortados ao meio na troca de página */
        .stPlotlyChart { page-break-inside: avoid !important; }
        h1, h2, h3, h4, p { color: black !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Título do Painel
st.title("📊 Painel de Controle de Chamados - CEFET/RJ")
st.markdown("---")

# 3. Busca de Arquivos
arquivos_csv = sorted([f for f in os.listdir('.') if f.endswith('.csv')], reverse=True)

st.sidebar.header("📁 Opções do Relatório")

if arquivos_csv:
    arquivo_selecionado = st.sidebar.selectbox("Escolha o Trimestre:", arquivos_csv)
    
    # Campo para a data nominal (03/abr/2025 a 03/jul/2025)
    nome_peridodo = arquivo_selecionado.replace('.csv', '').replace('-', ' ').replace('_', ' ')
    periodo_input = st.sidebar.text_input("Confirmar Período:", value=nome_peridodo)

    try:
        df = pd.read_csv(arquivo_selecionado)
        unidade = df['Departamento'].iloc[0] if 'Departamento' in df.columns else "SINFO - Maria da Graça"

        # --- CABEÇALHO CLÁSSICO COM PINO E CALENDÁRIO ---
        st.markdown(f"### 📅 Período: {periodo_input}")
        st.markdown(f"### 📍 Unidade: {unidade}")

        # KPIs (Métricas)
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

        # --- GRÁFICOS (VERTICAIS E GRANDES PARA O PDF) ---
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.write("### Distribuição por Status")
            status_cols = ['Aberto', 'Atribuído', 'Atrasado', 'Encerrado', 'Reaberto', 'Deletado']
            cols_ok = [c for c in status_cols if c in df.columns]
            df_status = pd.DataFrame({'Status': cols_ok, 'Qtd': df[cols_ok].iloc[0].values})
            
            fig1 = px.bar(df_status, x='Status', y='Qtd', color='Status', text_auto=True)
            fig1.update_traces(textposition='outside') # Coloca o número fora da barra
            # Altura diminuída de 450 para 350
            fig1.update_layout(showlegend=False, height=350, margin=dict(l=10, r=10, t=50, b=10))
            st.plotly_chart(fig1, use_container_width=True)

        with col_b:
            st.write("### Médias de Tempo - SLA (Minutos)")
            if 'Tempo de Serviço' in df.columns:
                df_tempo = pd.DataFrame({
                    'Métrica': ['Resposta', 'Serviço'],
                    'Minutos': [df['Tempo de Resposta'].iloc[0], df['Tempo de Serviço'].iloc[0]]
                })
                # Gráfico Vertical como solicitado
                fig2 = px.bar(df_tempo, x='Métrica', y='Minutos', text_auto=True, color_discrete_sequence=['#2ecc71'])
                fig2.update_traces(textposition='outside')
                # Altura diminuída de 450 para 350
                fig2.update_layout(height=350, margin=dict(l=10, r=10, t=50, b=10))
                st.plotly_chart(fig2, use_container_width=True)

        # Base de dados (Apenas consulta digital)
        with st.expander("Ver dados brutos do CSV"):
            st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Erro ao processar o arquivo: {e}")

else:
    st.warning("Nenhum arquivo CSV encontrado no GitHub.")

st.sidebar.markdown("---")
st.sidebar.info("Para o PDF: Pressione Ctrl+P e marque 'Gráficos de segundo plano'.")
