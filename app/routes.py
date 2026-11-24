from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user

from . import db
from .models import Category, Tournament
from .tournament import start_tournament, get_current_matchup, apply_choice, get_ranking

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    categorie = db.session.scalars(db.select(Category).order_by(Category.name)).all()
    return render_template("index.html", categories=categorie)


@bp.route("/category/<int:category_id>")
def category(category_id):
    cat = db.get_or_404(Category, category_id)
    return render_template("category.html", category=cat)


def get_my_tournament(tournament_id):
    # un utente puo' vedere solo i suoi tornei
    torneo = db.get_or_404(Tournament, tournament_id)
    if torneo.user_id != current_user.id:
        abort(403)
    return torneo


@bp.route("/tournament/start/<int:category_id>")
@login_required
def start(category_id):
    cat = db.get_or_404(Category, category_id)
    torneo = start_tournament(current_user, cat)
    if torneo is None:
        flash("Servono almeno 2 elementi per fare un torneo.", "warning")
        return redirect(url_for("main.category", category_id=cat.id))
    return redirect(url_for("main.show_tournament", tournament_id=torneo.id))


@bp.route("/tournament/<int:tournament_id>")
@login_required
def show_tournament(tournament_id):
    torneo = get_my_tournament(tournament_id)
    if torneo.status == "completed":
        return redirect(url_for("main.results", tournament_id=torneo.id))

    sinistra, destra = get_current_matchup(torneo)
    # un confronto si' e uno no scambio i lati, cosi' il vincitore non sta sempre a sinistra
    if torneo.next_index % 2 == 0:
        sinistra, destra = destra, sinistra
    return render_template("tournament.html", torneo=torneo, sinistra=sinistra, destra=destra)


@bp.route("/tournament/<int:tournament_id>/choose", methods=["POST"])
@login_required
def choose(tournament_id):
    torneo = get_my_tournament(tournament_id)
    if torneo.status == "completed":
        return redirect(url_for("main.results", tournament_id=torneo.id))

    try:
        winner_id = int(request.form.get("winner_id", ""))
    except ValueError:
        abort(400)

    if not apply_choice(torneo, winner_id):
        flash("Scelta non valida, riprova.", "warning")
        return redirect(url_for("main.show_tournament", tournament_id=torneo.id))

    if torneo.status == "completed":
        return redirect(url_for("main.results", tournament_id=torneo.id))
    return redirect(url_for("main.show_tournament", tournament_id=torneo.id))


@bp.route("/tournament/<int:tournament_id>/results")
@login_required
def results(tournament_id):
    torneo = get_my_tournament(tournament_id)
    if torneo.status != "completed":
        return redirect(url_for("main.show_tournament", tournament_id=torneo.id))
    return render_template("results.html", torneo=torneo, classifica=get_ranking(torneo))


@bp.route("/my-rankings")
@login_required
def my_rankings():
    tornei = db.session.scalars(
        db.select(Tournament)
        .filter_by(user_id=current_user.id, status="completed")
        .order_by(Tournament.completed_at.desc())
    ).all()
    # per ogni torneo prendo i primi 3 della classifica
    classifiche = [(t, get_ranking(t, 3)) for t in tornei]
    return render_template("my_rankings.html", classifiche=classifiche)
