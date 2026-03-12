#!/usr/bin/env python3
"""
WhatsApp Watcher for AI Employee (Silver Tier)

Monitors WhatsApp Web for urgent messages and creates action files in Obsidian vault.
Uses Playwright for browser automation.

NOTE: Be aware of WhatsApp's terms of service when using automation.

Usage:
    # First-time session setup
    python whatsapp_watcher.py --setup-session

    # One-time scan
    python whatsapp_watcher.py --vault /path/to/vault

    # Continuous monitoring
    python whatsapp_watcher.py --vault /path/to/vault --continuous --interval 30
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


# Keywords that indicate urgent messages
KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'help', 'deadline', 'emergency', 'important']

# Session path
SESSION_PATH = Path.home() / '.whatsapp_session'


class WhatsAppWatcher:
    """Monitor WhatsApp Web for urgent messages."""
    
    def __init__(self, vault_path: str, check_interval: int = 30, session_path: str = None):
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
        """Open browser for WhatsApp Web login."""
        print("Opening WhatsApp Web for QR code scan...")
        print("Scan the QR code with your WhatsApp mobile app.")
        print("Wait for chat list to load, then close the browser.")
        
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                str(self.session_path),
                headless=False,
                args=['--start-maximized']
            )
            page = browser.pages[0]
            page.goto('https://web.whatsapp.com')
            
            # Wait for user to scan QR and load chats
            try:
                page.wait_for_selector('[data-testid="chat-list"]', timeout=120000)
                print("WhatsApp Web loaded successfully!")
                print("Session saved. You can close the browser.")
            except PlaywrightTimeout:
                print("Timeout waiting for WhatsApp Web to load.")
                print("Please run again and scan QR code quickly.")
                
            browser.close()
            
    def clear_session(self):
        """Clear saved session."""
        import shutil
        if self.session_path.exists():
            shutil.rmtree(self.session_path)
            print(f"Session cleared: {self.session_path}")
        else:
            print("No session to clear")
            
    def check_for_messages(self) -> list:
        """Check WhatsApp Web for unread messages with keywords."""
        messages = []
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=True,
                    args=['--disable-gpu', '--no-sandbox']
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                try:
                    page.goto('https://web.whatsapp.com', wait_until='networkidle')
                    
                    # Wait for chat list
                    try:
                        page.wait_for_selector('[data-testid="chat-list"]', timeout=10000)
                    except PlaywrightTimeout:
                        self.logger.warning("Chat list not found - may need to re-authenticate")
                        browser.close()
                        return []
                    
                    # Give time for messages to load
                    time.sleep(2)
                    
                    # Find unread messages
                    # WhatsApp Web structure may change - these selectors are current as of 2026
                    unread_chats = page.query_selector_all('[aria-label*="unread"]')
                    
                    for chat in unread_chats:
                        try:
                            # Get chat name
                            name_elem = chat.query_selector('[title]')
                            chat_name = name_elem.get_attribute('title') if name_elem else 'Unknown'
                            
                            # Get message text
                            msg_elem = chat.query_selector('[data-testid="chat-message"]')
                            msg_text = msg_elem.inner_text() if msg_elem else ''
                            
                            # Check for keywords
                            msg_lower = msg_text.lower()
                            if any(kw in msg_lower for kw in KEYWORDS):
                                messages.append({
                                    'chat': chat_name,
                                    'text': msg_text,
                                    'timestamp': datetime.now().isoformat()
                                })
                                self.logger.info(f"Found urgent message from {chat_name}")
                                
                        except Exception as e:
                            self.logger.debug(f"Error processing chat: {e}")
                            continue
                            
                except Exception as e:
                    self.logger.error(f"Error during WhatsApp check: {e}")
                finally:
                    browser.close()
                    
        except Exception as e:
            self.logger.error(f"Playwright error: {e}")
            
        return messages
        
    def create_action_file(self, message: dict) -> Path:
        """Create action file in Needs_Action folder."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = "".join(c if c.isalnum() else '_' for c in message['chat'][:20])
        
        content = f"""---
type: whatsapp
from: {message['chat']}
received: {message['timestamp']}
priority: high
status: pending
---

# WhatsApp Message for Processing

**From:** {message['chat']}

**Message:**
{message['text']}

---

## Suggested Actions

- [ ] Read message
- [ ] Draft reply in WhatsApp
- [ ] Take any required action
- [ ] Move to /Done when complete

---
*Created by WhatsApp Watcher v0.1 (Silver Tier)*
"""
        
        filename = f"WHATSAPP_{safe_name}_{timestamp}.md"
        filepath = self.needs_action / filename
        filepath.write_text(content, encoding='utf-8')
        
        self.logger.info(f"Created action file: {filename}")
        return filepath
        
    def run_continuous(self):
        """Run watcher continuously."""
        self.logger.info(f"Starting WhatsApp Watcher (interval: {self.check_interval}s)")
        self.logger.info(f"Session: {self.session_path}")
        
        while True:
            try:
                messages = self.check_for_messages()
                for msg in messages:
                    # Create unique ID for deduplication
                    msg_id = f"{msg['chat']}:{msg['text'][:50]}"
                    if msg_id not in self.processed_messages:
                        self.create_action_file(msg)
                        self.processed_messages.add(msg_id)
                        
            except Exception as e:
                self.logger.error(f"Error in watch loop: {e}")
                time.sleep(10)  # Wait before retrying
                
            time.sleep(self.check_interval)


