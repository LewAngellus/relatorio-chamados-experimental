import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Configurações de layout (Sempre no topo)
st.set_page_config(
    page_title="Relatórios SINFO - CEFET/RJ",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS PARA IMPRESSÃO A4 E VISIBILIDADE DE VALORES ---
st.markdown("""
    <style>
    @media print {
        /* Esconde o que não vai pro papel */
        [data-testid="stSidebar"], .stButton, header, [data-testid="stToolbar"], .stDetails, .stCheckbox {
            display: none !important;
        }
        
        /* Empilha as colunas para o gráfico ocupar a largura total do A4 */
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
            margin-bottom: 30px !important;
        }

        .main .block-container {
            max-width: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        /* Melhora a nitidez dos textos na impressão */
        h1, h2, h3, h4, p { color: black !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Interface e Dados
st.title("📊 Gestão de Chamados - CEFET/RJ")
st.markdown("---")

arquivos_csv = sorted([f for f in os.listdir('.') if f.endswith('.csv')], reverse=True)

st.sidebar.header("📁 Configurações do PDF")

if arquivos_csv:
    arquivo_selecionado = st.sidebar.selectbox("1. Escolha o arquivo:", arquivos_csv)
    
    # Campo para a data no formato que você pediu (03/abr/2025 a 03/jul/2025)
    periodo_input = st.sidebar.text_input("2. Período do Relatório:", value="03/abr/2025 a 03/jul/2025")

    df = pd.read_csv(arquivo_selecionado)
    unidade = df['Departamento'].iloc[0] if 'Departamento' in df.columns else "SINFO"

    # --- CABEÇALHO DO RELATÓRIO ---
    st.markdown(f"""
        <div style='text-align: center;'>
            <h2 style='margin-bottom: 0;'>Relatório de Atividades TI</h2>
            <h4 style='margin-top: 0; color: #333;'>CEFET/RJ - {unidade}</h4>
            <p style='font-size: 1.2rem;'><b>Período:</b> {periodo_input}</p>
        </div>
    """, unsafe_allow_html=True)

    # 3. KPIs
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    abertos = df['Aberto'].iloc[0]
    encerrados = df['Encerrado'].iloc[0]
    taxa = (encerrados / abertos * 100) if abertos > 0 else 0

    c1.metric("Abertos", abertos)
    c2.metric("Encerrados", encerrados, f"{taxa:.1f}%")
    c3.metric("Atrasados", df['Atrasado'].iloc[0], delta_color="inverse")
    c4.metric("Atribuídos", df['Atribuído'].iloc[0])

    st.markdown("---")

    # 4. Gráficos (Ambos Verticais para o PDF)
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.write("#### Distribuição de Status")
        status_cols = ['Aberto', 'Atribuído', 'Atrasado', 'Encerrado']
        df_status = pd.DataFrame({'Status': status_cols, 'Qtd': df[status_cols].iloc[0].values})
        
        fig1 = px.bar(df_status, x='Status', y='Qtd', color='Status', text_auto=True)
        # Força os valores a ficarem no topo (fora da barra) para melhor leitura
        fig1.update_traces(textposition='outside')
        fig1.update_layout(showlegend=False, height=450, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        st.write("#### Médias de Tempo - SLA (Minutos)")
        if 'Tempo de Serviço' in df.columns:
            df_tempo = pd.DataFrame({
                'Métrica': ['Resposta', 'Serviço'],
                'Minutos': [df['Tempo de Resposta'].iloc[0], df['Tempo de Serviço'].iloc[0]]
            })
            # AGORA NA VERTICAL: x='Métrica', y='Minutos'
            fig2 = px.bar(df_tempo, x='Métrica', y='Minutos', text_auto=True, color_discrete_sequence=['#2ecc71'])
            # Força valores no topo
            fig2.update_traces(textposition='outside')
            fig2.update_layout(height=450, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig2, use_container_width=True)

    # Expander de dados (Não sai na impressão)
    with st.expander("Ver dados brutos"):
        st.dataframe(df, use_container_width=True)

else:
    st.warning("Nenhum CSV encontrado.")
