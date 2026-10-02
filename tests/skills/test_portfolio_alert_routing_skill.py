"""Behavioral checks for local reservations; no Discord/network calls."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sqlite3
import subprocess
import sys


SCRIPT = Path(__file__).resolve().parents[2] / "optional-skills/finance/portfolio-alert-routing/scripts/alert_history.py"


def run(db, action, key="EXAMPLE:ADD:STOCK", check=True, **options):
    command = [sys.executable, str(SCRIPT), action, "--db", str(db), "--key", key]
    for key, value in options.items():
        command += ["--" + key.replace("_", "-"), str(value)]
    result = subprocess.run(command, text=True, capture_output=True, check=check)
    return json.loads(result.stdout) if check else result


def deliver(db, key="EXAMPLE:ADD:STOCK", revision="qualified-v1", day="2026-10-02", receipt="thread-1"):
    result = run(db, "reserve", key=key, revision=revision, day=day)
    assert result["send"]
    if result["create_thread"]:
        run(db, "bind-thread", key=key, token=result["token"], receipt=receipt)
    run(db, "commit", key=key, token=result["token"], receipt="message-1")
    return result


def test_same_decision_suppressed_but_material_change_allowed(tmp_path):
    db = tmp_path / "history.db"
    deliver(db)
    assert not run(db, "reserve", revision="qualified-v1", day="2026-10-02")["send"]
    update = run(db, "reserve", revision="qualified-v2", day="2026-10-02")
    assert update["send"] and update["thread_id"] == "thread-1"
    assert not update["create_thread"]


def test_same_ticker_different_instrument_reuses_daily_thread(tmp_path):
    db = tmp_path / "history.db"
    deliver(db)
    update = run(db, "reserve", key="EXAMPLE:CSP:PUT", revision="put-qualified", day="2026-10-02")
    assert update["thread_id"] == "thread-1" and not update["create_thread"]


def test_new_day_or_ticker_gets_new_thread(tmp_path):
    db = tmp_path / "history.db"
    deliver(db)
    update = run(db, "reserve", revision="qualified-v2", day="2026-10-03")
    assert update["create_thread"] and update["thread_id"] is None
    other = run(db, "reserve", key="OTHER:ADD:STOCK", revision="qualified", day="2026-10-02")
    assert other["create_thread"]


def test_thread_creation_has_one_concurrent_owner(tmp_path):
    db = tmp_path / "history.db"
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(lambda i: run(db, "reserve", key=f"EXAMPLE:ADD:INSTRUMENT{i}", revision="qualified", day="2026-10-02"), range(6)))
    assert sum(result["send"] for result in results) == 1


def test_release_and_uncertain_results_do_not_duplicate(tmp_path):
    db = tmp_path / "history.db"
    first = run(db, "reserve", revision="qualified", day="2026-10-02")
    run(db, "release", token=first["token"])
    second = run(db, "reserve", revision="qualified", day="2026-10-02")
    assert second["send"]
    run(db, "uncertain", token=second["token"])
    assert not run(db, "reserve", revision="qualified", day="2026-10-02")["send"]
    assert not run(db, "reserve", key="EXAMPLE:TRIM:STOCK", revision="new-action", day="2026-10-02")["send"]


def test_commit_requires_bound_thread_and_matching_token(tmp_path):
    db = tmp_path / "history.db"
    first = run(db, "reserve", revision="qualified", day="2026-10-02")
    assert run(db, "commit", token=first["token"], receipt="message", check=False).returncode
    assert run(db, "release", token="wrong", check=False).returncode
    assert not run(db, "reserve", revision="qualified", day="2026-10-02")["send"]


def test_reservation_keeps_its_day_across_midnight(tmp_path):
    db = tmp_path / "history.db"
    first = run(db, "reserve", revision="qualified", day="2000-01-01")
    run(db, "bind-thread", token=first["token"], receipt="old-day-thread")
    run(db, "commit", token=first["token"], receipt="message")
    assert run(db, "inspect", day="2000-01-01")["thread"]["receipt"] == "old-day-thread"


def test_reject_changed_day_or_ticker_for_same_reservation(tmp_path):
    db = tmp_path / "history.db"
    first = run(db, "reserve", revision="qualified", day="2026-10-02")
    assert run(db, "bind-thread", token=first["token"], receipt="wrong", day="2026-10-03", check=False).returncode
    assert run(db, "bind-thread", token=first["token"], receipt="wrong", ticker="OTHER", check=False).returncode
    run(db, "bind-thread", token=first["token"], receipt="right")


def test_old_schema_is_migrated_without_losing_history(tmp_path):
    db = tmp_path / "history.db"
    with sqlite3.connect(db) as connection:
        connection.execute("CREATE TABLE alerts (key TEXT PRIMARY KEY, revision TEXT, sent_at REAL, receipt TEXT, summary TEXT, token TEXT, reserved_at REAL, pending_revision TEXT, uncertain INTEGER NOT NULL DEFAULT 0)")
        connection.execute("INSERT INTO alerts(key,revision,summary) VALUES('EXAMPLE:ADD:STOCK','previous','retain me')")
    assert run(db, "inspect")["previous"]["summary"] == "retain me"
    deliver(db)
