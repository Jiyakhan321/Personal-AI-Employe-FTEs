#!/usr/bin/env python3
"""
LinkedIn Watcher for AI Employee (Silver Tier)

Monitors LinkedIn for new messages and connection requests.
Uses Playwright for browser automation.

NOTE: Be aware of LinkedIn's terms of service when using automation.

Usage:
    # First-time session setup (login to LinkedIn)
    python linkedin_watcher.py --setup-session

    # One-time scan
    python linkedin_watcher.py --vault /path/to/vault

    # Continuous monitoring (every 5 minutes)
    python linkedin_watcher.py --vault /path/to/vault --continuous --interval 300
"""

import argparse
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

# Playwright imports
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Playwright not installed.")
    print("Install with: pip install playwright && playwright install chromium")


# Session path
SESSION_PATH = Path.home() / '.linkedin_session'

# Keywords that indicate important messages
PRIORITY_KEYWORDS = ['opportunity', 'job', 'interview', 'position', 'project', 'collaboration', 'urgent', 'meeting']


class LinkedInWatcher:
    """Monitor LinkedIn for messages and opportunities."""
    
    def __init__(self, vault_path: str, check_interval: int = 300, session_path: str = None):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.session_path = Path(session_path) if session_path else SESSION_PATH
        self.processed_messages = set()
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_session(self):
        """Open browser for LinkedIn login."""
        print("\n" + "="*60)
        print("LinkedIn Session Setup")
        print("="*60)
        print("\nOpening LinkedIn for login...")
        print("1. Log in to your LinkedIn account")
        print("2. Wait for your feed to load completely")
        print("3. Close the browser when done")
        print("="*60 + "\n")
        
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                str(self.session_path),
                headless=False,
                args=['--start-maximized']
            )
            page = browser.pages[0]
            page.goto('https://www.linkedin.com')
            
            # Wait for user to log in and feed to load
            try:
                page.wait_for_url('https://www.linkedin.com/feed/*', timeout=120000)
                # Wait additional time for full page load
                time.sleep(5)
                print("\n✓ LinkedIn login successful!")
                print(f"✓ Session saved to: {self.session_path}")
            except PlaywrightTimeout:
                print("\n⚠ Timeout waiting for LinkedIn to load.")
                print("Please run again and complete login quickly.")
                
            browser.close()
            
    def clear_session(self):
        """Clear saved session."""
        import shutil
        if self.session_path.exists():
            shutil.rmtree(self.session_path)
            print(f"✓ Session cleared: {self.session_path}")
            print("Run --setup-session to login again")
        else:
            print("No session to clear")
            
    def check_for_messages(self) -> list:
        """Check LinkedIn for new messages and notifications."""
        notifications = []
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=True,
                    args=['--disable-gpu', '--no-sandbox'],
                    timeout=60000
                )

                page = browser.pages[0] if browser.pages else browser.new_page()

                try:
                    # Go to LinkedIn with longer timeout
                    page.goto('https://www.linkedin.com', timeout=60000, wait_until='domcontentloaded')
                    
                    # Wait for page to stabilize
                    time.sleep(5)

                    # Check if logged in by looking for feed
                    try:
                        page.wait_for_selector('[data-control-name="updates_dish"]', timeout=15000)
                    except PlaywrightTimeout:
                        # Try alternative selector
                        try:
                            page.wait_for_selector('.share-box-feed-entry', timeout=10000)
                        except PlaywrightTimeout:
                            self.logger.warning("Not logged in or session expired")
                            browser.close()
                            return []

                    # Give time for notifications to load
                    time.sleep(3)
                    
                    # Check for notification bell
                    try:
                        notification_bell = page.query_selector('[data-control-name="notifications"]')
                        if notification_bell:
                            # Get notification count if available
                            badge = notification_bell.query_selector('.notification-badge')
                            if badge:
                                count = badge.inner_text().strip()
                                self.logger.info(f"Found {count} notifications")
                    except:
                        pass
                    
                    # Navigate to messaging page to check for new messages
                    page.goto('https://www.linkedin.com/messaging/', wait_until='networkidle')
                    time.sleep(3)
                    
                    # Find conversation threads
                    try:
                        conversations = page.query_selector_all('li.conversation')
                        self.logger.info(f"Found {len(conversations)} conversations")
                        
                        for conv in conversations[:5]:  # Check top 5 conversations
                            try:
                                # Get sender name
                                name_elem = conv.query_selector('.message-sender__name')
                                sender_name = name_elem.inner_text().strip() if name_elem else 'Unknown'
                                
                                # Get last message
                                msg_elem = conv.query_selector('.message-body')
                                last_message = msg_elem.inner_text().strip() if msg_elem else ''
                                
                                # Get timestamp
                                time_elem = conv.query_selector('.message-time')
                                timestamp = time_elem.get_attribute('datetime') if time_elem else datetime.now().isoformat()
                                
                                # Check if unread
                                is_unread = 'unread' in conv.get_attribute('class', '').lower()
                                
                                if is_unread or self._contains_keywords(last_message):
                                    notifications.append({
                                        'type': 'message',
                                        'from': sender_name,
                                        'message': last_message,
                                        'timestamp': timestamp,
                                        'unread': is_unread
                                    })
                                    self.logger.info(f"Found message from {sender_name}")
                                    
                            except Exception as e:
                                self.logger.debug(f"Error processing conversation: {e}")
                                continue
                                
                    except Exception as e:
                        self.logger.debug(f"Error finding conversations: {e}")
                    
                    # Check for connection requests
                    page.goto('https://www.linkedin.com/mynetwork/', wait_until='networkidle')
                    time.sleep(2)
                    
                    try:
                        connection_requests = page.query_selector_all('.invitation-card')
                        for req in connection_requests[:5]:
                            try:
                                name_elem = req.query_selector('.invitation-link__name')
                                sender_name = name_elem.inner_text().strip() if name_elem else 'Unknown'
                                
                                title_elem = req.query_selector('.invitation-link__headline')
                                headline = title_elem.inner_text().strip() if title_elem else ''
                                
                                notifications.append({
                                    'type': 'connection',
                                    'from': sender_name,
                                    'headline': headline,
                                    'timestamp': datetime.now().isoformat()
                                })
                                self.logger.info(f"Found connection request from {sender_name}")
                                
                            except Exception as e:
                                self.logger.debug(f"Error processing connection request: {e}")
                                continue
                                
                    except Exception as e:
                        self.logger.debug(f"Error finding connection requests: {e}")
                    
                except Exception as e:
                    self.logger.error(f"Error during LinkedIn check: {e}")
                finally:
                    browser.close()
                    
        except Exception as e:
            self.logger.error(f"Playwright error: {e}")
            
        return notifications
        
    def _contains_keywords(self, text: str) -> bool:
        """Check if text contains priority keywords."""
        if not text:
            return False
        text_lower = text.lower()
        return any(kw in text_lower for kw in PRIORITY_KEYWORDS)
        
    def create_action_file(self, notification: dict) -> Path:
        """Create action file in Needs_Action folder."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = "".join(c if (c.isalnum() or c in '._-') else '_' for c in notification['from'][:20])
        
        if notification['type'] == 'message':
            filename = f"LINKEDIN_MSG_{safe_name}_{timestamp}"
            
            content = f"""---
