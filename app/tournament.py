import json
import random
from datetime import datetime

from . import db
from .models import Item, Tournament, TournamentItem


def start_tournament(user, category):
    # crea un torneo nuovo: gli item vengono mescolati e salvati nel db
    ids = [item.id for item in category.items]
    if len(ids) < 2:
        return None

    random.shuffle(ids)
    torneo = Tournament(
        user_id=user.id,
        category_id=category.id,
        status="in_progress",
        current_winner_id=ids[0],  # all'inizio il vincitore e' il primo della coda
        next_index=1,
        queue_json=json.dumps(ids),
    )
    db.session.add(torneo)
    db.session.commit()
    return torneo


def get_current_matchup(torneo):
    # restituisce (vincitore attuale, sfidante), oppure None se il torneo e' finito
    queue = json.loads(torneo.queue_json)
    if torneo.next_index >= len(queue):
        return None

    vincitore = db.session.get(Item, torneo.current_winner_id)
    sfidante = db.session.get(Item, queue[torneo.next_index])
    return vincitore, sfidante


def apply_choice(torneo, winner_id):
    # registra la scelta dell'utente, restituisce False se winner_id non e' valido
    queue = json.loads(torneo.queue_json)
    sfidante_id = queue[torneo.next_index]

    if winner_id == torneo.current_winner_id:
        perdente_id = sfidante_id
    elif winner_id == sfidante_id:
        perdente_id = torneo.current_winner_id
    else:
        return False

    # il perdente prende la posizione piu' bassa ancora libera (8, 7, 6, ...)
    posizione = len(queue) - torneo.next_index + 1
    db.session.add(TournamentItem(
        tournament_id=torneo.id, item_id=perdente_id, final_position=posizione))

    torneo.current_winner_id = winner_id
    torneo.next_index += 1

    # finiti i confronti, l'ultimo vincitore e' primo
    if torneo.next_index >= len(queue):
        db.session.add(TournamentItem(
            tournament_id=torneo.id, item_id=winner_id, final_position=1))
        torneo.status = "completed"
        torneo.completed_at = datetime.now()

    db.session.commit()
    return True


def get_ranking(torneo, limit=None):
    # classifica del torneo: lista di (posizione, item) in ordine di posizione
    query = (
        db.select(TournamentItem.final_position, Item)
        .select_from(TournamentItem)
        .join(Item, Item.id == TournamentItem.item_id)
        .where(TournamentItem.tournament_id == torneo.id)
        .order_by(TournamentItem.final_position)
    )
    if limit:
        query = query.limit(limit)
    return db.session.execute(query).all()
