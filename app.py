import streamlit as st
from sqlalchemy import text
from database import get_engine

st.set_page_config(page_title="GestoBap Edu - Teste", page_icon="🐝")

st.title("🐝 GestoBap Edu - Fase 1")
st.subheader("Teste de Infraestrutura (Supabase)")

st.write("Clique no botão abaixo para testar a comunicação entre a nuvem e o seu banco de dados.")

if st.button("🔌 Testar Conexão", type="primary"):
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # Envia um comando SQL básico para ver a versão do banco
            resultado = conn.execute(text("SELECT version();")).fetchone()
            
            st.success("✅ Conexão bem-sucedida! A Ponte de Aço está de pé.")
            st.info(f"O banco de dados respondeu: {resultado[0]}")
            st.balloons()
            
    except Exception as e:
        st.error("❌ Falha na comunicação com o Supabase.")
        st.code(str(e)) # Mostra o erro exato na tela para investigarmos
