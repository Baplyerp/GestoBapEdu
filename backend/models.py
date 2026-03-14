# backend/models.py
from datetime import datetime, timezone
import uuid
import enum
from typing import Optional 
from sqlalchemy import String, Text, Integer, Boolean, ForeignKey, DateTime, Enum, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

class Base(DeclarativeBase):
    pass

class AuditMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_active: Mapped[bool] = mapped_column(default=True, index=True)

# --- ENUMS ---
class EscolaridadeEnum(enum.Enum):
    MEDIO = "Médio"
    SUPERIOR = "Superior"

class CarreiraEnum(enum.Enum):
    CONTROLE = "Controle e Gestão"
    FISCAL = "Fiscal"
    ADMINISTRATIVA = "Administrativa"
    TRIBUNAIS = "Tribunais"
    POLICIAL = "Policial"
    EDUCACAO = "Educação"
    SAUDE = "Saúde"
    OUTROS = "Outros"

class RegraPenalidadeEnum(enum.Enum):
    PADRAO = "Padrão (1 Certa = +1 | Errada = 0)"
    CEBRASPE_1X1 = "CEBRASPE 1x1 (1 Errada anula 1 Certa)"
    CEBRASPE_MEIO = "CEBRASPE 0.5 (1 Errada anula 0.5 Certa)"

class StatusConcursoEnum(enum.Enum):
    PREVISTO = "Previsto / Boato"
    SOLICITADO = "Solicitado"
    AUTORIZADO = "Autorizado"
    BANCA_DEFINIDA = "Banca Definida"
    EDITAL_LANCADO = "Edital Lançado"
    PROVA_REALIZADA = "Prova Realizada"
    FINALIZADO = "Finalizado / Homologado"

class PrioridadeConcursoEnum(enum.Enum):
    FOCO_TOTAL = "Foco Total (O Alvo)"
    ESCADA = "Concurso Escada"
    TESTE = "Concurso Treino"
    SECUNDARIO = "Secundário"

class ResultadoConcursoEnum(enum.Enum):
    APROVADO_VAGAS = "Aprovado dentro das vagas"
    APROVADO_CR = "Aprovado no Cadastro Reserva"
    REPROVADO_CORTE = "Reprovado (Nota de Corte)"
    REPROVADO_MINIMOS = "Reprovado (Mínimos por matéria)"
    AUSENTE = "Ausente / Excluído"

# --- CATÁLOGO BASE ---
class Disciplina(Base, AuditMixin):
    __tablename__ = 'tb_disciplina'
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    assuntos: Mapped[list["Assunto"]] = relationship(back_populates="disciplina")

class Assunto(Base, AuditMixin):
    __tablename__ = 'tb_assunto'
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(150))
    disciplina_id: Mapped[int] = mapped_column(ForeignKey('tb_disciplina.id'))
    disciplina: Mapped["Disciplina"] = relationship(back_populates="assuntos")

class Banca(Base, AuditMixin):
    __tablename__ = 'tb_banca'
    id: Mapped[int] = mapped_column(primary_key=True)
    sigla: Mapped[str] = mapped_column(String(20), unique=True)
    nome: Mapped[str] = mapped_column(String(100))

class Orgao(Base, AuditMixin):
    __tablename__ = 'tb_orgao'
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

class Cargo(Base, AuditMixin):
    __tablename__ = 'tb_cargo'
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(150), index=True)

# --- MOTOR DE AVALIAÇÃO ---
class Questao(Base, AuditMixin):
    __tablename__ = 'tb_questao'
    id: Mapped[int] = mapped_column(primary_key=True)
    enunciado_html: Mapped[str] = mapped_column(Text) 
    ano: Mapped[int] = mapped_column(index=True)
    dificuldade: Mapped[str] = mapped_column(String(20), default="MEDIA")
    is_inedita: Mapped[bool] = mapped_column(default=False, index=True)
    escolaridade: Mapped[Optional[EscolaridadeEnum]] = mapped_column(Enum(EscolaridadeEnum), nullable=True)
    carreira: Mapped[Optional[CarreiraEnum]] = mapped_column(Enum(CarreiraEnum), nullable=True)
    comentario_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    assunto_id: Mapped[int] = mapped_column(ForeignKey('tb_assunto.id'), index=True)
    banca_id: Mapped[int] = mapped_column(ForeignKey('tb_banca.id'), index=True)
    orgao_id: Mapped[Optional[int]] = mapped_column(ForeignKey('tb_orgao.id'), nullable=True)
    cargo_id: Mapped[Optional[int]] = mapped_column(ForeignKey('tb_cargo.id'), nullable=True)
    
    alternativas: Mapped[list["Alternativa"]] = relationship(back_populates="questao", cascade="all, delete-orphan")

