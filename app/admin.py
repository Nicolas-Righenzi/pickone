import json
from functools import wraps

from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from . import db
from .forms import CategoryForm, ItemForm
from .models import Category, Item, Tournament

bp = Blueprint("admin", __name__)


def admin_required(f):
    # va messo sotto @login_required
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return wrapper


def get_item_form():
    # il menu delle categorie si riempie con quelle che sono nel db
    form = ItemForm()
    categorie = db.session.scalars(db.select(Category).order_by(Category.name)).all()
    form.category_id.choices = [(c.id, c.name) for c in categorie]
    return form


def show_errors(form):
    for errori in form.errors.values():
        for errore in errori:
            flash(errore, "danger")


def item_in_uso(item):
    # vero se l'item e' dentro a un torneo (finito o no)
    tornei = db.session.scalars(
        db.select(Tournament).filter_by(category_id=item.category_id)).all()
    return any(item.id in json.loads(t.queue_json) for t in tornei)


@bp.route("/admin")
@login_required
@admin_required
def dashboard():
    categorie = db.session.scalars(db.select(Category).order_by(Category.name)).all()
    return render_template("admin.html", categories=categorie,
                           category_form=CategoryForm(), item_form=get_item_form())


@bp.route("/admin/category/add", methods=["POST"])
@login_required
@admin_required
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        db.session.add(Category(name=form.name.data, description=form.description.data))
        db.session.commit()
        flash("Categoria aggiunta.", "success")
    else:
        show_errors(form)
    return redirect(url_for("admin.dashboard"))


@bp.route("/admin/item/add", methods=["POST"])
@login_required
@admin_required
def add_item():
    form = get_item_form()
    if form.validate_on_submit():
        item = Item(name=form.name.data, category_id=form.category_id.data)
        db.session.add(item)
        db.session.commit()
        flash("Item aggiunto. Ricorda di mettere l'immagine in app/static/images/" + item.image_file, "success")
    else:
        show_errors(form)
    return redirect(url_for("admin.dashboard"))


@bp.route("/admin/item/<int:item_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_item(item_id):
    item = db.get_or_404(Item, item_id)
    if item_in_uso(item):
        flash("Non si può eliminare " + item.name + ": è già usato in dei tornei.", "warning")
    else:
        db.session.delete(item)
        db.session.commit()
        flash("Item eliminato.", "success")
    return redirect(url_for("admin.dashboard"))
