import streamlit as st
import os
import pandas as pd
import numpy as np
from supabase import create_client, Client
from streamlit_option_menu import option_menu

# ==========================================
# 🎨 IDENTIDADE VISUAL (Substitua o link abaixo)
# ==========================================
URL_LOGO_BAPLY = "https://raw.githubusercontent.com/Baplyerp/GestoBapEdu/refs/heads/main/logo_baply.png" # <- COLE O LINK RAW DA LOGO AQUI

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
        # LOGO E TÍTULO NO LOGIN (Aumentado e Elegante)
        st.markdown(f"""
            <div style='text-align: center; margin-bottom: 20px;'>
                <img src='{URL_LOGO_BAPLY}' width='160' style='margin-bottom: 15px;'>
                <h2 style='color: #D4AF37; margin-top: 0px;'>🐝 GestoBap Edu</h2>
                <p style='color: #7F8C8D; margin-top: -10px;'>Acesso Restrito à Plataforma de Elite</p>
            </div>
        """, unsafe_allow_html=True)
        
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
                        st.success("📩 Link enviado! Verifique a sua caixa de entrada.")
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
                    st.warning("⚠️ Importante: Verifique a sua caixa de entrada (e Spam). Clique no link para ativar a conta.")
                except Exception as e:
                    st.error(f"❌ Erro ao registar: {e}")

