import streamlit as st
import os
import pandas as pd
import numpy as np
from supabase import create_client, Client
from streamlit_option_menu import option_menu

# 1. Configuração Inicial
st.set_page_config(page_title="GestoBap Edu", page_icon="🐝", layout="wide")

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

# 3. Gestão da Sessão
if 'utilizador' not in st.session_state:
    st.session_state.utilizador = None

# ==========================================
# 🔐 ECRÃ DE LOGIN E REGISTO
# ==========================================
if st.session_state.utilizador is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://upload.wikimedia.org/wikipedia/commons/c/ca/1x1.png", width=80) # Placeholder Logo
        st.markdown("<h2 style='text-align: center; color: #D4AF37;'>🐝 GestoBap Edu</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #7F8C8D;'>Acesso Restrito à Plataforma de Elite</p>", unsafe_allow_html=True)
        
        tab_login, tab_registo = st.tabs(["Entrar", "Criar Conta"])
        
        # --- ABA DE LOGIN ---
        with tab_login:
            email_login = st.text_input("Email", key="login_email")
            senha_login = st.text_input("Palavra-passe", type="password", key="login_senha")
            
            if st.button("Aceder ao Hub ➡️", type="primary", use_container_width=True):
                try:
                    resposta = supabase.auth.sign_in_with_password({"email": email_login, "password": senha_login})
                    st.session_state.utilizador = resposta.user
                    st.rerun()
                except Exception as e:
                    st.error("❌ Credenciais inválidas. Verifique se confirmou o seu e-mail.")
            
            # Esqueci minha senha
            with st.expander("Esqueci minha palavra-passe"):
                recup_email = st.text_input("Digite o seu e-mail de registo:", key="recup_email")
                if st.button("Enviar link de recuperação", use_container_width=True):
                    try:
                        supabase.auth.reset_password_email(recup_email)
                        st.success("📩 Link enviado! Verifique a sua caixa de entrada para criar uma nova senha.")
                    except Exception as e:
                        st.error("❌ Erro ao solicitar recuperação. Verifique o e-mail digitado.")

        # --- ABA DE REGISTO ---            
        with tab_registo:
            st.info("Crie o seu perfil isolado. Os seus dados de estudo são privados.")
            email_novo = st.text_input("Novo Email", key="reg_email")
            senha_nova = st.text_input("Nova Palavra-passe (Mínimo 6 caracteres)", type="password", key="reg_senha")
            
            if st.button("Registar Conta 📝", use_container_width=True):
                try:
                    resposta = supabase.auth.sign_up({"email": email_novo, "password": senha_nova})
                    st.success("🎉 Quase lá! Enviamos um link de confirmação para o seu e-mail.")
                    st.warning("⚠️ Importante: Verifique a sua caixa de entrada (e a pasta de Spam). Clique no link do e-mail para ativar a conta.")
                except Exception as e:
                    st.error(f"❌ Erro ao registar: {e}")

