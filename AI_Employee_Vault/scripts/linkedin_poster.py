#!/usr/bin/env python3
"""
LinkedIn Poster for AI Employee (Silver Tier)

Posts to LinkedIn using Playwright browser automation.
Requires human approval before posting (HITL pattern).

Usage:
    # Setup session (first-time login)
    python linkedin_poster.py --setup-session

    # Create draft post for approval
    python linkedin_poster.py --vault PATH --create-draft "Your post content here"

    # Post approved content
    python linkedin_poster.py --vault PATH --post-approved
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
    print("Install: pip install playwright && playwright install chromium")


class LinkedInPoster:
    """Post to LinkedIn using Playwright."""
    
    def __init__(self, vault_path: str = None, session_path: str = None):
        self.vault_path = Path(vault_path) if vault_path else None
        # Use same session as LinkedIn Watcher
        self.session_path = Path(session_path) if session_path else (Path.home() / '.linkedin_session')
        self.pending_approval = self.vault_path / 'Pending_Approval' if self.vault_path else None
        self.approved = self.vault_path / 'Approved' if self.vault_path else None
        self.done = self.vault_path / 'Done' if self.vault_path else None
        
        # Ensure directories exist
        if self.vault_path:
            for directory in [self.pending_approval, self.approved, self.done]:
                directory.mkdir(parents=True, exist_ok=True)
                
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_session(self):
        """Open browser for LinkedIn login."""
        print("\n" + "="*60)
        print("LinkedIn Poster - Session Setup")
        print("="*60)
        print("\nOpening LinkedIn for login...")
        print("1. Log in to your LinkedIn account")
        print("2. Wait for your feed to load")
        print("3. Close the browser when done")
        print("="*60 + "\n")
        
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                str(self.session_path),
                headless=False,
                args=['--start-maximized'],
                timeout=60000
            )
            page = browser.pages[0]
            page.goto('https://www.linkedin.com', timeout=60000, wait_until='domcontentloaded')
            
            # Wait for user to log in
            try:
                page.wait_for_url('https://www.linkedin.com/feed/*', timeout=120000)
                time.sleep(3)  # Wait for full page load
                print("\n[OK] LinkedIn login successful!")
                print(f"[OK] Session saved to: {self.session_path}")
            except PlaywrightTimeout:
                print("\n[WARN] Timeout waiting for LinkedIn to load.")
                print("You can manually log in. Close browser when done.")
                time.sleep(30)  # Give user time to log in
                
            browser.close()
            
    def clear_session(self):
        """Clear saved session."""
        import shutil
        if self.session_path.exists():
            shutil.rmtree(self.session_path)
            print(f"[OK] Session cleared: {self.session_path}")
        else:
            print("No session to clear")
            
    def create_draft(self, content: str, priority: str = 'medium') -> Path:
        """Create a draft post for approval."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"LINKEDIN_POST_{timestamp}.md"
        
        # Count characters
        char_count = len(content)
        max_chars = 3000
        
        draft_content = f"""---
type: approval_request
action: linkedin_post
created: {datetime.now().isoformat()}
priority: {priority}
status: pending
character_count: {char_count}
---

# LinkedIn Post for Approval

## Content

{content}

---

## Post Details

- **Character Count:** {char_count} / {max_chars}
- **Priority:** {priority}
- **Created:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## To Approve
Move this file to `/Approved/` folder.

## To Reject
Move this file to `/Rejected/` folder with reason.

---
*Created by LinkedIn Poster v0.1 (Silver Tier)*
*AI Employee - Qwen Code Brain*
"""
        
        filepath = self.pending_approval / filename
        filepath.write_text(draft_content, encoding='utf-8')
        
        self.logger.info(f"Created draft: {filename}")
        return filepath
        
    def post_to_linkedin(self, content: str) -> bool:
        """Post content to LinkedIn."""
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
                    self.logger.info("Navigating to LinkedIn...")
                    page.goto('https://www.linkedin.com', timeout=60000, wait_until='domcontentloaded')
                    
                    # Wait for page to be ready
                    time.sleep(5)
                    
                    # Check if logged in
                    try:
                        page.wait_for_selector('[data-control-name="updates_dish"]', timeout=15000)
                    except PlaywrightTimeout:
                        self.logger.error("Not logged in or session expired")
                        browser.close()
                        return False
                    
                    # Click to start post
                    self.logger.info("Looking for post creation button...")
                    
                    # Try different selectors for "Start a post"
                    post_selectors = [
                        '[data-control-name="updates_dish"]',
                        '.share-box-feed-entry__trigger',
                        'button:has-text("Start a post")',
                        'button:has-text("Start")'
                    ]
                    
                    post_button = None
                    for selector in post_selectors:
                        post_button = page.query_selector(selector)
                        if post_button:
                            self.logger.info(f"Found post button with selector: {selector}")
                            break
                    
                    if post_button:
                        post_button.click()
                        time.sleep(3)
                    else:
                        self.logger.error("Could not find post creation button")
                        browser.close()
                        return False
                    
                    # Find the text input and type content
                    self.logger.info("Entering post content...")
                    
                    # LinkedIn uses a contenteditable div for post input
                    text_input = page.query_selector('[contenteditable="true"][role="textbox"]')
                    if text_input:
                        # Clear any existing text
                        text_input.fill('')
                        time.sleep(0.5)
                        
                        # Type content
                        text_input.fill(content)
                        self.logger.info("Post content entered")
                    else:
                        self.logger.error("Could not find post text input")
                        browser.close()
                        return False
                        
                    time.sleep(3)
                    
                    # Click Post button
                    self.logger.info("Looking for Post button...")
                    
                    post_button_selectors = [
                        'button:has-text("Post")',
                        'button[data-control-name="compose-submit"]'
                    ]
                    
                    submit_button = None
                    for selector in post_button_selectors:
                        submit_button = page.query_selector(selector)
                        if submit_button:
                            break
                    
                    if submit_button:
                        submit_button.click()
                        self.logger.info("Post button clicked")
                        
                        # Wait for confirmation
                        time.sleep(5)
                        
                        self.logger.info("Post submitted successfully")
                        browser.close()
                        return True
                    else:
                        self.logger.error("Could not find Post button")
                        browser.close()
                        return False
                    
                except Exception as e:
                    self.logger.error(f"Error during posting: {e}")
                    browser.close()
                    return False
                    
        except Exception as e:
            self.logger.error(f"Playwright error: {e}")
            return False
            
    def process_approved_posts(self) -> int:
        """Process approved posts and publish them."""
        if not self.approved or not self.approved.exists():
            return 0
            
        count = 0
        for post_file in self.approved.glob('LINKEDIN_POST_*.md'):
            content = post_file.read_text(encoding='utf-8')
            
            # Extract post content (between ## Content and ---)
            parts = content.split('## Content')
            if len(parts) < 2:
                self.logger.warning(f"Invalid format: {post_file.name}")
                continue
                
            post_content = parts[1].split('---')[0].strip()
            
            # Post to LinkedIn
            if self.post_to_linkedin(post_content):
                # Move to Done with timestamp
                dest = self.done / post_file.name
                dest.write_text(f"{content}\n\n**Posted:** {datetime.now().isoformat()}", 
                               encoding='utf-8')
                self.logger.info(f"[OK] Posted and moved to Done: {post_file.name}")
                count += 1
            else:
                self.logger.error(f"[ERROR] Failed to post: {post_file.name}")
                
        return count


