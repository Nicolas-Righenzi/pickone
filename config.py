import os
from dotenv import load_dotenv

# legge il file .env (se esiste)
load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///pickone.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # chi si registra con questa email diventa admin
    ADMIN_EMAIL = "admin@pickone.local"
