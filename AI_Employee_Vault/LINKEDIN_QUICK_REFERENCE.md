# LinkedIn Auto-Posting - Quick Reference Card

**Status:** ✅ Complete - Persistent Session

---

## 🚀 Quick Start (First Time)

```bash
cd D:\Hackathone-0\Personal-AI-Employe-FTEs\AI_Employee_Vault\scripts

# 1. Test installation
python test_linkedin_setup.py ..

# 2. Setup session (login to LinkedIn)
python linkedin_auto_poster.py --setup-session --vault ..

# 3. Verify session
python linkedin_auto_poster.py --check-session --vault ..
```

---

## 📝 Create & Post

### Method 1: Manual Approval (Recommended)

```bash
# Create draft
python linkedin_auto_poster.py --vault .. --create-draft "Your post content #hashtags"

# Move draft from Pending_Approval/ to Approved/ in Obsidian

# Post
python linkedin_auto_poster.py --vault .. --post-approved
```

### Method 2: Batch File

```bash
post-to-linkedin.bat
```

---

## 🔧 Common Commands

| Command | Purpose |
|---------|---------|
| `--setup-session` | First-time LinkedIn login |
| `--check-session` | Verify session is valid |
| `--create-draft "text"` | Create draft for approval |
| `--post-approved` | Post all approved content |
| `--clear-session` | Clear session, re-login |

---

## 📅 Schedule Posts

```bash
# Install daily task (9 AM)
python scheduler_linkedin.py --vault .. --install

# Check status
python scheduler_linkedin.py --vault .. --status

# Remove schedule
python scheduler_linkedin.py --vault .. --uninstall
```

---

## 📁 Folders

| Folder | Purpose |
|--------|---------|
| `Pending_Approval/` | Draft posts awaiting approval |
| `Approved/` | Approved posts (auto-posts from here) |
| `Done/` | Successfully posted |
| `.linkedin_session/` | Saved session data |
| `Logs/` | Activity logs |

---

## 🛠️ Troubleshooting

**Session expired?**
```bash
python linkedin_auto_poster.py --setup-session --vault ..
```

**Check logs:**
```
Open: Logs/linkedin_YYYY-MM-DD.log
```

**Test installation:**
```bash
python test_linkedin_setup.py ..
```

---

## 📝 Example Posts

### Test Post
```
Test auto post from AI Employee Hackathon! 🚀
Building autonomous agents with local-first AI.
#AIEmployee #Hackathon2026 #Panaversity #Test
```

### Business Update
```
Excited to build my Digital FTE in Panaversity Hackathon 0!
Boosting productivity with local-first AI agents.
#AIEmployee #Hackathon2026 #Panaversity #Automation
```

### Milestone
```
🎉 Silver Tier Complete!
My AI Employee now auto-posts to LinkedIn.
#AI #Automation #Milestone #Hackathon
```

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| `LINKEDIN_AUTO_POST_SETUP.md` | Full setup guide |
| `LINKEDIN_AUTO_POST_COMPLETE.md` | Implementation summary |
| `.qwen/skills/linkedin-auto-post/skill.md` | Agent Skill docs |

---

## ✅ Silver Tier Status

| Requirement | Status |
|-------------|--------|
| Auto-post to LinkedIn | ✅ Complete |
| Persistent session | ✅ Complete |
| HITL approval | ✅ Complete |
| Orchestrator integration | ✅ Complete |
| Scheduling | ✅ Complete |

---

*Quick Reference - LinkedIn Auto-Posting v0.2*
*AI Employee Hackathon 0 - Silver Tier*
