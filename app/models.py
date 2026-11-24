import json
import re
import unicodedata
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from . import db, login_manager


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(10), nullable=False, default="user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == "admin"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300))

    items = db.relationship("Item", order_by="Item.id")


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)

    @property
    def image_file(self):
        # nome del file in static/images, ricavato dal nome dell'item:
        # "Pizza" -> pizza.jpg, "Tiramisù" -> tiramisu.jpg, "Fiat 500" -> fiat-500.jpg
        senza_accenti = unicodedata.normalize("NFKD", self.name).encode("ascii", "ignore").decode()
        slug = re.sub(r"[^a-z0-9]+", "-", senza_accenti.lower()).strip("-")
        return slug + ".jpg"

    @property
    def image_url(self):
        return "/static/images/" + self.image_file


class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    # "in_progress" oppure "completed"
    status = db.Column(db.String(20), nullable=False, default="in_progress")
    current_winner_id = db.Column(db.Integer, db.ForeignKey("item.id"))
    # posizione nella coda dello sfidante da mostrare
    next_index = db.Column(db.Integer, nullable=False, default=1)
    # lista degli id degli item (in json) nell'ordine in cui vengono mostrati
    queue_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    completed_at = db.Column(db.DateTime)

    category = db.relationship("Category")

    @property
    def totale_confronti(self):
        # con 8 item i confronti sono 7
        return len(json.loads(self.queue_json)) - 1


class TournamentItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey("tournament.id"), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"), nullable=False)
    final_position = db.Column(db.Integer, nullable=False)
