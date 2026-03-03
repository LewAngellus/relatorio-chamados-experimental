import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configurações Iniciais
st.set_page_config(page_title="Relatório SINFO - CEFET/RJ", layout="wide")

# Título Principal
st.title("📊 Painel de Controle de Chamados")
st.markdown("---")

# 2. Função Robusta para Carregar Dados
@st.cache_data
def carregar_dados():
    try:
        # Nome do arquivo deve ser exatamente este
        return pd.read_csv('stats-dept-20260303.csv')
    except Exception as e:
        st.error(f"Erro ao ler o arquivo CSV: {e}")
        return None

df = carregar_dados()

if df is not None:
    # 3. Tratamento de Colunas (Evita o erro de 'coluna não encontrada')
    # Definimos o que é padrão
    unidade = df['Departamento'].iloc[0] if 'Departamento' in df.columns else "Unidade Não Identificada"
    
    # Verificação de Datas
    if 'Data_Inicio' in df.columns and 'Data_Fim' in df.columns:
        periodo_texto = f"{df['Data_Inicio'].iloc[0]} até {df['Data_Fim'].iloc[0]}"
    else:
        # Se não houver data no CSV, criamos um seletor na lateral
        periodo_texto = st.sidebar.text_input("Defina o período (Ex: Março 2026)", "Período Atual")

    # 4. Exibição do Cabeçalho
    st.subheader(f"Resumo Operacional: {periodo_texto}")
    st.info(f"Setor: {unidade}")

    # 5. Indicadores (KPIs)
    col1, col2, col3, col4 = st.columns(4)
    
    # Usamos .get() ou checagem simples para evitar que o app quebre
    abertos = df['Aberto'].iloc[0] if 'Aberto' in df.columns else 0
    encerrados = df['Encerrado'].iloc[0] if 'Encerrado' in df.columns else 0
    atrasados = df['Atrasado'].iloc[0] if 'Atrasado' in df.columns else 0
    atribuídos = df['Atribuído'].iloc[0] if 'Atribuído' in df.columns else 0
    
    taxa_sucesso = (encerrados / abertos * 100) if abertos > 0 else 0

    col1.metric("Total Abertos", abertos)
    col2.metric("Encerrados", encerrados, f"{taxa_sucesso:.1f}% Eficiência")
    col3.metric("Atrasados", atrasados, delta_color="inverse")
    col4.metric("Em Atendimento", atribuídos)

    st.markdown("---")

    # 6. Visualização Gráfica
    c1, c2 = st.columns(2)

    with c1:
        st.write("### Volume por Status")
        status_lista = ['Aberto', 'Atribuído', 'Atrasado', 'Encerrado', 'Reaberto', 'Deletado']
        # Filtra apenas o que existe no seu CSV
        cols_ok = [c for c in status_lista if c in df.columns]
        
        df_status = pd.DataFrame({
            'Status': cols_ok,
            'Quantidade': df[cols_ok].iloc[0].values
        })
        fig1 = px.bar(df_status, x='Status', y='Quantidade', color='Status', text_auto=True)
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        st.write("### Desempenho (Tempos)")
        tempo_lista = ['Tempo de Serviço', 'Tempo de Resposta']
        cols_t_ok = [c for c in tempo_lista if c in df.columns]
        
        if cols_t_ok:
            df_tempo = pd.DataFrame({
                'Métrica': cols_t_ok,
                'Minutos': df[cols_t_ok].iloc[0].values
            })
            fig2 = px.bar(df_tempo, y='Métrica', x='Minutos', orientation='h', text_auto=True, color_discrete_sequence=['#3498db'])
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("Métricas de tempo não encontradas no arquivo.")

    # Tabela final
    with st.expander("Clique para ver os dados brutos"):
        st.write(df)

else:
    st.warning("⚠️ Aguardando upload do arquivo CSV no GitHub...")