class Alternativa(Base):
    __tablename__ = 'tb_alternativa'
    id: Mapped[int] = mapped_column(primary_key=True)
    questao_id: Mapped[int] = mapped_column(ForeignKey('tb_questao.id'))
    texto_html: Mapped[str] = mapped_column(Text) 
    is_correta: Mapped[bool] = mapped_column(default=False)
    letra: Mapped[str] = mapped_column(String(1)) 
    questao: Mapped["Questao"] = relationship(back_populates="alternativas")

# --- RADAR E SIMULADOS ---
class ConcursoRadar(Base, AuditMixin):
    __tablename__ = 'tb_concurso_radar'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    nome: Mapped[str] = mapped_column(String(200))
    banca_id: Mapped[Optional[int]] = mapped_column(ForeignKey('tb_banca.id'))
    orgao_id: Mapped[Optional[int]] = mapped_column(ForeignKey('tb_orgao.id'))
    
    banca: Mapped[Optional["Banca"]] = relationship()
    orgao: Mapped[Optional["Orgao"]] = relationship()
    
    status: Mapped[StatusConcursoEnum] = mapped_column(Enum(StatusConcursoEnum), default=StatusConcursoEnum.PREVISTO)
    prioridade: Mapped[PrioridadeConcursoEnum] = mapped_column(Enum(PrioridadeConcursoEnum), default=PrioridadeConcursoEnum.SECUNDARIO)
    data_prova: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    resultado_status: Mapped[Optional[ResultadoConcursoEnum]] = mapped_column(Enum(ResultadoConcursoEnum), nullable=True)
    nota_real: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    nota_corte: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    posicao: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

class EditalItem(Base):
    __tablename__ = 'tb_edital_item'
    id: Mapped[int] = mapped_column(primary_key=True)
    concurso_id: Mapped[int] = mapped_column(ForeignKey('tb_concurso_radar.id'), index=True)
    assunto_id: Mapped[int] = mapped_column(ForeignKey('tb_assunto.id'))
    lido_teoria: Mapped[bool] = mapped_column(default=False)
    revisado: Mapped[bool] = mapped_column(default=False)

# --- 🚀 MUDANÇA AQUI: SESSÃO DE ESTUDO ADAPTADA ---
class SessaoEstudo(Base, AuditMixin):
    """Registro manual de horas (espelho do Estudaqui)"""
    __tablename__ = 'tb_sessao_estudo'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    disciplina_id: Mapped[int] = mapped_column(ForeignKey('tb_disciplina.id'))
    duracao_segundos: Mapped[int] = mapped_column(Integer) 
    foco_score: Mapped[int] = mapped_column(Integer, default=3)
    # 🚀 NOVO: Para o seu diário de bordo
    observacoes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # 🚀 NOVO: Permite lançar estudos com datas passadas
    data_sessao: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Simulado(Base, AuditMixin):
    __tablename__ = 'tb_simulado'
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(200), unique=True)
    regra_penalidade: Mapped[RegraPenalidadeEnum] = mapped_column(Enum(RegraPenalidadeEnum), default=RegraPenalidadeEnum.PADRAO)

class SimuladoQuestao(Base):
    __tablename__ = 'tb_simulado_questao'
    id: Mapped[int] = mapped_column(primary_key=True)
    simulado_id: Mapped[int] = mapped_column(ForeignKey('tb_simulado.id'))
    questao_id: Mapped[int] = mapped_column(ForeignKey('tb_questao.id'))

class HistoricoResolucao(Base):
    __tablename__ = 'tb_historico_resolucao'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    questao_id: Mapped[int] = mapped_column(ForeignKey('tb_questao.id'), index=True)
    alternativa_selecionada_id: Mapped[Optional[int]] = mapped_column(ForeignKey('tb_alternativa.id'), nullable=True)
    acertou: Mapped[bool] = mapped_column(index=True)
    tempo_gasto_segundos: Mapped[Optional[int]] = mapped_column(nullable=True)
    resolvido_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class SessaoEstudo(Base, AuditMixin):
    __tablename__ = 'tb_sessao_estudo'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    disciplina_id: Mapped[int] = mapped_column(ForeignKey('tb_disciplina.id'))
    
    # 🚀 ADICIONE ESTA LINHA PARA O JOINEDLOAD FUNCIONAR:
    disciplina: Mapped["Disciplina"] = relationship()
    
    duracao_segundos: Mapped[int] = mapped_column(Integer) 
    foco_score: Mapped[int] = mapped_column(Integer, default=3)
    observacoes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    data_sessao: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
