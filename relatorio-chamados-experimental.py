import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Configuração da página
st.set_page_config(page_title="Relatórios SINFO - CEFET/RJ", layout="wide")

# 2. Título do Dashboard
st.title("📊 Portal de Relatórios de Chamados")
st.markdown("---")

# 3. Função para listar e carregar os arquivos CSV
def buscar_arquivos():
    # Procura todos os arquivos que terminam com .csv na pasta
    arquivos = [f for f in os.listdir('.') if f.endswith('.csv')]
    return arquivos

arquivos_csv = buscar_arquivos()

# 4. Interface na Barra Lateral (Sidebar)
st.sidebar.header("📁 Gerenciador de Dados")

if arquivos_csv:
    # Cria a caixinha de seleção com os nomes dos arquivos encontrados
    arquivo_selecionado = st.sidebar.selectbox(
        "Selecione o relatório que deseja analisar:",
        arquivos_csv
    )
    
    st.sidebar.success(f"Arquivo carregado: {arquivo_selecionado}")
    
    # Carrega os dados do arquivo escolhido
    df = pd.read_csv(arquivo_selecionado)
    
    # --- INÍCIO DA EXIBIÇÃO DO RELATÓRIO ---
    
    unidade = df['Departamento'].iloc[0] if 'Departamento' in df.columns else "Unidade não identificada"
    st.subheader(f"Análise: {unidade}")
    st.info(f"Arquivo atual: {arquivo_selecionado}")

    # Indicadores principais (KPIs)
    col1, col2, col3, col4 = st.columns(4)
    
    abertos = df['Aberto'].iloc[0] if 'Aberto' in df.columns else 0
    encerrados = df['Encerrado'].iloc[0] if 'Encerrado' in df.columns else 0
    atrasados = df['Atrasado'].iloc[0] if 'Atrasado' in df.columns else 0
    
    col1.metric("Total Abertos", abertos)
    col2.metric("Encerrados", encerrados)
    col3.metric("Atrasados", atrasados, delta_color="inverse")
    col4.metric("Em Atendimento", df['Atribuído'].iloc[0] if 'Atribuído' in df.columns else 0)

    st.markdown("---")

    # Gráficos
    c1, c2 = st.columns(2)

    with c1:
        st.write("### Status dos Chamados")
        status_cols = ['Aberto', 'Atribuído', 'Atrasado', 'Encerrado', 'Reaberto', 'Deletado']
        # Filtra apenas colunas que existem no CSV
        cols_ok = [c for c in status_cols if c in df.columns]
        
        df_status = pd.DataFrame({
            'Status': cols_ok,
            'Qtd': df[cols_ok].iloc[0].values
        })
        fig1 = px.bar(df_status, x='Status', y='Qtd', color='Status', text_auto=True)
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        st.write("### Médias de Tempo")
        tempo_cols = ['Tempo de Serviço', 'Tempo de Resposta']
        cols_t_ok = [c for c in tempo_cols if c in df.columns]
        
        if cols_t_ok:
            df_tempo = pd.DataFrame({
                'Métrica': cols_t_ok,
                'Valor': df[cols_t_ok].iloc[0].values
            })
            fig2 = px.bar(df_tempo, y='Métrica', x='Valor', orientation='h', text_auto=True, color_discrete_sequence=['#E67E22'])
            st.plotly_chart(fig2, use_container_width=True)

    # Tabela detalhada
    with st.expander("Ver dados brutos da tabela"):
        st.write(df)

else:
    st.warning("⚠️ Nenhum arquivo .csv foi encontrado no repositório. Por favor, suba os arquivos de dados para o GitHub.")

st.sidebar.markdown("---")
st.sidebar.markdown("Dica: Para adicionar novos dados, basta fazer o upload de um novo arquivo .csv no seu GitHub.")
