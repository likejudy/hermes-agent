#!/usr/bin/env python3
"""Reserve and record portfolio alert deliveries across recurring jobs."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import sqlite3
import time
import uuid
from zoneinfo import ZoneInfo


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("inspect", "reserve", "bind-thread", "commit", "release", "uncertain"))
    parser.add_argument("--key", required=True, help="Stable ticker/action/instrument key, shared across jobs")
    parser.add_argument("--revision", default="", help="Material decision state; exclude wording and ordinary quote changes")
    parser.add_argument("--token", default="")
    parser.add_argument("--receipt", default="", help="Confirmed Discord thread/message ID")
    parser.add_argument("--summary", default="")
    parser.add_argument("--ticker", default="", help="Defaults to the first colon-separated part of --key")
    parser.add_argument("--day", help="Ticker routing day; mutations reuse the reserved day when omitted")
    parser.add_argument("--timezone", default="America/Los_Angeles", help="IANA timezone for a new routing day")
    parser.add_argument("--db", type=Path, default=Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")) / "state" / "portfolio_alert_history.db")
    args = parser.parse_args()
    if not args.key.strip() or len(args.key) > 300:
        parser.error("key must contain 1-300 characters")
    if args.action == "reserve" and not args.revision.strip():
        parser.error("reserve requires --revision")
    if args.action in ("bind-thread", "commit", "release", "uncertain") and not args.token:
        parser.error("a reservation token is required")
    if args.action in ("bind-thread", "commit") and not args.receipt:
        parser.error("commit requires a confirmed delivery receipt")
    args.db.parent.mkdir(parents=True, exist_ok=True)
    ticker = (args.ticker or args.key.split(":", 1)[0]).strip().upper()
    if not ticker or any(c not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.^-" for c in ticker):
        parser.error("ticker must be a symbol; specify --ticker when the key does not start with one")
    if args.day:
        datetime.strptime(args.day, "%Y-%m-%d")
    requested_day = args.day
    args.day = args.day or datetime.now(ZoneInfo(args.timezone)).date().isoformat()
    db = sqlite3.connect(args.db, timeout=10)
    try:
        args.db.chmod(0o600)
        db.execute("BEGIN IMMEDIATE")
        db.execute("CREATE TABLE IF NOT EXISTS alerts (key TEXT PRIMARY KEY, revision TEXT, sent_at REAL, receipt TEXT, summary TEXT, token TEXT, reserved_at REAL, pending_revision TEXT, uncertain INTEGER NOT NULL DEFAULT 0,pending_ticker TEXT,pending_day TEXT)")
        db.execute("CREATE TABLE IF NOT EXISTS threads (day TEXT,ticker TEXT,receipt TEXT,token TEXT,reserved_at REAL,uncertain INTEGER NOT NULL DEFAULT 0,PRIMARY KEY(day,ticker))")
        columns = {item[1] for item in db.execute("PRAGMA table_info(alerts)")}
        for column in ("pending_ticker", "pending_day"):
            if column not in columns:
                db.execute(f"ALTER TABLE alerts ADD COLUMN {column} TEXT")
        row = db.execute("SELECT revision,sent_at,receipt,summary,token,reserved_at,pending_revision,uncertain,pending_ticker,pending_day FROM alerts WHERE key=?", (args.key,)).fetchone()
        now = time.time()
        prior = dict(zip(("revision", "sent_at", "receipt", "summary", "token", "reserved_at", "pending_revision", "uncertain", "pending_ticker", "pending_day"), row)) if row else {}
        if args.action not in ("inspect", "reserve"):
            if prior.get("token") != args.token:
                raise ValueError("reservation token mismatch")
            if prior.get("pending_ticker"):
                if ticker != prior["pending_ticker"] and args.ticker:
                    raise ValueError("ticker does not match the reservation")
                if requested_day and requested_day != prior["pending_day"]:
                    raise ValueError("day does not match the reservation")
                ticker, args.day = prior["pending_ticker"], prior["pending_day"]
            elif not requested_day:
                raise ValueError("legacy reservation requires an explicit routing day; reconcile before changing it")
        thread_row = db.execute("SELECT receipt,token,reserved_at,uncertain FROM threads WHERE day=? AND ticker=?", (args.day, ticker)).fetchone()
        thread = dict(zip(("receipt", "token", "reserved_at", "uncertain"), thread_row)) if thread_row else {}
        if args.action == "inspect":
            result = {"key": args.key, "previous": prior, "ticker": ticker, "day": args.day, "thread": thread}
        elif args.action == "reserve":
            if prior.get("uncertain"):
                result = {"send": False, "reason": "delivery uncertain; reconcile before retry", "previous": prior}
            elif prior.get("token"):
                result = {"send": False, "reason": "another run reserved this alert; reconcile before reclaiming", "previous": prior}
            elif prior.get("revision") == args.revision and prior.get("sent_at") and now - prior["sent_at"] < 86400:
                result = {"send": False, "reason": "same decision already delivered within 24 hours", "previous": prior}
            elif thread.get("uncertain") or thread.get("token"):
                result = {"send": False, "reason": "ticker thread creation pending or uncertain; reconcile before retry", "thread": thread}
            else:
                token = uuid.uuid4().hex
                db.execute("INSERT INTO alerts(key,token,reserved_at,pending_revision,pending_ticker,pending_day) VALUES(?,?,?,?,?,?) ON CONFLICT(key) DO UPDATE SET token=excluded.token,reserved_at=excluded.reserved_at,pending_revision=excluded.pending_revision,pending_ticker=excluded.pending_ticker,pending_day=excluded.pending_day", (args.key, token, now, args.revision, ticker, args.day))
                if not thread.get("receipt"):
                    db.execute("INSERT INTO threads(day,ticker,token,reserved_at) VALUES(?,?,?,?) ON CONFLICT(day,ticker) DO UPDATE SET token=excluded.token,reserved_at=excluded.reserved_at", (args.day, ticker, token, now))
                result = {"send": True, "token": token, "previous": prior, "ticker": ticker, "day": args.day, "thread_id": thread.get("receipt"), "create_thread": not bool(thread.get("receipt"))}
        else:
            if prior.get("token") != args.token:
                raise ValueError("reservation token mismatch")
            if args.action == "bind-thread":
                if thread.get("token") != args.token:
                    raise ValueError("ticker thread reservation token mismatch")
                db.execute("UPDATE threads SET receipt=?,token=NULL,reserved_at=NULL,uncertain=0 WHERE day=? AND ticker=?", (args.receipt, args.day, ticker))
            elif args.action == "commit":
                if not thread.get("receipt"):
                    raise ValueError("bind the ticker's confirmed Discord thread before committing delivery")
                db.execute("UPDATE alerts SET revision=?,sent_at=?,receipt=?,summary=?,token=NULL,reserved_at=NULL,pending_revision=NULL,pending_ticker=NULL,pending_day=NULL,uncertain=0 WHERE key=?", (prior["pending_revision"], now, args.receipt, args.summary, args.key))
            elif args.action == "release":
                db.execute("UPDATE alerts SET token=NULL,reserved_at=NULL,pending_revision=NULL,pending_ticker=NULL,pending_day=NULL,uncertain=0 WHERE key=?", (args.key,))
                db.execute("DELETE FROM threads WHERE day=? AND ticker=? AND token=? AND receipt IS NULL", (args.day, ticker, args.token))
            else:
                db.execute("UPDATE alerts SET uncertain=1 WHERE key=?", (args.key,))
                db.execute("UPDATE threads SET uncertain=1 WHERE day=? AND ticker=? AND token=?", (args.day, ticker, args.token))
            result = {"status": args.action, "key": args.key}
        db.commit()
        print(json.dumps(result))
    finally:
        db.close()


if __name__ == "__main__":
    main()
