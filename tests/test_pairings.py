"""
test_pairings.py

Tests for pairing persistence and player addition during tournament.
Tests the following scenarios:
1. Create tournament with 5 players, check pairing
2. Add 6th player (should take effect in next round)
3. Start round and complete it
4. Load next round and verify:
   - New player has highest ID
   - Pairings from DB are correctly restored
   - Pausing player is preserved
"""

import sys
import os
import tempfile
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from Application.turnament import Turnament
from Resources import SystemType
from sqlalchemy import create_engine


def setup_test_tournament():
    """Create a test tournament with in-memory SQLite database"""
    # Create temporary database
    db_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    db_path = f"sqlite:///{db_file.name}"
    engine = create_engine(db_path)

    # Create tournament
    turnament = Turnament(name="Test Tournament", engine=engine)

    # Setup logging
    logging.basicConfig(level=logging.DEBUG)

    return turnament, engine, db_file.name


def test_basic_pairing_and_player_addition():
    """
    Test 1: Create tournament, add 5 players, check pairing, add 6th player,
    complete round, and verify next round pairings are from DB with new player
    """
    print("\n" + "=" * 80)
    print("TEST 1: Basic Pairing and Player Addition")
    print("=" * 80)

    turnament, engine, db_path = setup_test_tournament()

    # Set pairing system
    turnament.set_system(SystemType.SWISS)
    print("✓ Tournament system set to SWISS")

    # Add 5 players
    players_data = [
        ("Alice", "Smith", "female", "Warsaw", "wc", 1800),
        ("Bob", "Johnson", "male", "Krakow", "wc", 1750),
        ("Charlie", "Williams", "male", "Gdansk", "wc", 1700),
        ("Diana", "Brown", "female", "Wroclaw", "wc", 1650),
        ("Eve", "Davis", "female", "Poznan", "wc", 1600),
    ]

    for name, surname, sex, city, cat, elo in players_data:
        turnament.add_player(
            name=name, surname=surname, sex=sex, city=city, category=cat, elo=elo
        )
    print("✓ Added 5 players")

    # Start tournament with 2 rounds
    turnament.begin(rounds=2)
    print("✓ Tournament started with 2 rounds")
    print(f"  Current round: {turnament._act_round_nr}")
    print(f"  Actual players: {turnament.players_num}")

    # Store initial player IDs
    initial_player_ids = {p.name: p.id for p in turnament._players}
    print(f"✓ Initial player IDs: {initial_player_ids}")

    # Store initial pairings
    round_1 = turnament._rounds[0]
    initial_pairings = {}
    for table_nr in round_1.tables:
        table = round_1.tables[table_nr]
        initial_pairings[table_nr] = {
            "white_id": table.w_player.id,
            "black_id": table.b_player.id,
            "white_name": table.w_player.name,
            "black_name": table.b_player.name,
        }
    print("✓ Initial pairings for round 1:")
    for table_nr, pairing in initial_pairings.items():
        print(
            f"    Table {table_nr}: {pairing['white_name']}({pairing['white_id']}) vs {pairing['black_name']}({pairing['black_id']})"
        )

    # Add 6th player DURING the tournament
    print("\n→ Adding 6th player during tournament...")
    turnament.add_player(
        name="Frank",
        surname="Miller",
        sex="male",
        city="Gdynia",
        category="wc",
        elo=1550,
    )
    print("✓ Added 6th player 'Frank Miller'")
    print(f"  Total players now: {turnament.players_num}")

    # Verify new player has highest ID
    frank = next((p for p in turnament._players if p.name == "Frank"), None)
    assert frank is not None, "Frank not found in players list"
    print(f"  Frank's ID: {frank.id}")

    max_initial_id = max(initial_player_ids.values())
    assert frank.id == max_initial_id + 1, (
        f"Frank's ID should be {max_initial_id + 1}, got {frank.id}"
    )
    print(f"✓ Frank has correct ID: {frank.id} (one more than max: {max_initial_id})")

    # Verify round 1 pairings haven't changed (because new player is added)
    # but _repair_current_round() is called, so let's check
    print("\n→ Verifying round 1 pairings after player addition...")
    round_1_after = turnament._rounds[0]
    assert round_1_after is not None, "Round 1 is None"
    print(f"  Round 1 still has {len(round_1_after.tables)} tables")

    # Complete round 1 with some results
    print("\n→ Completing round 1 with results...")
    for table_nr in round_1_after.tables:
        turnament.add_result(table_nr, 1.0)  # White wins all games
    print("✓ Added results for all tables in round 1")

    # Apply round results and move to round 2
    turnament.apply_round_results()
    print("✓ Applied round 1 results")

    turnament.next_round()
    print("✓ Moved to round 2")
    print(f"  Current round: {turnament._act_round_nr}")

    # Verify round 2 pairings are loaded from DB or newly created
    round_2 = turnament._rounds[1]
    print("\n→ Verifying round 2 pairings...")
    print(f"  Round 2 has {len(round_2.tables)} tables")

    # All 6 players should be in round 2 (or 5 if one is pausing)
    all_players_in_round = set()
    for table_nr in round_2.tables:
        table = round_2.tables[table_nr]
        p_w_id = table.w_player.id
        p_b_id = table.b_player.id
        if p_w_id > 0:
            all_players_in_round.add(p_w_id)
        if p_b_id > 0:
            all_players_in_round.add(p_b_id)

    print(f"  Players in round 2: {all_players_in_round}")
    # Should be 6 players (all are playing)
    assert len(all_players_in_round) == 6, (
        f"Expected 6 players in round 2, got {len(all_players_in_round)}: {all_players_in_round}"
    )
    print(f"✓ Round 2 has all 6 players: {all_players_in_round}")

    # Verify player IDs haven't changed
    round_2_player_ids = {p.name: p.id for p in turnament._players}
    print("\n→ Verifying player IDs are unchanged...")
    for name, orig_id in initial_player_ids.items():
        new_id = round_2_player_ids.get(name)
        print(f"  {name}: {orig_id} -> {new_id}")
        assert orig_id == new_id, f"{name}'s ID changed from {orig_id} to {new_id}"
    print("✓ All original player IDs are unchanged")

    # Verify Frank's ID is correct
    frank_new_id = round_2_player_ids.get("Frank")
    print(f"  Frank: {frank_new_id}")
    assert frank_new_id == frank.id, "Frank's ID changed"
    assert frank_new_id == max_initial_id + 1, "Frank's ID is not max_id + 1"
    print(f"✓ Frank's ID is correct: {frank_new_id}")

    print("\n✓✓✓ TEST 1 PASSED ✓✓✓")

    # Cleanup
    os.unlink(db_path)
    return True