# ==========================================
# 🏛️ A PLATAFORMA (Logado)
# ==========================================
else:
    # CSS ATUALIZADO: Fundo Branco e Listra Marrom Baply
    st.markdown("""
        <style>
        /* Fundo principal limpo e branco (Setor do meio) */
        .stApp { background-color: #FFFFFF; }
        
        /* Barra lateral com um leve off-white para desgrudar do centro e a listra marrom forte na direita */
        [data-testid="stSidebar"] { 
            background-color: #FAFAFA; 
            border-right: 6px solid #3E2723; /* A listra estilo Sweet Home! */
        }
        
        /* Textos da barra lateral em Marrom Escuro */
        [data-testid="stSidebar"] * { color: #3E2723 !important; }
        
        /* Ajuste do contraste dos textos principais do meio */
        h1, h2, h3, h4, p { color: #2C3E50; }
        
        .baply-card {
            background-color: #FFFFFF; padding: 20px; border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.06); border-left: 6px solid #D4AF37; 
            border-top: 1px solid #F2F3F4; border-right: 1px solid #F2F3F4; border-bottom: 1px solid #F2F3F4;
            height: 100%;
        }
        .card-title { color: #95A5A6; font-size: 0.85rem; text-transform: uppercase; font-weight: 700; margin-bottom: 5px; }
        .card-metric { color: #3E2723; font-size: 1.4rem; font-weight: 800; }
        </style>
    """, unsafe_allow_html=True)

    # MENU LATERAL ANIMADO
    with st.sidebar:
        # 1. A LOGO DA PLATAFORMA
        # Dica: Quando tiver a imagem no GitHub, troque o link abaixo por "BAPLY.jpg" ou o nome do seu arquivo
        url_logo_baply = "https://github.com/Baplyerp/GestoBapEdu/blob/main/logo_baply.png?raw=true" # Substitua pelo link ou caminho da logo
        
        st.markdown(f"""
            <div style='text-align: center; padding-top: 10px;'>
                <img src='{url_logo_baply}' width='80' style='margin-bottom: 10px;'>
                <h2 style='color: #D4AF37; margin-top: 0px;'>GestoBap</h2>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 2. O MENU ANIMADO (Atualizado com Meu Perfil)
        selecao = option_menu(
            menu_title=None, 
            options=["Hub Central", "Resolver Questões", "Meu Desempenho", "Zona de Estudo", "Meu Perfil"],
            icons=["house", "bullseye", "bar-chart-line", "stopwatch", "person-badge"],
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#D4AF37", "font-size": "18px"}, 
                "nav-link": {"font-size": "15px", "text-align": "left", "margin":"5px 0px", "--hover-color": "#EAE0D5"}, 
                "nav-link-selected": {"background-color": "#3E2723", "color": "#D4AF37", "font-weight": "bold"}, 
            }
        )
        
        st.markdown("---")
        
        # 3. O AVATAR DO USUÁRIO (Miniatura)
        email_usuario = st.session_state.utilizador.email
        inicial = email_usuario[0].upper()
        # Gerador automático de avatar com as cores da Baply (Marrom e Ouro)
        url_avatar = f"https://ui-avatars.com/api/?name={inicial}&background=3E2723&color=D4AF37&rounded=true&bold=true"
        
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px; padding: 10px; background-color: #FFFFFF; border-radius: 10px; border: 1px solid #EAE0D5;">
                <img src="{url_avatar}" style="width: 45px; height: 45px; border-radius: 50%; border: 2px solid #D4AF37; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="line-height: 1.2; overflow: hidden;">
                    <span style="font-size: 0.75rem; color: #7F8C8D; text-transform: uppercase; font-weight: bold;">Logado como</span><br>
                    <span style="font-size: 0.9rem; color: #3E2723; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: block;">
                        {email_usuario}
                    </span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Botão de Sair
        if st.button("Sair da Conta 🚪", use_container_width=True):
            supabase.auth.sign_out()
            st.session_state.utilizador = None
            st.rerun()

    # ROTEADOR DE PÁGINAS
    if selecao == "Hub Central":
        st.markdown("## 🏛️ Hub Central de Estudos")
        st.markdown("<p style='color: #7F8C8D; margin-top: -10px; margin-bottom: 30px;'>Bem-vindo de volta! Aqui está o resumo da sua jornada.</p>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="baply-card"><div class="card-title">🎯 Foco Atual</div><div class="card-metric">Auditoria e LRF</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="baply-card" style="border-left-color: #27AE60;"><div class="card-title">✅ Simulado Geral</div><div class="card-metric">85% de Acertos</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="baply-card" style="border-left-color: #F39C12;"><div class="card-title">⚠️ Atenção Necessária</div><div class="card-metric">Receita Pública</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col_grafico, col_ciclo = st.columns([2, 1])
        with col_grafico:
            st.markdown("#### 📈 Evolução do Desempenho")
            chart_data = pd.DataFrame(np.random.randn(7, 1) * 10 + 70, columns=['Acertos'])
            st.area_chart(chart_data, color="#D4AF37") 

        with col_ciclo:
            st.markdown("""
                <div class="baply-card" style="border-left: none; border-top: 6px solid #8B5A2B;">
                    <div style="font-size: 1.1rem; font-weight: bold; color: #2C3E50; margin-bottom: 10px;">🧠 Status do Ciclo</div>
                    <p style="font-size: 0.9rem; color: #7F8C8D;"><b>Insight de Neurociência:</b> Seu foco atinge o pico em blocos de 50 min. Sugerimos uma pausa agora.</p>
                    <hr style="opacity: 0.2">
                    <div style="display: flex; justify-content: space-between; text-align: center;">
                        <div><div style="font-size: 1.2rem; font-weight: bold; color: #3E2723;">50m</div><div style="font-size: 0.7rem; color: #7F8C8D;">FOCO</div></div>
                        <div><div style="font-size: 1.2rem; font-weight: bold; color: #D4AF37;">10m</div><div style="font-size: 0.7rem; color: #7F8C8D;">PAUSA</div></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    elif selecao == "Resolver Questões":
        st.title("🎯 Resolver Questões")
        st.info("O motor de questões será conectado aqui!")

    elif selecao == "Meu Desempenho":
        st.title("📊 Meu Desempenho")
        st.info("Estatísticas da conta.")
        
    elif selecao == "Zona de Estudo":
        st.title("🧠 Zona de Estudo")
        st.info("Gerenciador Pomodoro.")

    elif selecao == "Meu Perfil":
        st.markdown("## 👤 Meu Perfil")
        st.markdown("<p style='color: #7F8C8D; margin-top: -10px; margin-bottom: 30px;'>Gerencie as suas informações pessoais e configurações de segurança.</p>", unsafe_allow_html=True)
        
        # Gerar URL do avatar para usar na tela principal
        email_usuario = st.session_state.utilizador.email
        inicial = email_usuario[0].upper()
        url_avatar_grande = f"https://ui-avatars.com/api/?name={inicial}&background=3E2723&color=D4AF37&rounded=true&bold=true&size=256"

        col_foto, col_dados = st.columns([1, 2])
        
        with col_foto:
            st.markdown(f"""
                <div class="baply-card" style="text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                    <img src="{url_avatar_grande}" style="width: 140px; height: 140px; border-radius: 50%; border: 4px solid #D4AF37; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin-bottom: 20px;">
                    <h4 style="color: #3E2723; margin-bottom: 0px;">{inicial}</h4>
                    <p style="color: #7F8C8D; font-size: 0.85rem;">Estudante de Elite</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📸 Alterar Avatar (Em breve)", use_container_width=True):
                st.toast("A conexão com o Supabase Storage será ativada na próxima fase!")

        with col_dados:
            with st.container():
                st.markdown('<div class="baply-card" style="border-left-color: #3E2723;">', unsafe_allow_html=True)
                st.markdown("<h4 style='color: #3E2723; margin-bottom: 20px;'>Dados da Conta</h4>", unsafe_allow_html=True)
                
                with st.form("form_perfil"):
                    st.text_input("E-mail de Acesso (Fixo)", value=email_usuario, disabled=True)
                    nome_input = st.text_input("Nome de Exibição", placeholder="Ex: Jean Dias")
                    foco_input = st.text_input("Foco / Edital Principal", placeholder="Ex: Prefeitura de Catende / TGP")
                    
                    st.markdown("---")
                    st.markdown("<h4 style='color: #3E2723; margin-bottom: 20px;'>Segurança</h4>", unsafe_allow_html=True)
                    st.warning("Para redefinir a sua palavra-passe, termine a sessão e utilize a opção 'Esqueci minha palavra-passe' no ecrã de login.")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    submit_perfil = st.form_submit_button("Salvar Alterações", type="primary", use_container_width=True)
                    
                    if submit_perfil:
                        st.success("✅ Layout de perfil testado com sucesso! Os dados serão gravados no banco na Fase 3.")
                
                st.markdown('</div>', unsafe_allow_html=True)
