"""
test_player_club.py

Tests for the optional player "Club" information:
1. Club can be added and edited, and is persisted in the database.
2. Club is optional and may stay empty.
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
            city=f"City{index}",
            club=f"Club{index}",
            category="IV",
            elo=1500 + index * 10,
        )


def test_club_is_added_edited_and_persisted():
    url = _new_db()
    engine = create_engine(url)
    turnament = Turnament(name="Test Tournament", engine=engine)
    turnament.set_system(SystemType.SWISS)
    _add_players(turnament)

    player = next(p for p in turnament._players if p.name == "Player0")
    assert player.club == "Club0"

    actions = Actions("test_club")
    actions.turnament = turnament
    result = actions.player_edit(
        player_id=player.id,
        name=player.name,
        surname=player.surname,
        sex=player.sex,
        city=player.city,
        club="Edited Club",
        category=player.category,
        elo=player.elo,
    )
    assert result["status"] is True
    assert player.club == "Edited Club"

    engine.dispose()
    reopened = Turnament(name="Test Tournament", engine=create_engine(url))
    reopened_player = next(p for p in reopened._players if p.name == "Player0")
    assert reopened_player.club == "Edited Club"


def test_club_is_optional():
    url = _new_db()
    engine = create_engine(url)
    turnament = Turnament(name="Test Tournament", engine=engine)
    turnament.set_system(SystemType.SWISS)

    turnament.add_player(
        name="No",
        surname="Club",
        sex="male",
        city="",
        category="IV",
        elo=0,
    )
    player = next(p for p in turnament._players if p.name == "No")
    assert player.club == ""

    engine.dispose()
    reopened = Turnament(name="Test Tournament", engine=create_engine(url))
    player = next(p for p in reopened._players if p.name == "No")
    assert player.club == ""
