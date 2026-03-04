import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Configurações de layout
st.set_page_config(
    page_title="Relatórios SINFO - CEFET/RJ",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS AVANÇADO: ADAPTAÇÃO AUTOMÁTICA PARA A4 ---
st.markdown("""
    <style>
    /* Estilo para a tela do computador/celular */
    @media screen {
        .main .block-container { padding-top: 2rem; }
    }

    /* Estilo EXCLUSIVO para Impressão (PDF/A4) */
    @media print {
        /* Esconde menus e barras laterais */
        [data-testid="stSidebar"], .stButton, header, [data-testid="stToolbar"], .stDetails, .stCheckbox {
            display: none !important;
        }
        
        /* Força os gráficos e colunas a ocuparem 100% da largura (Empilhamento) */
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
            margin-bottom: 20px !important;
        }

        /* Ajusta o container principal para a folha A4 */
        .main .block-container {
            max-width: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        
        /* Evita que gráficos sejam cortados entre duas páginas */
        .stPlotlyChart {
            page-break-inside: avoid !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Título e Seleção de Arquivos
st.title("📊 Gestão de Chamados - CEFET/RJ")
st.markdown("---")

arquivos_csv = sorted([f for f in os.listdir('.') if f.endswith('.csv')], reverse=True)

st.sidebar.header("📁 Opções do PDF")

if arquivos_csv:
    arquivo_selecionado = st.sidebar.selectbox("1. Escolha o arquivo:", arquivos_csv)
    periodo_input = st.sidebar.text_input("2. Período do Relatório:", value="Janeiro a Março / 2026")

    df = pd.read_csv(arquivo_selecionado)
    unidade = df['Departamento'].iloc[0] if 'Departamento' in df.columns else "SINFO"

    # --- CABEÇALHO DO RELATÓRIO ---
    st.markdown(f"""
        <div style='text-align: center;'>
            <h2 style='margin-bottom: 0;'>Relatório Trimestral de Atividades - TI</h2>
            <h4 style='margin-top: 0; color: #333;'>{unidade}</h4>
            <p><b>Período:</b> {periodo_input}</p>
        </div>
    """, unsafe_allow_html=True)

    # 3. KPIs em 4 colunas (No PDF elas vão se ajustar)
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

    # 4. Gráficos com "Empilhamento Automático" no PDF
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.write("#### Distribuição de Status")
        status_cols = ['Aberto', 'Atribuído', 'Atrasado', 'Encerrado']
        df_status = pd.DataFrame({'Status': status_cols, 'Qtd': df[status_cols].iloc[0].values})
        fig1 = px.bar(df_status, x='Status', y='Qtd', color='Status', text_auto=True)
        # Ajustamos a altura para ficar bom tanto na tela quanto no papel
        fig1.update_layout(showlegend=False, height=400, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        st.write("#### Médias de Tempo (SLA)")
        if 'Tempo de Serviço' in df.columns:
            df_tempo = pd.DataFrame({
                'Métrica': ['Resposta', 'Serviço'],
                'Minutos': [df['Tempo de Resposta'].iloc[0], df['Tempo de Serviço'].iloc[0]]
            })
            fig2 = px.bar(df_tempo, x='Minutos', y='Métrica', orientation='h', text_auto=True, color_discrete_sequence=['#2ecc71'])
            fig2.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig2, use_container_width=True)

    # Rodapé apenas para o PDF
    st.markdown("""
        <div style='position: fixed; bottom: 0; width: 100%; text-align: right; font-size: 10px; color: gray;' class='only-print'>
            Gerado automaticamente pelo Sistema de Relatórios SINFO/CEFET-RJ
        </div>
    """, unsafe_allow_html=True)

    # Expander (Não sai na impressão)
    with st.expander("Ver dados detalhados"):
        st.dataframe(df, use_container_width=True)

else:
    st.warning("Nenhum CSV encontrado.")
