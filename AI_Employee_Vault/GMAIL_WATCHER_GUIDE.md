# 📧 Gmail Watcher - Complete Setup & Usage Guide

**Status:** ✅ **Installed, Requires Authentication**

---

## 📋 What Gmail Watcher Does

The Gmail Watcher monitors your Gmail inbox 24/7 and:

1. **Detects new important emails** (filters out promotions/social)
2. **Creates action files** in `Needs_Action/` folder
3. **Priority detection** - marks urgent emails as high priority
4. **Continuous monitoring** - checks every 2 minutes

### Example Workflow

```
New Email arrives
    ↓
Gmail Watcher detects it
    ↓
Creates: Needs_Action/GMAIL_12345.md
    ↓
Orchestrator reads it → Creates Plan.md
    ↓
You review → Take action
```

---

## 🔧 Setup Steps

### Step 1: Check Prerequisites

```bash
cd D:\Hackathone-0\Personal-AI-Employe-FTEs\AI_Employee_Vault\scripts

# Check if credentials.json exists
dir credentials.json
```

✅ **You have:** `credentials.json` (413 bytes)

### Step 2: Authenticate with Gmail (FIRST TIME ONLY)

```bash
cd D:\Hackathone-0\Personal-AI-Employe-FTEs\AI_Employee_Vault\scripts

# Run authentication
python gmail_watcher.py --authenticate --vault ..
```

**What happens:**
1. Browser opens automatically
2. Google login page appears
3. Sign in with your Gmail account
4. Grant permissions to the app
5. Browser closes automatically
6. `token.json` is saved (your session)

**Expected output:**
```
Starting Gmail OAuth authentication...
Opening browser for authentication...

[OK] Authentication successful!
Token saved to: D:\...\AI_Employee_Vault\scripts\token.json

You can now run the watcher with: python gmail_watcher.py --vault PATH
```

### Step 3: Test Gmail Connection

```bash
# One-time scan
python gmail_watcher.py --vault .. --interval 60
```

This will:
- Connect to Gmail
- Check last 10 emails
- Create action files for important ones
- Show what it found

### Step 4: Run Continuous Monitoring

```bash
# Run in background (checks every 2 minutes)
python gmail_watcher.py --vault .. --continuous --interval 120
```

**Keep this running** - it monitors Gmail 24/7!

---

## 📁 Files Created

### Action File Format

When Gmail Watcher finds an important email, it creates:

```markdown
---
type: email
from: sender@example.com
subject: Urgent: Invoice Needed
received: 2026-03-12T21:30:00
priority: high
status: pending
---

## Email Content

[Email body here...]

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
```

### Priority Detection

Emails are marked as **high priority** if subject/body contains:
- `urgent`
- `asap`
- `invoice`
- `payment`
- `deadline`
- `important`
- `help`
- `emergency`

### Filtered Out (Ignored)

Emails are **skipped** if they contain:
- `unsubscribe`
- `promotion`
- `sale`
- `newsletter`
- `no-reply`

---

## 🚀 Usage Commands

### Authentication
```bash
# First-time setup
python gmail_watcher.py --authenticate --vault ..
```

### Check Session
```bash
# Verify authentication
python gmail_watcher.py --check-auth --vault ..
```

### One-Time Scan
```bash
# Scan once and exit
python gmail_watcher.py --vault ..
```

### Continuous Monitoring
```bash
# Run continuously (every 2 minutes)
python gmail_watcher.py --vault .. --continuous --interval 120

# Run continuously (every 1 minute)
python gmail_watcher.py --vault .. --continuous --interval 60
```

### With Orchestrator
```bash
# Start Gmail Watcher
start python gmail_watcher.py --vault .. --continuous --interval 120

# Start Orchestrator (processes emails)
start python orchestrator.py .. --continuous --interval 60
```

---

## 🔄 Complete Workflow Example

### 1. Start Services

```bash
cd AI_Employee_Vault\scripts

# Start Gmail Watcher (Terminal 1)
python gmail_watcher.py --vault .. --continuous --interval 120

# Start Orchestrator (Terminal 2)
python orchestrator.py .. --continuous --interval 60
```

### 2. Email Arrives

Someone sends email to your Gmail:
```
From: client@example.com
Subject: Urgent: Need Invoice
Body: Hi, please send me the invoice for January. Thanks!
```

### 3. Watcher Detects

Within 2 minutes:
```
2026-03-12 21:35:00 - INFO - Found 1 new email(s)
2026-03-12 21:35:00 - INFO - Created: Needs_Action/GMAIL_18f3d2a1b5c6e789.md
```

