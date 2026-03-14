# backend/models.py
from datetime import datetime, timezone
import uuid
import enum
from typing import Optional # <-- IMPORTANTE: Adicionado para campos nulos
from sqlalchemy import String, Text, Integer, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

class Base(DeclarativeBase):
    pass

class AuditMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_active: Mapped[bool] = mapped_column(default=True, index=True)

# --- ENUMS PARA FILTROS INTELIGENTES ---
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

# --- CATÁLOGO ---
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

class Cargo(Base, AuditMixin):
    __tablename__ = 'tb_cargo'
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(150), index=True)

# --- AVALIAÇÃO ---
class DificuldadeEnum(enum.Enum):
    FACIL = "FACIL"
    MEDIA = "MEDIA"
    DIFICIL = "DIFICIL"

class Questao(Base, AuditMixin):
    __tablename__ = 'tb_questao'
    id: Mapped[int] = mapped_column(primary_key=True)
    
    enunciado_html: Mapped[str] = mapped_column(Text) 
    ano: Mapped[int] = mapped_column(index=True)
    dificuldade: Mapped[DificuldadeEnum] = mapped_column(Enum(DificuldadeEnum), default=DificuldadeEnum.MEDIA)
    
    # 🚀 NOVO CAMPO: Filtro de Inéditas adicionado
    is_inedita: Mapped[bool] = mapped_column(default=False, index=True)
    
    # Novos campos de metadados (Usando Optional)
    escolaridade: Mapped[Optional[EscolaridadeEnum]] = mapped_column(Enum(EscolaridadeEnum), nullable=True, index=True)
    carreira: Mapped[Optional[CarreiraEnum]] = mapped_column(Enum(CarreiraEnum), nullable=True, index=True)
    
    comentario_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    video_explicacao_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Chaves Estrangeiras (IDs Opcionais usam Optional)
    assunto_id: Mapped[int] = mapped_column(ForeignKey('tb_assunto.id'), index=True)
    banca_id: Mapped[int] = mapped_column(ForeignKey('tb_banca.id'), index=True)
    orgao_id: Mapped[Optional[int]] = mapped_column(ForeignKey('tb_orgao.id'), index=True, nullable=True)
    cargo_id: Mapped[Optional[int]] = mapped_column(ForeignKey('tb_cargo.id'), index=True, nullable=True)
    
    # RELACIONAMENTOS (Se a ForeignKey é opcional, o relacionamento também é)
    banca: Mapped["Banca"] = relationship()
    assunto: Mapped["Assunto"] = relationship()
    orgao: Mapped[Optional["Orgao"]] = relationship()
    cargo: Mapped[Optional["Cargo"]] = relationship()
    alternativas: Mapped[list["Alternativa"]] = relationship(back_populates="questao", cascade="all, delete-orphan")

class Alternativa(Base):
    __tablename__ = 'tb_alternativa'
    id: Mapped[int] = mapped_column(primary_key=True)
    questao_id: Mapped[int] = mapped_column(ForeignKey('tb_questao.id'))
    
    texto_html: Mapped[str] = mapped_column(Text) 
    is_correta: Mapped[bool] = mapped_column(default=False)
    letra: Mapped[str] = mapped_column(String(1)) 
    
    questao: Mapped["Questao"] = relationship(back_populates="alternativas")

# --- ENGAJAMENTO ---
class HistoricoResolucao(Base):
    __tablename__ = 'tb_historico_resolucao'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    questao_id: Mapped[int] = mapped_column(ForeignKey('tb_questao.id'), index=True)
    
    # Usando Optional
    alternativa_selecionada_id: Mapped[Optional[int]] = mapped_column(ForeignKey('tb_alternativa.id'), nullable=True)
    acertou: Mapped[bool] = mapped_column(index=True)
    tempo_gasto_segundos: Mapped[Optional[int]] = mapped_column(nullable=True)
    
    resolvido_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
