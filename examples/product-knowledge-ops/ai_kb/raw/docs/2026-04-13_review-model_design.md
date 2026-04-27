---
date: 2026-04-13
type: design
project: Team Workflow Expansion
projects:
  - Team Workflow Expansion
  - Core Knowledge Portal
---

# Product Model Design

This design proposes a generic review workflow model with reusable fields for review scope, approver group,
review window, team constraints, and audit category.

Implications:

- Team Workflow Expansion can reuse the review configuration model.
- Flexible Review Workflow can use the same model for review-level constraints.
- Core Knowledge Portal remains the system of record for evidence and review status.

Non-goals:

- The design does not define AI ranking behavior.
- The design does not replace the existing review intake flow.
