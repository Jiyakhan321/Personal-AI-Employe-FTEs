# 🚀 Automatic LinkedIn Posting - Quick Start

## ✅ Complete Automatic Setup

Your AI Employee now has **fully automatic LinkedIn posting**!

---

## 📋 Step 1: Setup LinkedIn Session (First Time Only)

```bash
cd D:\Hackathone-0\Personal-AI-Employe-FTEs\AI_Employee_Vault\scripts
python linkedin_poster.py --setup-session
```

**What happens:**
- Browser opens
- You log in to LinkedIn
- Session is saved
- Browser closes

---

## 🎯 Step 2: Start All Services (One Command)

```bash
cd D:\Hackathone-0\Personal-AI-Employe-FTEs\AI_Employee_Vault\scripts
start-all-services.bat
```

**This starts 4 windows:**
1. **Gmail Watcher** - Monitors Gmail every 2 min
2. **LinkedIn Watcher** - Monitors LinkedIn every 5 min
3. **Orchestrator** - Creates plans every 60 sec
4. **LinkedIn Auto-Poster** - Posts approved content every 60 sec

---

## 📝 Step 3: Create Post (Automatic Posting)

### Option A: AI-Generated Post

```bash
cd D:\Hackathone-0\Personal-AI-Employe-FTEs\AI_Employee_Vault\scripts
python linkedin_poster.py --vault .. --create-draft "🚀 Excited to announce our AI Employee!

Autonomous digital worker that:
✅ Monitors Gmail 24/7
✅ Tracks LinkedIn messages
✅ Creates action plans automatically
✅ Auto-posts to LinkedIn

Built with Qwen Code + Obsidian + Playwright

#AI #Automation #Productivity #FutureOfWork"
```

### Option B: Move to Approved (Triggers Auto-Post)

```bash
cd D:\Hackathone-0\Personal-AI-Employe-FTEs\AI_Employee_Vault
move Pending_Approval\LINKEDIN_POST_*.md Approved\
```

**That's it!** The Auto-Poster will:
1. Detect the file in Approved/ (within 60 seconds)
2. Extract the content
3. Post to LinkedIn automatically
4. Move file to Done/ when complete

---

## 🔄 Complete Automatic Workflow

```
1. Create draft
   ↓
2. Move to Approved/
   ↓
3. Auto-Poster detects (within 60 sec)
   ↓
4. Posts to LinkedIn automatically
   ↓
5. Moves to Done/
   ↓
✅ Posted!
```

---

## 📊 Monitor Posting

### Check Logs
```bash
cd D:\Hackathone-0\Personal-AI-Employe-FTEs\AI_Employee_Vault\Logs
type linkedin_poster_*.log
```

### Check Posted Files
```bash
cd D:\Hackathone-0\Personal-AI-Employe-FTEs\AI_Employee_Vault\Done
dir LINKEDIN_POST_*.md
```

---

## 🛑 Stop Auto-Posting

**Close the "LinkedIn Auto-Poster" window** or press `Ctrl+C` in that window.

---

## ⚡ Quick Commands

| Command | Purpose |
|---------|---------|
| `start-all-services.bat` | Start everything |
| `--create-draft "text"` | Create post draft |
| `move ... Approved\` | Approve for auto-post |
| `type Logs\*.log` | Check logs |

---

## 🎯 Example: Complete Auto-Post

```bash
# 1. Navigate
cd D:\Hackathone-0\Personal-AI-Employe-FTEs\AI_Employee_Vault\scripts

# 2. Create draft
python linkedin_poster.py --vault .. --create-draft "📈 Weekly Update

Completed Silver Tier AI Employee!

Features:
✅ Gmail monitoring
✅ LinkedIn monitoring
✅ Auto-posting
✅ Plan creation

#AI #Automation"

# 3. Approve (triggers auto-post)
cd ..
move Pending_Approval\LINKEDIN_POST_*.md Approved\

# 4. Wait 60 seconds
# Auto-Poster will post automatically!

# 5. Check result
cd Logs
type linkedin_poster_*.log
```

---

## ✅ What's Automatic Now:

| Task | Status |
|------|--------|
| Gmail monitoring | ✅ Automatic |
| LinkedIn monitoring | ✅ Automatic |
| Plan creation | ✅ Automatic |
| **LinkedIn posting** | ✅ **AUTOMATIC** |
| Approval workflow | ✅ Manual (you decide) |

---

## 🎉 Your AI Employee is Fully Automatic!

Just create drafts and move them to Approved/ - the rest is handled automatically!

---

*AI Employee v0.3 - Silver Tier (Auto-Post)*  
*Powered by Qwen Code*
