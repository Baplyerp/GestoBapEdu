import os
from sqlalchemy import create_engine
# Importamos a nossa Base e todos os modelos que você acabou de criar!
from backend.models import Base 

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def get_engine():
    if not DATABASE_URL:
        raise ValueError("🚨 DATABASE_URL não encontrada! Verifique os Secrets.")
    return create_engine(DATABASE_URL, pool_pre_ping=True)

# NOVA FUNÇÃO: O "Gatilho" de criação das tabelas
def init_db():
    engine = get_engine()
    # O comando mágico que lê os modelos e cria as tabelas no Supabase
    Base.metadata.create_all(bind=engine)
