#!/usr/bin/env python3
"""
Gmail Watcher for AI Employee (Silver Tier)

Monitors Gmail for new important emails and creates action files in Obsidian vault.
Uses Gmail API with OAuth 2.0 authentication.

Usage:
    # First-time authentication (required)
    python gmail_watcher.py --authenticate

    # One-time scan
    python gmail_watcher.py --vault /path/to/vault

    # Continuous monitoring (every 2 minutes)
    python gmail_watcher.py --vault /path/to/vault --continuous --interval 120
"""

import argparse
import base64
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from email import message_from_bytes

# Google API imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Gmail API scopes - read only for watcher
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send'
]

# Priority keywords - emails containing these are marked as high priority
PRIORITY_KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'deadline', 'important', 'help', 'emergency']

# Keywords to filter out (promotions, social, etc.)
FILTER_KEYWORDS = ['unsubscribe', 'promotion', 'sale', 'newsletter', 'no-reply']


class GmailWatcher:
    """Monitor Gmail and create action files in Obsidian vault."""
    
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
        if self.token_path.parent:
            self.token_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def authenticate(self):
        """Perform OAuth authentication."""
        creds_path = self.credentials_path or (self.vault_path / 'scripts' / 'credentials.json')
        
        if not creds_path.exists():
            print(f"Error: credentials.json not found at {creds_path}")
            print("Please ensure credentials.json is in the scripts folder.")
            return False
            
        print("Starting Gmail OAuth authentication...")
        print("Opening browser for authentication...")
        
        try:
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0, open_browser=True)
            
            # Save credentials
            self.token_path.write_text(creds.to_json())
            
            print("\n[OK] Authentication successful!")
            print(f"Token saved to: {self.token_path}")
            print("\nYou can now run the watcher with: python gmail_watcher.py --vault PATH")
            return True
            
        except Exception as e:
            print(f"\n[X] Authentication failed: {e}")
            return False
        
    def get_credentials(self):
        """Get or refresh OAuth credentials."""
        creds = None
        creds_path = self.credentials_path or (self.vault_path / 'scripts' / 'credentials.json')
        
        # Load token if exists
        if self.token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)
            except Exception as e:
                self.logger.warning(f"Failed to load token: {e}")
                
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    self.logger.warning(f"Token refresh failed: {e}")
                    creds = None
                    
            if not creds:
                if not creds_path.exists():
                    self.logger.error("credentials.json not found. Run --authenticate first.")
                    return None
                    
                print("Opening browser for re-authentication...")
                flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
                creds = flow.run_local_server(port=0)
                
            # Save refreshed credentials
            self.token_path.write_text(creds.to_json())
                
        return creds
        
    def connect(self):
        """Connect to Gmail API."""
        creds = self.get_credentials()
        if not creds:
            return False
            
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            # Test connection
            profile = self.service.users().getProfile(userId='me').execute()
            self.logger.info(f"Connected to Gmail: {profile['emailAddress']}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Gmail API: {e}")
            return False
            
    def check_for_updates(self) -> list:
        """Fetch new unread messages."""
        if not self.service:
            return []
            
        try:
            # Fetch unread messages, exclude promotions
            query = 'is:unread -category:promotions -category:social'
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=10
            ).execute()
            
            messages = results.get('messages', [])
            new_messages = []
            
            for msg in messages:
                if msg['id'] not in self.processed_ids:
                    # Get message details to check if should be filtered
                    details = self.get_message_details(msg['id'])
                    if details and not self._should_filter(details):
                        new_messages.append(msg)
                        self.processed_ids.add(msg['id'])
                        
            if new_messages:
                self.logger.info(f"Found {len(new_messages)} new important message(s)")
            return new_messages
            
        except HttpError as e:
            self.logger.error(f"Gmail API error: {e}")
            if e.resp.status == 401:
                self.logger.info("Token expired, will re-authenticate on next run")
                self.token_path.unlink(missing_ok=True)
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return []
            
    def _should_filter(self, message: dict) -> bool:
        """Check if message should be filtered out."""
        text = f"{message['from']} {message['subject']} {message['body']}".lower()
        
        # Filter out no-reply emails
        if 'no-reply' in message['from'].lower():
            return True
            
        # Filter out newsletters and promotions
        for keyword in FILTER_KEYWORDS:
            if keyword in text:
                return True
                
        return False
        
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
                    elif part['mimeType'] == 'text/html' and 'data' in part['body']:
                        # Strip HTML tags for plain text
                        import re
                        html = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                        body = re.sub('<.*?>', '', html)
                        break
            elif 'body' in message['payload'] and 'data' in message['payload']['body']:
                body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8', errors='ignore')
                
            return {
                'id': message_id,
                'from': header_dict.get('From', 'Unknown'),
                'to': header_dict.get('To', ''),
                'subject': header_dict.get('Subject', 'No Subject'),
                'date': header_dict.get('Date', ''),
                'body': body[:3000]  # Limit body length
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
        safe_from = "".join(c if (c.isalnum() or c in '._-') else '_' for c in message['from'].split('<')[0].strip()[:20])
        safe_subject = "".join(c if (c.isalnum() or c in '._-') else '_' for c in message['subject'][:30])
        filename = f"GMAIL_{safe_from}_{safe_subject}_{timestamp}"
        
        # Clean up filename
        filename = filename.replace(' ', '_').replace('__', '_')
        
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
- [ ] Create approval request if sending (HITL)
- [ ] Move to /Done when complete

---
*Created by Gmail Watcher v0.1 (Silver Tier)*
*AI Employee - Qwen Code Brain*
"""
        
        filepath = self.needs_action / f"{filename}.md"
        filepath.write_text(content, encoding='utf-8')
        
        self.logger.info(f"[OK] Created action file: {filepath.name}")
        return filepath
        
    def run_continuous(self):
        """Run watcher continuously."""
        self.logger.info(f"Starting Gmail Watcher (interval: {self.check_interval}s)")
        self.logger.info(f"Vault: {self.vault_path}")
        
        consecutive_errors = 0
        max_errors = 5
        
        while True:
            try:
                # Connect if not connected
                if not self.service:
                    if not self.connect():
                        consecutive_errors += 1
                        if consecutive_errors >= max_errors:
                            self.logger.error("Too many connection errors. Please re-authenticate.")
                            break
                        time.sleep(self.check_interval)
                        continue
                        
                consecutive_errors = 0
                
                # Check for new messages
                messages = self.check_for_updates()
                for msg in messages:
                    details = self.get_message_details(msg['id'])
                    if details:
                        self.create_action_file(details)
                        
            except Exception as e:
                self.logger.error(f"Error in watch loop: {e}")
                consecutive_errors += 1
                
            time.sleep(self.check_interval)


def main():
    parser = argparse.ArgumentParser(
        description='Gmail Watcher for AI Employee',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # First-time authentication (REQUIRED before first use)
    python gmail_watcher.py --authenticate
    
    # One-time scan
    python gmail_watcher.py --vault /path/to/vault
    
    # Continuous monitoring (every 2 minutes)
    python gmail_watcher.py --vault /path/to/vault --continuous --interval 120
    
    # Custom credentials location
    python gmail_watcher.py --vault /path/to/vault --credentials /path/to/credentials.json
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
            print("\n" + "="*60)
            print("Gmail Watcher Setup Complete!")
            print("="*60)
            print("\nNext steps:")
            print("1. Run watcher: python gmail_watcher.py --vault PATH --continuous")
            print("2. Check Needs_Action/ folder for new email tasks")
            print("3. Run orchestrator to process emails")
        else:
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
            print("Error: --vault is required")
            print("\nUsage: python gmail_watcher.py --vault /path/to/vault")
            print("       python gmail_watcher.py --authenticate")
            sys.exit(1)
    
    # Create watcher
    watcher = GmailWatcher(args.vault, args.credentials, args.interval)
    
    if args.continuous:
        print("\n" + "="*60)
        print("Gmail Watcher Started (Continuous Mode)")
        print("="*60)
        print(f"Vault: {args.vault}")
        print(f"Interval: {args.interval} seconds")
        print("Press Ctrl+C to stop")
        print("="*60 + "\n")
        watcher.run_continuous()
    else:
        # One-time scan
        print("\n" + "="*60)
        print("Gmail Watcher - One-time Scan")
        print("="*60)
        print("Running scan...")
        
        if watcher.connect():
            messages = watcher.check_for_updates()
            for msg in messages:
                details = watcher.get_message_details(msg['id'])
                if details:
                    watcher.create_action_file(details)
                    
            print("\n" + "-"*60)
            if messages:
                print(f"[OK] Processed {len(messages)} message(s)")
                print(f"[OK] Check {watcher.needs_action} for action files")
            else:
                print("[OK] No new messages found")
            print("-"*60)
        else:
            print("\n[X] Failed to connect to Gmail API")
            print("Run 'python gmail_watcher.py --authenticate' first")
            sys.exit(1)


if __name__ == "__main__":
    main()
