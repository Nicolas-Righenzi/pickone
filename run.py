import os
import subprocess
import sys

# Se le librerie non sono ancora installate le installa da solo e riparte
try:
    import flask_sqlalchemy  # noqa: F401  (serve solo a controllare)
except ImportError:
    print("Installo le librerie da requirements.txt (solo la prima volta)...")
    cartella = os.path.dirname(os.path.abspath(__file__))
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r",
                           os.path.join(cartella, "requirements.txt")])
    sys.exit(subprocess.call([sys.executable] + sys.argv))

from app import create_app
from seed import popola_db

app = create_app()  # crea anche le tabelle

# categorie, item e admin di default (se ci sono già non fa niente)
with app.app_context():
    popola_db()

if __name__ == "__main__":
    app.run(debug=True)
