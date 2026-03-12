# LinkedIn Auto-Posting Setup Guide

**Version:** 0.2 (Enhanced with Persistent Session)

**Last Updated:** 2026-03-01

---

## 🎯 Overview

This guide walks you through setting up **fully autonomous LinkedIn posting** with persistent sessions. Once configured, your AI Employee can post to LinkedIn automatically without manual login.

### Key Features

- ✅ **Persistent Session:** Login once, post automatically for weeks
- ✅ **Human-in-the-Loop:** Draft posts require approval before publishing (configurable)
- ✅ **Retry Logic:** Automatic session recovery on expiration
- ✅ **Audit Trail:** All posts logged in Obsidian vault
- ✅ **Orchestrator Integration:** Auto-posts from Plan.md workflows

---

## 📋 Prerequisites

| Component | Status | How to Check |
|-----------|--------|--------------|
| **Python 3.13+** | Required | `python --version` |
| **Playwright** | Required | `python -c "import playwright"` |
| **Chromium Browser** | Required | `playwright install chromium` |
| **LinkedIn Account** | Required | Active account |
| **Obsidian Vault** | Required | AI_Employee_Vault setup |

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Install Playwright (if not already done)

```bash
cd D:\Hackathone-0\Personal-AI-Employe-FTEs\AI_Employee_Vault\scripts
pip install playwright
playwright install chromium
```

### Step 2: Setup LinkedIn Session (FIRST TIME ONLY)

```bash
python linkedin_auto_poster.py --setup-session --vault ..
```

**What happens:**
1. Browser window opens
2. Log in to LinkedIn normally
3. Wait for your feed to load
4. Browser closes automatically
5. Session saved to `vault/.linkedin_session/`

### Step 3: Verify Session

```bash
python linkedin_auto_poster.py --check-session --vault ..
```

**Expected output:**
```
✓ Session is VALID - Ready to post!
```

### Step 4: Create Your First Test Post

```bash
python linkedin_auto_poster.py --vault .. --create-draft "Test auto post from AI Employee Hackathon project! Building autonomous agents with local-first AI. #Test #AIEmployee #Hackathon2026 #Panaversity"
```

**What happens:**
- Draft created in `Pending_Approval/LINKEDIN_POST_*.md`

### Step 5: Approve and Post

**Option A: Manual Approval (Recommended for first 5 posts)**

1. Open Obsidian vault
2. Navigate to `Pending_Approval/` folder
3. Open the draft file
4. Move file to `Approved/` folder
5. Run:
   ```bash
   python linkedin_auto_poster.py --vault .. --post-approved
   ```

**Option B: Direct Post (After trust established)**

Skip approval - post directly from orchestrator.

---

## 📁 File Structure

After setup, your vault will have:

```
AI_Employee_Vault/
├── .linkedin_session/           # Auto-created
│   ├── user_data/               # Browser profile (persistent)
│   └── storage_state.json       # Cookies/tokens backup
├── Pending_Approval/
│   └── LINKEDIN_POST_*.md       # Draft posts awaiting approval
├── Approved/
│   └── LINKEDIN_POST_*.md       # Approved posts (auto-posts from here)
├── Done/
│   └── LINKEDIN_POST_*.md       # Successfully posted
├── Logs/
│   └── linkedin_YYYY-MM-DD.log  # Daily activity logs
└── scripts/
    └── linkedin_auto_poster.py  # Main posting script
```

---

## 🤖 Usage Modes

### Mode 1: Manual Approval (HITL) - Default

**Best for:** First 5-10 posts, sensitive content

```bash
# 1. Create draft
python linkedin_auto_poster.py --vault .. --create-draft "Your post content"

# 2. Move draft from Pending_Approval/ to Approved/

# 3. Post
python linkedin_auto_poster.py --vault .. --post-approved
```

### Mode 2: Fully Autonomous

**Best for:** Regular business updates, after trust established

Integrate with orchestrator:

```bash
# Orchestrator auto-posts when Plan.md contains LinkedIn task
python orchestrator.py .. --continuous
```

### Mode 3: Agent Skill (Qwen Code)

Invoke from Qwen Code:

```
skill: "linkedin-auto-post"
```

---

## 📝 Post Content Guidelines

### Recommended Content Types

| Type | Example | Frequency |
|------|---------|-----------|
| **Project Updates** | "Just launched X project..." | Weekly |
| **Business Milestones** | "Reached 100 clients!" | Monthly |
| **Event Participation** | "Speaking at Hackathon 0..." | As occurs |
| **Industry Insights** | "3 trends in AI for 2026..." | Bi-weekly |
| **Achievement Posts** | "Completed Silver Tier!" | As achieved |

