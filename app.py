import streamlit as st
import os
import pandas as pd
import numpy as np
from supabase import create_client, Client
from streamlit_option_menu import option_menu

# ==========================================
# 🚀 ENGENHARIA DE ALTA PERFORMANCE (Imports Top-Level)
# ==========================================
# Ao importar tudo aqui em cima, evitamos o "congelamento" ao trocar de abas
import uuid
from database import get_engine
from sqlalchemy.orm import Session, joinedload
try:
    # ATUALIZADO: Incluindo as classes da Zona de Estudo
    from backend.models import (
        Questao, HistoricoResolucao, Assunto, Banca, Disciplina, Orgao, Cargo, 
        EscolaridadeEnum, CarreiraEnum, Simulado, SimuladoQuestao, RegraPenalidadeEnum,
        ConcursoRadar, StatusConcursoEnum, PrioridadeConcursoEnum, ResultadoConcursoEnum, EditalItem
    )
    BANCO_PRONTO = True
except Exception as e:
    BANCO_PRONTO = False
    ERRO_BANCO = str(e)

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
        
        # 🛡️ GESTÃO DE ESTADO DO MENU (Evita o congelamento)
        if 'aba_atual' not in st.session_state:
            st.session_state.aba_atual = "Hub Central"

        selecao = option_menu(
            menu_title=None, 
            options=["Hub Central", "Resolver Questões", "Meu Desempenho", "Zona de Estudo", "Área do Professor", "Meu Perfil"],
            icons=["house", "bullseye", "bar-chart-line", "stopwatch", "pencil-square", "person-badge"],
            default_index=["Hub Central", "Resolver Questões", "Meu Desempenho", "Zona de Estudo", "Área do Professor", "Meu Perfil"].index(st.session_state.aba_atual),
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#D4AF37", "font-size": "18px"}, 
                "nav-link": {"font-size": "15px", "text-align": "left", "margin":"5px 0px", "--hover-color": "#EAE0D5"}, 
                "nav-link-selected": {"background-color": "#3E2723", "color": "#D4AF37", "font-weight": "bold"}, 
            }
        )
        
        # Se o usuário clicou em uma aba diferente, limpamos o cache de busca e recarregamos a tela rápido
        if selecao != st.session_state.aba_atual:
            st.session_state.aba_atual = selecao
            # Limpa memórias residuais para não travar a próxima tela
            keys_to_clear = ['mgr_buscar', 'mgr_f_banca', 'mgr_f_assunto', 'lista_questoes', 'idx_questao', 'estado_resposta', 'alt_escolhida_id', 'comentario_prof']
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

        st.markdown("---")
        
        email_usuario = st.session_state.utilizador.email
        inicial = email_usuario[0].upper()
        url_avatar = f"https://ui-avatars.com/api/?name={inicial}&background=3E2723&color=D4AF37&rounded=true&bold=true"
        
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px; padding: 10px; background-color: #FFFFFF; border-radius: 10px; border: 1px solid #EAE0D5;">
                <img src="{url_avatar}" style="width: 45px; height: 45px; border-radius: 50%; border: 2px solid #D4AF37; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="line-height: 1.2; overflow: hidden;">
                    <span style="font-size: 0.75rem; color: #7F8C8D; text-transform: uppercase; font-weight: bold;">Logado como</span><br>
                    <span style="font-size: 0.9rem; color: #3E2723; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: block;">{email_usuario}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Sair da Conta 🚪", use_container_width=True):
            supabase.auth.sign_out()
            st.session_state.utilizador = None
            st.rerun()

    # ==========================================
    # ROTEADOR DE PÁGINAS
    # ==========================================
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
        st.markdown("<p style='color: #7F8C8D; margin-top: -10px; margin-bottom: 30px;'>Modo de Resolução de Alto Desempenho.</p>", unsafe_allow_html=True)
        
        if not BANCO_PRONTO:
            st.error(f"⚠️ O sistema está aguardando a construção do banco de dados. Vá em 'Meu Perfil' e clique em 'Construir Tabelas'. Detalhe: {ERRO_BANCO}")
            st.stop()
            
        try:
            # --- 1. FILTRO INTELIGENTE ---
            with st.expander("🔍 Criar Novo Caderno de Questões (Filtros)", expanded=False):
                with Session(get_engine()) as session:
                    bancas_db = session.query(Banca).all()
                    materias_db = session.query(Disciplina).all()
                    orgaos_db = session.query(Orgao).all()
                    anos_db = session.query(Questao.ano).distinct().all()
                
                with st.form("form_filtro_aluno"):
                    col_f1, col_f2, col_f3 = st.columns(3)
                    with col_f1:
                        f_banca = st.multiselect("Banca", options=[b.sigla for b in bancas_db])
                        f_orgao = st.multiselect("Órgão", options=[o.nome for o in orgaos_db])
                    with col_f2:
                        f_materia = st.multiselect("Matéria", options=[m.nome for m in materias_db])
                        f_escolaridade = st.multiselect("Escolaridade", options=[e.value for e in EscolaridadeEnum])
                    with col_f3:
                        f_ano = st.multiselect("Ano", options=[str(a[0]) for a in anos_db])
                        f_carreira = st.multiselect("Carreira", options=[c.value for c in CarreiraEnum])
                        
                    # 🚀 NOVO FILTRO DE INÉDITAS
                    f_inedita = st.radio("Origem da Questão:", ["Todas", "Apenas Inéditas", "Apenas Concursos Oficiais"], horizontal=True)

                    if st.form_submit_button("Gerar Caderno e Iniciar 🚀", type="primary", use_container_width=True):
                        with Session(get_engine()) as session:
                            query = session.query(Questao.id) 
                            
                            if f_banca: query = query.join(Banca).filter(Banca.sigla.in_(f_banca))
                            if f_orgao: query = query.join(Orgao).filter(Orgao.nome.in_(f_orgao))
                            if f_materia: query = query.join(Assunto).join(Disciplina).filter(Disciplina.nome.in_(f_materia))
                            if f_ano: query = query.filter(Questao.ano.in_([int(a) for a in f_ano]))
                            if f_escolaridade: query = query.filter(Questao.escolaridade.in_(f_escolaridade))
                            if f_carreira: query = query.filter(Questao.carreira.in_(f_carreira))
                            
                            # 🚀 APLICAÇÃO DO FILTRO DE INÉDITAS
                            if f_inedita == "Apenas Inéditas":
                                query = query.filter(Questao.is_inedita == True)
                            elif f_inedita == "Apenas Concursos Oficiais":
                                query = query.filter(Questao.is_inedita == False)
                            
                            res_ids = [q[0] for q in query.all()]
                            st.session_state.lista_questoes = res_ids
                            st.session_state.idx_questao = 0
                            st.session_state.estado_resposta = "aguardando"
                            st.toast(f"Caderno gerado com {len(res_ids)} questões!")
                            st.rerun()

            # --- 2. GESTÃO DO CADERNO ATUAL ---
            if 'idx_questao' not in st.session_state: st.session_state.idx_questao = 0
            if 'estado_resposta' not in st.session_state: st.session_state.estado_resposta = "aguardando"
            if 'lista_questoes' not in st.session_state:
                with Session(get_engine()) as session:
                    st.session_state.lista_questoes = [q[0] for q in session.query(Questao.id).all()]

            ids_questoes = st.session_state.lista_questoes

            # --- 3. MOTOR DE RENDERIZAÇÃO 1-CLICK BLINDADO ---
            if not ids_questoes:
                st.info("📭 Seu caderno está vazio. Ajuste os filtros acima para buscar questões.")
            elif st.session_state.idx_questao >= len(ids_questoes):
                st.success("🎉 Você finalizou este caderno de questões!")
                if st.button("🔄 Refazer Caderno", type="primary"):
                    st.session_state.idx_questao = 0
                    st.session_state.estado_resposta = "aguardando"
                    st.rerun()
            else:
                id_atual = ids_questoes[st.session_state.idx_questao]
                with Session(get_engine()) as session:
                    questao = session.query(Questao).options(
                        joinedload(Questao.banca),
                        joinedload(Questao.orgao),
                        joinedload(Questao.cargo),
                        joinedload(Questao.assunto).joinedload(Assunto.disciplina),
                        joinedload(Questao.alternativas)
                    ).filter(Questao.id == id_atual).first()

                    if questao:
                        # Cabeçalho da Questão
                        orgao_nome = questao.orgao.nome if questao.orgao else 'Geral'
                        cargo_nome = questao.cargo.nome if questao.cargo else 'Geral'
                        prefixo = questao.assunto.disciplina.nome[:3].upper() if questao.assunto else "GER"
                        qid_baply = f"BAP-{prefixo}{questao.id:04d}"
                        
                        selo_inedita = "<span style='background-color: #3498DB; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; margin-left: 10px;'>INÉDITA</span>" if getattr(questao, 'is_inedita', False) else ""
                        
                        st.markdown(f"""
                            <div style='background-color: #FAFAFA; padding: 12px; border-radius: 8px; border-left: 5px solid #3E2723; border-right: 1px solid #EAE0D5; border-top: 1px solid #EAE0D5; border-bottom: 1px solid #EAE0D5;'>
                                <div style='display: flex; justify-content: space-between;'>
                                    <span style='color: #7F8C8D; font-size: 0.8rem; font-weight: bold; text-transform: uppercase;'>
                                        {questao.banca.sigla} • {questao.ano} • {orgao_nome} • {cargo_nome} {selo_inedita}
                                    </span>
                                    <span style='color: #D4AF37; font-size: 0.8rem; font-weight: bold;'>🏷️ {qid_baply}</span>
                                </div>
                                <div style='color: #3E2723; font-size: 0.95rem; margin-top: 5px;'>
                                    <b>{questao.assunto.disciplina.nome}</b> > {questao.assunto.nome}
                                </div>
                                <div style='text-align: right; color: #7F8C8D; font-size: 0.75rem; margin-top: 5px;'>Questão {st.session_state.idx_questao + 1} de {len(ids_questoes)}</div>
                            </div>
                        """, unsafe_allow_html=True)
                        st.markdown("<br>", unsafe_allow_html=True)

                        # 🛡️ PROTEÇÃO HTML: Sem quebras de linha para o Streamlit não bugar o CSS
                        html_enunciado = f"<div style='font-size: 1.15rem; color: #2C3E50; font-family: \"Helvetica Neue\", Helvetica, Arial, sans-serif; line-height: 1.6;'>{questao.enunciado_html}</div>"
                        st.markdown(html_enunciado, unsafe_allow_html=True)
                        
                        st.markdown("<br>**Alternativas:**", unsafe_allow_html=True)
                        
                        for alt in sorted(questao.alternativas, key=lambda x: x.letra):
                            col_btn, col_txt = st.columns([1, 11])
                            
                            with col_btn:
                                if st.session_state.estado_resposta == "aguardando":
                                    if st.button(alt.letra, key=f"btn_{questao.id}_{alt.id}", use_container_width=True):
                                        novo_h = HistoricoResolucao(
                                            user_id=uuid.UUID(st.session_state.utilizador.id),
                                            questao_id=questao.id,
                                            alternativa_selecionada_id=alt.id,
                                            acertou=alt.is_correta
                                        )
                                        session.add(novo_h)
                                        session.commit()
                                        st.session_state.estado_resposta = "respondido"
                                        st.session_state.acertou_ultima = alt.is_correta
                                        st.session_state.alt_escolhida_id = alt.id
                                        st.session_state.letra_correta = next(a.letra for a in questao.alternativas if a.is_correta)
                                        st.session_state.comentario_prof = questao.comentario_html
                                        st.rerun()
                                else:
                                    if alt.is_correta:
                                        st.markdown(f"<div style='background-color: #27AE60; color: white; text-align: center; padding: 7px; border-radius: 5px; font-weight: bold; margin-top: 5px;'>{alt.letra}</div>", unsafe_allow_html=True)
                                    elif alt.id == st.session_state.get("alt_escolhida_id") and not alt.is_correta:
                                        st.markdown(f"<div style='background-color: #E74C3C; color: white; text-align: center; padding: 7px; border-radius: 5px; font-weight: bold; margin-top: 5px;'>{alt.letra}</div>", unsafe_allow_html=True)
                                    else:
                                        st.markdown(f"<div style='background-color: #ECF0F1; color: #95A5A6; text-align: center; padding: 7px; border-radius: 5px; font-weight: bold; margin-top: 5px;'>{alt.letra}</div>", unsafe_allow_html=True)

                            with col_txt:
                                bg_color, border_color = "#FFFFFF", "#F2F3F4"
                                
                                if st.session_state.estado_resposta == "respondido":
                                    if alt.is_correta:
                                        bg_color, border_color = "#E9F7EF", "#27AE60"
                                    elif alt.id == st.session_state.get("alt_escolhida_id"):
                                        bg_color, border_color = "#FDEDEC", "#E74C3C"
                                        
                                # 🛡️ PROTEÇÃO HTML NA ALTERNATIVA
                                html_alt = f"<div style='padding: 10px; border-radius: 8px; background-color: {bg_color}; border: 1px solid {border_color}; margin-bottom: 10px; min-height: 45px; display: flex; align-items: center;'><div style='width: 100%;'>{alt.texto_html}</div></div>"
                                st.markdown(html_alt, unsafe_allow_html=True)

                        # --- BARRA DE AÇÕES PÓS-RESPOSTA E COMENTÁRIO ---
                        if st.session_state.estado_resposta == "respondido":
                            st.markdown("---")
                            col_result, col_next = st.columns([2, 1])
                            
                            with col_result:
                                if st.session_state.acertou_ultima:
                                    st.markdown(f"<h4 style='color: #27AE60; margin-bottom: 0px;'>✅ Resposta Correta!</h4>", unsafe_allow_html=True)
                                else:
                                    st.markdown(f"<h4 style='color: #E74C3C; margin-bottom: 0px;'>❌ Resposta Incorreta.</h4>", unsafe_allow_html=True)
                            
                            with col_next:
                                if st.button("Próxima Questão ➡️", type="primary", use_container_width=True):
                                    st.session_state.idx_questao += 1
                                    st.session_state.estado_resposta = "aguardando"
                                    st.rerun()

                            if st.session_state.get("comentario_prof") and st.session_state.comentario_prof != "<p><br></p>":
                                with st.expander("👨‍🏫 Comentário do Professor", expanded=True):
                                    # 🛡️ PROTEÇÃO HTML NO COMENTÁRIO (Sem as quebras que geravam o erro do </div> solto)
                                    html_comentario = f"<div style='background-color: #FFFDF8; padding: 20px; border-radius: 8px; border-left: 5px solid #D4AF37; font-family: \"Helvetica Neue\", Helvetica, Arial, sans-serif; color: #2C3E50; line-height: 1.6; font-size: 1rem;'>{st.session_state.comentario_prof}</div>"
                                    st.markdown(html_comentario, unsafe_allow_html=True)
                                    
        except Exception as e:
            st.error(f"⚠️ Erro ao carregar a interface de questões. Detalhe técnico: {e}")

    # ==========================================
    # 📊 ABA: MEU DESEMPENHO (DASHBOARD ANALÍTICO)
    # ==========================================
    elif selecao == "Meu Desempenho":
        st.markdown("## 📊 Meu Desempenho")
        st.markdown("<p style='color: #7F8C8D; margin-top: -10px; margin-bottom: 30px;'>Inteligência de dados sobre a sua jornada de aprovação.</p>", unsafe_allow_html=True)
        
        if not BANCO_PRONTO:
            st.error("⚠️ Banco de dados não inicializado. Vá em 'Meu Perfil'.")
            st.stop()
            
        try:
            with Session(get_engine()) as session:
                # 1. Busca todo o histórico do usuário logado cruzando com as Disciplinas
                uid = uuid.UUID(st.session_state.utilizador.id)
                historico = session.query(
                    HistoricoResolucao.acertou,
                    HistoricoResolucao.resolvido_em,
                    Disciplina.nome.label('disciplina')
                ).join(Questao, HistoricoResolucao.questao_id == Questao.id)\
                 .join(Assunto, Questao.assunto_id == Assunto.id)\
                 .join(Disciplina, Assunto.disciplina_id == Disciplina.id)\
                 .filter(HistoricoResolucao.user_id == uid).all()
                
            # 2. Processamento dos Dados com Pandas
            if not historico:
                st.info("📭 Não há dados suficientes. Vá para 'Resolver Questões' e inicie uma bateria para gerar as suas primeiras métricas!")
            else:
                df = pd.DataFrame(historico)
                
                # Conversão de fuso horário simples para os gráficos
                df['resolvido_em'] = pd.to_datetime(df['resolvido_em']).dt.tz_convert('America/Sao_Paulo')
                df['data'] = df['resolvido_em'].dt.date
                
                # Cálculos Globais
                total_questoes = len(df)
                total_acertos = df['acertou'].sum()
                aproveitamento_global = (total_acertos / total_questoes) * 100
                
                # Cálculo da Melhor Disciplina
                df_disc = df.groupby('disciplina').agg(
                    total=('acertou', 'count'),
                    acertos=('acertou', 'sum')
                ).reset_index()
                df_disc['aproveitamento'] = (df_disc['acertos'] / df_disc['total']) * 100
                melhor_disc = df_disc.loc[df_disc['aproveitamento'].idxmax()]['disciplina'] if not df_disc.empty else "N/A"
                
                # --- RENDERIZAÇÃO DOS CARDS (VISUAL PREMIUM) ---
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f'<div class="baply-card"><div class="card-title">🎯 Questões Resolvidas</div><div class="card-metric">{total_questoes}</div></div>', unsafe_allow_html=True)
                with col2:
                    cor_taxa = "#27AE60" if aproveitamento_global >= 70 else "#F39C12" if aproveitamento_global >= 50 else "#E74C3C"
                    st.markdown(f'<div class="baply-card" style="border-left-color: {cor_taxa};"><div class="card-title">📈 Taxa de Acerto</div><div class="card-metric" style="color: {cor_taxa};">{aproveitamento_global:.1f}%</div></div>', unsafe_allow_html=True)
                with col3:
                    st.markdown(f'<div class="baply-card" style="border-left-color: #8B5A2B;"><div class="card-title">🏆 Ponto Forte</div><div class="card-metric" style="font-size: 1.1rem; padding-top: 5px;">{melhor_disc}</div></div>', unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # --- GRÁFICOS E TABELAS ---
                col_grafico, col_tabela = st.columns([1.5, 1])
                
                with col_grafico:
                    st.markdown("#### 📅 Volume de Resoluções (Últimos Dias)")
                    # Agrupa por data para o gráfico
                    df_evolucao = df.groupby('data').size().reset_index(name='Questões Feitas')
                    df_evolucao.set_index('data', inplace=True)
                    st.bar_chart(df_evolucao, color="#D4AF37")
                    
                with col_tabela:
                    st.markdown("#### 🔬 Raio-X por Disciplina")
                    # Formata o dataframe de disciplinas para exibição limpa
                    df_show = df_disc[['disciplina', 'total', 'aproveitamento']].copy()
                    df_show['aproveitamento'] = df_show['aproveitamento'].apply(lambda x: f"{x:.1f}%")
                    df_show.rename(columns={'disciplina': 'Matéria', 'total': 'Qtd', 'aproveitamento': 'Acerto'}, inplace=True)
                    
                    st.dataframe(
                        df_show, 
                        hide_index=True, 
                        use_container_width=True,
                        column_config={
                            "Matéria": st.column_config.TextColumn("Matéria", width="large"),
                        }
                    )
                    
        except Exception as e:
            st.error(f"⚠️ Erro ao processar métricas de desempenho: {e}")
        
    # ==========================================
    # 🧠 ABA: ZONA DE ESTUDO (O Cockpit)
    # ==========================================
    elif selecao == "Zona de Estudo":
        st.markdown("## 🧠 Zona de Estudo")
        st.markdown("<p style='color: #7F8C8D; margin-top: -10px; margin-bottom: 30px;'>Gestão estratégica de concursos e neurociência do aprendizado.</p>", unsafe_allow_html=True)

        if not BANCO_PRONTO:
            st.error("⚠️ Banco não sincronizado. Vá em 'Meu Perfil'.")
            st.stop()

        # Tabs internas para manter a organização e evitar carregamento pesado
        tab_radar, tab_ciclo, tab_edital, tab_leiseca = st.tabs([
            "🎯 Radar de Missões", 
            "🔄 Ciclo de Foco", 
            "🧬 Edital Vivo", 
            "🔥 Desafio Lei Seca"
        ])

        # --- 🎯 MÓDULO 1: RADAR DE MISSÕES & AUTÓPSIA ---
        with tab_radar:
            col_inf1, col_inf2 = st.columns([1.5, 1])
            
            with col_inf2:
                st.markdown("#### ➕ Nova Missão (Concurso)")
                with st.form("form_novo_concurso"):
                    nome_concurso = st.text_input("Nome do Certame", placeholder="Ex: SEFAZ/PE - Auditor")
                    
                    with Session(get_engine()) as session:
                        bancas_r = session.query(Banca).all()
                        orgaos_r = session.query(Orgao).all()
                    
                    c1, c2 = st.columns(2)
                    banca_sel = c1.selectbox("Banca", options=["N/D"] + [b.sigla for b in bancas_r])
                    orgao_sel = c2.selectbox("Órgão", options=["N/D"] + [o.nome for o in orgaos_r])
                    
                    status_sel = st.selectbox("Status Atual", [e.value for e in StatusConcursoEnum])
                    prioridade_sel = st.selectbox("Prioridade", [e.value for e in PrioridadeConcursoEnum])
                    data_p = st.date_input("Data da Prova (Se houver)", value=None)
                    
                    if st.form_submit_button("Lançar Missão no Radar 🚀", type="primary", use_container_width=True):
                        if not nome_concurso:
                            st.error("Nome é obrigatório.")
                        else:
                            with Session(get_engine()) as session:
                                try:
                                    # Busca IDs correspondentes
                                    id_b = next((b.id for b in bancas_r if b.sigla == banca_sel), None)
                                    id_o = next((o.nome for o in orgaos_r if o.nome == orgao_sel), None)
                                    
                                    novo_c = ConcursoRadar(
                                        user_id=uuid.UUID(st.session_state.utilizador.id),
                                        nome=nome_concurso,
                                        banca_id=id_b,
                                        status=next(e for e in StatusConcursoEnum if e.value == status_sel),
                                        prioridade=next(e for e in PrioridadeConcursoEnum if e.value == prioridade_sel),
                                        data_prova=data_p
                                    )
                                    session.add(novo_c)
                                    session.commit()
                                    st.success(f"Missão {nome_concurso} adicionada!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro ao salvar: {e}")

            with col_inf1:
                st.markdown("#### 📡 Pipeline de Concursos")
                
                with Session(get_engine()) as session:
                    minhas_missoes = session.query(ConcursoRadar).options(joinedload(ConcursoRadar.banca))\
                        .filter_by(user_id=uuid.UUID(st.session_state.utilizador.id))\
                        .order_by(ConcursoRadar.data_prova.asc()).all()
                
                if not minhas_missoes:
                    st.info("Seu radar está limpo. Cadastre seu primeiro objetivo ao lado.")
                else:
                    for c in minhas_missoes:
                        # Estilização baseada na prioridade
                        border_color = "#3E2723" if c.prioridade == PrioridadeConcursoEnum.FOCO_TOTAL else "#D4AF37"
                        
                        with st.expander(f"📌 {c.nome} | {c.status.value}"):
                            st.markdown(f"""
                                <div style='border-left: 5px solid {border_color}; padding-left: 15px;'>
                                    <p style='margin-bottom: 5px;'><b>Banca:</b> {c.banca.sigla if c.banca else 'N/D'} | <b>Prioridade:</b> {c.prioridade.value}</p>
                                    <p style='margin-bottom: 15px;'>📅 <b>Data da Prova:</b> {c.data_prova.strftime('%d/%m/%Y') if c.data_prova else 'A definir'}</p>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # 🧬 INTERFACE DE AUTÓPSIA (Apenas se finalizado/prova realizada)
                            if c.status in [StatusConcursoEnum.PROVA_REALIZADA, StatusConcursoEnum.FINALIZADO]:
                                st.markdown("---")
                                st.markdown("#### 🩺 Autópsia da Prova (Seu 'Olho na Vaga' Pessoal)")
                                with st.form(f"autopsia_{c.id}"):
                                    col_r1, col_r2, col_r3 = st.columns(3)
                                    res_status = col_r1.selectbox("Resultado Final", [e.value for e in ResultadoConcursoEnum], 
                                                                  index=([e.value for e in ResultadoConcursoEnum].index(c.resultado_status.value) if c.resultado_status else 0))
                                    n_real = col_r2.number_input("Sua Nota", value=c.nota_real or 0.0)
                                    n_corte = col_r3.number_input("Nota de Corte", value=c.nota_corte or 0.0)
                                    
                                    posic = st.number_input("Sua Posição Final", value=c.posicao or 0, step=1)
                                    
                                    if st.form_submit_button("Registrar Desempenho Histórico"):
                                        with Session(get_engine()) as session:
                                            db_c = session.query(ConcursoRadar).get(c.id)
                                            db_c.resultado_status = next(e for e in ResultadoConcursoEnum if e.value == res_status)
                                            db_c.nota_real = n_real
                                            db_c.nota_corte = n_corte
                                            db_c.posicao = posic
                                            session.commit()
                                            st.success("Autópsia registrada. Seus dados alimentaram o histórico global.")
                                            st.rerun()
                            else:
                                if st.button("Marcar como Prova Realizada ✅", key=f"btn_done_{c.id}"):
                                    with Session(get_engine()) as session:
                                        db_c = session.query(ConcursoRadar).get(c.id)
                                        db_c.status = StatusConcursoEnum.PROVA_REALIZADA
                                        session.commit()
                                        st.rerun()

        # --- 🔄 CICLO DE FOCO (EM CONSTRUÇÃO) ---
        with tab_ciclo:
            st.info("🚀 O Motor de Ciclos baseado em Intercalação e Pomodoro será ativado na Fase 2.")

        # --- 🧬 EDITAL VIVO (EM CONSTRUÇÃO) ---
        with tab_edital:
            st.info("🧬 O Edital Vivo com progresso automatizado por questões será ativado na Fase 2.")

        # --- 🔥 LEI SECA ---
        with tab_leiseca:
            st.info("🔥 O Desafio de Micro-hábitos de Leitura de Legislação será ativado na Fase 2.")
        
    elif selecao == "Área do Professor":
        st.markdown("## 👨‍🏫 Área do Professor (Seed)")
        st.markdown("<p style='color: #7F8C8D; margin-top: -10px; margin-bottom: 30px;'>Gestão da base de conhecimento, bancas e questões.</p>", unsafe_allow_html=True)

        if not BANCO_PRONTO:
            st.error(f"⚠️ O sistema está aguardando a construção do banco de dados. Vá em 'Meu Perfil' e clique em 'Construir Tabelas'. Detalhe: {ERRO_BANCO}")
            st.stop()
            
        try:
            # 👇 AQUI É A CORREÇÃO: Pressione a tecla TAB uma vez antes do "tab_banca" para ele ficar "dentro" do try
            tab_banca, tab_disc, tab_orgao, tab_questao, tab_gerenciar, tab_simulados = st.tabs(["🏛️ 1. Bancas", "📚 2. Disciplinas & Assuntos", "🏢 3. Órgãos/Cargos", "✍️ 4. Nova Questão", "⚙️ 5. Gerenciar", "📝 6. Simulados"])

            # ABA 1: BANCAS
            with tab_banca:
                st.markdown("#### Cadastrar Nova Banca")
                # ... o resto do seu código continua aqui normalmente ...
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

            with tab_orgao:
                st.markdown("#### Gestão de Órgãos e Cargos")
                col_o, col_c = st.columns(2)
                with col_o:
                    with st.form("form_orgao_add"):
                        n_orgao = st.text_input("Nome do Órgão", placeholder="Ex: Prefeitura de Catende")
                        if st.form_submit_button("Salvar Órgão", type="primary"):
                            with Session(get_engine()) as s: 
                                s.add(Orgao(nome=n_orgao)); s.commit(); st.success("✅ Órgão Salvo!")
                with col_c:
                    with st.form("form_cargo_add"):
                        n_cargo = st.text_input("Nome do Cargo", placeholder="Ex: Analista de Controle Interno")
                        if st.form_submit_button("Salvar Cargo", type="primary"):
                            with Session(get_engine()) as s: 
                                s.add(Cargo(nome=n_cargo)); s.commit(); st.success("✅ Cargo Salvo!")

            with tab_questao:
                st.markdown("#### ✍️ Cadastrar Questão Completa")
                
                with Session(get_engine()) as session:
                    bancas = session.query(Banca).all()
                    assuntos = session.query(Assunto).all()
                    orgaos = session.query(Orgao).all()
                    cargos = session.query(Cargo).all()
                    
                    opcoes_banca = {b.sigla: b.id for b in bancas}
                    opcoes_assunto = {f"{a.disciplina.nome} - {a.nome}": a.id for a in assuntos} if assuntos else {}
                    opcoes_orgao = {o.nome: o.id for o in orgaos}
                    opcoes_cargo = {c.nome: c.id for c in cargos}
                
                if not opcoes_banca or not opcoes_assunto:
                    st.warning("⚠️ Você precisa cadastrar pelo menos 1 Banca e 1 Assunto nas abas anteriores.")
                else:
                    from streamlit_quill import st_quill
                    
                    st.markdown("**1. Defina o formato da questão:**")
                    tipo_q = st.radio("Formato:", ["Múltipla Escolha (ABCDE)", "Múltipla Escolha (ABCD)", "Certo/Errado (CE)"], horizontal=True, label_visibility="collapsed")
                    
                    st.markdown("**2. Preencha os dados:**")
                    with st.form("form_questao"):
                        # 🚀 NOVO: MARCAÇÃO DE QUESTÃO INÉDITA (Professor)
                        is_inedita_form = st.checkbox("🎯 Marcar como Questão Inédita (Baply)", value=False)
                        st.markdown("---")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            banca_sel = st.selectbox("Banca", options=list(opcoes_banca.keys()))
                        with col2:
                            assunto_sel = st.selectbox("Disciplina - Assunto", options=list(opcoes_assunto.keys()))
                        with col3:
                            ano_q = st.number_input("Ano", min_value=1990, max_value=2030, value=2024)
                        
                        col4, col5, col6, col7 = st.columns(4)
                        with col4:
                            orgao_sel = st.selectbox("Órgão", options=["Nenhum"] + list(opcoes_orgao.keys()))
                        with col5:
                            cargo_sel = st.selectbox("Cargo", options=["Nenhum"] + list(opcoes_cargo.keys()))
                        with col6:
                            esc_sel = st.selectbox("Escolaridade", options=["Nenhuma"] + [e.value for e in EscolaridadeEnum])
                        with col7:
                            carreira_sel = st.selectbox("Carreira", options=["Nenhuma"] + [c.value for c in CarreiraEnum])

                        st.markdown("**Enunciado da Questão:**")
                        enunciado = st_quill(placeholder="Cole o texto aqui, use negrito, tabelas, links...", key="quill_enunciado")
                        
                        st.markdown("---")
                        st.markdown(f"**Alternativas ({tipo_q}):**")
                        
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
                            st.info("No formato C/E, as alternativas 'Certo' e 'Errado' são geradas automaticamente.")
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
                                        id_orgao = opcoes_orgao[orgao_sel] if orgao_sel != "Nenhum" else None
                                        id_cargo = opcoes_cargo[cargo_sel] if cargo_sel != "Nenhum" else None
                                        val_esc = next((e for e in EscolaridadeEnum if e.value == esc_sel), None) if esc_sel != "Nenhuma" else None
                                        val_car = next((c for c in CarreiraEnum if c.value == carreira_sel), None) if carreira_sel != "Nenhuma" else None

                                        nova_q = Questao(
                                            enunciado_html=enunciado,
                                            ano=ano_q,
                                            banca_id=opcoes_banca[banca_sel],
                                            assunto_id=opcoes_assunto[assunto_sel],
                                            orgao_id=id_orgao,
                                            cargo_id=id_cargo,
                                            escolaridade=val_esc,
                                            carreira=val_car,
                                            comentario_html=comentario,
                                            is_inedita=is_inedita_form # 🚀 SALVA O STATUS INÉDITA NO BANCO
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
                                        
                                        st.success("🎉 Questão gravada com sucesso!")
                                        st.balloons()
                                    except Exception as e:
                                        session.rollback()
                                        st.error(f"Erro Crítico: {e}")
                                        
            with tab_gerenciar:
                st.markdown("#### ⚙️ Gerenciar e Corrigir Questões")
                
                with Session(get_engine()) as session:
                    bancas_prof = session.query(Banca).all()
                    assuntos_prof = session.query(Assunto).all()
                    
                with st.form("form_busca_prof"):
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        filtro_banca = st.multiselect("Banca", options=[b.sigla for b in bancas_prof])
                    with c2:
                        filtro_assunto = st.multiselect("Assunto", options=[a.nome for a in assuntos_prof])
                    with c3:
                        # 🚀 NOVO FILTRO DE INÉDITAS (Professor)
                        filtro_inedita = st.radio("Tipo:", ["Todas", "Apenas Inéditas", "Apenas Concursos"], horizontal=True)
                    
                    btn_buscar = st.form_submit_button("🔍 Buscar Questões", type="primary", use_container_width=True)
                
                if btn_buscar:
                    st.session_state.mgr_buscar = True
                    st.session_state.mgr_f_banca = filtro_banca
                    st.session_state.mgr_f_assunto = filtro_assunto
                    st.session_state.mgr_f_inedita = filtro_inedita
                    
                if st.session_state.get("mgr_buscar", False):
                    try:
                        with Session(get_engine()) as session:
                            query_prof = session.query(Questao).options(
                                joinedload(Questao.banca),
                                joinedload(Questao.assunto).joinedload(Assunto.disciplina)
                            )
                            
                            if st.session_state.mgr_f_banca:
                                query_prof = query_prof.join(Banca, Questao.banca_id == Banca.id).filter(Banca.sigla.in_(st.session_state.mgr_f_banca))
                            if st.session_state.mgr_f_assunto:
                                query_prof = query_prof.join(Assunto, Questao.assunto_id == Assunto.id).filter(Assunto.nome.in_(st.session_state.mgr_f_assunto))
                            
                            # 🚀 APLICA O FILTRO INÉDITA NA BUSCA DO PROFESSOR
                            v_inedita = st.session_state.get("mgr_f_inedita", "Todas")
                            if v_inedita == "Apenas Inéditas":
                                query_prof = query_prof.filter(Questao.is_inedita == True)
                            elif v_inedita == "Apenas Concursos":
                                query_prof = query_prof.filter(Questao.is_inedita == False)
                                
                            resultados = query_prof.all()
                            
                            if not resultados:
                                st.warning("Nenhuma questão encontrada com esses filtros.")
                            else:
                                st.success(f"Encontradas {len(resultados)} questões cadastradas.")
                                
                                for q in resultados:
                                    if q.assunto and q.assunto.disciplina:
                                        prefixo_disc = q.assunto.disciplina.nome[:3].upper()
                                    else:
                                        prefixo_disc = "GER"
                                        
                                    codigo_unico = f"BAP-{prefixo_disc}{q.id:04d}" 
                                    nome_banca = q.banca.sigla if q.banca else "Banca ND"
                                    nome_assunto = q.assunto.nome if q.assunto else "Assunto ND"
                                    
                                    # Selo Inédita no Acordeão do Professor
                                    tag_inedita = " 🔹 INÉDITA" if getattr(q, 'is_inedita', False) else ""
                                    
                                    with st.expander(f"🏷️ {codigo_unico} | {nome_banca} - {q.ano}{tag_inedita}"):
                                        st.markdown(f"**Assunto:** {nome_assunto}")
                                        st.markdown(f"<div style='background: #FAFAFA; padding: 10px; border-radius: 5px; font-size: 0.9rem; max-height: 100px; overflow-y: auto;'>{q.enunciado_html}</div>", unsafe_allow_html=True)
                                        
                                        col_edit, col_del = st.columns(2)
                                        with col_edit:
                                            if st.button(f"✏️ Editar", key=f"edit_{q.id}", use_container_width=True):
                                                st.toast(f"Preparando edição para o {codigo_unico}... (Fase 4)")
                                        with col_del:
                                            if st.button(f"🗑️ Inativar", key=f"del_{q.id}", use_container_width=True):
                                                st.toast("Rotina de arquivamento será ativada na Fase 4.")
                    except Exception as err:
                        st.error(f"Erro interno ao buscar: {err}")

    # 🚀 ABA 6: CONSTRUTOR DE SIMULADOS DE EDITAL
            with tab_simulados:
                st.markdown("#### 📝 Construtor de Simulados (Regras de Edital)")
                
                # Sub-menu interno usando o option_menu
                menu_sim = option_menu(None, ["1. Criar Simulado", "2. Adicionar Questões"], icons=["plus-circle", "list-check"], orientation="horizontal", styles={"nav-link": {"font-size": "14px"}})
                
                # --- PASSO A: CRIAR A "CASCA" DO SIMULADO ---
                if menu_sim == "1. Criar Simulado":
                    with st.form("form_novo_simulado"):
                        st.info("Defina as regras de penalidade fiéis ao edital do seu concurso.")
                        nome_sim = st.text_input("Nome do Simulado", placeholder="Ex: Simulado Reta Final - TCE/PE")
                        
                        # Usa o Enum para garantir a tipagem correta no banco
                        regra_sim = st.selectbox("Regra de Pontuação/Penalidade da Banca", [e.value for e in RegraPenalidadeEnum])
                        
                        if st.form_submit_button("💾 Criar Estrutura do Simulado", type="primary", use_container_width=True):
                            if not nome_sim:
                                st.error("❌ O simulado precisa de um nome.")
                            else:
                                with Session(get_engine()) as session:
                                    try:
                                        novo_sim = Simulado(
                                            nome=nome_sim,
                                            regra_penalidade=next(e for e in RegraPenalidadeEnum if e.value == regra_sim)
                                        )
                                        session.add(novo_sim)
                                        session.commit()
                                        st.success(f"✅ Simulado '{nome_sim}' criado com sucesso! Agora vá para a aba 'Adicionar Questões'.")
                                        st.balloons()
                                    except Exception as e:
                                        session.rollback()
                                        st.error(f"Erro ao criar (Verifique se o nome já existe): {e}")

                # --- PASSO B: INJETAR AS QUESTÕES LÁ DENTRO ---
                elif menu_sim == "2. Adicionar Questões":
                    with Session(get_engine()) as session:
                        # Carrega os simulados que acabamos de criar
                        simulados_disp = {s.nome: s.id for s in session.query(Simulado).all()}
                        bancas_s = session.query(Banca).all()
                        assuntos_s = session.query(Assunto).all()
                    
                    if not simulados_disp:
                        st.warning("⚠️ Você precisa criar um simulado na aba anterior primeiro.")
                    else:
                        sim_selecionado = st.selectbox("🎯 1. Selecione o Simulado Alvo:", list(simulados_disp.keys()))
                        st.markdown("---")
                        st.markdown("**🔍 2. Busque as Questões no Banco para Adicionar:**")
                        
                        with st.form("form_busca_add"):
                            c1, c2, c3 = st.columns(3)
                            with c1: fb = st.multiselect("Filtrar por Banca", [b.sigla for b in bancas_s])
                            with c2: fa = st.multiselect("Filtrar por Assunto", [a.nome for a in assuntos_s])
                            with c3: f_ine = st.radio("Tipo:", ["Todas", "Apenas Inéditas"], horizontal=True)
                            
                            buscar_btn = st.form_submit_button("Buscar Questões Disponíveis", use_container_width=True)
                            
                        # Usa o state para a tela não apagar quando clicarmos nos checkboxes
                        if buscar_btn:
                            st.session_state.sim_buscar = True
                            st.session_state.sim_fb = fb
                            st.session_state.sim_fa = fa
                            st.session_state.sim_ine = f_ine
                            
                        if st.session_state.get("sim_buscar", False):
                            with Session(get_engine()) as session:
                                query = session.query(Questao).options(joinedload(Questao.banca), joinedload(Questao.assunto).joinedload(Assunto.disciplina))
                                
                                if st.session_state.sim_fb: query = query.join(Banca, Questao.banca_id == Banca.id).filter(Banca.sigla.in_(st.session_state.sim_fb))
                                if st.session_state.sim_fa: query = query.join(Assunto, Questao.assunto_id == Assunto.id).filter(Assunto.nome.in_(st.session_state.sim_fa))
                                
                                v_ine = st.session_state.get("sim_ine", "Todas")
                                if v_ine == "Apenas Inéditas": query = query.filter(Questao.is_inedita == True)
                                
                                resultados = query.all()
                                
                                if not resultados:
                                    st.info("📭 Nenhuma questão encontrada no banco com esses filtros.")
                                else:
                                    st.success(f"{len(resultados)} questões prontas para inserção.")
                                    
                                    # Formulário de inserção em lote
                                    with st.form("form_add_lote"):
                                        st.markdown("Selecione as questões que farão parte deste simulado:")
                                        
                                        selecionadas = []
                                        for q in resultados:
                                            prefixo = q.assunto.disciplina.nome[:3].upper() if q.assunto else "GER"
                                            q_id = f"BAP-{prefixo}{q.id:04d}"
                                            banca_n = q.banca.sigla if q.banca else "ND"
                                            assunto_n = q.assunto.nome if q.assunto else "ND"
                                            
                                            # O segredo: se o chk for True, guardamos o ID da questão
                                            chk = st.checkbox(f"🏷️ {q_id} | {banca_n} | {assunto_n}", key=f"add_{q.id}")
                                            if chk:
                                                selecionadas.append(q.id)
                                                
                                        st.markdown("<br>", unsafe_allow_html=True)
                                        if st.form_submit_button("➕ Adicionar Lote Selecionado ao Simulado", type="primary", use_container_width=True):
                                            if not selecionadas:
                                                st.warning("⚠️ Marque pelo menos uma questão na caixa de seleção.")
                                            else:
                                                try:
                                                    id_sim = simulados_disp[sim_selecionado]
                                                    adicionadas = 0
                                                    
                                                    for q_add_id in selecionadas:
                                                        # Evita duplicidade no mesmo simulado
                                                        existe = session.query(SimuladoQuestao).filter_by(simulado_id=id_sim, questao_id=q_add_id).first()
                                                        if not existe:
                                                            session.add(SimuladoQuestao(simulado_id=id_sim, questao_id=q_add_id))
                                                            adicionadas += 1
                                                            
                                                    session.commit()
                                                    if adicionadas > 0:
                                                        st.success(f"✅ Sucesso! {adicionadas} questões foram vinculadas ao '{sim_selecionado}'.")
                                                    else:
                                                        st.info("As questões selecionadas já faziam parte deste simulado.")
                                                except Exception as e:
                                                    st.error(f"Erro ao vincular questões: {e}")

        except Exception as e:
            st.error(f"⚠️ Erro crítico na Área do Professor: {e}")

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
