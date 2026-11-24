from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError

from . import db
from .models import User


def minuscolo(valore):
    # toglie gli spazi e mette tutto minuscolo (per le email)
    if valore:
        return valore.strip().lower()
    return valore


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[
        DataRequired("Inserisci uno username"),
        Length(min=3, max=30, message="Lo username deve avere da 3 a 30 caratteri"),
    ])
    email = StringField("Email", filters=[minuscolo], validators=[
        DataRequired("Inserisci l'email"),
        Length(max=120, message="Email troppo lunga"),
        Regexp(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", message="Email non valida"),
    ])
    password = PasswordField("Password", validators=[
        DataRequired("Inserisci la password"),
        Length(min=6, message="La password deve avere almeno 6 caratteri"),
    ])
    submit = SubmitField("Registrati")

    def validate_username(self, field):
        if db.session.scalar(db.select(User).filter_by(username=field.data)):
            raise ValidationError("Username già usato")

    def validate_email(self, field):
        if db.session.scalar(db.select(User).filter_by(email=field.data)):
            raise ValidationError("Email già registrata")


class LoginForm(FlaskForm):
    email = StringField("Email", filters=[minuscolo], validators=[
        DataRequired("Inserisci l'email"),
    ])
    password = PasswordField("Password", validators=[
        DataRequired("Inserisci la password"),
    ])
    submit = SubmitField("Accedi")


class CategoryForm(FlaskForm):
    name = StringField("Nome", validators=[
        DataRequired("Inserisci il nome della categoria"),
        Length(max=100, message="Nome categoria troppo lungo"),
    ])
    description = TextAreaField("Descrizione", validators=[
        Length(max=300, message="Descrizione troppo lunga (massimo 300 caratteri)"),
    ])
    submit = SubmitField("Aggiungi categoria")


class ItemForm(FlaskForm):
    # le scelte della categoria vengono messe in admin.py
    category_id = SelectField("Categoria", coerce=int)
    name = StringField("Nome", validators=[
        DataRequired("Inserisci il nome dell'item"),
        Length(max=100, message="Nome item troppo lungo"),
    ])
    submit = SubmitField("Aggiungi item")
