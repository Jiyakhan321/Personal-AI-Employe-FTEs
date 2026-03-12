# AI Employee - Silver Tier Setup Guide

## Quick Start

Follow these steps to set up and run your Silver Tier AI Employee.

---

## Prerequisites Check

```bash
# Check Python version (need 3.13+)
python --version

# Check if in vault directory
cd AI_Employee_Vault
```

---

## Step 1: Gmail Watcher Setup

### 1.1 Credentials Already Configured ✓

Your `credentials.json` is already in the scripts folder.

### 1.2 Authenticate with Gmail

```bash
cd scripts
python gmail_watcher.py --authenticate
```

This will:
1. Open your default browser
2. Ask you to sign in to Google
3. Request Gmail API permissions
4. Save authentication token

### 1.3 Test Gmail Watcher

```bash
# One-time scan
python gmail_watcher.py --vault ..

# Or continuous monitoring
python gmail_watcher.py --vault .. --continuous --interval 120
```

---

## Step 2: LinkedIn Watcher Setup

### 2.1 Install Playwright (if not already done)

```bash
pip install playwright
playwright install chromium
```

### 2.2 Setup LinkedIn Session

```bash
python linkedin_watcher.py --setup-session
```

This will:
1. Open browser to LinkedIn
2. You log in to your account
3. Wait for feed to load
4. Close browser (session saved)

### 2.3 Test LinkedIn Watcher

```bash
# One-time scan
python linkedin_watcher.py --vault ..

# Or continuous monitoring (every 5 minutes)
python linkedin_watcher.py --vault .. --continuous --interval 300
```

---

## Step 3: Orchestrator (Silver Tier)

The updated orchestrator now:
- Creates Plan.md files for tasks
- Manages approval workflow (HITL)
- Checks for expired approvals
- Updates dashboard with plan counts

### Run Orchestrator

```bash
# One-time cycle
python orchestrator.py ..

# Continuous mode
python orchestrator.py .. --continuous --interval 60
```

---

## Step 4: Complete System Test

### Open 3 Terminal Windows

**Window 1 - Gmail Watcher:**
```bash
cd AI_Employee_Vault\scripts
python gmail_watcher.py --vault .. --continuous --interval 120
```

**Window 2 - LinkedIn Watcher:**
```bash
cd AI_Employee_Vault\scripts
python linkedin_watcher.py --vault .. --continuous --interval 300
```

**Window 3 - Orchestrator:**
```bash
cd AI_Employee_Vault\scripts
python orchestrator.py .. --continuous --interval 60
```

### Send Test Email

1. Send an email to your Gmail account with subject "Test AI Employee"
2. Within 2 minutes, Gmail Watcher should detect it
3. Check `Needs_Action/` for new GMAIL_*.md file
4. Orchestrator will create a Plan.md file
5. Check `Plans/` folder

---

## Step 5: Human-in-the-Loop Workflow

### When AI Needs Approval

1. AI creates approval request in `Pending_Approval/`
2. You review the file in Obsidian
3. **To Approve:** Move file to `Approved/`
4. **To Reject:** Move file to `Rejected/`
5. Orchestrator executes approved actions

### Example Approval Flow

```markdown
# In Pending_Approval/APPROVAL_send_email_*.md

---
type: approval_request
action: send_email
to: client@example.com
subject: Re: Project Inquiry
---

Ready to send. Move to /Approved to proceed.
```

**You move to Approved/ → Orchestrator sends email → Moves to Done/**

---

## Folder Structure

```
AI_Employee_Vault/
├── Dashboard.md              # Updated with Silver Tier stats
├── Company_Handbook.md       # Updated with Silver Tier rules
├── Business_Goals.md
├── Needs_Action/             # New tasks from watchers
│   ├── GMAIL_*.md           # Email tasks
│   ├── WHATSAPP_*.md        # WhatsApp tasks
│   ├── LINKEDIN_MSG_*.md    # LinkedIn messages
│   └── LINKEDIN_CONN_*.md   # LinkedIn connections
├── Plans/                    # NEW: Plan.md files (Silver)
│   └── PLAN_*.md
├── Pending_Approval/         # Awaiting your decision
├── Approved/                 # Approved actions
├── Rejected/                 # Rejected actions
├── Done/                     # Completed tasks
├── Logs/                     # System logs
└── scripts/
    ├── gmail_watcher.py      # NEW: Gmail monitoring
    ├── linkedin_watcher.py   # NEW: LinkedIn monitoring
    ├── filesystem_watcher.py # Bronze: File monitoring
    ├── orchestrator.py       # UPDATED: Silver Tier orchestrator
    └── credentials.json      # Your Gmail credentials
```

---

## Commands Reference

### Gmail Watcher

```bash
# Authenticate (first time only)
python gmail_watcher.py --authenticate

# One-time scan
python gmail_watcher.py --vault PATH

# Continuous monitoring
python gmail_watcher.py --vault PATH --continuous --interval 120
```

### LinkedIn Watcher

```bash
# Setup session (first time only)
python linkedin_watcher.py --setup-session

# Clear session
python linkedin_watcher.py --clear-session

# One-time scan
python linkedin_watcher.py --vault PATH

# Continuous monitoring
python linkedin_watcher.py --vault PATH --continuous --interval 300
```

### Orchestrator

```bash
# One-time cycle
python orchestrator.py PATH

# Continuous mode
python orchestrator.py PATH --continuous --interval 60

# Verbose logging
python orchestrator.py PATH --verbose
```

---

## Troubleshooting

### Gmail Watcher Issues

**Problem:** Authentication fails
- **Solution:** Delete `scripts/token.json` and re-run `--authenticate`

**Problem:** No emails found
- **Solution:** Check if emails are in Primary tab (not Promotions/Social)

**Problem:** API quota exceeded
- **Solution:** Wait 24 hours or request quota increase in Google Cloud Console

### LinkedIn Watcher Issues

**Problem:** Session expired
- **Solution:** Run `--clear-session` then `--setup-session` again

**Problem:** Not logged in
- **Solution:** Make sure you complete login when browser opens

**Problem:** Playwright errors
- **Solution:** Run `playwright install chromium` again

### Orchestrator Issues

**Problem:** Plans not created
- **Solution:** Check logs in `Logs/` folder for errors

**Problem:** Dashboard not updating
- **Solution:** Ensure Dashboard.md exists and is writable

---

## Silver Tier Features Checklist

- [x] Gmail Watcher (monitors every 2 minutes)
- [x] LinkedIn Watcher (monitors every 5 minutes)
- [x] Plan.md creation for tasks
- [x] Human-in-the-Loop approval workflow
- [x] Approval expiration handling
- [x] Enhanced dashboard with plan counts
- [x] Comprehensive logging

---

## Next Steps (Gold Tier)

To advance to Gold Tier, add:
- [ ] WhatsApp Watcher (Playwright-based)
- [ ] Email MCP Server (for sending emails)
- [ ] Odoo accounting integration
- [ ] Ralph Wiggum loop for autonomous completion
- [ ] Weekly CEO Briefing generation

---

*AI Employee v0.2 - Silver Tier*
*Powered by Qwen Code*
