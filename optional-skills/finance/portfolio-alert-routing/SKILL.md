---
name: portfolio-alert-routing
description: Filter portfolio alerts and reuse daily ticker threads.
version: 1.0.0
author: Brian Su (likejudy), Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [portfolio, alerts, discord, cron, deduplication]
    category: finance
---

# Portfolio Alert Routing Skill

Filter recurring portfolio alerts and keep every actionable update for a ticker in one Discord thread per day. This skill routes decision-support messages; it does not execute trades or decide which securities to buy.

## When to Use

- A recurring portfolio monitor has an actionable new decision to report.
- Several jobs share a portfolio alert channel and need common delivery history.
- A later alert for the same ticker should continue its existing daily thread.

## Prerequisites

- Python 3.9+ and an IANA timezone database.
- Native Hermes `discord` and `send_message` tools with access to the intended channel.
- A defined job scope, market timezone, destination, and actionable-alert contract.
- One shared database under the active `HERMES_HOME` for all jobs targeting that channel. Use separate `--db` paths for separate channels/portfolios.

## How to Run

Use `terminal` to run `scripts/alert_history.py` from this skill directory. The helper stores reservations and receipts locally; it does not contact Discord. Default state is `${HERMES_HOME:-$HOME/.hermes}/state/portfolio_alert_history.db`.

## Quick Reference

| Action | Purpose |
|---|---|
| `inspect` | Read the prior decision and ticker/day thread receipt. |
| `reserve` | Atomically claim a new material decision and, if needed, thread creation. |
| `bind-thread` | Record a confirmed thread ID for the reservation. |
| `commit` | Record a confirmed alert message receipt after sending. |
| `release` | Clear a reservation only after a definite no-send result. |
| `uncertain` | Block retries until an ambiguous external result is reconciled. |

`--key` is a stable `TICKER:ACTION:INSTRUMENT` key shared across jobs. `--revision` represents the material decision state, excluding wording and ordinary quote drift. `--timezone` defaults to `America/Los_Angeles`; pass the portfolio's actual timezone. `--day` can pin an explicit routing date. Subsequent mutations reuse the date saved with the reservation.

## Procedure

1. Respect the current job's scope and cadence. Refresh the relevant exposure, market/event facts, and decision triggers. Keep hold/watch/wait outcomes, unmet triggers, stale tickets, and non-actionable commentary local.
2. Define the stable decision key and revision. Do not create a new revision merely because the prose, timestamp, or quote changed.
3. Inspect and reserve through the helper:

   ```bash
   python scripts/alert_history.py inspect --key 'EXAMPLE:ADD:STOCK'
   python scripts/alert_history.py reserve --key 'EXAMPLE:ADD:STOCK' --revision 'trigger-confirmed-sizing-v1'
   ```

4. If `send` is false, keep the result local. An identical decision within 24 hours, a live reservation, or an uncertain delivery must not produce a second alert.
5. If `thread_id` exists, reuse it even when the new alert has a different action or instrument. If `create_thread` is true, use `discord` with `action="create_thread"` in the intended channel, titled `Portfolio TICKER — YYYY-MM-DD`. Record its confirmed ID with `bind-thread`, the same key, and the reservation token.
6. Use `send_message` to deliver the actionable ticket to `discord:<channel_id>:<thread_id>`. Include what materially changed, the exact instrument/action/size/trigger, evidence timestamps, and relevant uncertainty.
7. Commit only after a confirmed message receipt. On a definite failure before delivery, release. On a timeout or otherwise ambiguous result, mark uncertain and inspect Discord before any retry. Do not auto-expire or reclaim reservations.
8. Keep scheduler auto-delivery disabled when the job manually sends its alert. A run has one delivery path. Routine non-actionable results stay silent.

## Pitfalls

- Using separate histories for watchlist, holdings, or hedge jobs targeting the same channel.
- Using the decision key as the thread key: different instruments for one ticker still share its daily thread.
- Treating quote drift as a new decision or failed retrieval as a confirmed all-clear.
- Sending before reserving, committing before delivery, or retrying an uncertain send.
- Forgetting the destination boundary: one database routes one portfolio alert channel.
- Claiming that a helper unit test proves a live scheduled Discord delivery.

## Verification

Use a temporary database and synthetic decisions to check duplicate suppression, thread reuse across action/instrument keys, a new day's thread, concurrent reservations, failed-send release, and uncertain-send blocking. Check real scheduled delivery separately without creating unsolicited test alerts.
