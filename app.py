import streamlit as st

# 1. Configuração da Página (Título e layout largo)
st.set_page_config(page_title="GestoBap Edu | Hub", page_icon="🐝", layout="wide")

# 2. INJEÇÃO DE CSS (A Mágica do Design Baply)
st.markdown("""
    <style>
    /* Fundo da tela principal (Off-white elegante) */
    .stApp {
        background-color: #FDFCF8;
    }
    
    /* Barra Lateral (Marrom aveludado da Baply) */
    [data-testid="stSidebar"] {
        background-color: #3E2723;
    }
    
    /* Textos da Barra Lateral em Dourado/Branco */
    [data-testid="stSidebar"] * {
        color: #F8F9F9 !important;
    }
    
    /* Cartões Premium (Cards) */
    .baply-card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.04);
        border-left: 6px solid #D4AF37; /* Dourado Baply */
        height: 100%;
    }
    
    /* Tipografia dos Cartões */
    .card-title { 
        color: #95A5A6; 
        font-size: 0.85rem; 
        text-transform: uppercase; 
        font-weight: 700; 
        margin-bottom: 5px;
    }
    .card-metric { 
        color: #2C3E50; 
        font-size: 1.4rem; 
        font-weight: 800; 
    }
    
    /* Esconde o menu padrão do Streamlit (opcional, para visual mais limpo) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 3. MENU LATERAL (Simulação de Navegação)
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/c/ca/1x1.png", width=50) # Espaço para a logo oficial depois
    st.markdown("### 🐝 GestoBap Edu")
    st.markdown("---")
    st.button("🏛️ Hub Central", use_container_width=True, type="primary")
    st.button("🎯 Resolver Questões", use_container_width=True)
    st.button("📊 Meu Desempenho", use_container_width=True)
    st.button("🧠 Zona de Estudo", use_container_width=True)
    st.markdown("---")
    st.caption("Usuário: **Jean Dias**")
    st.caption("Foco: **TGP & Catende**")

# 4. CORPO PRINCIPAL (Dashboard)
st.markdown("## 🏛️ Hub Central de Estudos")
st.markdown("<p style='color: #7F8C8D; margin-top: -10px; margin-bottom: 30px;'>Bem-vindo de volta! Aqui está o resumo da sua jornada de aprendizagem.</p>", unsafe_allow_html=True)

# Linha de Métricas (Os 3 Cartões)
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div class="baply-card">
            <div class="card-title">🎯 Foco Atual</div>
            <div class="card-metric">Auditoria e LRF</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="baply-card" style="border-left-color: #27AE60;">
            <div class="card-title">✅ Simulado Geral</div>
            <div class="card-metric">85% de Acertos</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="baply-card" style="border-left-color: #F39C12;">
            <div class="card-title">⚠️ Atenção Necessária</div>
            <div class="card-metric">Receita Pública</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Área Inferior (Gráfico e Ciclo)
col_grafico, col_ciclo = st.columns([2, 1])

with col_grafico:
    st.markdown("#### 📈 Evolução do Desempenho")
    # Aqui usaremos um gráfico Chart nativo para simular o visual
    import pandas as pd
    import numpy as np
    chart_data = pd.DataFrame(np.random.randn(7, 1) * 10 + 70, columns=['Acertos'])
    st.area_chart(chart_data, color="#D4AF37") # Gráfico na cor Dourada!

with col_ciclo:
    st.markdown("""
        <div class="baply-card" style="border-left: none; border-top: 6px solid #8B5A2B;">
            <div style="font-size: 1.1rem; font-weight: bold; color: #2C3E50; margin-bottom: 10px;">🧠 Status do Ciclo</div>
            <p style="font-size: 0.9rem; color: #7F8C8D;"><b>Insight de Neurociência:</b> Seu foco atinge o pico em blocos de 50 min. Sugerimos uma pausa agora para consolidação (LTP).</p>
            <hr style="opacity: 0.2">
            <div style="display: flex; justify-content: space-between; text-align: center;">
                <div>
                    <div style="font-size: 1.2rem; font-weight: bold; color: #3E2723;">50m</div>
                    <div style="font-size: 0.7rem; color: #7F8C8D;">FOCO</div>
                </div>
                <div>
                    <div style="font-size: 1.2rem; font-weight: bold; color: #D4AF37;">10m</div>
                    <div style="font-size: 0.7rem; color: #7F8C8D;">PAUSA</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
