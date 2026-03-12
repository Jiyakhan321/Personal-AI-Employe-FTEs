#!/usr/bin/env python3
"""
Gmail Watcher for AI Employee (Silver Tier)

Monitors Gmail for new important emails and creates action files in Obsidian vault.

Usage:
    # First-time authentication
    python gmail_watcher.py --authenticate

    # One-time scan
    python gmail_watcher.py --vault /path/to/vault

    # Continuous monitoring
    python gmail_watcher.py --vault /path/to/vault --continuous --interval 120
"""

import argparse
import base64
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from email import message_from_bytes

# Google API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    print("Gmail API libraries not installed.")
    print("Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")


# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Priority keywords
PRIORITY_KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'deadline', 'important', 'help']


class GmailWatcher:
    """Monitor Gmail and create action files."""
    
    def __init__(self, vault_path: str, credentials_path: str = None, check_interval: int = 120):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.credentials_path = Path(credentials_path) if credentials_path else None
        self.token_path = self.vault_path / 'scripts' / 'token.json'
        self.check_interval = check_interval
        self.processed_ids = set()
        self.service = None
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def authenticate(self):
        """Perform OAuth authentication."""
        if not GMAIL_AVAILABLE:
            print("Gmail API libraries not installed. Please install dependencies.")
            return False
            
        creds_path = self.credentials_path or (self.vault_path / 'scripts' / 'credentials.json')
        
        if not creds_path.exists():
            print(f"Error: credentials.json not found at {creds_path}")
            print("Please download credentials.json from Google Cloud Console and place it in scripts/")
            return False
            
        flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
        creds = flow.run_local_server(port=0)
        
        # Save credentials
        self.token_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.token_path, 'w') as f:
            f.write(creds.to_json())
            
        print("Authentication successful! Token saved.")
        return True
        
    def get_credentials(self):
        """Get or refresh OAuth credentials."""
        creds = None
        creds_path = self.credentials_path or (self.vault_path / 'scripts' / 'credentials.json')
        
        # Load token if exists
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)
            
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not creds_path.exists():
                    self.logger.error("credentials.json not found. Run --authenticate first.")
                    return None
                flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
                creds = flow.run_local_server(port=0)
                
            # Save refreshed credentials
            with open(self.token_path, 'w') as f:
                f.write(creds.to_json())
                
        return creds
        
    def connect(self):
        """Connect to Gmail API."""
        if not GMAIL_AVAILABLE:
            return False
            
        creds = self.get_credentials()
        if not creds:
            return False
            
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            self.logger.info("Connected to Gmail API")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect: {e}")
            return False
            
    def check_for_updates(self) -> list:
        """Fetch new unread/important messages."""
        if not self.service:
            return []
            
        try:
            # Fetch unread messages
            query = 'is:unread'
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=10
            ).execute()
            
            messages = results.get('messages', [])
            new_messages = []
            
            for msg in messages:
                if msg['id'] not in self.processed_ids:
                    new_messages.append(msg)
                    self.processed_ids.add(msg['id'])
                    
            self.logger.info(f"Found {len(new_messages)} new messages")
            return new_messages
            
        except HttpError as e:
            self.logger.error(f"Gmail API error: {e}")
            return []
            
    def get_message_details(self, message_id: str) -> dict:
        """Get full message details."""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = message['payload']['headers']
            header_dict = {h['name']: h['value'] for h in headers}
            
            # Get body
            body = ''
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                        break
            elif 'body' in message['payload'] and 'data' in message['payload']['body']:
                body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8', errors='ignore')
                
            return {
                'id': message_id,
                'from': header_dict.get('From', 'Unknown'),
                'to': header_dict.get('To', ''),
                'subject': header_dict.get('Subject', 'No Subject'),
                'date': header_dict.get('Date', ''),
                'body': body[:2000]  # Limit body length
            }
            
        except Exception as e:
            self.logger.error(f"Error getting message details: {e}")
            return None
            
    def determine_priority(self, message: dict) -> str:
        """Determine message priority based on content."""
        text = f"{message['subject']} {message['body']}".lower()
        
        for keyword in PRIORITY_KEYWORDS:
            if keyword in text:
                return 'high'
                
        return 'medium'
        
    def create_action_file(self, message: dict) -> Path:
        """Create action file in Needs_Action folder."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        priority = self.determine_priority(message)
        
        # Sanitize filename
        safe_subject = "".join(c if c.isalnum() else '_' for c in message['subject'][:30])
        filename = f"EMAIL_{safe_subject}_{timestamp}"
        
        content = f"""---
