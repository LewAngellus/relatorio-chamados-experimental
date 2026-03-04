import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Configurações de layout (Inicia recolhida)
st.set_page_config(
    page_title="Relatório SINFO - CEFET/RJ",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS: REMOVE O LOGO "LA", FORÇA MODO CLARO E AJUSTA A4 ---
st.markdown("""
    <style>
    /* Força fundo branco na tela */
    .stApp { background-color: white !important; color: black !important; }
    
    /* ESCONDE O LOGO "LA" E ELEMENTOS DE INTERFACE (TELA E IMPRESSÃO) */
    header, footer, [data-testid="stToolbar"], [data-testid="stStatusWidget"] {
        display: none !important;
        visibility: hidden !important;
    }

    @media print {
        /* Garante que nada da interface saia no PDF */
        [data-testid="stSidebar"], .stButton, .stCheckbox, .stExpander, .stTooltip {
            display: none !important;
        }
        /* Mantém as duas colunas lado a lado na folha A4 */
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

# 2. Título do Painel
st.title("📊 Relatório de Chamados - CEFET/RJ")
st.markdown("---")

# 3. Gerenciamento de Arquivos
arquivos_csv = sorted([f for f in os.listdir('.') if f.endswith('.csv')], reverse=True)

if arquivos_csv:
    # Sidebar acessível para trocar o arquivo
    arquivo_selecionado = st.sidebar.selectbox("Escolha o Trimestre:", arquivos_csv)
    # Valor padrão como o formato que você solicitou
    periodo_input = st.sidebar.text_input("Data p/ Relatório:", value="03 abr 2025 a 03 jul 2025")
    
    try:
        df = pd.read_csv(arquivo_selecionado)
        unidade = df['Departamento'].iloc[0] if 'Departamento' in df.columns else "SINFO - Maria da Graça"

        # --- CABEÇALHO CLÁSSICO (O QUE VOCÊ GOSTA) ---
        st.markdown(f"### 📅 Período: {periodo_input}")
        st.markdown(f"### 📍 Unidade: {unidade}")

        # KPIs Compactos (Cálculo da taxa blindado contra erros)
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        abertos = int(df['Aberto'].iloc[0])
        encerrados = int(df['Encerrado'].iloc[0])
        
        # Corrigido o erro de SyntaxError: taxa = (divisão segura)
        taxa_calc = (encerrados / abertos * 100) if abertos > 0 else 0

        c1.metric("Total", abertos)
        c2.metric("Concluídos", encerrados, f"{taxa_calc:.1f}%")
        c3.metric("Atrasados", int(df['Atrasado'].iloc[0]))
        c4.metric("Atribuídos", int(df['Atribuído'].iloc[0]))

        st.markdown("---")

        # --- GRÁFICOS HORIZONTAIS COM NÚMEROS NA BASE ---
        st.write("#### 📈 Distribuição de Status e Tempos (SLA)")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            status_cols = ['Aberto', 'Atribuído', 'Atrasado', 'Encerrado']
            df_status = pd.DataFrame({'Status': status_cols, 'Qtd': df[status_cols].iloc[0].values})
            
            fig1 = px.bar(df_status, x='Qtd', y='Status', orientation='h', text_auto=True, color='Status')
            # Números na base da barra (alinhados à esquerda)
            fig1.update_traces(textposition='inside', insidetextanchor='start')
            fig1.update_layout(showlegend=False, height=250, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig1, use_container_width=True)

        with col_b:
            if 'Tempo de Serviço' in df.columns:
                df_tempo = pd.DataFrame({
                    'Métrica': ['Resposta', 'Serviço'],
                    'Minutos': [df['Tempo de Resposta'].iloc[0], df['Tempo de Serviço'].iloc[0]]
                })
                fig2 = px.bar(df_tempo, x='Minutos', y='Métrica', orientation='h', text_auto=True, color_discrete_sequence=['#2ecc71'])
                fig2.update_traces(textposition='inside', insidetextanchor='start')
                fig2.update_layout(height=250, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig2, use_container_width=True)

        # Rodapé Oficial
        st.markdown("---")
        st.caption("Relatório Oficial SINFO/CEFET-RJ | Documento Gerado Automaticamente")

    except Exception as e:
        st.error(f"Erro ao processar dados: {e}")

else:
    st.warning("⚠️ Nenhum arquivo .csv encontrado no repositório.")
