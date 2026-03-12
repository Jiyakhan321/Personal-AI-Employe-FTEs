# linkedin-auto-post Skill

**Description:** Automatically posts content to LinkedIn with persistent session management.

**Category:** Social Media Automation

**Tier:** Silver

---

## Overview

This skill enables autonomous LinkedIn posting with:
- **Persistent Session:** Login once, post automatically for weeks
- **Human-in-the-Loop:** Draft posts require approval before publishing
- **Retry Logic:** Automatic session recovery on expiration
- **Audit Trail:** All posts logged in Obsidian vault

---

## Installation

### Prerequisites

1. **Playwright installed:**
   ```bash
   pip install playwright
   playwright install chromium
   ```

2. **Vault structure:**
   ```
   AI_Employee_Vault/
   ├── Pending_Approval/
   ├── Approved/
   ├── Done/
   └── Logs/
   ```

### Setup Steps

1. **First-time session setup:**
   ```bash
   cd AI_Employee_Vault/scripts
   python linkedin_auto_poster.py --setup-session --vault ..
   ```

2. **Verify session:**
   ```bash
   python linkedin_auto_poster.py --check-session --vault ..
   ```

---

## Usage

### As Qwen Code Skill

Invoke from Qwen Code:

```
skill: "linkedin-auto-post"
```

### Command Line

**Create draft post:**
```bash
python linkedin_auto_poster.py --vault PATH --create-draft "Your post content here #hashtags"
```

**Post approved content:**
```bash
python linkedin_auto_poster.py --vault PATH --post-approved
```

**Check session status:**
```bash
python linkedin_auto_poster.py --check-session --vault PATH
```

---

## Workflow

### Standard Flow (HITL)

```
1. Qwen Code creates draft
   ↓
2. Draft saved to: Pending_Approval/LINKEDIN_POST_*.md
   ↓
3. Human reviews and moves to: Approved/
   ↓
4. Auto-poster processes approved posts
   ↓
5. Success → Move to: Done/
   Failure → Log error, keep in Approved/
```

### Autonomous Flow (After 5 successful posts)

```
1. Qwen Code detects posting opportunity
   ↓
2. Creates Plan.md with post content
   ↓
3. Executes: linkedin_auto_poster.py --post-approved
   ↓
4. Logs result in Dashboard.md
```

---

## Post Content Guidelines

### Recommended Content
- Business updates
- Project milestones
- Achievement announcements
- Industry insights
- Event participation

### Character Limits
- **Maximum:** 3,000 characters
- **Optimal:** 150-300 characters
- **Hashtags:** 3-5 relevant tags

### Example Posts

**Project Announcement:**
```
Excited to build my Digital FTE in Panaversity Hackathon 0! 
Boosting productivity with local-first AI agents. 
#AIEmployee #Hackathon2026 #Panaversity #Automation
```

**Business Update:**
```
Just launched our new AI consulting service! 
Helping businesses automate with local-first AI agents. 
DM me if you want to learn more. 
#AI #Automation #Business #TechStartup
```

---

## Troubleshooting

### Session Expired

**Symptom:** Posting fails, redirected to login page

**Fix:**
```bash
python linkedin_auto_poster.py --setup-session --vault PATH
```

### Post Button Not Found

**Symptom:** Error: "Could not find Post button"

**Cause:** LinkedIn UI changed or page didn't load fully

**Fix:**
1. Check internet connection
2. Increase wait time in script
3. Run with `--check-session` first

### Rate Limiting

**Symptom:** Post fails after multiple attempts

**Fix:**
- Wait 24 hours before next post
- LinkedIn limits to ~15 posts/day
- Space posts 1-2 hours apart

---

## Integration with Orchestrator

The skill integrates with `orchestrator.py` for automated workflows:

```python
# In orchestrator.py
def process_linkedin_task(self, task_file: Path):
    """Process LinkedIn posting task from Plan.md"""
    content = self.extract_post_content(task_file)
    
    # Create approval request
    poster = LinkedInAutoPoster(str(self.vault_path))
    draft_path = poster.create_draft(content)
    
    # Log action
    self.logger.info(f"Created LinkedIn draft: {draft_path.name}")
```

---

## Files

| File | Purpose |
|------|---------|
| `scripts/linkedin_auto_poster.py` | Main posting script |
| `.linkedin_session/user_data/` | Browser profile (auto-created) |
| `.linkedin_session/storage_state.json` | Cookies/tokens (auto-saved) |
| `Logs/linkedin_YYYY-MM-DD.log` | Daily activity logs |

---

## Security Notes

- **Session tokens** stored locally in vault
- **No credentials** stored (OAuth via browser)
- **Vault should be private** (gitignored, encrypted backup recommended)
- **Never share** `.linkedin_session/` folder

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.2 | 2026-03-01 | Persistent session, retry logic, better selectors |
| 0.1 | 2026-02-27 | Initial implementation |

---

*LinkedIn Auto Poster Skill v0.2 - Silver Tier Enhanced*
*Powered by Playwright + Qwen Code*