type: email
from: {message['from']}
to: {message['to']}
subject: {message['subject']}
received: {datetime.now().isoformat()}
priority: {priority}
status: pending
---

# Email for Processing

**From:** {message['from']}

**Subject:** {message['subject']}

**Date:** {message['date']}

---

## Email Content

{message['body']}

---

## Suggested Actions

- [ ] Read and understand email
- [ ] Draft reply if needed
- [ ] Take any required action
- [ ] Move to /Done when complete

---
*Created by Gmail Watcher v0.1 (Silver Tier)*
"""
        
        filepath = self.needs_action / f"{filename}.md"
        filepath.write_text(content, encoding='utf-8')
        
        self.logger.info(f"Created action file: {filepath.name}")
        return filepath
        
    def run_continuous(self):
        """Run watcher continuously."""
        import time
        
        self.logger.info(f"Starting Gmail Watcher (interval: {self.check_interval}s)")
        
        while True:
            try:
                if not self.service:
                    self.connect()
                    
                if self.service:
                    messages = self.check_for_updates()
                    for msg in messages:
                        details = self.get_message_details(msg['id'])
                        if details:
                            self.create_action_file(details)
                            
            except Exception as e:
                self.logger.error(f"Error in watch loop: {e}")
                
            time.sleep(self.check_interval)


def main():
    if not GMAIL_AVAILABLE:
        print("Gmail API libraries not installed.")
        print("Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        sys.exit(1)
        
    parser = argparse.ArgumentParser(
        description='Gmail Watcher for AI Employee',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # First-time authentication
    python gmail_watcher.py --authenticate
    
    # One-time scan
    python gmail_watcher.py --vault /path/to/vault
    
    # Continuous monitoring (every 2 minutes)
    python gmail_watcher.py --vault /path/to/vault --continuous --interval 120
        """
    )
    
    parser.add_argument('--vault', '-v', help='Path to Obsidian vault')
    parser.add_argument('--authenticate', '-a', action='store_true', help='Perform OAuth authentication')
    parser.add_argument('--continuous', '-c', action='store_true', help='Run continuously')
    parser.add_argument('--interval', '-i', type=int, default=120, help='Check interval in seconds')
    parser.add_argument('--credentials', help='Path to credentials.json')
    
    args = parser.parse_args()
    
    # Handle authentication
    if args.authenticate:
        watcher = GmailWatcher(args.vault or '.', args.credentials)
        if watcher.authenticate():
            print("Authentication successful! You can now run the watcher.")
        else:
            print("Authentication failed.")
            sys.exit(1)
        return
        
    # Require vault for normal operation
    if not args.vault:
        # Try to auto-detect
        possible_vaults = list(Path('.').glob('*/Dashboard.md'))
        if possible_vaults:
            args.vault = str(possible_vaults[0].parent)
            print(f"Auto-detected vault: {args.vault}")
        else:
            parser.error("--vault is required")
    
    # Create watcher
    watcher = GmailWatcher(args.vault, args.credentials, args.interval)
    
    if args.continuous:
        watcher.run_continuous()
    else:
        # One-time scan
        print("Running one-time scan...")
        if watcher.connect():
            messages = watcher.check_for_updates()
            for msg in messages:
                details = watcher.get_message_details(msg['id'])
                if details:
                    watcher.create_action_file(details)
                    
            if messages:
                print(f"Processed {len(messages)} message(s)")
            else:
                print("No new messages found")
        else:
            print("Failed to connect to Gmail API. Run --authenticate first.")
            sys.exit(1)


if __name__ == "__main__":
    main()
