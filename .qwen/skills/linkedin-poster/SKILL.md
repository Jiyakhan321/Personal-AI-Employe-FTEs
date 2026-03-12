---
name: linkedin-poster
description: |
  Automatically post to LinkedIn using Playwright browser automation.
  Creates scheduled posts for business promotion and lead generation.
  Requires human approval before posting (Silver tier HITL pattern).
---

# LinkedIn Poster

Automate LinkedIn posting for business promotion.

## Prerequisites

- Playwright installed (see `browsing-with-playwright` skill)
- LinkedIn account
- Human approval for posts (Silver tier requirement)

## Setup

### 1. Install Dependencies

```bash
pip install playwright
playwright install chromium
```

### 2. First-Time Login

```bash
python scripts/linkedin_poster.py --setup-session
```

Log in to LinkedIn when the browser opens.

## Usage

### Create Post (Draft for Approval)

```bash
python scripts/linkedin_poster.py --vault /path/to/vault \
  --create-draft "Excited to announce our new AI Employee service!"
```

### Post with Approval Workflow

1. **AI creates draft** in `Pending_Approval/`
2. **Human reviews** the post content
3. **Human approves** by moving to `Approved/`
4. **Orchestrator posts** to LinkedIn

### Schedule Regular Posts

```bash
# Create weekly business update post
python scripts/linkedin_poster.py --vault /path/to/vault \
  --schedule "weekly" \
  --template "business_update"
```

## Post Templates

### Business Update

```markdown
# Business Update Template

📈 Weekly Business Update

This week we accomplished:
- {accomplishment_1}
- {accomplishment_2}

Looking forward to:
- {next_week_goal}

#BusinessUpdate #AI #Automation
```

### Product Announcement

```markdown
# Product Announcement Template

🚀 Exciting News!

We're launching {product_name} to help you {benefit}.

Key features:
- {feature_1}
- {feature_2}

Learn more: {link}

#ProductLaunch #Innovation
```

## Configuration

### Session Path

- **Windows:** `%APPDATA%/linkedin_session/`
- **Mac/Linux:** `~/.linkedin_session/`

### Clear Session

```bash
python scripts/linkedin_poster.py --clear-session
```

## Approval Workflow

### Example Approval Request

```markdown
---
type: approval_request
action: linkedin_post
created: 2026-02-27T10:30:00Z
status: pending
---

# LinkedIn Post for Approval

## Content

📈 Weekly Business Update

This week we accomplished:
- Completed Bronze Tier AI Employee
- Started Silver Tier development

Looking forward to:
- Implementing Gmail integration

#BusinessUpdate #AI #Automation

---

## To Approve
Move to /Approved/

## To Reject
Move to /Rejected/
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Login required | Run --setup-session again |
| Post failed | Check LinkedIn session is valid |
| Content too long | LinkedIn limit is 3000 characters |
