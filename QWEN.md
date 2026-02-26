# Personal AI Employee (Digital FTE) - Project Context

## Project Overview

This is a **hackathon project** for building an autonomous "Digital FTE" (Full-Time Equivalent) - an AI employee that manages personal and business affairs 24/7. The architecture is **local-first**, **agent-driven**, and uses **human-in-the-loop** patterns for sensitive actions.

### Core Architecture

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Brain** | Claude Code | Reasoning engine for decision-making |
| **Memory/GUI** | Obsidian (Markdown) | Dashboard, knowledge base, task tracking |
| **Senses** | Python Watchers | Monitor Gmail, WhatsApp, filesystems |
| **Hands** | MCP Servers | External actions (email, browser automation, payments) |

### Key Concepts

- **Watcher Pattern**: Lightweight Python scripts run continuously, monitoring inputs and creating `.md` files in `/Needs_Action` folder
- **Ralph Wiggum Loop**: A Stop hook pattern that keeps Claude iterating until multi-step tasks are complete
- **Human-in-the-Loop**: Sensitive actions require approval via file movement (`/Pending_Approval` → `/Approved`)
- **Monday Morning CEO Briefing**: Autonomous weekly audit generating revenue/bottleneck reports

## Project Structure

```
Personal-AI-Employee-FTEs/
├── Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md  # Main blueprint
├── skills-lock.json          # Skill dependencies tracking
├── .qwen/skills/             # Agent skills (modular capabilities)
│   └── browsing-with-playwright/
│       ├── SKILL.md          # Skill documentation
│       ├── references/
│       │   └── playwright-tools.md  # MCP tool schemas
│       └── scripts/
│           ├── mcp-client.py      # Universal MCP client (HTTP/stdio)
│           ├── verify.py          # Server health check
│           ├── start-server.sh    # Start Playwright MCP
│           └── stop-server.sh     # Stop Playwright MCP
└── .git/
```

## Building and Running

### Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| [Claude Code](https://claude.com/product/claude-code) | Active subscription | Primary reasoning engine |
| [Obsidian](https://obsidian.md/download) | v1.10.6+ | Knowledge base & dashboard |
| [Python](https://www.python.org/downloads/) | 3.13+ | Watcher scripts & orchestration |
| [Node.js](https://nodejs.org) | v24+ LTS | MCP servers |

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

# Emit tool schemas as markdown
python scripts/mcp-client.py emit -u http://localhost:8808
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
└── Briefings/                # CEO briefings (auto-generated)
```

## Development Conventions

### Agent Skills

All AI functionality should be implemented as **[Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)** - modular, reusable capabilities that Claude can invoke.

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

### Approval Request Schema

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

## Hackathon Tiers

| Tier | Time | Deliverables |
|------|------|--------------|
| **Bronze** | 8-12h | Obsidian dashboard, 1 watcher, Claude reading/writing |
| **Silver** | 20-30h | 2+ watchers, MCP server, HITL workflow, scheduling |
| **Gold** | 40+h | Full integration, Odoo accounting, Ralph Wiggum loop, audit logging |
| **Platinum** | 60+h | Cloud deployment, domain specialization, A2A upgrade |

## Key MCP Servers

| Server | Capabilities | Use Case |
|--------|--------------|----------|
| `filesystem` | Read, write, list files | Built-in vault access |
| `email-mcp` | Send, draft, search emails | Gmail integration |
| `browser-mcp` | Navigate, click, fill forms | Payment portals, web automation |
| `calendar-mcp` | Create, update events | Scheduling |
| `@playwright/mcp` | Full browser automation | Web scraping, form submission |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Playwright MCP not responding | Run `bash scripts/stop-server.sh && bash scripts/start-server.sh` |
| Element click fails | Run `browser_snapshot` first to get current refs |
| Watcher not triggering | Check Python script is running, verify folder permissions |
| Claude exits prematurely | Implement Ralph Wiggum Stop hook pattern |
| Double agent work | Use claim-by-move rule with `/In_Progress/<agent>/` |

## Resources

- [Ralph Wiggum Pattern](https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum)
- [Agent Skills Documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [MCP Server Documentation](https://github.com/AlanOgic/mcp-odoo-adv)
- [Oracle Cloud Free VMs](https://www.oracle.com/cloud/free/) (for Platinum tier deployment)
