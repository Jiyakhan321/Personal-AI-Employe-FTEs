---
name: whatsapp-watcher
description: |
  Monitor WhatsApp Web for urgent messages and create action files in Obsidian vault.
  Uses Playwright to automate WhatsApp Web and extract messages containing keywords.
  Use when you need to automatically process WhatsApp messages as tasks.
  
  NOTE: This uses WhatsApp Web automation. Be aware of WhatsApp's terms of service.
---

# WhatsApp Watcher

Monitor WhatsApp Web for urgent messages and create actionable tasks.

## Prerequisites

- Playwright MCP server installed (see `browsing-with-playwright` skill)
- WhatsApp Web account
- Python 3.13+

## Setup

### 1. Install Dependencies

```bash
pip install playwright
playwright install chromium
```

### 2. First-Time WhatsApp Web Login

```bash
# Run once to create session
python scripts/whatsapp_watcher.py --setup-session
```

This will open a browser where you can scan the QR code to log in to WhatsApp Web.

## Usage

### One-Time Scan

```bash
python scripts/whatsapp_watcher.py --vault /path/to/vault
```

### Continuous Monitoring

```bash
# Check every 30 seconds
python scripts/whatsapp_watcher.py --vault /path/to/vault --continuous

# Custom interval (check every 60 seconds)
python scripts/whatsapp_watcher.py --vault /path/to/vault --continuous --interval 60
```

## How It Works

1. **Launches WhatsApp Web** in headless mode with persistent session
2. **Scans chat list** for unread messages
3. **Filters by keywords** (urgent, asap, invoice, payment, help)
4. **Creates action files** in `Needs_Action/` folder

## Configuration

### Priority Keywords

Messages containing these keywords trigger action files:

```python
KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'help', 'deadline', 'emergency']
```

### Filter Settings

Edit `whatsapp_watcher.py` to customize:

```python
# Check interval in seconds
CHECK_INTERVAL = 30

# Session storage path
SESSION_PATH = './whatsapp_session'

# Keywords to watch for
KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'help']
```

## Output Files

Each urgent message creates an action file:

```markdown
---
type: whatsapp
from: +1234567890
chat: Contact Name
received: 2026-02-27T10:30:00
priority: high
status: pending
---

# WhatsApp Message

**From:** Contact Name (+1234567890)

**Message:**
Hey, can you send me the invoice ASAP?

---

## Suggested Actions

- [ ] Read message
- [ ] Draft reply
- [ ] Take required action
- [ ] Move to /Done when complete

---
*Created by WhatsApp Watcher v0.1*
```

## Session Management

### Session Location

Sessions are stored in:
- **Windows:** `%APPDATA%/whatsapp_session/`
- **Mac/Linux:** `~/.whatsapp_session/`

### Clear Session

```bash
python scripts/whatsapp_watcher.py --clear-session
```

### Re-authenticate

```bash
python scripts/whatsapp_watcher.py --setup-session
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| QR code shows every time | Session not saving - check session path permissions |
| No messages found | Check if keywords match your messages |
| Browser won't close | Run `--cleanup` flag or use stop script |
| WhatsApp Web stuck | Clear session and re-authenticate |

## Security Notes

- Session data contains authentication tokens - keep secure
- Don't commit session files to git
- Log out from WhatsApp Web when not in use
- Monitor for unusual account activity

## Integration with Orchestrator

After WhatsApp Watcher creates action files:

```bash
python scripts/orchestrator.py --vault /path/to/vault
```

Then process with Qwen Code:

```bash
qwen "Review WhatsApp messages in Needs_Action/ and create response plans"
```

## Example Output

```
2026-02-27 10:30:00 - INFO - Starting WhatsApp Watcher
2026-02-27 10:30:05 - INFO - Found 2 urgent messages
2026-02-27 10:30:06 - INFO - Created action file: WHATSAPP_contact_name_20260227_103006.md
2026-02-27 10:30:06 - INFO - Created action file: WHATSAPP_contact_name_20260227_103006_2.md
```
