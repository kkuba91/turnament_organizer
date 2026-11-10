"""
test_pairing_bye_reopen.py

Regression test for an odd number of active players after reopening a
tournament. The bye must always be assigned and reported, even when the
fantom pauser is paired as the white player and even when another player
already had a bye earlier in the tournament.

Reproduces the case where a player joined mid-tournament, played round 2 and
was then suspended from round 3 onwards. Three players remain paired, one gets
a bye. Previously the bye table was hidden without setting ``Round.pausing``,
so the UI showed a missing player and no bye.
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


def _add_players(turnament):
    players = [
        ("Magnus", 2810, "male", "GM"),
        ("Garri", 2721, "male", "GM"),
        ("Zbig", 1621, "male", "II"),
        ("Kuba", 1620, "male", "II"),
        ("Asia", 0, "female", "wc"),
    ]
    for name, elo, sex, category in players:
        turnament.add_player(
            name=name,
            surname=name,
            sex=sex,
            category=category,
            elo=elo,
        )


def _players_at_tables(round_obj):
    ids = set()
    for table in round_obj.tables.values():
        ids.add(table.w_player.id)
        ids.add(table.b_player.id)
    return ids


def test_bye_is_reported_after_reopen_when_player_leaves():
    url = _new_db()
    engine = create_engine(url)
    turnament = Turnament(name="Test Tournament", engine=engine)
    turnament.set_system(SystemType.SWISS)
    _add_players(turnament)
    turnament.begin(rounds=5)

    # With 5 players, #5 (Asia) gets the bye in round 1.
    assert turnament._rounds[0].pausing == 5

    turnament.add_result(1, 1.0)
    turnament.add_result(2, 0.0)

    # A sixth player joins while round 1 is still active. He is registered for
    # round 1 but starts playing in round 2.
    turnament.add_player(
        name="Late",
        surname="Entry",
        sex="male",
        category="III",
        elo=1511,
    )
    late = next(p for p in turnament._players if p.name == "Late")
    assert late.id == 6

    actions = Actions("test_pairing_bye_reopen")
    actions.turnament = turnament
    assert actions.apply_round() is True

    # Late Entry plays round 2.
    assert late.id in _players_at_tables(turnament._rounds[1])

    turnament.add_result(1, 0.5)
    turnament.add_result(2, 0.0)
    turnament.add_result(3, 0.0)

    # Late Entry leaves after round 2.
    turnament.suspend_player(late, range(3, 6))
    engine.dispose()

    # Close and reopen the tournament before moving on to round 3.
    reopened = Turnament(name="Test Tournament", engine=create_engine(url))
    actions = Actions("test_pairing_bye_reopen")
    actions.turnament = reopened
    late = next(p for p in reopened._players if p.name == "Late")
    assert late.is_suspended(3)

    assert actions.apply_round() is True
    round_three = reopened._rounds[2]

    active_ids = {p.id for p in reopened._players if p.id > 0 and not p.is_suspended(3)}
    assert active_ids == {1, 2, 3, 4, 5}

    # A bye must be assigned and shown.
    assert round_three.pausing > 0
    assert round_three.pausing in active_ids
    assert round_three.pausing != late.id

    # Every active player must be either at a table or marked as pausing.
    displayed_ids = {round_three.pausing}
    visible_round = round_three.get()
    for table in visible_round["tables"]:
        assert table["white"]["id"] > 0
        assert table["black"]["id"] > 0
        displayed_ids.add(table["white"]["id"])
        displayed_ids.add(table["black"]["id"])

    assert visible_round["pauser"] == round_three.pausing
    assert displayed_ids == active_ids
    assert len(visible_round["tables"]) == 2

    reopened.sql.engine.dispose()
