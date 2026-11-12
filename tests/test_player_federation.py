"""
test_player_federation.py

Tests for the player "Federation" information:
1. Federation defaults to the "no country" flag.
2. An explicit federation is stored, edited and persisted in the database.
3. Databases created before the Federation column was introduced are migrated.
"""

import sqlite3
import sys
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from Application.actions import Actions
from Application.turnament import Turnament
from Resources import SystemType
from sqlalchemy import create_engine, inspect

DEFAULT_FEDERATION = "🇺🇳"


def _new_db():
    db_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    return db_file.name, f"sqlite:///{db_file.name}"


def test_federation_defaults_to_no_country():
    _, url = _new_db()
    engine = create_engine(url)
    turnament = Turnament(name="Test Tournament", engine=engine)
    turnament.set_system(SystemType.SWISS)

    turnament.add_player(name="Default", surname="Player", sex="male", category="IV")
    player = next(p for p in turnament._players if p.name == "Default")
    assert player.federation == DEFAULT_FEDERATION

    engine.dispose()
    reopened = Turnament(name="Test Tournament", engine=create_engine(url))
    reopened_player = next(p for p in reopened._players if p.name == "Default")
    assert reopened_player.federation == DEFAULT_FEDERATION


def test_federation_is_added_edited_and_persisted():
    _, url = _new_db()
    engine = create_engine(url)
    turnament = Turnament(name="Test Tournament", engine=engine)
    turnament.set_system(SystemType.SWISS)

    turnament.add_player(
        name="Polish",
        surname="Player",
        sex="male",
        federation="🇵🇱 POL",
        category="IV",
    )
    player = next(p for p in turnament._players if p.name == "Polish")
    assert player.federation == "🇵🇱 POL"

    actions = Actions("test_federation")
    actions.turnament = turnament
    result = actions.player_edit(
        player_id=player.id,
        name=player.name,
        surname=player.surname,
        sex=player.sex,
        city=player.city,
        club=player.club,
        federation="🇺🇸 USA",
        category=player.category,
        elo=player.elo,
    )
    assert result["status"] is True
    assert player.federation == "🇺🇸 USA"

    engine.dispose()
    reopened = Turnament(name="Test Tournament", engine=create_engine(url))
    reopened_player = next(p for p in reopened._players if p.name == "Polish")
    assert reopened_player.federation == "🇺🇸 USA"


def test_legacy_database_is_migrated_with_default_federation():
    path, url = _new_db()
    connection = sqlite3.connect(path)
    connection.execute(
        'CREATE TABLE "Players" ('
        '"_Id" INTEGER NOT NULL, '
        '"Nr" INTEGER, '
        '"Name" VARCHAR, '
        '"Surname" VARCHAR, '
        '"Sex" VARCHAR, '
        '"City" VARCHAR, '
        '"Club" VARCHAR, '
        '"Birth" DATE, '
        '"Category" VARCHAR, '
        '"Elo" INTEGER, '
        '"Elo_rapid" INTEGER, '
        '"Elo_blitz" INTEGER, '
        'PRIMARY KEY ("_Id"))'
    )
    connection.execute(
        'INSERT INTO "Players" '
        '("_Id", "Nr", "Name", "Surname", "Sex", "City", "Club", "Birth", '
        '"Category", "Elo", "Elo_rapid", "Elo_blitz") '
        "VALUES (1, 1, 'Legacy', 'Player', 'male', '', '', NULL, 'IV', 1500, NULL, NULL)"
    )
    connection.commit()
    connection.close()

    engine = create_engine(url)
    turnament = Turnament(name="Legacy Tournament", engine=engine)
    legacy = next(p for p in turnament._players if p.name == "Legacy")
    assert legacy.federation == DEFAULT_FEDERATION

    columns = {col["name"] for col in inspect(engine).get_columns("Players")}
    assert "Federation" in columns

    turnament.add_player(
        name="Modern",
        surname="Player",
        sex="male",
        federation="🇩🇪 GER",
        category="IV",
    )
    modern = next(p for p in turnament._players if p.name == "Modern")
    assert modern.federation == "🇩🇪 GER"

    engine.dispose()
    reopened = Turnament(name="Legacy Tournament", engine=create_engine(url))
    assert next(p for p in reopened._players if p.name == "Legacy").federation == (
        DEFAULT_FEDERATION
    )
    assert next(p for p in reopened._players if p.name == "Modern").federation == (
        "🇩🇪 GER"
    )
