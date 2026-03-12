---
name: email-mcp-server
description: |
  Send emails via Gmail API using Model Context Protocol (MCP).
  Provides tools for sending, drafting, and searching emails.
  Integrates with AI Employee for automated email responses.
---

# Email MCP Server

Send emails programmatically via Gmail API using MCP protocol.

## Features

- **send_email**: Send emails with attachments
- **draft_email**: Create drafts for review
- **search_emails**: Find emails by query
- **mark_read**: Mark emails as read

## Setup

### 1. Enable Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/library/gmail.googleapis.com)
2. Enable Gmail API
3. Create OAuth 2.0 credentials
4. Download `credentials.json` to `scripts/` folder

### 2. Install Dependencies

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 3. Authenticate

```bash
cd scripts
python email_mcp_server.py --authenticate
```

## Usage

### Start MCP Server

```bash
# Start the server
python scripts/email_mcp_server.py --serve

# Or with custom port
python scripts/email_mcp_server.py --serve --port 8809
```

### Call Tools via MCP Client

```bash
# Send email
python scripts/mcp-client.py call -u http://localhost:8809 -t send_email \
  -p '{"to": "recipient@example.com", "subject": "Hello", "body": "Test message"}'

# Draft email (for approval)
python scripts/mcp-client.py call -u http://localhost:8809 -t draft_email \
  -p '{"to": "recipient@example.com", "subject": "Invoice", "body": "Please find attached..."}'

# Search emails
python scripts/mcp-client.py call -u http://localhost:8809 -t search_emails \
  -p '{"query": "is:unread", "max_results": 5}'

# Mark as read
python scripts/mcp-client.py call -u http://localhost:8809 -t mark_read \
  -p '{"message_id": "18a3b2c4d5e6f7g8"}'
```

### List Available Tools

```bash
python scripts/mcp-client.py list -u http://localhost:8809
```

## Tool Reference

### `send_email`

Send an email via Gmail.

**Parameters:**
- `to` (string, required): Recipient email address
- `subject` (string, required): Email subject
- `body` (string, required): Email body (plain text)
- `cc` (string, optional): CC recipients
- `bcc` (string, optional): BCC recipients
- `attachment` (string, optional): Path to attachment file

### `draft_email`

Create a draft email for review.

**Parameters:**
- `to` (string, required): Recipient email address
- `subject` (string, required): Email subject
- `body` (string, required): Email body
- `cc` (string, optional): CC recipients
- `attachment` (string, optional): Path to attachment

### `search_emails`

Search Gmail for messages.

**Parameters:**
- `query` (string, required): Gmail search query
- `max_results` (number, optional): Maximum results (default: 10)

### `mark_read`

Mark an email as read.

**Parameters:**
- `message_id` (string, required): Gmail message ID

## Integration with AI Employee

### Human-in-the-Loop Pattern

For sensitive actions, use draft + approval workflow:

1. **AI creates draft:**
   ```bash
   python scripts/mcp-client.py call -u http://localhost:8809 \
     -t draft_email -p '{"to": "client@example.com", ...}'
   ```

2. **AI creates approval request:**
   ```markdown
   ---
   type: approval_request
   action: send_email
   draft_id: 18a3b2c4d5e6f7g8
   ---
   
   Ready to send. Move to /Approved to proceed.
   ```

3. **Human approves:** Move file to `/Approved/`

4. **Orchestrator sends:**
   ```bash
   python scripts/mcp-client.py call -u http://localhost:8809 \
     -t send_draft -p '{"draft_id": "18a3b2c4d5e6f7g8"}'
   ```

## Configuration

### Environment Variables

```bash
# Gmail API credentials
GMAIL_CREDENTIALS_PATH=./scripts/credentials.json
GMAIL_TOKEN_PATH=./scripts/token.json

# Server settings
MCP_PORT=8809
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Authentication failed | Re-run `--authenticate` |
| Token expired | Delete token.json and re-authenticate |
| API quota exceeded | Wait 24 hours or request quota increase |
| Server won't start | Check if port 8809 is available |

## Security Notes

- Never commit `credentials.json` or `token.json` to git
- Rotate credentials monthly
- Use app-specific passwords if 2FA enabled
- Review sent emails regularly

## Example: Automated Reply Workflow

```python
# 1. Gmail Watcher detects email
# 2. Orchestrator creates plan
# 3. Qwen Code drafts reply
# 4. Email MCP sends (or drafts for approval)

# Draft for approval
python scripts/mcp-client.py call -u http://localhost:8809 \
  -t draft_email \
  -p '{"to": "client@example.com", "subject": "Re: Invoice Request", "body": "Hi, Please find attached..."}'
```