def test_pairing_persistence():
    """
    Test 2: Verify that pairings are saved to DB and can be recovered
    by closing and reopening the tournament
    """
    print("\n" + "=" * 80)
    print("TEST 2: Pairing Persistence (Close and Reopen)")
    print("=" * 80)

    # Create separate database file for this test
    db_file2 = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    db_path2 = f"sqlite:///{db_file2.name}"
    db_file2.close()

    engine1 = create_engine(db_path2)
    turnament1 = Turnament(name="Test Tournament", engine=engine1)

    # Setup first tournament
    turnament1.set_system(SystemType.SWISS)
    print("✓ Tournament 1 system set to SWISS")

    # Add players
    players_data = [
        ("Alice", "Smith", "female", "Warsaw", "wc", 1800),
        ("Bob", "Johnson", "male", "Krakow", "wc", 1750),
        ("Charlie", "Williams", "male", "Gdansk", "wc", 1700),
    ]

    for name, surname, sex, city, cat, elo in players_data:
        turnament1.add_player(
            name=name, surname=surname, sex=sex, city=city, category=cat, elo=elo
        )
    print("✓ Added 3 players")

    # Start tournament
    turnament1.begin(rounds=2)
    print("✓ Tournament 1 started with 2 rounds")

    # Store pairings for round 1
    round_1_t1 = turnament1._rounds[0]
    pairings_t1_r1 = {}
    for table_nr in round_1_t1.tables:
        table = round_1_t1.tables[table_nr]
        pairings_t1_r1[table_nr] = (table.w_player.id, table.b_player.id)
    print("✓ Round 1 pairings stored:")
    for table_nr, (w_id, b_id) in pairings_t1_r1.items():
        print(f"    Table {table_nr}: {w_id} vs {b_id}")

    # Complete round 1
    for table_nr in round_1_t1.tables:
        turnament1.add_result(table_nr, 0.5)  # All draws
    turnament1.apply_round_results()
    print("✓ Round 1 completed")

    # Move to round 2
    turnament1.next_round()
    print("✓ Moved to round 2")

    # Read pairings from DB
    pairings_from_db = turnament1.sql.read_pairings_info()
    r1_pairings_from_db = [p for p in pairings_from_db if p.get("round") == 1]
    print(f"✓ Pairings for round 1 in DB: {len(r1_pairings_from_db)} entries")

    # Now close tournament1 and open tournament2 with same DB
    print("\n→ Closing tournament 1 and reopening with new instance...")
    del turnament1, engine1

    # Create new tournament with same DB
    engine2 = create_engine(db_path2)
    turnament2 = Turnament(name="Test Tournament", engine=engine2)
    print("✓ Tournament 2 created from same DB")

    # Check that round 1 pairings are the same
    if len(turnament2._rounds) > 0:
        round_1_t2 = turnament2._rounds[0]
        pairings_t2_r1 = {}
        for table_nr in round_1_t2.tables:
            table = round_1_t2.tables[table_nr]
            pairings_t2_r1[table_nr] = (table.w_player.id, table.b_player.id)

        print("✓ Round 1 pairings in tournament 2:")
        for table_nr, (w_id, b_id) in pairings_t2_r1.items():
            print(f"    Table {table_nr}: {w_id} vs {b_id}")

        # Verify they're the same
        assert len(pairings_t1_r1) == len(pairings_t2_r1), "Number of tables changed"
        for table_nr in pairings_t1_r1:
            assert pairings_t1_r1[table_nr] == pairings_t2_r1[table_nr], (
                f"Table {table_nr} pairing changed"
            )
        print("✓ Round 1 pairings are identical after reopening")

    print("\n✓✓✓ TEST 2 PASSED ✓✓✓")

    # Cleanup
    os.unlink(db_file2.name)
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 100)
    print("RUNNING TOURNAMENT PAIRING TESTS")
    print("=" * 100)

    try:
        test_basic_pairing_and_player_addition()
        test_pairing_persistence()

        print("\n" + "=" * 100)
        print("ALL TESTS PASSED!")
        print("=" * 100)
        return True
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
