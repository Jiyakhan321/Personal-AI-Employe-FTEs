#!/usr/bin/env python3
"""
LinkedIn Poster for AI Employee (Silver Tier)

Post to LinkedIn using Playwright browser automation.
Requires human approval before posting (HITL pattern).

Usage:
    # Setup session (first-time login)
    python linkedin_poster.py --setup-session

    # Create draft for approval
    python linkedin_poster.py --vault /path/to/vault --create-draft "Post content"

    # Post approved content
    python linkedin_poster.py --vault /path/to/vault --post-approved
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


SESSION_PATH = Path.home() / '.linkedin_session'


class LinkedInPoster:
    """Post to LinkedIn using Playwright."""
    
    def __init__(self, vault_path: str = None, session_path: str = None):
        self.vault_path = Path(vault_path) if vault_path else None
        self.session_path = Path(session_path) if session_path else SESSION_PATH
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
        print("Opening LinkedIn for login...")
        print("Log in to your LinkedIn account, then close the browser.")
        
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                str(self.session_path),
                headless=False,
                args=['--start-maximized']
            )
            page = browser.pages[0]
            page.goto('https://www.linkedin.com')
            
            # Wait for user to log in
            try:
                page.wait_for_url('https://www.linkedin.com/feed/*', timeout=120000)
                print("LinkedIn login successful!")
                print("Session saved.")
            except PlaywrightTimeout:
                print("Timeout waiting for login.")
                
            browser.close()
            
    def clear_session(self):
        """Clear saved session."""
        import shutil
        if self.session_path.exists():
            shutil.rmtree(self.session_path)
            print(f"Session cleared: {self.session_path}")
        else:
            print("No session to clear")
            
    def create_draft(self, content: str, priority: str = 'medium') -> Path:
        """Create a draft post for approval."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"LINKEDIN_POST_{timestamp}.md"
        
        # Truncate for preview
        preview = content[:100] + '...' if len(content) > 100 else content
        
        draft_content = f"""---
type: approval_request
action: linkedin_post
created: {datetime.now().isoformat()}
priority: {priority}
status: pending
---

# LinkedIn Post for Approval

## Content

{content}

---

## Preview
{preview}

## Character Count
{len(content)} / 3000

---

## To Approve
Move this file to `/Approved/` folder.

## To Reject
Move this file to `/Rejected/` folder with reason.

---
*Created by LinkedIn Poster v0.1 (Silver Tier)*
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
                    args=['--disable-gpu', '--no-sandbox']
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                try:
                    # Go to LinkedIn
                    page.goto('https://www.linkedin.com', wait_until='networkidle')
                    
                    # Wait for feed to load
                    try:
                        page.wait_for_selector('[data-control-name="updates_dish"]', timeout=10000)
                    except PlaywrightTimeout:
                        # Try alternative selector
                        page.wait_for_selector('.share-box-feed-entry', timeout=10000)
                    
                    # Click to start post
                    start_post_button = page.query_selector('[data-control-name="updates_dish"]')
                    if start_post_button:
                        start_post_button.click()
                    else:
                        # Alternative: find share box
                        share_box = page.query_selector('.share-box-feed-entry')
                        if share_box:
                            share_box.click()
                            
                    time.sleep(2)
                    
                    # Find the text input and type content
                    # LinkedIn uses a contenteditable div
                    text_input = page.query_selector('[contenteditable="true"][role="textbox"]')
                    if text_input:
                        text_input.fill(content)
                        self.logger.info("Post content entered")
                    else:
                        self.logger.error("Could not find post text input")
                        browser.close()
                        return False
                        
                    time.sleep(1)
                    
                    # Click Post button
                    post_button = page.query_selector('button:has-text("Post")')
                    if post_button:
                        post_button.click()
                        self.logger.info("Post button clicked")
                    else:
                        self.logger.error("Could not find Post button")
                        browser.close()
                        return False
                        
                    # Wait for confirmation
                    time.sleep(3)
                    
                    self.logger.info("Post submitted successfully")
                    browser.close()
                    return True
                    
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
                # Move to Done
                dest = self.done / post_file.name
                dest.write_text(f"{content}\n\n**Posted:** {datetime.now().isoformat()}", 
                               encoding='utf-8')
                self.logger.info(f"Posted and moved to Done: {post_file.name}")
                count += 1
            else:
                self.logger.error(f"Failed to post: {post_file.name}")
                
        return count


def main():
    if not PLAYWRIGHT_AVAILABLE:
        print("Playwright not installed.")
        print("Install with: pip install playwright && playwright install chromium")
        sys.exit(1)
        
    parser = argparse.ArgumentParser(description='LinkedIn Poster')
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
            print("--vault is required for --create-draft")
            sys.exit(1)
        draft_path = poster.create_draft(args.create_draft)
        print(f"Draft created: {draft_path.name}")
        print("Move to /Approved/ to post, or /Rejected/ to discard")
        return
        
    if args.post_approved:
        if not args.vault:
            print("--vault is required for --post-approved")
            sys.exit(1)
        count = poster.process_approved_posts()
        print(f"Posted {count} content(s)")
        return
        
    parser.print_help()


if __name__ == "__main__":
    main()
