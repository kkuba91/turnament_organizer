"""
test_suspensions.py

Tests for player suspensions and their persistence across tournament reopen.
Covers:
1. A player added during a round is shown as suspended in all previous rounds
   and starts playing from the next round (also after reopening the tournament).
2. Suspensions set by the user are persisted in the database.
3. A player playing a round and suspended from the next one is shown as
   "Future suspended" with the last round they play.
"""

import sys
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from Application.actions import Actions
from Application.turnament import Turnament
from Resources import SystemType
from sqlalchemy import create_engine


def _new_db():
    db_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    return f"sqlite:///{db_file.name}"


def _add_players(turnament, quantity=5, elo=0):
    for index in range(quantity):
        turnament.add_player(
            name=f"Player{index}",
            surname=f"Surname{index}",
            sex="male",
            city="",
            category="IV",
            elo=elo,
        )


def _complete_round(turnament):
    for table_nr in turnament._rounds[turnament._act_round_nr - 1].tables:
        turnament.add_result(table_nr, 1.0)
    turnament.apply_round_results()


def _reopen(url):
    engine = create_engine(url)
    return Turnament(name="Test Tournament", engine=engine)


def test_player_added_mid_round_is_suspended_after_reopen():
    url = _new_db()
    engine = create_engine(url)
    turnament = Turnament(name="Test Tournament", engine=engine)
    turnament.set_system(SystemType.SWISS)
    _add_players(turnament, quantity=5)
    turnament.begin(rounds=3)

    turnament.add_player(
        name="Late",
        surname="Entry",
        sex="male",
        category="IV",
        elo=0,
    )
    late = next(p for p in turnament._players if p.name == "Late")
    assert late.id == 6
    assert late.is_suspended(1)

    engine.dispose()
    reopened = _reopen(url)
    late = next(p for p in reopened._players if p.name == "Late")

    # The suspension is restored from the database.
    assert late.id == 6
    assert late.is_suspended(1)
    assert late in reopened.get_suspended_players(1)

    # The player is listed as absent in the round with the next round info.
    absent = {p.id: plays_in for p, plays_in in reopened.get_round_absent_players(1)}
    assert absent[late.id] == 2
    assert 5 in reopened.get_round_participants(1)

    # Round data returned to the frontend contains the extra information.
    actions = Actions("test_mid_round_add")
    actions.turnament = reopened
    round_data = actions.turnament_round(nr=1)
    suspended = {p["id"]: p for p in round_data["round"]["suspended"]}
    assert suspended[late.id]["plays_in"] == 2
    # The player was added in the still-unfinished current round.
    assert suspended[late.id]["added_in_round"] == 1
    assert suspended[late.id]["can_edit"] is True

    # The new player takes part in the next round.
    _complete_round(reopened)
    reopened.next_round()
    assert late.id in reopened.get_round_participants(2)


def test_mid_round_player_delete_cleans_persistence():
    url = _new_db()
    engine = create_engine(url)
    turnament = Turnament(name="Test Tournament", engine=engine)
    turnament.set_system(SystemType.SWISS)
    _add_players(turnament, quantity=5)
    turnament.begin(rounds=3)

    turnament.add_player(
        name="Late",
        surname="Entry",
        sex="male",
        category="IV",
        elo=0,
    )
    late = next(p for p in turnament._players if p.name == "Late")
    assert any(
        row["player_id"] == late.id for row in turnament.sql.read_suspensions_info()
    )
    assert any(
        row["player_id"] == late.id for row in turnament.sql.read_registrations_info()
    )

    assert turnament.del_player(name=late.name, surname=late.surname) is True
    assert not any(
        row["player_id"] == late.id for row in turnament.sql.read_suspensions_info()
    )
    assert not any(
        row["player_id"] == late.id for row in turnament.sql.read_registrations_info()
    )


def test_empty_delete_filters_do_not_wipe_tables():
    url = _new_db()
    engine = create_engine(url)
    turnament = Turnament(name="Test Tournament", engine=engine)
    turnament.set_system(SystemType.SWISS)
    _add_players(turnament, quantity=5)
    turnament.begin(rounds=3)

    player = next(p for p in turnament._players if p.name == "Player0")
    turnament.suspend_player(player=player, rounds=[2, 3])
    assert len(turnament.sql.read_suspensions_info()) == 2

    # Calling the new delete helpers without filters must be a no-op.
    turnament.sql.remove_suspension()
    turnament.sql.remove_registration()
    assert len(turnament.sql.read_suspensions_info()) == 2


def test_suspension_is_persisted_and_skips_pairing():
    url = _new_db()
    engine = create_engine(url)
    turnament = Turnament(name="Test Tournament", engine=engine)
    turnament.set_system(SystemType.SWISS)
    _add_players(turnament, quantity=5)
    turnament.begin(rounds=3)

    player = next(p for p in turnament._players if p.name == "Player0")
    turnament.suspend_player(player=player, rounds=range(2, 4))
    assert player.is_suspended(2)
    assert player.is_suspended(3)

    engine.dispose()
    reopened = _reopen(url)
    player = next(p for p in reopened._players if p.name == "Player0")
    assert player.is_suspended(2)
    assert player.is_suspended(3)

    _complete_round(reopened)
    reopened.next_round()
    assert player.id not in reopened.get_round_participants(2)
    absent = {p.id: plays_in for p, plays_in in reopened.get_round_absent_players(2)}
    assert player.id in absent


def test_future_suspended_player_in_active_round():
    url = _new_db()
    engine = create_engine(url)
    turnament = Turnament(name="Test Tournament", engine=engine)
    turnament.set_system(SystemType.SWISS)
    _add_players(turnament, quantity=5)
    turnament.begin(rounds=4)

    actions = Actions("test_future_suspended")
    actions.turnament = turnament

    # Mark a player who plays round 1 as suspended from round 2 onwards.
    player = next(p for p in turnament._players if p.name == "Player0")
    turnament.suspend_player(player=player, rounds=range(2, 5))
    assert player.id in turnament.get_round_participants(1)

    round_data = actions.turnament_round(nr=1)["round"]
    future = {p["id"]: p for p in round_data["future_suspended"]}
    assert future[player.id]["plays_until"] == 1
    assert future[player.id]["can_unsuspend"] is True
    assert not any(p["id"] == player.id for p in round_data["suspended"])

    # The marking can be cancelled while the round is still active.
    actions.players_suspend(suspended=[], unsuspended=[player.id])
    assert not player.is_suspended(2)
    round_data = actions.turnament_round(nr=1)["round"]
    assert not any(p["id"] == player.id for p in round_data["future_suspended"])

    # Set it again - the player is listed as suspended from the next round.
    turnament.suspend_player(player=player, rounds=range(2, 5))
    _complete_round(turnament)
    turnament.next_round()
    assert player.id not in turnament.get_round_participants(2)

    engine.dispose()
    reopened = _reopen(url)
    actions.turnament = reopened

    # From round 2 on the player is shown as "Suspended".
    round_data = actions.turnament_round(nr=2)["round"]
    suspended = {p["id"]: p for p in round_data["suspended"]}
    assert player.id in suspended
    assert suspended[player.id]["plays_in"] is None
    assert not round_data["future_suspended"]

    # In the earlier round the player is shown as "Future suspended", but the
    # option to cancel is available only for the active round.
    round_data = actions.turnament_round(nr=1)["round"]
    future = {p["id"]: p for p in round_data["future_suspended"]}
    assert player.id in future
    assert future[player.id]["can_unsuspend"] is False
