import streamlit as st
import os
from supabase import create_client, Client

# 1. Configuração Inicial
st.set_page_config(page_title="GestoBap Edu", page_icon="🐝", layout="centered")

# 2. Inicializar Cliente Supabase
@st.cache_resource
def init_supabase() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        st.error("🚨 Chaves da API do Supabase não encontradas nos Secrets.")
        st.stop()
    return create_client(url, key)

supabase = init_supabase()

# 3. Gestão da Sessão (O "Crachá" do Utilizador)
if 'utilizador' not in st.session_state:
    st.session_state.utilizador = None

# ==========================================
# 🔐 ECRÃ DE LOGIN E REGISTO
# ==========================================
if st.session_state.utilizador is None:
    st.image("https://upload.wikimedia.org/wikipedia/commons/c/ca/1x1.png", width=80) # Placeholder para Logo
    st.markdown("<h2 style='text-align: center; color: #D4AF37;'>🐝 GestoBap Edu</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #7F8C8D;'>Acesso Restrito à Plataforma de Elite</p>", unsafe_allow_html=True)
    
    tab_login, tab_registo = st.tabs(["Entrar", "Criar Conta"])
    
    with tab_login:
        email_login = st.text_input("Email", key="login_email")
        senha_login = st.text_input("Palavra-passe", type="password", key="login_senha")
        
        if st.button("Aceder ao Hub ➡️", type="primary", use_container_width=True):
            try:
                resposta = supabase.auth.sign_in_with_password({"email": email_login, "password": senha_login})
                st.session_state.utilizador = resposta.user
                st.rerun() # Atualiza a página automaticamente
            except Exception as e:
                st.error("❌ Credenciais inválidas. Tente novamente.")
                
    with tab_registo:
        st.info("Crie o seu perfil isolado. Os seus dados de estudo são privados.")
        email_novo = st.text_input("Novo Email", key="reg_email")
        senha_nova = st.text_input("Nova Palavra-passe (Mínimo 6 caracteres)", type="password", key="reg_senha")
        
        if st.button("Registar Conta 📝", use_container_width=True):
            try:
                # O Supabase cria o utilizador automaticamente
                resposta = supabase.auth.sign_up({"email": email_novo, "password": senha_nova})
                st.success("✅ Registo efetuado com sucesso! Já pode fazer o login no separador 'Entrar'.")
                # Nota: O Supabase pode enviar um email de confirmação dependendo das suas definições.
            except Exception as e:
                st.error(f"❌ Erro ao registar: {e}")

# ==========================================
# 🏛️ O HUB CENTRAL (Só aparece se estiver logado)
# ==========================================
else:
    # Reiniciamos o layout para wide porque o Hub precisa de espaço
    st.markdown("""<style> .stApp { background-color: #FDFCF8; } </style>""", unsafe_allow_html=True)
    
    # Botão de Logout no topo
    col_saudacao, col_sair = st.columns([4, 1])
    with col_saudacao:
        st.success(f"Bem-vindo(a), **{st.session_state.utilizador.email}**!")
    with col_sair:
        if st.button("Sair 🚪", use_container_width=True):
            supabase.auth.sign_out()
            st.session_state.utilizador = None
            st.rerun()
            
    st.markdown("---")
    st.markdown("### 🏛️ O seu Dashboard de Estudos aparecerá aqui.")
    st.info("A infraestrutura Multi-tenant está pronta! Os seus dados estão isolados.")
