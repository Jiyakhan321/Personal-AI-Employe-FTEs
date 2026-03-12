# Personal AI Employee (Digital FTE) - Project Context

## Project Overview

This is a **hackathon project** for building an autonomous "Digital FTE" (Full-Time Equivalent) - an AI employee that manages personal and business affairs 24/7. The architecture is **local-first**, **agent-driven**, and uses **human-in-the-loop** patterns for sensitive actions.

### Core Architecture

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Brain** | Qwen Code | Reasoning engine for decision-making |
| **Memory/GUI** | Obsidian (Markdown) | Dashboard, knowledge base, task tracking |
| **Senses** | Python Watchers | Monitor Gmail, WhatsApp, filesystems |
| **Hands** | MCP Servers | External actions (email, browser automation, payments) |

### Key Concepts

- **Watcher Pattern**: Lightweight Python scripts run continuously, monitoring inputs and creating `.md` files in `/Needs_Action` folder
- **Ralph Wiggum Loop**: A Stop hook pattern that keeps AI iterating until multi-step tasks are complete
- **Human-in-the-Loop (HITL)**: Sensitive actions require approval via file movement (`/Pending_Approval` → `/Approved`)
- **Monday Morning CEO Briefing**: Autonomous weekly audit generating revenue/bottleneck reports

---

## Project Structure

```
Personal-AI-Employee-FTEs/
├── Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md  # Main blueprint
├── skills-lock.json          # Skill dependencies tracking
├── .qwen/skills/             # Agent skills (modular capabilities)
│   ├── browsing-with-playwright/    # Browser automation (Bronze)
│   ├── gmail-watcher/               # Gmail monitoring (Silver)
│   ├── whatsapp-watcher/            # WhatsApp monitoring (Silver)
│   ├── email-mcp-server/            # Email sending (Silver)
│   ├── approval-workflow/           # HITL approvals (Silver)
│   ├── linkedin-poster/             # LinkedIn posting (Silver)
│   ├── plan-creator/                # Plan.md generation (Silver)
│   └── scheduler/                   # Task scheduling (Silver)
├── AI_Employee_Vault/        # Obsidian vault (Bronze tier)
│   ├── Dashboard.md
│   ├── Company_Handbook.md
│   ├── Business_Goals.md
│   ├── scripts/
│   │   ├── filesystem_watcher.py
│   │   ├── orchestrator.py
│   │   └── test_bronze_tier.py
│   └── ...
└── .git/
```

---

## Silver Tier Skills Summary

| Skill | Description | Command |
|-------|-------------|---------|
| **gmail-watcher** | Monitor Gmail for important emails | `python gmail_watcher.py --vault PATH --continuous` |
| **whatsapp-watcher** | Monitor WhatsApp for urgent messages | `python whatsapp_watcher.py --vault PATH --continuous` |
| **email-mcp-server** | Send emails via Gmail API | `python email_mcp_server.py --serve --port 8809` |
| **approval-workflow** | Human-in-the-loop approval management | `python approval_manager.py --vault PATH --continuous` |
| **linkedin-poster** | Auto-post to LinkedIn (with approval) | `python linkedin_poster.py --vault PATH --create-draft "content"` |
| **plan-creator** | Generate structured Plan.md files | `python plan_creator.py --vault PATH --create "objective"` |
| **scheduler** | Schedule recurring tasks (cron/Task Scheduler) | `python scheduler.py --vault PATH --install` |

---

## Building and Running

### Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| [Qwen Code](https://github.com/anthropics/claude-code) | Active subscription | Primary reasoning engine |
| [Obsidian](https://obsidian.md/download) | v1.10.6+ | Knowledge base & dashboard |
| [Python](https://www.python.org/downloads/) | 3.13+ | Watcher scripts & orchestration |
| [Node.js](https://nodejs.org) | v24+ LTS | MCP servers |

### Bronze Tier Commands

```bash
# Navigate to vault
cd AI_Employee_Vault

# Run file watcher (one-time)
python scripts\filesystem_watcher.py .

# Run orchestrator (one-time)
python scripts\orchestrator.py .

# Continuous mode
python scripts\filesystem_watcher.py . --continuous --interval 30
python scripts\orchestrator.py . --continuous --interval 60

# Test installation
python scripts\test_bronze_tier.py .
```

### Silver Tier Commands

```bash
# Gmail Watcher (requires Gmail API setup)
python .qwen/skills/gmail-watcher/scripts/gmail_watcher.py --vault AI_Employee_Vault --continuous

# WhatsApp Watcher (requires Playwright)
python .qwen/skills/whatsapp-watcher/scripts/whatsapp_watcher.py --vault AI_Employee_Vault --continuous

# Email MCP Server (requires Gmail API setup)
python .qwen/skills/email-mcp-server/scripts/email_mcp_server.py --serve --port 8809

# Approval Workflow Manager
python .qwen/skills/approval-workflow/scripts/approval_manager.py --vault AI_Employee_Vault --continuous

# LinkedIn Poster (requires Playwright)
python .qwen/skills/linkedin-poster/scripts/linkedin_poster.py --vault AI_Employee_Vault --create-draft "Post content"

# Plan Creator
python .qwen/skills/plan-creator/scripts/plan_creator.py --vault AI_Employee_Vault --create "Task objective"

# Scheduler (install scheduled tasks)
python .qwen/skills/scheduler/scripts/scheduler.py --vault AI_Employee_Vault --install
```

### MCP Server Commands (Playwright)

```bash
# Start browser automation server
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh [port]

# Stop server (graceful browser close)
bash .qwen/skills/browsing-with-playwright/scripts/stop-server.sh [port]

# Verify server is running
python .qwen/skills/browsing-with-playwright/scripts/verify.py
```

### MCP Client Usage

```bash
# List available tools
python scripts/mcp-client.py list -u http://localhost:8808

# Call a tool
python scripts/mcp-client.py call -u http://localhost:8808 -t browser_navigate \
  -p '{"url": "https://example.com"}'

# Email MCP (Silver tier)
python .qwen/skills/email-mcp-server/scripts/mcp-client.py list -u http://localhost:8809
```

### Obsidian Vault Structure (Recommended)

```
AI_Employee_Vault/
├── Dashboard.md              # Real-time summary
├── Company_Handbook.md       # Rules of engagement
├── Business_Goals.md         # Q1/Q2 objectives
├── Inbox/                    # Raw incoming items
├── Needs_Action/             # Pending tasks
├── In_Progress/<agent>/      # Claimed by specific agent
├── Pending_Approval/         # Awaiting human approval
├── Approved/                 # Approved actions (triggers execution)
├── Done/                     # Completed tasks
├── Accounting/               # Bank transactions, invoices
├── Briefings/                # CEO briefings (auto-generated)
└── Plans/                    # Action plans (Silver tier)
```

---

## Development Conventions

### Agent Skills

All AI functionality should be implemented as **[Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)** - modular, reusable capabilities that Qwen Code can invoke.

### Watcher Pattern Template

```python
from pathlib import Path
from abc import ABC, abstractmethod
import time

class BaseWatcher(ABC):
    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval

    @abstractmethod
    def check_for_updates(self) -> list:
        '''Return list of new items to process'''
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        '''Create .md file in Needs_Action folder'''
        pass

    def run(self):
        while True:
            items = self.check_for_updates()
            for item in items:
                self.create_action_file(item)
            time.sleep(self.check_interval)
```

### Action File Schema

```markdown
---
type: email|whatsapp|file_drop|payment
from: <sender>
subject: <subject>
received: <ISO timestamp>
priority: high|medium|low
status: pending
---

## Content
<content here>

## Suggested Actions
- [ ] Action 1
- [ ] Action 2
```

### Approval Request Schema (Silver Tier)

```markdown
---
type: approval_request
action: payment|send_email|post_social
amount: 500.00
recipient: <name>
created: <ISO timestamp>
expires: <ISO timestamp + 24h>
status: pending
---

## Details
<details here>

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
```

### Plan.md Schema (Silver Tier)

```markdown
---
created: 2026-02-27T10:30:00Z
type: plan
status: pending
objective: Process client invoice request
priority: high
---

# Action Plan

## Objective
Process client invoice request and send response

## Steps
- [ ] Review email content
- [ ] Check accounting records
- [ ] Generate invoice PDF
- [ ] Draft email response
- [ ] Send email
```

---

## Hackathon Tiers

| Tier | Time | Deliverables |
|------|------|--------------|
| **Bronze** | 8-12h | Obsidian dashboard, 1 watcher (filesystem), Qwen Code reading/writing |
| **Silver** | 20-30h | 2+ watchers (Gmail, WhatsApp), MCP server (email), HITL workflow, scheduling |
| **Gold** | 40+h | Full integration, Odoo accounting, Ralph Wiggum loop, audit logging |
| **Platinum** | 60+h | Cloud deployment, domain specialization, A2A upgrade |

---

## Key MCP Servers

| Server | Capabilities | Use Case |
|--------|--------------|----------|
| `filesystem` | Read, write, list files | Built-in vault access |
| `email-mcp` | Send, draft, search emails | Gmail integration (Silver) |
| `browser-mcp` | Navigate, click, fill forms | Payment portals, web automation |
| `calendar-mcp` | Create, update events | Scheduling |
| `@playwright/mcp` | Full browser automation | WhatsApp Web, LinkedIn (Silver) |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Playwright MCP not responding | Run `bash scripts/stop-server.sh && bash scripts/start-server.sh` |
| Element click fails | Run `browser_snapshot` first to get current refs |
| Watcher not triggering | Check Python script is running, verify folder permissions |
| AI exits prematurely | Implement Ralph Wiggum Stop hook pattern |
| Double agent work | Use claim-by-move rule with `/In_Progress/<agent>/` |
| Gmail API auth failed | Re-run `--authenticate` flag, check credentials.json |
| WhatsApp session expired | Run `--setup-session` to re-authenticate |

---

## Resources

- [Ralph Wiggum Pattern](https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum)
- [Agent Skills Documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [MCP Server Documentation](https://github.com/AlanOgic/mcp-odoo-adv)
- [Oracle Cloud Free VMs](https://www.oracle.com/cloud/free/) (for Platinum tier deployment)
- [Gmail API Setup](https://developers.google.com/gmail/api/quickstart)
- [Playwright Documentation](https://playwright.dev/python/docs/intro)

---

*Generated for Personal AI Employee Hackathon 0 - Silver Tier*