### Character Limits

- **Maximum:** 3,000 characters
- **Optimal:** 150-300 characters (higher engagement)
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

**Milestone Celebration:**
```
🎉 Silver Tier complete!
My AI Employee now:
✓ Monitors Gmail 24/7
✓ Tracks LinkedIn messages
✓ Auto-posts business updates
✓ Manages approvals autonomously

Next: Gold Tier with Odoo integration!
#AI #Automation #Milestone
```

---

## 🔧 Troubleshooting

### Problem: Session Expired

**Symptoms:**
- `--check-session` returns "Session EXPIRED"
- Posting fails with "Not logged in"

**Solution:**
```bash
python linkedin_auto_poster.py --setup-session --vault ..
```

**Prevention:**
- Session should last 2-4 weeks
- LinkedIn may invalidate on suspicious activity
- Use consistent IP/location

### Problem: Post Button Not Found

**Symptoms:**
- Error: "Could not find Post button"
- Timeout during posting

**Solution:**
1. Check internet connection
2. Run `--check-session` first
3. Wait 5 seconds between retry
4. LinkedIn UI may have changed - check logs

### Problem: Rate Limiting

**Symptoms:**
- Post fails after multiple successful posts
- "Too many requests" error

**Solution:**
- LinkedIn limits: ~15 posts/day
- Wait 24 hours
- Space posts 1-2 hours apart

### Problem: Chromium Download Fails

**Symptoms:**
- `playwright install chromium` times out

**Solution:**
```bash
# Retry with mirror
set PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright
playwright install chromium

# Or download manually from:
# https://github.com/microsoft/playwright/releases
```

---

## 📊 Logs and Monitoring

### View Today's Logs

```bash
type Logs\linkedin_%date:~10,4%-%date:~4,2%-%date:~7,2%.log
```

Or open in Obsidian: `Logs/linkedin_YYYY-MM-DD.log`

### Log Events

| Event | Meaning |
|-------|---------|
| `Session valid` | Session check passed |
| `Post submitted successfully` | Post published |
| `Session expired - re-authentication needed` | Login required |
| `Timeout during posting` | Network/page load issue |

---

## 🔐 Security Notes

- **Session tokens** stored locally in vault
- **No credentials** stored (OAuth via browser)
- **Vault should be private** (gitignored, encrypted backup recommended)
- **Never share** `.linkedin_session/` folder
- **Use dedicated business account** (not personal if possible)

---

## 📅 Scheduling (Bonus)

### Windows Task Scheduler

Create daily post schedule:

```batch
@echo off
REM File: daily_linkedin_post.bat
cd /d D:\Hackathone-0\Personal-AI-Employe-FTEs\AI_Employee_Vault\scripts
python linkedin_auto_poster.py --vault .. --post-approved
```

**Schedule:**
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 9:00 AM
4. Action: Start program → `daily_linkedin_post.bat`

### Orchestrator Continuous Mode

```bash
python orchestrator.py .. --continuous --interval 60
```

Orchestrator checks `Approved/` folder every 60 seconds.

---

## 🎯 Success Checklist

- [ ] Playwright installed
- [ ] Chromium browser downloaded
- [ ] Session setup complete (`--setup-session`)
- [ ] Session verified (`--check-session`)
- [ ] Test draft created
- [ ] Test post approved and published
- [ ] Logs checked for errors
- [ ] Orchestrator integration tested

---

## 🆘 Support

**For issues:**
1. Check `Logs/` folder first
2. Run `--check-session` to verify
3. Re-run `--setup-session` if expired
4. Review this guide's troubleshooting section

**Common Commands:**

```bash
# Setup (first time)
python linkedin_auto_poster.py --setup-session --vault ..

# Check status
python linkedin_auto_poster.py --check-session --vault ..

# Create draft
python linkedin_auto_poster.py --vault .. --create-draft "Content"

# Post approved
python linkedin_auto_poster.py --vault .. --post-approved

# Clear and re-setup
python linkedin_auto_poster.py --clear-session --vault ..
python linkedin_auto_poster.py --setup-session --vault ..
```

---

*LinkedIn Auto-Posting v0.2 - Silver Tier Enhanced*
*Powered by Playwright + Qwen Code*
*AI Employee Hackathon 0 - Panaversity*
