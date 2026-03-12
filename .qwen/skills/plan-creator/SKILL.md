---
name: plan-creator
description: |
  Create structured Plan.md files for AI reasoning loops.
  Generates actionable plans with checkboxes for multi-step tasks.
  Essential for Silver tier Claude/Qwen Code reasoning workflow.
---

# Plan Creator

Create structured action plans for AI Employee tasks.

## Overview

This skill generates `Plan.md` files that guide AI reasoning through multi-step tasks.

## Plan Template

```markdown
---
created: 2026-02-27T10:30:00Z
type: plan
status: in_progress
objective: Process client invoice request
priority: high
---

# Action Plan

## Objective
Process client invoice request and send response

## Context
- **Source:** EMAIL_client_invoice_20260227.md
- **From:** client@example.com
- **Request:** Invoice for January services

## Steps

- [ ] Review email content
- [ ] Check accounting records for outstanding invoices
- [ ] Generate invoice PDF
- [ ] Draft email response
- [ ] Create approval request (if amount > $500)
- [ ] Send email (after approval)
- [ ] Log transaction
- [ ] Move to /Done

## Resources Needed
- Accounting system access
- Invoice template
- Email client

## Blockers
None

## Notes
- Client prefers PDF invoices
- Payment terms: Net 30

---
*Created by Plan Creator v0.1*
```

## Usage

### Create Plan from Task

```python
from plan_creator import PlanCreator

creator = PlanCreator('/path/to/vault')

plan = creator.create_plan(
    objective="Process client invoice request",
    source_file="EMAIL_client_20260227.md",
    steps=[
        "Review email content",
        "Check accounting records",
        "Generate invoice PDF",
        "Draft email response",
        "Send email"
    ],
    priority="high"
)
```

### Update Plan Status

```python
creator.update_step(plan_file, step_number=3, completed=True)
creator.set_status(plan_file, "in_progress")
```

### Complete Plan

```python
creator.complete_plan(plan_file, notes="Invoice sent successfully")
```

## Integration with Orchestrator

The orchestrator automatically creates plans for batch tasks:

```python
# In orchestrator.py
def process_tasks_with_qwen(self):
    pending_tasks = self.get_pending_tasks()
    
    for task in pending_tasks:
        plan = plan_creator.create_plan(
            objective=f"Process {task.name}",
            source_file=task.name,
            steps=extract_steps(task.content)
        )
```

## Plan Statuses

| Status | Description |
|--------|-------------|
| `pending` | Plan created, not started |
| `in_progress` | Currently working |
| `blocked` | Waiting on external factor |
| `completed` | All steps done |
| `cancelled` | Plan abandoned |

## Best Practices

1. **One objective per plan** - Keep plans focused
2. **Numbered steps** - Clear sequence
3. **Checkboxes** - Track progress visually
4. **Context section** - Include relevant background
5. **Notes section** - Document decisions

## Example: Email Response Plan

```markdown
---
created: 2026-02-27T10:30:00Z
objective: Reply to client inquiry
priority: medium
---

# Plan: Reply to Client Inquiry

## Steps
- [ ] Read email thoroughly
- [ ] Identify key questions
- [ ] Gather information needed
- [ ] Draft response
- [ ] Review for clarity
- [ ] Send (or create approval request)

## Notes
Client asked about pricing and timeline
```

## Example: Payment Processing Plan

```markdown
---
created: 2026-02-27T10:30:00Z
objective: Process vendor payment
priority: high
requires_approval: true
---

# Plan: Process Vendor Payment

## Steps
- [ ] Verify invoice details
- [ ] Check budget allocation
- [ ] Confirm receipt of goods/services
- [ ] Create approval request (amount > $500)
- [ ] Wait for human approval
- [ ] Process payment
- [ ] Log transaction

## Approval Required
Amount: $750.00
Threshold: $500.00
```
