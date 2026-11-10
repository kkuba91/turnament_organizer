"""
test_pairing_reopen.py

Regression test for a player joining mid-round followed by closing and
reopening the tournament. The next round must pair all active players and must
not create a bye or mark players as suspended when the player count is even.
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


def _add_players(turnament, quantity=5):
    for index in range(quantity):
        turnament.add_player(
            name=f"Player{index}",
            surname=f"Surname{index}",
            sex="male",
            category="IV",
            elo=1600 - index * 10,
        )


def _complete_round(turnament):
    round_nr = turnament._act_round_nr
    for table_nr in list(turnament._rounds[round_nr - 1].tables):
        turnament.add_result(table_nr, 1.0)


def _assert_round_pairs_everyone(turnament):
    assert turnament._act_round_nr == 2
    assert len(turnament._rounds) == 2

    round_two = turnament._rounds[1]
    paired_ids = set()
    games = 0
    for table in round_two.tables.values():
        ids = {table.w_player.id, table.b_player.id}
        assert -1 not in ids, f"Unexpected bye in round 2: {ids}"
        paired_ids |= ids
        games += 1

    assert games == 3, f"Expected 3 games for 6 players, got {games}"
    assert paired_ids == {1, 2, 3, 4, 5, 6}
    assert round_two.pausing == 0

    for player in turnament._players:
        assert not player.is_suspended(2), f"{player.name} is suspended in round 2"

    # Round 1 must be counted exactly once: 2 games + 1 bye = 3 points total.
    assert sum(player.points for player in turnament._players) == 3.0
    for player in turnament._players:
        assert len(player.opponents) == len(set(player.opponents)), (
            f"{player.name} has duplicated opponents: {player.opponents}"
        )


def _run_after_reopen(results_before_close):
    url = _new_db()
    engine = create_engine(url)
    turnament = Turnament(name="Test Tournament", engine=engine)
    turnament.set_system(SystemType.SWISS)
    _add_players(turnament, quantity=5)
    turnament.begin(rounds=3)

    # With 5 players player #5 gets the bye in round 1.
    assert turnament._rounds[0].pausing == 5

    # A sixth player joins while round 1 is still in progress.
    turnament.add_player(
        name="Late",
        surname="Entry",
        sex="male",
        category="IV",
        elo=1500,
    )
    late = next(p for p in turnament._players if p.name == "Late")
    assert late.id == 6
    assert late.is_suspended(1)

    if results_before_close:
        _complete_round(turnament)
    engine.dispose()

    # Close and reopen the tournament.
    reopened = Turnament(name="Test Tournament", engine=create_engine(url))
    actions = Actions("test_pairing_reopen")
    actions.turnament = reopened

    if not results_before_close:
        _complete_round(reopened)

    assert actions.apply_round() is True
    _assert_round_pairs_everyone(reopened)
    reopened.sql.engine.dispose()


def test_next_round_after_reopen_with_mid_round_join():
    # Results entered before closing the tournament.
    _run_after_reopen(results_before_close=True)
    # Results entered after reopening the tournament.
    _run_after_reopen(results_before_close=False)
