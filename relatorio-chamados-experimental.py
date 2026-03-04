import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Configurações de layout
st.set_page_config(
    page_title="Relatórios SINFO - CEFET/RJ",
    layout="wide",
    initial_sidebar_state="collapsed" # Isso garante que comece escondida
)

# --- BLOCO DE IMPRESSÃO (A4) ---
# Este código garante que ao imprimir (Ctrl+P), a barra lateral e menus sumam
st.markdown("""
    <style>
    @media print {
        [data-testid="stSidebar"], .stButton, header, [data-testid="stToolbar"], .stDetails {
            display: none !important;
        }
        .main .block-container {
            padding: 0 !important;
            margin: 0 !important;
            width: 100% !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Painel de Controle de Chamados - CEFET/RJ")
st.markdown("---")

# 1. Lista os arquivos e ordena (essencial para trimestres)
arquivos_csv = sorted([f for f in os.listdir('.') if f.endswith('.csv')])

st.sidebar.header("📁 Seleção do Período")

if arquivos_csv:
    # O usuário escolhe o arquivo (ex: 2026-Q1-Jan_a_Mar.csv)
    arquivo_selecionado = st.sidebar.selectbox("Escolha o Trimestre:", arquivos_csv)
    
    # TRATAMENTO DO NOME: Transforma "2026-Q1-Jan_a_Mar.csv" em "2026 Q1 - Jan a Mar"
    nome_exibicao = arquivo_selecionado.replace('.csv', '').replace('-', ' ').replace('_', ' ')
    
    # Campo para ajuste fino (caso queira mudar algo na hora de apresentar)
    periodo_final = st.sidebar.text_input("Confirmar Período:", value=nome_exibicao)

    # Carrega os dados
    df = pd.read_csv(arquivo_selecionado)
    unidade = df['Departamento'].iloc[0] if 'Departamento' in df.columns else "SINFO"

    # --- CABEÇALHO FORMAL (Aparece no topo do relatório) ---
    st.markdown(f"""
        <div style='text-align: center;'>
            <h2 style='margin-bottom: 0;'>CEFET/RJ - Relatório de Atividades TI</h2>
            <h4 style='margin-top: 0;'>Unidade: {unidade}</h4>
        </div>
    """, unsafe_allow_html=True)

    st.header(f"📅 Período: {periodo_final}")
    
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

    # Gráficos
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.write("### Distribuição por Status")
        status_cols = ['Aberto', 'Atribuído', 'Atrasado', 'Encerrado', 'Reaberto', 'Deletado']
        cols_presentes = [c for c in status_cols if c in df.columns]
        df_status = pd.DataFrame({'Status': cols_presentes, 'Qtd': df[cols_presentes].iloc[0].values})
        st.plotly_chart(px.bar(df_status, x='Status', y='Qtd', color='Status', text_auto=True), use_container_width=True)

    with col_b:
        st.write("### Médias de Tempo (SLA)")
        if 'Tempo de Serviço' in df.columns:
            df_tempo = pd.DataFrame({
                'Métrica': ['Tempo de Resposta', 'Tempo de Serviço'],
                'Minutos': [df['Tempo de Resposta'].iloc[0], df['Tempo de Serviço'].iloc[0]]
            })
            st.plotly_chart(px.bar(df_tempo, x='Minutos', y='Métrica', orientation='h', text_auto=True, color_discrete_sequence=['#2ecc71']), use_container_width=True)

    # --- CAMPO DE ASSINATURAS PARA O DIRETOR ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div style='display: flex; justify-content: space-around; margin-top: 50px;'>
            <div style='border-top: 1px solid black; width: 250px; text-align: center;'>
                <small>Responsável Técnico SINFO</small>
            </div>
            <div style='border-top: 1px solid black; width: 250px; text-align: center;'>
                <small>Direção Geral CEFET/RJ</small>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Base de dados para conferência (Ela não sai bem na impressão, então fica no expander)
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("Ver dados brutos do CSV"):
        st.dataframe(df)

else:
    st.warning("Nenhum arquivo CSV encontrado no repositório GitHub.")

st.sidebar.markdown("---")
st.sidebar.info("Dica: Para gerar o PDF, use Ctrl+P e selecione 'Salvar como PDF'. Certifique-se de que a barra lateral esteja fechada.")
