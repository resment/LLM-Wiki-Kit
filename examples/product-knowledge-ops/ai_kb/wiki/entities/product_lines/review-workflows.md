---
title: Review Workflows
entity_type: product_line
entity_id: product_line.review-workflows
aliases: [Workflow Review]
included_surfaces: [review intake, routing configuration, evidence status]
excluded_surfaces: [billing approval]
adjacent_product_lines: [Knowledge Portal]
relationships:
  - relationship_type: informs
    target_entity: project.knowledge-ai-assistant
    effective_from: 2026-04-21
    effective_to:
    source_path: ai_kb/raw/meetings/2026-04-21_flexible-review-workflow_meeting.md
---

# Review Workflows

## Boundary

Includes review intake, routing configuration, review windows, approver groups, and evidence status.
Billing approval is outside this product-line boundary.

Sources:

- `ai_kb/raw/docs/2026-04-13_review-model_design.md`
- `ai_kb/raw/meetings/2026-04-21_flexible-review-workflow_meeting.md`

## Related Teams

- team.review-operations

## Related Projects

- Flexible Review Workflow
- Team Workflow Expansion
