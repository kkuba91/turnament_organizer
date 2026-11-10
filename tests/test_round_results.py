"""
test_round_results.py

Tests that round data exposes whether all table results are completed.
The UI uses this flag to enable or disable the round action button.
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


def test_round_all_results_flag_toggles_with_results():
    url = f"sqlite:///{tempfile.NamedTemporaryFile(delete=False, suffix='.db').name}"
    engine = create_engine(url)
    turnament = Turnament(name="Test Tournament", engine=engine)
    turnament.set_system(SystemType.SWISS)
    for index in range(5):
        turnament.add_player(
            name=f"Player{index}",
            surname=f"Surname{index}",
            sex="male",
            category="IV",
            elo=1500 + index * 10,
        )
    turnament.begin(rounds=2)

    actions = Actions("test_round_results")
    actions.turnament = turnament

    round_data = actions.turnament_round(nr=1)["round"]
    assert round_data["all_results"] is False

    table_numbers = list(turnament._rounds[0].tables)
    turnament.add_result(table_numbers[0], 1.0)
    assert actions.turnament_round(nr=1)["round"]["all_results"] is False

    for table_nr in table_numbers:
        turnament.add_result(table_nr, 1.0)
    assert actions.turnament_round(nr=1)["round"]["all_results"] is True

    # Removing one result must mark the round as incomplete again.
    turnament.add_result(table_numbers[0], -1.0)
    assert actions.turnament_round(nr=1)["round"]["all_results"] is False

    engine.dispose()


def test_all_results_is_restored_after_reopen():
    url = f"sqlite:///{tempfile.NamedTemporaryFile(delete=False, suffix='.db').name}"
    engine = create_engine(url)
    turnament = Turnament(name="Test Tournament", engine=engine)
    turnament.set_system(SystemType.SWISS)
    for index in range(5):
        turnament.add_player(
            name=f"Player{index}",
            surname=f"Surname{index}",
            sex="male",
            category="IV",
            elo=1500 + index * 10,
        )
    turnament.begin(rounds=2)

    for table_nr in list(turnament._rounds[0].tables):
        turnament.add_result(table_nr, 1.0)
    assert turnament._rounds[0].all_results is True
    engine.dispose()

    reopened = Turnament(name="Test Tournament", engine=create_engine(url))
    actions = Actions("test_round_results_reopen")
    actions.turnament = reopened
    assert actions.turnament_round(nr=1)["round"]["all_results"] is True
    reopened.sql.engine.dispose()
