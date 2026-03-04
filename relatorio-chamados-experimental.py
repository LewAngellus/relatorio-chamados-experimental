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

# --- CSS PARA FORMATAÇÃO DE IMPRESSÃO (PDF/A4) ---
st.markdown("""
    <style>
    @media print {
        /* Esconde elementos do site que não devem sair no PDF */
        [data-testid="stSidebar"], .stButton, header, [data-testid="stToolbar"], .stDetails, .stCheckbox {
            display: none !important;
        }
        /* Ajusta o conteúdo para o centro da página A4 */
        .main .block-container {
            max-width: 800px !important;
            padding-top: 20px !important;
            margin: 0 auto !important;
        }
        /* Remove sombras e fundos que gastam tinta */
        .main {
            background-color: white !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Título do Relatório
st.title("📊 Relatório de Chamados - CEFET/RJ")
st.markdown("---")

# 3. Lista e Ordena os arquivos CSV
arquivos_csv = sorted([f for f in os.listdir('.') if f.endswith('.csv')])

st.sidebar.header("📁 Seleção do Período")

if arquivos_csv:
    arquivo_selecionado = st.sidebar.selectbox("Escolha o Trimestre:", arquivos_csv)
    
    # Tratamento do nome para exibição
    nome_exibicao = arquivo_selecionado.replace('.csv', '').replace('-', ' ').replace('_', ' ')
    periodo_final = st.sidebar.text_input("Confirmar Período:", value=nome_exibicao)

    # Carrega os dados
    df = pd.read_csv(arquivo_selecionado)
    unidade = df['Departamento'].iloc[0] if 'Departamento' in df.columns else "SINFO"

    # --- CORPO DO RELATÓRIO ---
    st.header(f"📅 Período: {periodo_final}")
    st.subheader(f"📍 Unidade: {unidade}")

    # KPIs Principais
    c1, c2, c3, c4 = st.columns(4)
    abertos = df['Aberto'].iloc[0]
    encerrados = df['Encerrado'].iloc[0]
    taxa = (encerrados / abertos * 100) if abertos > 0 else 0

    c1.metric("Total de Chamados", abertos)
    c2.metric("Encerrados", encerrados, f"{taxa:.1f}% Eficiência")
    c3.metric("Atrasados", df['Atrasado'].iloc[0], delta_color="inverse")
    c4.metric("Atribuídos", df['Atribuído'].iloc[0])

    st.markdown("---")

    # Gráficos (Ajustados para caber no A4)
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.write("### Status dos Chamados")
        status_cols = ['Aberto', 'Atribuído', 'Atrasado', 'Encerrado', 'Reaberto', 'Deletado']
        cols_presentes = [c for c in status_cols if c in df.columns]
        df_status = pd.DataFrame({'Status': cols_presentes, 'Qtd': df[cols_presentes].iloc[0].values})
        fig1 = px.bar(df_status, x='Status', y='Qtd', color='Status', text_auto=True)
        fig1.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        st.write("### Médias de Tempo (SLA)")
        if 'Tempo de Serviço' in df.columns:
            df_tempo = pd.DataFrame({
                'Métrica': ['Resposta', 'Serviço'],
                'Minutos': [df['Tempo de Resposta'].iloc[0], df['Tempo de Serviço'].iloc[0]]
            })
            fig2 = px.bar(df_tempo, x='Minutos', y='Métrica', orientation='v', text_auto=True, color_discrete_sequence=['#2ecc71'])
            fig2.update_layout(height=350)
            st.plotly_chart(fig2, use_container_width=True)

    # Base de dados (Aparece apenas no site)
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("Ver dados brutos do CSV"):
        st.dataframe(df)

else:
    st.warning("Nenhum arquivo CSV encontrado.")

st.sidebar.markdown("---")
st.sidebar.info("Para gerar o PDF: Aperte Ctrl + P no teclado e selecione 'Salvar como PDF'.")