# ==========================================
# 🏛️ A PLATAFORMA (Logado)
# ==========================================
else:
    # CSS ATUALIZADO
    st.markdown("""
        <style>
        .stApp { background-color: #FFFFFF; }
        [data-testid="stSidebar"] { background-color: #FAFAFA; border-right: 6px solid #3E2723; }
        [data-testid="stSidebar"] * { color: #3E2723 !important; }
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
        # LOGO E TÍTULO NA BARRA LATERAL (Tamanho Aumentado)
        st.markdown(f"""
            <div style='text-align: center; padding-top: 10px;'>
                <img src='{URL_LOGO_BAPLY}' width='150' style='margin-bottom: 10px;'>
                <h2 style='color: #D4AF37; margin-top: 0px;'>🐝 GestoBap</h2>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        selecao = option_menu(
            menu_title=None, 
            options=["Hub Central", "Resolver Questões", "Meu Desempenho", "Zona de Estudo", "Área do Professor", "Meu Perfil"],
            icons=["house", "bullseye", "bar-chart-line", "stopwatch", "pencil-square", "person-badge"],
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#D4AF37", "font-size": "18px"}, 
                "nav-link": {"font-size": "15px", "text-align": "left", "margin":"5px 0px", "--hover-color": "#EAE0D5"}, 
                "nav-link-selected": {"background-color": "#3E2723", "color": "#D4AF37", "font-weight": "bold"}, 
            }
        )
        
        st.markdown("---")
        
        # O AVATAR DO USUÁRIO
        email_usuario = st.session_state.utilizador.email
        inicial = email_usuario[0].upper()
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
        
    elif selecao == "Área do Professor":
        st.markdown("## 👨‍🏫 Área do Professor (Seed)")
        st.markdown("<p style='color: #7F8C8D; margin-top: -10px; margin-bottom: 30px;'>Gestão da base de conhecimento, bancas e questões.</p>", unsafe_allow_html=True)

        from database import get_engine
        from sqlalchemy.orm import Session
        from backend.models import Banca, Disciplina, Assunto, Questao, Alternativa, DificuldadeEnum

        tab_banca, tab_disc, tab_questao = st.tabs(["🏛️ 1. Bancas", "📚 2. Disciplinas & Assuntos", "✍️ 3. Nova Questão"])

        # -----------------------------------------
        # ABA 1: BANCAS
        # -----------------------------------------
        with tab_banca:
            st.markdown("#### Cadastrar Nova Banca")
            with st.form("form_banca"):
                sigla_banca = st.text_input("Sigla", placeholder="Ex: FCC, CEBRASPE, IBFC")
                nome_banca = st.text_input("Nome Completo", placeholder="Ex: Fundação Carlos Chagas")
                
                if st.form_submit_button("Salvar Banca", type="primary"):
                    try:
                        with Session(get_engine()) as session:
                            nova_banca = Banca(sigla=sigla_banca.upper(), nome=nome_banca)
                            session.add(nova_banca)
                            session.commit()
                            st.success(f"✅ Banca {sigla_banca} cadastrada com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao salvar: Já existe? Detalhes: {e}")

        # -----------------------------------------
        # ABA 2: DISCIPLINAS E ASSUNTOS
        # -----------------------------------------
        with tab_disc:
            col_d, col_a = st.columns(2)
            with col_d:
                st.markdown("#### Nova Disciplina")
                with st.form("form_disc"):
                    nome_disc = st.text_input("Nome da Disciplina", placeholder="Ex: Auditoria Governamental")
                    if st.form_submit_button("Salvar Disciplina", type="primary"):
                        with Session(get_engine()) as session:
                            nova_disc = Disciplina(nome=nome_disc)
                            session.add(nova_disc)
                            session.commit()
                            st.success(f"✅ Disciplina {nome_disc} salva!")

            with col_a:
                st.markdown("#### Novo Assunto")
                with Session(get_engine()) as session:
                    todas_disciplinas = session.query(Disciplina).all()
                    opcoes_disc = {d.nome: d.id for d in todas_disciplinas}
                
                with st.form("form_assunto"):
                    if not opcoes_disc:
                        st.warning("Cadastre uma disciplina primeiro.")
                    
                    disc_selecionada = st.selectbox("Vincular à Disciplina:", options=list(opcoes_disc.keys()))
                    nome_assunto = st.text_input("Nome do Assunto", placeholder="Ex: Normas Internacionais (ISSAI)")
                    
                    if st.form_submit_button("Salvar Assunto", type="primary") and opcoes_disc:
                        with Session(get_engine()) as session:
                            novo_assunto = Assunto(nome=nome_assunto, disciplina_id=opcoes_disc[disc_selecionada])
                            session.add(novo_assunto)
                            session.commit()
                            st.success(f"✅ Assunto {nome_assunto} salvo!")

        # -----------------------------------------
        # ABA 3: NOVA QUESTÃO
        # -----------------------------------------
        with tab_questao:
            st.markdown("#### ✍️ Cadastrar Questão Completa")
            
            with Session(get_engine()) as session:
                bancas = session.query(Banca).all()
                assuntos = session.query(Assunto).all()
                opcoes_banca = {b.sigla: b.id for b in bancas}
                opcoes_assunto = {f"{a.disciplina.nome} - {a.nome}": a.id for a in assuntos} if assuntos else {}
            
            if not opcoes_banca or not opcoes_assunto:
                st.warning("⚠️ Você precisa cadastrar pelo menos 1 Banca, 1 Disciplina e 1 Assunto nas abas anteriores antes de criar uma questão.")
            else:
                with st.form("form_questao"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        banca_sel = st.selectbox("Banca", options=list(opcoes_banca.keys()))
                    with col2:
                        assunto_sel = st.selectbox("Disciplina - Assunto", options=list(opcoes_assunto.keys()))
                    with col3:
                        ano_q = st.number_input("Ano", min_value=1990, max_value=2030, value=2024)
                    
                    enunciado = st.text_area("Enunciado da Questão (Pode usar Markdown/HTML)", height=150)
                    
                    st.markdown("---")
                    st.markdown("**Alternativas**")
                    alt_a = st.text_input("A)", key="alt_a")
                    alt_b = st.text_input("B)", key="alt_b")
                    alt_c = st.text_input("C)", key="alt_c")
                    alt_d = st.text_input("D)", key="alt_d")
                    alt_e = st.text_input("E)", key="alt_e")
                    
                    correta = st.radio("Qual é a alternativa correta?", options=["A", "B", "C", "D", "E"], horizontal=True)
                    
                    st.markdown("---")
                    comentario = st.text_area("Comentário do Professor (Opcional)", placeholder="Explique por que a alternativa está correta...")
                    
                    if st.form_submit_button("💾 Gravar Questão no Banco", type="primary", use_container_width=True):
                        with Session(get_engine()) as session:
                            try:
                                # 1. Cria a Questão
                                nova_q = Questao(
                                    enunciado_html=enunciado,
                                    ano=ano_q,
                                    banca_id=opcoes_banca[banca_sel],
                                    assunto_id=opcoes_assunto[assunto_sel],
                                    comentario_html=comentario
                                )
                                session.add(nova_q)
                                session.flush() # Salva temporariamente para pegar o ID gerado
                                
                                # 2. Cria as Alternativas vinculadas ao ID da Questão
                                alternativas_obj = [
                                    Alternativa(questao_id=nova_q.id, texto_html=alt_a, letra="A", is_correta=(correta=="A")),
                                    Alternativa(questao_id=nova_q.id, texto_html=alt_b, letra="B", is_correta=(correta=="B")),
                                    Alternativa(questao_id=nova_q.id, texto_html=alt_c, letra="C", is_correta=(correta=="C")),
                                    Alternativa(questao_id=nova_q.id, texto_html=alt_d, letra="D", is_correta=(correta=="D")),
                                    Alternativa(questao_id=nova_q.id, texto_html=alt_e, letra="E", is_correta=(correta=="E"))
                                ]
                                session.add_all(alternativas_obj)
                                session.commit()
                                
                                st.success("🎉 Questão gravada com sucesso no Supabase! Ela já está pronta para ser resolvida.")
                                st.balloons()
                            except Exception as e:
                                session.rollback()
                                st.error(f"Erro Crítico: {e}")
