---
title: "Test Driven Development — Use behavioral tests for RED–GREEN–REFACTOR changes"
sidebar_label: "Test Driven Development"
description: "Use behavioral tests for RED–GREEN–REFACTOR changes"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Test Driven Development

Use behavioral tests for RED–GREEN–REFACTOR changes.

## Skill metadata

| | |
|---|---|
| Source | Bundled (installed by default) |
| Path | `skills/software-development/test-driven-development` |
| Version | `1.1.0` |
| Author | obra/superpowers contributors, Hermes Agent |
| License | MIT |
| Platforms | linux, macos, windows |
| Tags | `testing`, `tdd`, `development`, `quality`, `red-green-refactor` |
| Related skills | [`systematic-debugging`](../../bundled/software-development/software-development-systematic-debugging.md), [`subagent-driven-development`](../../optional/software-development/software-development-subagent-driven-development.md) |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that Hermes loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# Test-Driven Development Skill

Use a failing behavioral test to define an implementation change, then make it pass and refactor. Scale verification to the change and follow the repository’s own testing requirements.

## When to Use

- New behavior or a bug with a reproducible failure.
- Refactoring where existing behavior must remain stable.
- A task or repository explicitly requiring RED–GREEN–REFACTOR.

For prose, generated output, exploratory spikes, and low-impact configuration changes, use the appropriate inspection or smoke check. Do not add tests that merely mirror the implementation.

## Prerequisites

Read repository instructions, the relevant implementation, existing tests, and the documented test runner. Preserve the user’s changes and establish the current baseline before editing.

## How to Run

Use `read_file` and `search_files` to inspect relevant code/tests, `patch` for edits, and `terminal` for the repository’s test commands. In Hermes itself, run `scripts/run_tests.sh`; do not substitute a bare pytest invocation.

## Quick Reference

| Stage | Required evidence |
|---|---|
| RED | The new test fails for the intended missing/incorrect behavior. |
| GREEN | The smallest implementation makes that test pass. |
| REFACTOR | The relevant behavioral tests still pass after cleanup. |
| COMPLETE | Repository-required checks ran on the final diff. |

## Procedure

1. Express the intended behavior as one meaningful assertion. Prefer the real public interface; mock external dependencies only where necessary.
2. Run the test and inspect its failure. A syntax error, missing fixture, or incorrect test setup does not prove the intended regression.
3. Make the smallest implementation change that satisfies the behavior. Avoid speculative features.
4. Run the focused test, then the affected integration/regression checks and any broader checks required by the repository.
5. Refactor only when it improves the final change. Rerun the checks affected by the refactor.
6. Inspect the final diff for unintended behavior, obsolete branches, and unrelated edits.

If implementation already exists, preserve it. Build a behavioral regression test and, where safe, verify that it detects the earlier defect in an isolated checkout or by reverting only your own relevant change. Never delete someone else’s work to recreate an ideal sequence.

## Pitfalls

- A passing test that cannot distinguish the bug from correct behavior.
- Testing internal calls or current catalog/count literals instead of stable contracts.
- Replacing the entire system under test with mocks.
- Hiding failures, skipping required checks, or claiming a test ran when it did not.
- Asking for routine approval already provided in the task.
- Creating extra tests for reversible edits that are better verified by inspection.

## Verification

Report the behavior covered, checks run on the final diff, and any environmental limitation. Separate new failures from an established baseline. Expand testing when a changed dependency, new failure, or unresolved risk justifies it.
