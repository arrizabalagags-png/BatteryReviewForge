---
name: battery-review-forge
description: Coordinate a multi-stage battery Review or Perspective project across planning, evidence, writing, submission, and revision. Use for the full workflow or unclear stage requests, not a single specialized edit.
---

# Battery Review Forge

Coordinate a battery Review or Perspective across stages while keeping the current plan, evidence, and revision decisions inspectable. For a single-stage task, use the corresponding specialist skill. Do not apply this workflow to analysis of a new primary experimental paper. Respond in the user's language unless asked otherwise.

## Route the request

Identify the chemistry or device class, article type (narrative/critical Review, scoping review, systematic review, Perspective), target readership and venue if known, current manuscript state, accessible sources, and requested deliverable. Infer these from supplied files first. Ask only for missing decisions that block useful work. Read [codex-operations.md](references/codex-operations.md) for multi-session or multi-agent work.

| Stage | Specialist skill |
| --- | --- |
| Angle, scope, competing Reviews, outline | `battery-review-plan` |
| Search, screening, source-state inventory | `battery-literature-map` |
| Claim-to-source and citation verification | `battery-claim-check` |
| Battery metrics, mechanisms, cross-study comparisons | `battery-metrics-audit` |
| Draft or restructure sections | `battery-review-write` |
| Plan, create, or audit figures | `battery-review-figure` |
| Polish, translate, or compress existing prose | `battery-review-polish` |
| Whole-manuscript pre-submission audit | `battery-review-audit` |
| Journal rules and initial submission package | `battery-review-submission` |
| Independent referee-style assessment in a fresh session/agent | `battery-reviewer` |
| Editor/reviewer response and revision | `battery-review-response` |

For a full-project request, load each specialist only as the work reaches its stage. Do not read every skill or create every template at intake. If a specialist is unavailable, follow the shared rules below and state the missing capability only if it affects the result.

## Shared rules

1. **One current plan.** Record the review question, boundaries, central judgement, section roles, display-item roles, venue constraints, and open decisions in a project brief. Deliberately amend it when evidence changes the plan; mark older plans and figure numbers superseded. The brief is an alignment tool, not a reason to ignore new evidence.
2. **Count source states separately.** Search hits, verified metadata, obtained full texts, supplementary files, papers read, extracted studies, and studies actually supporting claims are different counts. Never present a large search library as a large evidence base.
3. **Trace important claims.** For numerical, mechanistic, priority, safety, scale-up, cost, or negative claims, keep the original source, exact location, conditions, counterevidence, and confidence. Cite primary studies for their measurements; cite Reviews for interpretations or field framing. Mark inaccessible or unverified sources explicitly. Do not invent DOIs, data, quotes, permissions, or reviewer positions.
4. **Compare like with like.** A battery number needs its chemistry, cell configuration, tested branch and cycle, normalization boundary, operating conditions, and source. Use `NR` only for a field checked and not reported; use `NV` for one not yet verified. Separate reported, recalculated, and modelled values. Do not rank across incompatible denominators or conditions.
5. **Make the synthesis visible.** Each major section should state what the evidence establishes, where studies disagree, what remains unresolved, and why that changes a research or engineering decision. A chronological catalog of papers is not a sufficient Review.
6. **Check display items independently.** A figure or table needs a scientific claim, source trace, readable final-size layout, and a rights status. A correct credit line does not itself grant reuse permission.
7. **Keep publication actions explicit.** Verify live journal rules for the exact article type and record source URL and access date. Prepare files and checks within the task scope; submit, contact editors/reviewers, publish, or disclose private manuscripts only when the user has authorized that action.

## Deliverables and stopping conditions

Choose the smallest useful durable outputs for the stage. Each specialist has optional empty templates; adapt to existing project files rather than duplicating them. Use [SESSION_HANDOFF.md](assets/templates/SESSION_HANDOFF.md) only when another session needs continuity.

- **Planning is complete** when the angle, closest competing Reviews, evidence feasibility, outline logic, and unresolved decisions are inspectable.
- **Evidence work is complete** when each requested claim or table cell can be traced to a checked source, or is clearly flagged as unresolved.
- **Drafting is complete** when the requested text is delivered with citations and remaining evidence gaps marked, without silently upgrading hypotheses into facts.
- **Preflight is complete** when all applicable venue requirements have checked evidence or an explicit blocker.
- **Response work is complete** when every reviewer point is mapped to a change, evidence-based explanation, or unresolved action, and manuscript locations agree with the response.

Report what was produced, what was verified, and any decision-blocking gaps. Do not call an unverified draft submission-ready or a revised manuscript independently re-reviewed.