def main():
    if not PLAYWRIGHT_AVAILABLE:
        print("Playwright not installed.")
        print("Install with: pip install playwright && playwright install chromium")
        sys.exit(1)
        
    parser = argparse.ArgumentParser(
        description='WhatsApp Watcher for AI Employee',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # First-time session setup
    python whatsapp_watcher.py --setup-session
    
    # One-time scan
    python whatsapp_watcher.py --vault /path/to/vault
    
    # Continuous monitoring (every 30 seconds)
    python whatsapp_watcher.py --vault /path/to/vault --continuous --interval 30
    
    # Clear session and re-authenticate
    python whatsapp_watcher.py --clear-session
        """
    )
    
    parser.add_argument('--vault', '-v', help='Path to Obsidian vault')
    parser.add_argument('--setup-session', action='store_true', help='Setup WhatsApp Web session')
    parser.add_argument('--clear-session', action='store_true', help='Clear saved session')
    parser.add_argument('--continuous', '-c', action='store_true', help='Run continuously')
    parser.add_argument('--interval', '-i', type=int, default=30, help='Check interval in seconds')
    parser.add_argument('--session-path', help='Custom session storage path')
    
    args = parser.parse_args()
    
    # Handle session setup
    if args.setup_session:
        watcher = WhatsAppWatcher('.', session_path=args.session_path)
        watcher.setup_session()
        return
        
    # Handle session clear
    if args.clear_session:
        watcher = WhatsAppWatcher('.', session_path=args.session_path)
        watcher.clear_session()
        return
        
    # Require vault for normal operation
    if not args.vault:
        possible_vaults = list(Path('.').glob('*/Dashboard.md'))
        if possible_vaults:
            args.vault = str(possible_vaults[0].parent)
            print(f"Auto-detected vault: {args.vault}")
        else:
            parser.error("--vault is required")
    
    # Create watcher
    watcher = WhatsAppWatcher(args.vault, args.interval, args.session_path)
    
    if args.continuous:
        watcher.run_continuous()
    else:
        # One-time scan
        print("Running one-time scan...")
        messages = watcher.check_for_messages()
        
        if messages:
            for msg in messages:
                watcher.create_action_file(msg)
            print(f"Found {len(messages)} urgent message(s)")
        else:
            print("No urgent messages found")


if __name__ == "__main__":
    main()