### 4. Orchestrator Processes

```
2026-03-12 21:36:00 - INFO - Processing: GMAIL_18f3d2a1b5c6e789.md
2026-03-12 21:36:00 - INFO - Created: Plans/PLAN_GMAIL_18f3d2a1b5c6e789.md
```

### 5. Check Obsidian

Open `AI_Employee_Vault` in Obsidian:

**Needs_Action/ folder:**
- `GMAIL_18f3d2a1b5c6e789.md` - New email action

**Plans/ folder:**
- `PLAN_GMAIL_18f3d2a1b5c6e789.md` - Action plan created

**Dashboard.md:**
- Stats updated automatically

---

## 🛠️ Troubleshooting

### Problem: "credentials.json not found"

**Solution:**
```bash
# Check if file exists
cd AI_Employee_Vault\scripts
dir credentials.json

# If missing, download from Google Cloud Console
# https://console.cloud.google.com/apis/credentials
```

### Problem: "Token expired" or "Authentication failed"

**Solution:**
```bash
# Delete old token
del token.json

# Re-authenticate
python gmail_watcher.py --authenticate --vault ..
```

### Problem: "No emails found"

**Possible causes:**
1. No new emails since last run
2. All emails filtered as promotions
3. Gmail API quota exceeded

**Solution:**
```bash
# Check logs
cd ..\Logs
type 2026-03-12.log

# Test with specific query
python gmail_watcher.py --vault .. --query "is:unread"
```

### Problem: "Watcher not detecting emails"

**Solution:**
```bash
# Check if running
tasklist | findstr python

# Restart watcher
python gmail_watcher.py --vault .. --continuous --interval 60
```

---

## 📊 Testing Checklist

Run these tests to verify Gmail Watcher:

```bash
cd AI_Employee_Vault\scripts

# Test 1: Check credentials
dir credentials.json
# Expected: File exists

# Test 2: Authenticate
python gmail_watcher.py --authenticate --vault ..
# Expected: Browser opens, login successful

# Test 3: Check token
dir token.json
# Expected: File created after auth

# Test 4: One-time scan
python gmail_watcher.py --vault ..
# Expected: Scans emails, creates action files

# Test 5: Continuous mode
python gmail_watcher.py --vault .. --continuous --interval 120
# Expected: Runs continuously, checks every 2 min
```

---

## 🔐 Security Notes

- **credentials.json** - Your Gmail API client credentials (NEVER share)
- **token.json** - Your OAuth session token (NEVER share)
- **Both files are .gitignored** - Won't be committed to Git
- **Read-only access** - Watcher only reads emails, doesn't modify
- **Separate credentials** - Use different credentials for Email MCP (sending)

---

## 📈 Integration with Other Components

### With Orchestrator

```bash
# Gmail Watcher creates files
python gmail_watcher.py --vault .. --continuous

# Orchestrator processes them
python orchestrator.py .. --continuous
```

### With Email MCP (Sending)

```bash
# Gmail Watcher (receives)
python gmail_watcher.py --vault .. --continuous

# Email MCP Server (sends)
python email_mcp_server.py --serve --port 8809
```

### With Approval Workflow

```
Email received
    ↓
Watcher creates action file
    ↓
Orchestrator creates plan
    ↓
Draft reply created → Pending_Approval/
    ↓
You approve → move to Approved/
    ↓
Email MCP sends reply
```

---

## 🎯 Quick Start (TL;DR)

```bash
cd D:\Hackathone-0\Personal-AI-Employe-FTEs\AI_Employee_Vault\scripts

# 1. Authenticate (first time only)
python gmail_watcher.py --authenticate --vault ..

# 2. Test it works
python gmail_watcher.py --vault ..

# 3. Run continuously
python gmail_watcher.py --vault .. --continuous --interval 120

# 4. Also run orchestrator
python orchestrator.py .. --continuous --interval 60
```

**Done!** Your AI Employee now monitors Gmail 24/7! 🎉

---

## 📚 Additional Resources

- **Gmail API Docs:** https://developers.google.com/gmail/api
- **OAuth Setup:** https://console.cloud.google.com/apis/credentials
- **Vault Path:** `D:\Hackathone-0\Personal-AI-Employe-FTEs\AI_Employee_Vault`
- **Logs:** `AI_Employee_Vault\Logs\`

---

*Gmail Watcher Guide - Silver Tier*
*AI Employee Hackathon 0*
