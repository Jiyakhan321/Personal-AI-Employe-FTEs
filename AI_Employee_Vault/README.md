# AI Employee Vault - README

## Quick Start

This is your **Obsidian Vault** for the AI Employee (Bronze Tier).

### Folder Structure

```
AI_Employee_Vault/
├── Dashboard.md           # Main dashboard - open this in Obsidian
├── Company_Handbook.md    # Rules and guidelines for AI
├── Business_Goals.md      # Your objectives and metrics
├── Inbox/                 # Drop files here for processing
├── Needs_Action/          # Tasks awaiting processing
├── Plans/                 # AI-generated action plans
├── Pending_Approval/      # Awaiting your decision
├── Approved/              # Approved actions (triggers execution)
├── Rejected/              # Rejected actions
├── Done/                  # Completed tasks
├── Logs/                  # System logs
├── Accounting/            # Financial records
├── Invoices/              # Generated invoices
├── Briefings/             # CEO briefings
└── scripts/               # Python scripts
    ├── filesystem_watcher.py
    └── orchestrator.py
```

## Setup Instructions

### 1. Open in Obsidian

1. Install [Obsidian](https://obsidian.md/download)
2. Click "Open folder as vault"
3. Select this `AI_Employee_Vault` folder

### 2. Install Python Dependencies

```bash
pip install watchdog
```

### 3. Test the System

#### Option A: Manual File Drop Test

1. Copy `scripts/sample_test_drop.txt` to `Inbox/` folder
2. Run the filesystem watcher:
   ```bash
   python scripts/filesystem_watcher.py . --continuous
   ```
3. Check `Needs_Action/` for the processed file

#### Option B: Run Orchestrator

```bash
# One-time cycle
python scripts/orchestrator.py .

# Continuous mode
python scripts/orchestrator.py . --continuous --interval 30
```

### 4. Verify Claude Code Integration

```bash
# Check if Claude Code is installed
claude --version

# If not installed, follow setup instructions in main README
```

## Daily Workflow

### Morning Check
1. Open `Dashboard.md` in Obsidian
2. Review pending tasks
3. Check `Pending_Approval/` for decisions needed

### During the Day
- Drop files into `Inbox/` for automatic processing
- Move files from `Pending_Approval/` to `Approved/` when ready

### Evening Review
1. Check `Done/` folder for completed tasks
2. Review `Logs/` for any errors
3. Update `Business_Goals.md` if needed

## Scripts Reference

### File System Watcher

Monitors a folder for new files and creates action items.

```bash
# One-time scan
python scripts/filesystem_watcher.py /path/to/vault

# Continuous monitoring
python scripts/filesystem_watcher.py /path/to/vault --continuous

# Custom drop folder
python scripts/filesystem_watcher.py /path/to/vault --drop /path/to/drop --continuous
```

### Orchestrator

Main processing engine that triggers Claude Code.

```bash
# One-time cycle
python scripts/orchestrator.py /path/to/vault

# Continuous mode (every 60 seconds)
python scripts/orchestrator.py /path/to/vault --continuous --interval 60
```

## Troubleshooting

### Watcher not detecting files
- Ensure the drop folder path is correct
- Check file permissions
- Try running with `--verbose` flag

### Orchestrator not processing
- Check logs in `Logs/` folder
- Verify Claude Code is installed: `claude --version`
- Ensure vault path is correct

### Dashboard not updating
- Check that `Dashboard.md` exists
- Verify write permissions
- Check logs for errors

## Next Steps (Silver Tier)

After mastering Bronze tier, consider adding:
- Gmail Watcher for email monitoring
- MCP server for sending emails
- Human-in-the-loop approval workflow
- Scheduled tasks via cron/Task Scheduler

---

*AI Employee v0.1 - Bronze Tier*
