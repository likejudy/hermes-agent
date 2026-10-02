# Research Paper Writing: detailed guide

Paths in command examples are relative to the skill directory unless stated otherwise. Read the relevant section for the current task; the SKILL.md entry point owns scope and verification. Confirm flags/APIs against the installed version before executing an example.

# Research Paper Writing Pipeline

End-to-end pipeline for producing publication-ready ML/AI research papers targeting **NeurIPS, ICML, ICLR, ACL, AAAI, and COLM**. This skill covers the full research lifecycle: experiment design, execution, monitoring, analysis, paper writing, review, revision, and submission.

This is **not a linear pipeline** — it is an iterative loop. Results trigger new experiments. Reviews trigger new analysis. The agent must handle these feedback loops.

<!-- ascii-guard-ignore -->
```
┌─────────────────────────────────────────────────────────────┐
│                    RESEARCH PAPER PIPELINE                  │
│                                                             │
│  Phase 0: Project Setup ──► Phase 1: Literature Review      │
│       │                          │                          │
│       ▼                          ▼                          │
│  Phase 2: Experiment     Phase 5: Paper Drafting ◄──┐      │
│       Design                     │                   │      │
│       │                          ▼                   │      │
│       ▼                    Phase 6: Self-Review      │      │
│  Phase 3: Execution &           & Revision ──────────┘      │
│       Monitoring                 │                          │
│       │                          ▼                          │
│       ▼                    Phase 7: Submission               │
│  Phase 4: Analysis ─────► (feeds back to Phase 2 or 5)     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```
<!-- ascii-guard-ignore-end -->

---

## When To Use This Skill

Use this skill when:
- **Starting a new research paper** from an existing codebase or idea
- **Designing and running experiments** to support paper claims
- **Writing or revising** any section of a research paper
- **Preparing for submission** to a specific conference or workshop
- **Responding to reviews** with additional experiments or revisions
- **Converting** a paper between conference formats
- **Writing non-empirical papers** — theory, survey, benchmark, or position papers (see [Paper Types Beyond Empirical ML](#paper-types-beyond-empirical-ml))
- **Designing human evaluations** for NLP, HCI, or alignment research
- **Preparing post-acceptance deliverables** — posters, talks, code releases

## Core Philosophy

1. **Be proactive.** Deliver complete drafts, not questions. Scientists are busy — produce something concrete they can react to, then iterate.
2. **Never hallucinate citations.** AI-generated citations have ~40% error rate. Always fetch programmatically. Mark unverifiable citations as `[CITATION NEEDED]`.
3. **Paper is a story, not a collection of experiments.** Every paper needs one clear contribution stated in a single sentence. If you can't do that, the paper isn't ready.
4. **Experiments serve claims.** Every experiment must explicitly state which claim it supports. Never run experiments that don't connect to the paper's narrative.
5. **Commit early, commit often.** Every completed experiment batch, every paper draft update — commit with descriptive messages. Git log is the experiment history.

### Proactivity and Collaboration

**Default: Be proactive. Draft first, ask with the draft.**

| Confidence Level | Action |
|-----------------|--------|
| **High** (clear repo, obvious contribution) | Write full draft, deliver, iterate on feedback |
| **Medium** (some ambiguity) | Write draft with flagged uncertainties, continue |
| **Low** (major unknowns) | Ask 1-2 targeted questions via `clarify`, then draft |

| Section | Draft Autonomously? | Flag With Draft |
|---------|-------------------|-----------------|
| Abstract | Yes | "Framed contribution as X — adjust if needed" |
| Introduction | Yes | "Emphasized problem Y — correct if wrong" |
| Methods | Yes | "Included details A, B, C — add missing pieces" |
| Experiments | Yes | "Highlighted results 1, 2, 3 — reorder if needed" |
| Related Work | Yes | "Cited papers X, Y, Z — add any I missed" |

**Block for input only when**: target venue unclear, multiple contradictory framings, results seem incomplete, explicit request to review first.

---


## Phase guides

- [Phase 0: Project Setup](phase-0-project-setup.md)
- [Phase 1: Literature Review](phase-1-literature-review.md)
- [Phase 2: Experiment Design](phase-2-experiment-design.md)
- [Phase 3: Experiment Execution & Monitoring](phase-3-experiment-execution-monitoring.md)
- [Phase 4: Result Analysis](phase-4-result-analysis.md)
- [Phase 5: Paper Drafting](phase-5-paper-drafting.md)
- [Phase 6: Self-Review & Revision](phase-6-self-review-revision.md)
- [Phase 7: Submission Preparation](phase-7-submission-preparation.md)
- [Phase 8: Post-Acceptance Deliverables](phase-8-post-acceptance-deliverables.md)
- [Workshop & Short Papers](workshop-short-papers.md)
- [Paper Types Beyond Empirical ML](paper-types-beyond-empirical-ml.md)
- [Hermes Agent Integration](hermes-agent-integration.md)
- [Reviewer Evaluation Criteria](reviewer-evaluation-criteria.md)
- [Common Issues and Solutions](common-issues-and-solutions.md)
- [Reference Documents](reference-documents.md)
