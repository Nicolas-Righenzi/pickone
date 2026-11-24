from app import create_app, db
from config import Config
from app.models import Category, Item, User

# categoria: (descrizione, [nomi degli item])
# l'immagine di ogni item e' app/static/images/<nome>.jpg (es. Pizza -> pizza.jpg)
DATI = {
    "Food Battle": (
        "Sfida tra i piatti più amati: qual è il tuo preferito?",
        [
            "Pizza",
            "Sushi",
            "Hamburger",
            "Tacos",
            "Pasta al pomodoro",
            "Gelato",
            "Ramen",
            "Tiramisù",
        ],
    ),
    "Car Battle": (
        "Quale auto porteresti a casa? Scegli la tua preferita.",
        [
            "Ferrari",
            "Lamborghini",
            "Porsche 911",
            "Tesla Model S",
            "Fiat 500",
            "Mini Cooper",
            "Jeep Wrangler",
            "Ford Mustang",
        ],
    ),
}

def popola_db():
    """Inserisce categorie, item e admin se mancano (si puo' rilanciare senza duplicare)."""
    for nome, (descrizione, items) in DATI.items():
        esiste = db.session.scalar(db.select(Category).filter_by(name=nome))
        if esiste:
            continue

        categoria = Category(name=nome, description=descrizione)
        db.session.add(categoria)
        db.session.flush()  # così categoria.id è già disponibile

        for nome_item in items:
            db.session.add(Item(name=nome_item, category_id=categoria.id))
        print("Creata " + nome + " con " + str(len(items)) + " item")

    # utente admin di default
    email_admin = Config.ADMIN_EMAIL
    if db.session.scalar(db.select(User).filter_by(email=email_admin)) is None:
        admin = User(username="admin", email=email_admin, role="admin")
        admin.set_password("admin1234")
        db.session.add(admin)
        print("Creato utente admin (" + email_admin + " / admin1234)")

    db.session.commit()


# lanciandolo a mano (python seed.py) fa la stessa cosa che fa run.py all'avvio
if __name__ == "__main__":
    with create_app().app_context():
        popola_db()
    print("Fatto.")
