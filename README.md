# PickOne – Your Personal Tournament

Web app Flask: un utente registrato sceglie una categoria (Food Battle, Car Battle), confronta le immagini due alla volta e ottiene la sua classifica personale. Ogni utente ha classifiche indipendenti. L'admin gestisce categorie e item.

## Stack

Flask 3.1.3, Werkzeug 3.1.9, Flask-SQLAlchemy 3.1.1 (SQLAlchemy 2.x), Flask-Login 0.6.3, Flask-WTF 1.2.2, python-dotenv 1.2.3, SQLite, Bootstrap 5.3 (CDN).

## Avvio

Dalla cartella `pickone/`:

```
python -m venv venv
venv\Scripts\activate          # Mac/Linux: source venv/bin/activate
python run.py
```

Al primo avvio `run.py` fa tutto da solo: installa le librerie di `requirements.txt`, crea il database (`instance/pickone.db`), inserisce le 2 categorie con 8 item e l'utente admin. L'app parte su http://127.0.0.1:5000.

Il file `.env` è facoltativo (serve solo per cambiare `SECRET_KEY` o `DATABASE_URL`, vedi `.env.example`). Se avevi già avviato una versione precedente, cancella `instance/pickone.db`.

## Immagini

Le immagini stanno in `app/static/images/` e si collegano agli item **dal nome**: l'item "Pizza" usa `pizza.jpg`, "Tiramisù" usa `tiramisu.jpg`, "Fiat 500" usa `fiat-500.jpg` (minuscolo, senza accenti, spazi → trattino, sempre `.jpg`).

Nel progetto ci sono già 16 immagini segnaposto (un colore con il nome): per usare foto vere basta sostituire i file tenendo lo stesso nome. Se aggiungi un item dall'admin, copia a mano la sua immagine nella cartella (l'admin mostra il nome file atteso).

## Admin

Creato da solo al primo avvio: email `admin@pickone.local`, password `admin1234`.
Chi si registra con quell'email diventa admin, tutti gli altri sono `user`.

Dal menu **Admin**: aggiungi una categoria, poi aggiungi i suoi item (solo il nome, poi copi l'immagine nella cartella; servono almeno 2 item per giocare). Un item già usato in un torneo non si può eliminare.

## Come funziona il torneo

1. Gli item della categoria vengono mescolati e l'ordine è salvato nel database.
2. Il primo item è il vincitore attuale (`current_winner`).
3. Ad ogni turno si confronta il vincitore attuale con l'item successivo e l'utente clicca il preferito.
4. Il perdente prende la posizione più bassa libera (8, 7, 6, ...), il vincitore resta in gara.
5. Dopo 7 confronti l'ultimo vincitore è in posizione 1. Lo stato è nel database, quindi si può riprendere dopo.

La logica è in `app/tournament.py`: `start_tournament`, `get_current_matchup`, `apply_choice`.

## Struttura

```
app/__init__.py     crea l'app
app/models.py       tabelle
app/forms.py        form
app/auth.py         register / login / logout
app/routes.py       home, categorie, torneo, my rankings
app/tournament.py   logica del torneo
app/admin.py        area admin
config.py  run.py  seed.py
```

## Verifica rapida

1. `python run.py`
2. Registrati, fai login, apri "Food Battle" → "Avvia torneo"
3. Fai le 7 scelte → compare la classifica
4. Menu "My Rankings": c'è il torneo con i primi 3
5. Logout, login come admin, menu "Admin": aggiungi categoria e item, elimina un item
