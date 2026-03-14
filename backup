import streamlit as st
import os
import pandas as pd
import numpy as np
from supabase import create_client, Client
from streamlit_option_menu import option_menu

# ==========================================
# 🎨 IDENTIDADE VISUAL
# ==========================================
URL_LOGO_BAPLY = "https://raw.githubusercontent.com/Baplyerp/GestoBapEdu/refs/heads/main/logo_baply.png"

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
        st.markdown(f"""
            <div style='text-align: center; margin-bottom: 20px;'>
                <img src='{URL_LOGO_BAPLY}' width='160' style='margin-bottom: 15px;'>
                <h2 style='color: #D4AF37; margin-top: 0px;'>🐝 GestoBap Edu</h2>
                <p style='color: #7F8C8D; margin-top: -10px;'>Acesso Restrito à Plataforma de Elite</p>
            </div>
        """, unsafe_allow_html=True)
        
        tab_login, tab_registo = st.tabs(["Entrar", "Criar Conta"])
        
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
            
            with st.expander("Esqueci minha palavra-passe"):
                recup_email = st.text_input("Digite o seu e-mail de registo:", key="recup_email")
                if st.button("Enviar link de recuperação", use_container_width=True):
                    try:
                        supabase.auth.reset_password_email(recup_email)
                        st.success("📩 Link enviado! Verifique a sua caixa de entrada.")
                    except Exception as e:
                        st.error("❌ Erro ao solicitar recuperação. Verifique o e-mail digitado.")

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

    with st.sidebar:
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
        st.markdown("## 🎯 Resolver Questões")
        st.markdown("<p style='color: #7F8C8D; margin-top: -10px; margin-bottom: 30px;'>Sua bateria de estudos ativa.</p>", unsafe_allow_html=True)

        from database import get_engine
        from sqlalchemy.orm import Session, joinedload
        from backend.models import Questao, HistoricoResolucao, Assunto, Banca # Importe a Banca aqui também
        import uuid

        if 'idx_questao' not in st.session_state:
            st.session_state.idx_questao = 0
        if 'estado_resposta' not in st.session_state:
            st.session_state.estado_resposta = "aguardando"
        
        # Carregar lista de IDs
        with Session(get_engine()) as session:
            todas = session.query(Questao.id).all()
            ids_questoes = [q.id for q in todas]

        if not ids_questoes:
            st.info("📭 Nenhuma questão encontrada. Cadastre uma na 'Área do Professor'!")
        elif st.session_state.idx_questao >= len(ids_questoes):
            st.success("🎉 Você finalizou todas as questões!")
            if st.button("🔄 Reiniciar Bateria"):
                st.session_state.idx_questao = 0
                st.session_state.estado_resposta = "aguardando"
                st.rerun()
        else:
            id_atual = ids_questoes[st.session_state.idx_questao]
            
            with Session(get_engine()) as session:
                # O joinedload agora vai funcionar porque corrigimos o models.py!
                questao = session.query(Questao).options(
                    joinedload(Questao.banca),
                    joinedload(Questao.assunto).joinedload(Assunto.disciplina),
                    joinedload(Questao.alternativas)
                ).filter(Questao.id == id_atual).first()
                
                if questao:
                    # --- RENDERIZAÇÃO (Tudo aqui dentro) ---
                    st.markdown(f"""
                        <div style='background-color: #FAFAFA; padding: 10px 15px; border-radius: 8px; border: 1px solid #EAE0D5; display: flex; justify-content: space-between;'>
                            <span style='color: #7F8C8D; font-size: 0.85rem;'><b>Banca:</b> {questao.banca.sigla} | <b>Ano:</b> {questao.ano} | <b>Assunto:</b> {questao.assunto.disciplina.nome} - {questao.assunto.nome}</span>
                            <span style='color: #D4AF37; font-weight: bold;'>Questão {st.session_state.idx_questao + 1} de {len(ids_questoes)}</span>
                        </div>
                    """, unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(f"<div style='font-size: 1.1rem; color: #2C3E50;'>{questao.enunciado_html}</div>", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)

                    opcoes_letras = []
                    mapa_alt = {}
                    st.markdown("**Alternativas:**")
                    for alt in sorted(questao.alternativas, key=lambda x: x.letra):
                        st.markdown(f"<div style='margin-bottom: 10px; padding: 10px; border-radius: 5px; background-color: #FFFFFF; border: 1px solid #F2F3F4;'><b>{alt.letra})</b> {alt.texto_html}</div>", unsafe_allow_html=True)
                        opcoes_letras.append(alt.letra)
                        mapa_alt[alt.letra] = alt

                    st.markdown("---")

                    if st.session_state.estado_resposta == "aguardando":
                        resp_sel = st.radio("Sua resposta:", options=opcoes_letras, horizontal=True, key=f"radio_{id_atual}")
                        if st.button("Confirmar Resposta ✅", type="primary", use_container_width=True):
                            alt_escolhida = mapa_alt[resp_sel]
                            novo_h = HistoricoResolucao(
                                user_id=uuid.UUID(st.session_state.utilizador.id),
                                questao_id=questao.id,
                                alternativa_selecionada_id=alt_escolhida.id,
                                acertou=alt_escolhida.is_correta
                            )
                            session.add(novo_h)
                            session.commit()
                            st.session_state.estado_resposta = "respondido"
                            st.session_state.acertou_ultima = alt_escolhida.is_correta
                            st.session_state.letra_correta = next(a.letra for a in questao.alternativas if a.is_correta)
                            st.session_state.comentario_prof = questao.comentario_html
                            st.rerun()

                    elif st.session_state.estado_resposta == "respondido":
                        if st.session_state.acertou_ultima:
                            st.success(f"🎯 Correto! Alternativa **{st.session_state.letra_correta}**.")
                        else:
                            st.error(f"❌ Incorreto. A certa era **{st.session_state.letra_correta}**.")

                        if st.session_state.comentario_prof:
                            st.info(f"**Comentário:**\n{st.session_state.comentario_prof}")

                        if st.button("Próxima Questão ➡️", type="primary", use_container_width=True):
                            st.session_state.idx_questao += 1
                            st.session_state.estado_resposta = "aguardando"
                            st.rerun()
                            
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

        # ABA 1: BANCAS
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

        # ABA 2: DISCIPLINAS E ASSUNTOS
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
                    
                    disc_selecionada = st.selectbox("Vincular à Disciplina:", options=list(opcoes_disc.keys()) if opcoes_disc else [])
                    nome_assunto = st.text_input("Nome do Assunto", placeholder="Ex: Normas Internacionais (ISSAI)")
                    
                    if st.form_submit_button("Salvar Assunto", type="primary") and opcoes_disc:
                        with Session(get_engine()) as session:
                            novo_assunto = Assunto(nome=nome_assunto, disciplina_id=opcoes_disc[disc_selecionada])
                            session.add(novo_assunto)
                            session.commit()
                            st.success(f"✅ Assunto {nome_assunto} salvo!")

       # -----------------------------------------
        # ABA 3: NOVA QUESTÃO (Avançada)
        # -----------------------------------------
        with tab_questao:
            st.markdown("#### ✍️ Cadastrar Questão Completa")
            
            with Session(get_engine()) as session:
                bancas = session.query(Banca).all()
                assuntos = session.query(Assunto).all()
                opcoes_banca = {b.sigla: b.id for b in bancas}
                opcoes_assunto = {f"{a.disciplina.nome} - {a.nome}": a.id for a in assuntos} if assuntos else {}
            
            if not opcoes_banca or not opcoes_assunto:
                st.warning("⚠️ Você precisa cadastrar pelo menos 1 Banca e 1 Assunto nas abas anteriores.")
            else:
                from streamlit_quill import st_quill # Importamos o editor rico
                
                # A MÁGICA AQUI: O controle de formato fica FORA do formulário para reagir na hora!
                st.markdown("**1. Defina o formato da questão:**")
                tipo_q = st.radio(
                    "Formato:", 
                    ["Múltipla Escolha (ABCDE)", "Múltipla Escolha (ABCD)", "Certo/Errado (CE)"], 
                    horizontal=True, 
                    label_visibility="collapsed"
                )
                
                st.markdown("**2. Preencha os dados:**")
                with st.form("form_questao"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        banca_sel = st.selectbox("Banca", options=list(opcoes_banca.keys()))
                    with col2:
                        assunto_sel = st.selectbox("Disciplina - Assunto", options=list(opcoes_assunto.keys()))
                    with col3:
                        ano_q = st.number_input("Ano", min_value=1990, max_value=2030, value=2024)
                    
                    st.markdown("**Enunciado da Questão:**")
                    enunciado = st_quill(placeholder="Cole o texto aqui, use negrito, tabelas, links...", key="quill_enunciado")
                    
                    st.markdown("---")
                    st.markdown(f"**Alternativas ({tipo_q}):**")
                    
                    # Como o tipo_q foi escolhido fora, o formulário já nasce com os campos certos!
                    if tipo_q == "Múltipla Escolha (ABCDE)":
                        alt_a = st.text_input("A)", key="ma_a")
                        alt_b = st.text_input("B)", key="ma_b")
                        alt_c = st.text_input("C)", key="ma_c")
                        alt_d = st.text_input("D)", key="ma_d")
                        alt_e = st.text_input("E)", key="ma_e")
                        correta = st.radio("Gabarito Correto:", ["A", "B", "C", "D", "E"], horizontal=True)
                        
                    elif tipo_q == "Múltipla Escolha (ABCD)":
                        alt_a = st.text_input("A)", key="mb_a")
                        alt_b = st.text_input("B)", key="mb_b")
                        alt_c = st.text_input("C)", key="mb_c")
                        alt_d = st.text_input("D)", key="mb_d")
                        correta = st.radio("Gabarito Correto:", ["A", "B", "C", "D"], horizontal=True)
                        
                    else:
                        st.info("No formato C/E, as alternativas 'Certo' e 'Errado' são geradas automaticamente. Selecione apenas o gabarito correto abaixo:")
                        correta = st.radio("Gabarito Correto:", ["Certo", "Errado"], horizontal=True)
                    
                    st.markdown("---")
                    st.markdown("**Comentário do Professor (Opcional):**")
                    comentario = st_quill(placeholder="Explicação, links de vídeos, etc.", key="quill_comentario")
                    
                    submit_questao = st.form_submit_button("💾 Gravar Questão no Banco", type="primary", use_container_width=True)
                    
                    if submit_questao:
                        if not enunciado or enunciado == "<p><br></p>":
                            st.error("❌ O enunciado não pode ficar vazio.")
                        else:
                            with Session(get_engine()) as session:
                                try:
                                    nova_q = Questao(
                                        enunciado_html=enunciado,
                                        ano=ano_q,
                                        banca_id=opcoes_banca[banca_sel],
                                        assunto_id=opcoes_assunto[assunto_sel],
                                        comentario_html=comentario
                                    )
                                    session.add(nova_q)
                                    session.flush() 
                                    
                                    alternativas_obj = []
                                    if tipo_q == "Certo/Errado (CE)":
                                        alternativas_obj.append(Alternativa(questao_id=nova_q.id, texto_html="Certo", letra="C", is_correta=(correta=="Certo")))
                                        alternativas_obj.append(Alternativa(questao_id=nova_q.id, texto_html="Errado", letra="E", is_correta=(correta=="Errado")))
                                    else:
                                        alternativas_obj.append(Alternativa(questao_id=nova_q.id, texto_html=alt_a, letra="A", is_correta=(correta=="A")))
                                        alternativas_obj.append(Alternativa(questao_id=nova_q.id, texto_html=alt_b, letra="B", is_correta=(correta=="B")))
                                        alternativas_obj.append(Alternativa(questao_id=nova_q.id, texto_html=alt_c, letra="C", is_correta=(correta=="C")))
                                        alternativas_obj.append(Alternativa(questao_id=nova_q.id, texto_html=alt_d, letra="D", is_correta=(correta=="D")))
                                        if tipo_q == "Múltipla Escolha (ABCDE)":
                                            alternativas_obj.append(Alternativa(questao_id=nova_q.id, texto_html=alt_e, letra="E", is_correta=(correta=="E")))

                                    session.add_all(alternativas_obj)
                                    session.commit()
                                    
                                    st.success("🎉 Questão gravada com sucesso! O formato e as formatações foram mantidos.")
                                    st.balloons()
                                except Exception as e:
                                    session.rollback()
                                    st.error(f"Erro Crítico: {e}")
                                    
    # -----------------------------------------
    # ABA RECUPERADA: MEU PERFIL
    # -----------------------------------------
    elif selecao == "Meu Perfil":
        st.markdown("## 👤 Meu Perfil")
        st.markdown("<p style='color: #7F8C8D; margin-top: -10px; margin-bottom: 30px;'>Gerencie as suas informações pessoais e configurações de segurança.</p>", unsafe_allow_html=True)
        
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
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("<h4 style='color: #C0392B; margin-bottom: 20px;'>⚙️ Administração do Sistema</h4>", unsafe_allow_html=True)
                st.info("Utilize este botão apenas uma vez para construir a estrutura do banco de dados no Supabase.")
                
                if st.button("🚨 [ADMIN] Construir Tabelas no Supabase", type="primary", use_container_width=True):
                    try:
                        from database import init_db
                        init_db()
                        st.success("✅ SUCESSO! A Engenharia da Fase 3 foi injetada no Supabase! Verifique o painel do banco de dados.")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ Erro ao criar tabelas: {e}")
                
                st.markdown('</div>', unsafe_allow_html=True)