def main():
    if not PLAYWRIGHT_AVAILABLE:
        print("Playwright not installed.")
        print("Install: pip install playwright && playwright install chromium")
        sys.exit(1)
        
    parser = argparse.ArgumentParser(
        description='LinkedIn Poster - Post to LinkedIn with approval workflow',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # First-time session setup
    python linkedin_poster.py --setup-session
    
    # Create draft post for approval
    python linkedin_poster.py --vault PATH --create-draft "Your post content here"
    
    # Post approved content
    python linkedin_poster.py --vault PATH --post-approved
    
    # Clear session and re-authenticate
    python linkedin_poster.py --clear-session
        """
    )
    
    parser.add_argument('--vault', '-v', help='Path to Obsidian vault')
    parser.add_argument('--setup-session', action='store_true', help='Setup LinkedIn session')
    parser.add_argument('--clear-session', action='store_true', help='Clear saved session')
    parser.add_argument('--create-draft', '-d', help='Create draft post for approval')
    parser.add_argument('--post-approved', action='store_true', help='Post approved content')
    parser.add_argument('--session-path', help='Custom session path')
    
    args = parser.parse_args()
    
    poster = LinkedInPoster(args.vault, args.session_path)
    
    if args.setup_session:
        poster.setup_session()
        return
        
    if args.clear_session:
        poster.clear_session()
        return
        
    if args.create_draft:
        if not args.vault:
            print("[ERROR] --vault is required for --create-draft")
            sys.exit(1)
        draft_path = poster.create_draft(args.create_draft)
        print(f"\n[OK] Draft created: {draft_path.name}")
        print("\nNext steps:")
        print("1. Review the draft in Pending_Approval/ folder")
        print("2. Move to Approved/ to post, or Rejected/ to discard")
        print("3. Run: python linkedin_poster.py --vault PATH --post-approved")
        return
        
    if args.post_approved:
        if not args.vault:
            print("[ERROR] --vault is required for --post-approved")
            sys.exit(1)
        count = poster.process_approved_posts()
        print(f"\n[OK] Posted {count} content(s)")
        return
        
    parser.print_help()


if __name__ == "__main__":
    main()
