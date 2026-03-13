import os
from sqlalchemy import create_engine

# 1. Puxa a URL do cofre (Secrets)
DATABASE_URL = os.environ.get("DATABASE_URL")

# 2. Ajuste automático de protocolo (O SQLAlchemy 2.0 exige 'postgresql://')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 3. Função para gerar o motor com 'pool_pre_ping' (testa a saúde da conexão antes de usar)
def get_engine():
    if not DATABASE_URL:
        raise ValueError("🚨 DATABASE_URL não encontrada! Verifique os Secrets do Streamlit.")
    return create_engine(DATABASE_URL, pool_pre_ping=True)