type: linkedin_message
from: {notification['from']}
received: {notification['timestamp']}
priority: {'high' if self._contains_keywords(notification.get('message', '')) else 'medium'}
status: pending
unread: {str(notification.get('unread', False))}
---

# LinkedIn Message for Processing

**From:** {notification['from']}

**Message:**
{notification.get('message', 'N/A')}

---

## Suggested Actions

- [ ] Read message
- [ ] Draft professional response
- [ ] Check sender's profile if needed
- [ ] Send reply via LinkedIn
- [ ] Move to /Done when complete

---
*Created by LinkedIn Watcher v0.1 (Silver Tier)*
*AI Employee - Qwen Code Brain*
"""
        else:  # connection request
            filename = f"LINKEDIN_CONN_{safe_name}_{timestamp}"
            
            content = f"""---
type: linkedin_connection
from: {notification['from']}
headline: {notification.get('headline', 'N/A')}
received: {datetime.now().isoformat()}
priority: medium
status: pending
---

# LinkedIn Connection Request

**From:** {notification['from']}

**Headline:**
{notification.get('headline', 'N/A')}

---

## Suggested Actions

- [ ] Review sender's profile
- [ ] Accept or decline connection
- [ ] Send personalized thank you message
- [ ] Move to /Done when complete

---
*Created by LinkedIn Watcher v0.1 (Silver Tier)*
*AI Employee - Qwen Code Brain*
"""
        
        filepath = self.needs_action / f"{filename}.md"
        filepath.write_text(content, encoding='utf-8')
        
        self.logger.info(f"✓ Created action file: {filename}")
        return filepath
        
    def run_continuous(self):
        """Run watcher continuously."""
        self.logger.info(f"Starting LinkedIn Watcher (interval: {self.check_interval}s)")
        self.logger.info(f"Session: {self.session_path}")
        
        consecutive_errors = 0
        max_errors = 3
        
        while True:
            try:
                notifications = self.check_for_messages()
                for notif in notifications:
                    # Create unique ID for deduplication
                    notif_id = f"{notif['type']}:{notif['from']}:{notif.get('timestamp', '')}"
                    if notif_id not in self.processed_messages:
                        self.create_action_file(notif)
                        self.processed_messages.add(notif_id)
                        
                consecutive_errors = 0
                
            except Exception as e:
                self.logger.error(f"Error in watch loop: {e}")
                consecutive_errors += 1
                if consecutive_errors >= max_errors:
                    self.logger.error("Too many errors, session may be expired")
                    self.logger.error("Run --setup-session to re-authenticate")
                    
            time.sleep(self.check_interval)


def main():
    if not PLAYWRIGHT_AVAILABLE:
        print("Playwright not installed.")
        print("Install with: pip install playwright && playwright install chromium")
        sys.exit(1)
        
    parser = argparse.ArgumentParser(
        description='LinkedIn Watcher for AI Employee',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # First-time session setup (REQUIRED)
    python linkedin_watcher.py --setup-session
    
    # One-time scan
    python linkedin_watcher.py --vault /path/to/vault
    
    # Continuous monitoring (every 5 minutes)
    python linkedin_watcher.py --vault /path/to/vault --continuous --interval 300
    
    # Clear session and re-authenticate
    python linkedin_watcher.py --clear-session
        """
    )
    
    parser.add_argument('--vault', '-v', help='Path to Obsidian vault')
    parser.add_argument('--setup-session', action='store_true', help='Setup LinkedIn session')
    parser.add_argument('--clear-session', action='store_true', help='Clear saved session')
    parser.add_argument('--continuous', '-c', action='store_true', help='Run continuously')
    parser.add_argument('--interval', '-i', type=int, default=300, help='Check interval in seconds')
    parser.add_argument('--session-path', help='Custom session storage path')
    
    args = parser.parse_args()
    
    # Handle session setup
    if args.setup_session:
        watcher = LinkedInWatcher('.', session_path=args.session_path)
        watcher.setup_session()
        print("\n" + "="*60)
        print("LinkedIn Watcher Setup Complete!")
        print("="*60)
        print("\nNext steps:")
        print("1. Run watcher: python linkedin_watcher.py --vault PATH --continuous")
        print("2. Check Needs_Action/ folder for new LinkedIn tasks")
        print("="*60)
        return
        
    # Handle session clear
    if args.clear_session:
        watcher = LinkedInWatcher('.', session_path=args.session_path)
        watcher.clear_session()
        return
        
    # Require vault for normal operation
    if not args.vault:
        possible_vaults = list(Path('.').glob('*/Dashboard.md'))
        if possible_vaults:
            args.vault = str(possible_vaults[0].parent)
            print(f"Auto-detected vault: {args.vault}")
        else:
            print("Error: --vault is required")
            print("\nUsage: python linkedin_watcher.py --vault /path/to/vault")
            print("       python linkedin_watcher.py --setup-session")
            sys.exit(1)
    
    # Create watcher
    watcher = LinkedInWatcher(args.vault, args.interval, args.session_path)
    
    if args.continuous:
        print("\n" + "="*60)
        print("LinkedIn Watcher Started (Continuous Mode)")
        print("="*60)
        print(f"Vault: {args.vault}")
        print(f"Interval: {args.interval} seconds")
        print("Press Ctrl+C to stop")
        print("="*60 + "\n")
        watcher.run_continuous()
    else:
        # One-time scan
        print("\n" + "="*60)
        print("LinkedIn Watcher - One-time Scan")
        print("="*60)
        print("Running scan...")
        
        notifications = watcher.check_for_messages()
        
        print("\n" + "-"*60)
        if notifications:
            for notif in notifications:
                watcher.create_action_file(notif)
            print(f"✓ Processed {len(notifications)} notification(s)")
            print(f"✓ Check {watcher.needs_action} for action files")
        else:
            print("✓ No new notifications found")
        print("-"*60)


if __name__ == "__main__":
    main()
