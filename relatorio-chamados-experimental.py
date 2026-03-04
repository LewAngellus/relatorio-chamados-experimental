import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Configuração de Página (Sempre a primeira)
st.set_page_config(
    page_title="Relatório SINFO - CEFET/RJ",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS PARA FORÇAR MODO CLARO E 1 PÁGINA A4 ---
st.markdown("""
    <style>
    /* Força Fundo Branco na Tela */
    .stApp { background-color: white !important; color: black !important; }
    [data-testid="stMetricValue"] { color: black !important; font-size: 24px !important; }
    
    @media print {
        /* Esconde tudo o que não é relatório */
        [data-testid="stSidebar"], .stButton, header, [data-testid="stToolbar"], .stDetails, .stCheckbox, .stExpander {
            display: none !important;
        }
        /* Ajuste de Margens para 1 folha A4 */
        .main .block-container {
            max-width: 100% !important;
            padding: 5mm !important;
            margin: 0 !important;
        }
        /* Gráficos um embaixo do outro no PDF para ficarem grandes */
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
            margin-bottom: 10px !important;
        }
        h1, h2, h3, h4 { color: black !important; text-align: left !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Título do Dashboard
st.title("📊 Painel de Controle de Chamados - CEFET/RJ")
st.markdown("---")

# 3. Gerenciamento de Arquivos
arquivos_csv = sorted([f for f in os.listdir('.') if f.endswith('.csv')], reverse=True)

if arquivos_csv:
    # Sidebar escondida por padrão, mas acessível para trocar o arquivo
    arquivo_selecionado = st.sidebar.selectbox("Arquivo:", arquivos_csv)
    periodo_input = st.sidebar.text_input("Data p/ Relatório:", value="03 abr 2025 a 03 jul 2025")
    
    try:
        df = pd.read_csv(arquivo_selecionado)
        unidade = df['Departamento'].iloc[0] if 'Departamento' in df.columns else "SINFO - Maria da Graça"

        # --- CABEÇALHO CLÁSSICO (O QUE VOCÊ GOSTOU) ---
        st.markdown(f"### 📅 Período: {periodo_input}")
        st.markdown(f"### 📍 Unidade: {unidade}")

        # KPIs Compactos em uma linha
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        abertos = int(df['Aberto'].iloc[0])
        encerrados = int(df['Encerrado'].iloc[0])
        # Correção do erro de sintaxe e divisão por zero
        taxa_calculada = (encerrados / abertos * 100) if abertos > 0 else 0

        c1.metric("Total", abertos)
        c2.metric("Concluídos", encerrados, f"{taxa_calculada:.1f}% Eficiência")
        c3.metric("Atrasados", int(df['Atrasado'].iloc[0]))
        c4.metric("Atribuídos", int(df['Atribuído'].iloc[0]))

        st.markdown("---")

        # --- GRÁFICOS ESCALÁVEIS (PARA CABER EM 1 PÁGINA) ---
        # No PDF, eles aparecerão um embaixo do outro, ocupando a largura total
        
        # Gráfico 1: Status
        st.write("#### 📈 Distribuição por Status")
        status_cols = ['Aberto', 'Atribuído', 'Atrasado', 'Encerrado']
        df_status = pd.DataFrame({'Status': status_cols, 'Qtd': df[status_cols].iloc[0].values})
        fig1 = px.bar(df_status, x='Qtd', y='Status', orientation='h', text_auto=True, color='Status')
        fig1.update_layout(showlegend=False, height=280, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig1, use_container_width=True)

        # Gráfico 2: SLA
        st.write("#### ⏱️ Médias de Tempo (SLA)")
        if 'Tempo de Serviço' in df.columns:
            df_tempo = pd.DataFrame({
                'Métrica': ['Resposta', 'Serviço'],
                'Minutos': [df['Tempo de Resposta'].iloc[0], df['Tempo de Serviço'].iloc[0]]
            })
            fig2 = px.bar(df_tempo, x='Minutos', y='Métrica', orientation='h', text_auto=True, color_discrete_sequence=['#2ecc71'])
            fig2.update_layout(height=200, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig2, use_container_width=True)

        # Rodapé Discreto
        st.markdown("---")
        st.caption("Relatório Oficial SINFO/CEFET-RJ | Documento Gerado Automaticamente")

    except Exception as e:
        st.error(f"Erro ao processar dados: {e}")

else:
    st.warning("⚠️ Nenhum arquivo .csv encontrado no repositório.")
