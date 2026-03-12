---
name: gmail-watcher
description: |
  Monitor Gmail for new important emails and create action files in Obsidian vault.
  Uses Gmail API to fetch unread/important messages and converts them to task files.
  Use when you need to automatically process emails as tasks for your AI Employee.
---

# Gmail Watcher

Monitor Gmail inbox and create actionable tasks from new emails.

## Setup

### 1. Enable Gmail API

```bash
# Go to Google Cloud Console
# https://console.cloud.google.com/apis/library/gmail.googleapis.com

# Enable Gmail API
# Create credentials (OAuth 2.0)
# Download credentials.json to scripts/ folder
```

### 2. Install Dependencies

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 3. First-Time Authentication

```bash
cd scripts
python gmail_watcher.py --authenticate
```

This will open a browser window for OAuth authentication.

## Usage

### One-Time Scan

```bash
python scripts/gmail_watcher.py --vault /path/to/vault
```

### Continuous Monitoring

```bash
# Check every 120 seconds
python scripts/gmail_watcher.py --vault /path/to/vault --continuous

# Custom interval (check every 60 seconds)
python scripts/gmail_watcher.py --vault /path/to/vault --continuous --interval 60
```

## How It Works

1. **Connects to Gmail API** using OAuth 2.0 credentials
2. **Fetches unread/important messages** from your inbox
3. **Creates action files** in `Needs_Action/` folder with format:
   ```markdown
   ---
   type: email
   from: sender@example.com
   subject: Email Subject
   received: 2026-02-27T10:30:00
   priority: high
   status: pending
   ---

   ## Email Content
   Email body text...

   ## Suggested Actions
   - [ ] Reply to sender
   - [ ] Forward to relevant party
   - [ ] Archive after processing
   ```
4. **Marks emails as processed** to avoid duplicates

## Configuration

### Priority Keywords

Emails containing these keywords are marked as high priority:

```python
PRIORITY_KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'deadline', 'important']
```

### Filter Settings

Edit `gmail_watcher.py` to customize:

```python
# Only fetch unread messages
UNREAD_ONLY = True

# Only fetch important messages
IMPORTANT_ONLY = True

# Check interval in seconds
CHECK_INTERVAL = 120
```

## Output Files

Each email creates two files in `Needs_Action/`:

1. **Email data file**: `EMAIL_{message_id}.eml` (raw email)
2. **Action metadata**: `EMAIL_{message_id}.md` (task file for AI)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Authentication failed | Re-run `--authenticate` and check credentials.json |
| No emails found | Check if UNREAD_ONLY is filtering all emails |
| API quota exceeded | Wait 24 hours or request quota increase |
| Token expired | Delete token.json and re-authenticate |

## Security Notes

- `credentials.json` contains your OAuth client secrets - never commit to git
- `token.json` contains refresh token - keep secure
- Add both files to `.gitignore`
- Rotate credentials monthly

## Example Output

```
2026-02-27 10:30:00 - INFO - Starting Gmail Watcher
2026-02-27 10:30:01 - INFO - Found 3 new messages
2026-02-27 10:30:02 - INFO - Created action file: EMAIL_18a3b2c4d5e6f7g8.md
2026-02-27 10:30:02 - INFO - Created action file: EMAIL_18a3b2c4d5e6f7g9.md
2026-02-27 10:30:02 - INFO - Created action file: EMAIL_18a3b2c4d5e6f7h0.md
```

## Integration with Orchestrator

After Gmail Watcher creates action files, run:

```bash
python scripts/orchestrator.py --vault /path/to/vault
```

This will process the emails and create plans for handling them.
