# How to Post on LinkedIn with AI Employee

## Overview

The AI Employee uses a **Human-in-the-Loop (HITL)** approach for LinkedIn posting:

1. **Create draft** → AI generates or you write content
2. **Review** → You review the draft in Obsidian
3. **Approve** → Move to Approved/ folder
4. **Post** → AI posts to LinkedIn

---

## Step-by-Step Guide

### Step 1: Setup Session (First Time Only)

```bash
cd D:\Hackathone-0\Personal-AI-Employe-FTEs\AI_Employee_Vault\scripts
set PLAYWRIGHT_BROWSERS_PATH=
python linkedin_poster.py --setup-session
```

**What happens:**
- Browser opens
- You log in to LinkedIn
- Session is saved
- Browser closes

---

### Step 2: Create a Post Draft

**Option A: Manual Content**

```bash
set PLAYWRIGHT_BROWSERS_PATH=
cd D:\Hackathone-0\Personal-AI-Employe-FTEs\AI_Employee_Vault\scripts
python linkedin_poster.py --vault .. --create-draft "Your post content here"
```

**Option B: AI-Generated Content**

Let Qwen Code generate the post:

```bash
cd AI_Employee_Vault
claude "Create a LinkedIn post about our new AI Employee project. Focus on automation and productivity."
```

Then copy the generated content to the draft command.

---

### Step 3: Review the Draft

**Open Obsidian:**
1. Open folder: `AI_Employee_Vault`
2. Navigate to: `Pending_Approval/`
3. Open the new `LINKEDIN_POST_*.md` file

**Review:**
- Content is appropriate
- No typos
- Character count is under 3000
- Hashtags are relevant

---

### Step 4: Approve or Reject

**To Approve:**
```bash
# Move file to Approved folder
move Pending_Approval\LINKEDIN_POST_*.md Approved\
```

**To Reject:**
```bash
# Move file to Rejected folder with reason
move Pending_Approval\LINKEDIN_POST_*.md Rejected\
```

---

### Step 5: Post to LinkedIn

```bash
set PLAYWRIGHT_BROWSERS_PATH=
cd D:\Hackathone-0\Personal-AI-Employe-FTEs\AI_Employee_Vault\scripts
python linkedin_poster.py --vault .. --post-approved
```

**What happens:**
1. Browser opens (headless)
2. Logs in to LinkedIn
3. Clicks "Start a post"
4. Enters your content
5. Clicks "Post"
6. Moves file to Done/

**Expected Output:**
```
[OK] Posted and moved to Done: LINKEDIN_POST_20260228_*.md
[OK] Posted 1 content(s)
```

---

## Complete Example

### Post About AI Employee

```bash
# Navigate to scripts
cd D:\Hackathone-0\Personal-AI-Employe-FTEs\AI_Employee_Vault\scripts

# Create draft
set PLAYWRIGHT_BROWSERS_PATH=
python linkedin_poster.py --vault .. --create-draft "🚀 Excited to announce our AI Employee project!

We've built an autonomous digital worker that:
✅ Monitors Gmail 24/7
✅ Tracks LinkedIn messages
✅ Creates action plans automatically
✅ Requires human approval for sensitive actions

Built with:
- Qwen Code (Brain)
- Obsidian (Memory)
- Playwright (Hands)
- Python (Glue)

This is the future of work - humans and AI collaborating seamlessly.

#AI #Automation #Productivity #FutureOfWork"

# Review in Obsidian
# ... open Pending_Approval/LINKEDIN_POST_*.md ...

# Approve
move Pending_Approval\LINKEDIN_POST_*.md Approved\

# Post
python linkedin_poster.py --vault .. --post-approved
```

---

## Automated Posting (Silver Tier)

### Auto-Generate Posts from Business Updates

Create a script that:
1. Reads `Business_Goals.md`
2. Generates weekly update posts
3. Creates drafts for approval

**Example:**
```python
# In scripts/auto_post.py
from datetime import datetime

content = f"""📈 Weekly Business Update

This week we accomplished:
- Completed Silver Tier AI Employee
- Integrated Gmail + LinkedIn watchers
- Processed 50+ emails automatically

Next week:
- Add WhatsApp monitoring
- Implement CEO Briefing

#BusinessUpdate #AI #Automation"""

# Create draft
poster.create_draft(content)
```

---

## Post Templates

### Template 1: Business Update

```markdown
📈 Weekly Business Update

This week we accomplished:
- {accomplishment_1}
- {accomplishment_2}
- {accomplishment_3}

Looking forward to:
- {next_week_goal}

#BusinessUpdate #AI #Automation
```

### Template 2: Product Announcement

```markdown
🚀 Exciting News!

We're launching {product_name} to help you {benefit}.

Key features:
- {feature_1}
- {feature_2}
- {feature_3}

Learn more: {link}

#ProductLaunch #Innovation #AI
```

### Template 3: Thought Leadership

```markdown
💡 Reflection on {topic}:

{insight_1}

{insight_2}

{insight_3}

What's your experience with {topic}?

#ThoughtLeadership #AI #FutureOfWork
```

---

## Best Practices

### Content Guidelines

✅ **Do:**
- Keep posts under 1500 characters (higher engagement)
- Use 3-5 relevant hashtags
- Include emojis for visual appeal
- Add call-to-action (CTA)
- Proofread before approving

❌ **Don't:**
- Post too frequently (max 1-2 per day)
- Use too many hashtags (max 5)
- Post controversial content
- Forget to review before posting

### Posting Schedule

| Day | Time | Type |
|-----|------|------|
| Monday | 9 AM | Weekly update |
| Wednesday | 2 PM | Thought leadership |
| Friday | 11 AM | Project showcase |

---

## Troubleshooting

### Problem: "Not logged in"

**Solution:**
```bash
python linkedin_poster.py --clear-session
python linkedin_poster.py --setup-session
```

### Problem: "Post button not found"

**Solution:**
- Check if LinkedIn changed UI
- Try manual posting to verify account
- Clear session and re-authenticate

### Problem: "Content too long"

**Solution:**
- LinkedIn limit is 3000 characters
- Edit draft to reduce length
- Split into multiple posts

---

## Command Reference

| Command | Purpose |
|---------|---------|
| `--setup-session` | First-time LinkedIn login |
| `--clear-session` | Clear saved session |
| `--create-draft "text"` | Create draft for approval |
| `--post-approved` | Post all approved drafts |
| `--vault PATH` | Specify Obsidian vault |

---

## Integration with AI Employee

### Full Workflow

```
1. Gmail Watcher detects inquiry
   ↓
2. Orchestrator creates Plan.md
   ↓
3. Qwen Code drafts LinkedIn response
   ↓
4. LinkedIn Poster creates draft
   ↓
5. You approve (move to Approved/)
   ↓
6. LinkedIn Poster posts
   ↓
7. Moves to Done/
```

---

*LinkedIn Poster v0.1 - Silver Tier*  
*AI Employee - Qwen Code Brain*
