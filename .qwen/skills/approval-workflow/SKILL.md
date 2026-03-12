---
name: approval-workflow
description: |
  Human-in-the-Loop approval workflow for sensitive AI actions.
  Manages approval requests via file movement between folders.
  Use for payments, email sending, and other sensitive operations.
---

# Approval Workflow

Human-in-the-Loop (HITL) pattern for sensitive AI actions.

## Overview

This skill implements a file-based approval workflow:

```
/Needs_Action/ → /Plans/ → /Pending_Approval/ → [Human: /Approved/] → Execute → /Done/
                                                            ↓
                                                     [Human: /Rejected/]
```

## Folder Structure

| Folder | Purpose |
|--------|---------|
| `/Pending_Approval/` | Awaiting human decision |
| `/Approved/` | Approved actions (triggers execution) |
| `/Rejected/` | Rejected actions |

## Approval Request Template

```markdown
---
type: approval_request
action: send_email | payment | post_social | file_operation
created: 2026-02-27T10:30:00Z
expires: 2026-02-28T10:30:00Z
priority: high | medium | low
status: pending
---

# Approval Request

## Action Details
- **Type:** Send Email
- **To:** client@example.com
- **Subject:** Invoice #1234
- **Amount:** $500.00 (if payment)

## Context
[Additional context about why this action is needed]

## Risk Assessment
- [ ] Verified recipient
- [ ] Amount within limits
- [ ] Content reviewed

---

## To Approve
Move this file to `/Approved/` folder.

## To Reject
Move this file to `/Rejected/` folder and add reason.

---
*Created by AI Employee v0.1*
```

## Usage

### 1. AI Creates Approval Request

When AI detects a sensitive action needed:

```python
# In your AI agent code
def create_approval_request(action_type: str, details: dict) -> Path:
    """Create approval request file."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"APPROVAL_{action_type}_{timestamp}.md"
    
    content = f"""---
type: approval_request
action: {action_type}
created: {datetime.now().isoformat()}
expires: {(datetime.now() + timedelta(days=1)).isoformat()}
status: pending
---

# Approval Request

## Details
{json.dumps(details, indent=2)}

## To Approve
Move to /Approved/

## To Reject
Move to /Rejected/
"""
    
    filepath = vault_path / 'Pending_Approval' / filename
    filepath.write_text(content)
    return filepath
```

### 2. Human Reviews

Open Obsidian and review files in `Pending_Approval/`:

- Read the request details
- Check risk assessment
- Verify context

### 3. Human Decides

**To Approve:**
```bash
move Pending_Approval\APPROVAL_*.* Approved\
```

**To Reject:**
```bash
move Pending_Approval\APPROVAL_*.* Rejected\
```

### 4. Orchestrator Executes

```python
# In orchestrator.py
def check_approvals():
    """Check for approved actions and execute."""
    approved_files = list(approved_folder.glob('*.md'))
    
    for approved_file in approved_files:
        content = approved_file.read_text()
        action_type = extract_action_type(content)
        
        if action_type == 'send_email':
            send_approved_email(approved_file)
        elif action_type == 'payment':
            process_approved_payment(approved_file)
            
        # Move to Done
        shutil.move(str(approved_file), str(done_folder / approved_file.name))
```

## Approval Thresholds

Configure what requires approval:

```python
# Configuration
APPROVAL_THRESHOLDS = {
    'email': {
        'new_contact': True,      # Always approve new contacts
        'bulk_send': True,         # Approve bulk emails
        'attachment': False        # No approval for attachments
    },
    'payment': {
        'new_payee': True,         # Always approve new payees
        'amount_over': 500,        # Approve payments over $500
        'international': True      # Approve international transfers
    },
    'social': {
        'reply': False,            # Auto-approve replies
        'new_post': True,          # Approve new posts
        'scheduled': False         # No approval for scheduled posts
    }
}
```

## Expiration Handling

Expired approvals are moved to Rejected:

```python
def check_expired_approvals():
    """Move expired approvals to Rejected."""
    now = datetime.now()
    
    for approval_file in pending_approval.glob('*.md'):
        content = approval_file.read_text()
        expires = extract_expires(content)
        
        if expires and datetime.fromisoformat(expires) < now:
            # Add expiration notice
            content += f"\n\n**EXPIRED:** {expires}"
            approval_file.write_text(content)
            
            # Move to Rejected
            shutil.move(
                str(approval_file),
                str(rejected_folder / approval_file.name)
            )
```

## Logging

All approval actions are logged:

```python
def log_approval(action: str, status: str, approved_by: str = 'human'):
    """Log approval decision."""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action': action,
        'status': status,
        'approved_by': approved_by
    }
    
    log_file = logs_folder / f"{datetime.now().strftime('%Y-%m-%d')}.jsonl'
    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
```

## Integration with AI Employee

### Qwen Code Integration

Add to your Qwen Code prompts:

```
For any sensitive actions:
1. Create approval request in /Pending_Approval/
2. Do NOT execute directly
3. Wait for human to move file to /Approved/
4. Orchestrator will execute approved actions
```

### Example Flow

```
1. Gmail Watcher detects invoice request
2. Qwen Code drafts reply
3. AI creates approval request:
   - /Pending_Approval/APPROVAL_send_email_20260227_103000.md
4. Human reviews in Obsidian
5. Human moves to /Approved/
6. Orchestrator detects approval
7. Email MCP sends email
8. File moved to /Done/
9. Log entry created
```

## Security Best Practices

1. **Never auto-approve:**
   - Payments to new recipients
   - Emails to new contacts
   - Large amounts (>$500)

2. **Always log:**
   - Who approved
   - When approved
   - What was approved

3. **Set expiration:**
   - Default: 24 hours
   - High-risk: 1 hour
   - Low-risk: 7 days

4. **Audit regularly:**
   - Review /Rejected/ folder weekly
   - Check logs for patterns
   - Adjust thresholds as needed

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Approval not executing | Check orchestrator is running |
| File stuck in Pending | Human hasn't moved it yet |
| Executed without approval | Check approval thresholds config |
| Expired too quickly | Adjust expiration settings |
