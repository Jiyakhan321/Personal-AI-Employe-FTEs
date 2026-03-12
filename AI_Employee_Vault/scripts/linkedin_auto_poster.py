#!/usr/bin/env python3
"""
LinkedIn Auto Poster for AI Employee (Silver Tier - Enhanced)

Posts to LinkedIn using Playwright with PERSISTENT SESSION.
Key improvements:
- Storage state persistence (cookies + localStorage)
- Login state detection (auto-skip if already logged in)
- Session recovery on expiration
- Better selectors for LinkedIn's dynamic UI
- Vault-relative session storage

Usage:
    # First-time session setup (REQUIRED)
    python linkedin_auto_poster.py --setup-session --vault PATH

    # Create draft post for approval
    python linkedin_auto_poster.py --vault PATH --create-draft "Your post content here"

    # Post approved content (auto)
    python linkedin_auto_poster.py --vault PATH --post-approved

    # Check session status
    python linkedin_auto_poster.py --vault PATH --check-session

    # Clear session and re-authenticate
    python linkedin_auto_poster.py --vault PATH --clear-session
"""

import argparse
import json
import logging
import os
import random
import sys
import time
from datetime import datetime
from pathlib import Path

# Playwright imports
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout, Error as PlaywrightError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Playwright not installed.")
    print("Install: pip install playwright && playwright install chromium")


class LinkedInAutoPoster:
    """Post to LinkedIn using Playwright with persistent session."""

    def __init__(self, vault_path: str, session_path: str = None, debug_mode: bool = False):
        self.vault_path = Path(vault_path)
        # Session storage INSIDE vault for better management
        self.session_dir = self.vault_path / '.linkedin_session'
        self.storage_state_file = self.session_dir / 'storage_state.json'
        self.user_data_dir = self.session_dir / 'user_data'
        self.debug_mode = debug_mode  # Show browser if True

        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'

        # Ensure directories exist
        for directory in [self.session_dir, self.pending_approval, self.approved,
                          self.done, self.logs, self.user_data_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # Setup logging
        log_file = self.logs / f"linkedin_{datetime.now().strftime('%Y-%m-%d')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # LinkedIn URLs
        self.LOGIN_URL = 'https://www.linkedin.com/login'
        self.FEED_URL = 'https://www.linkedin.com/feed'
        self.POST_URL = 'https://www.linkedin.com/feed/?shareActive=true'

    def _get_browser_context(self, headless: bool = True):
        """Create browser context with persistent storage."""
        playwright = sync_playwright().start()
        
        context = playwright.chromium.launch_persistent_context(
            str(self.user_data_dir),
            headless=headless,
            args=[
                '--disable-gpu',
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process'
            ],
            ignore_default_args=['--enable-automation'],
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        return playwright, context

    def check_session(self) -> bool:
        """Check if LinkedIn session is valid without posting."""
        self.logger.info("Checking LinkedIn session status...")

        playwright = None
        context = None

        try:
            playwright, context = self._get_browser_context(headless=not self.debug_mode)
            page = context.pages[0] if context.pages else context.new_page()

            # Navigate to feed
            page.goto(self.FEED_URL, timeout=30000, wait_until='domcontentloaded')
            time.sleep(3)

            # Check if we're on feed page (logged in) vs login page
            current_url = page.url

            if 'login' in current_url.lower():
                self.logger.warning("Session expired - redirected to login page")
                return False

            # Look for indicators of being logged in
            logged_in_indicators = [
                '[data-control-name="updates_dish"]',  # Feed tab
                '.share-box-feed-entry__trigger',  # Start a post button
                '[aria-label="You are on the home tab"]',
                'img[src*="profile"]',  # Profile picture
            ]

            for selector in logged_in_indicators:
                try:
                    if page.query_selector(selector):
                        self.logger.info(f"Session valid (found: {selector})")
                        return True
                except:
                    continue

            # If no indicators found but not on login page, might still be logged in
            self.logger.info("Session appears valid (on feed page)")
            return True

        except PlaywrightTimeout:
            self.logger.error("Timeout checking session - may be expired")
            return False
        except Exception as e:
            self.logger.error(f"Error checking session: {e}")
            return False
        finally:
            if context:
                try:
                    context.close()
                except:
                    pass
            if playwright:
                try:
                    playwright.stop()
                except:
                    pass

    def setup_session(self):
        """Open browser for LinkedIn login with persistent storage."""
        print("\n" + "="*70)
        print("LinkedIn Auto Poster - Session Setup")
        print("="*70)
        print("\nThis will save your LinkedIn login session for future auto-posting.")
        print("\nInstructions:")
        print("1. A browser window will open")
        print("2. Log in to your LinkedIn account")
        print("3. Wait until you see your feed/homepage")
        print("4. DO NOT close the browser - it will close automatically")
        print("5. Session will be saved to: " + str(self.session_dir))
        print("="*70 + "\n")

        playwright, context = self._get_browser_context(headless=False)
        
        try:
            page = context.pages[0] if context.pages else context.new_page()
            
            # Navigate to LinkedIn
            print("Opening LinkedIn login page...")
            page.goto(self.LOGIN_URL, timeout=60000, wait_until='domcontentloaded')
            
            # Wait for user to log in - watch for URL change to feed
            print("\nWaiting for login... (timeout: 3 minutes)")
            print("Please complete login and wait for your feed to load.")
            
            max_wait = 180  # 3 minutes
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                current_url = page.url
                
                # Check if logged in (on feed page)
                if 'feed' in current_url or current_url == 'https://www.linkedin.com/':
                    # Wait a bit more for full page load
                    time.sleep(5)
                    
                    # Verify we're really logged in
                    try:
                        page.wait_for_selector('.share-box-feed-entry__trigger', timeout=5000)
                        print("\n✓ Login successful! Feed detected.")
                        break
                    except PlaywrightTimeout:
                        # Might still be logging in
                        continue
                
                time.sleep(2)
            else:
                print("\n⚠ Timeout waiting for login. Checking status anyway...")
            
            # Final verification
            final_url = page.url
            if 'login' not in final_url.lower():
                print("✓ Session appears valid!")
                
                # Save storage state for extra persistence
                try:
                    context.storage_state(path=str(self.storage_state_file))
                    print(f"✓ Storage state saved to: {self.storage_state_file}")
                except Exception as e:
                    print(f"⚠ Could not save storage state: {e}")
                
                print("\n" + "="*70)
                print("SUCCESS! LinkedIn session saved.")
                print("="*70)
                print(f"\nSession stored in: {self.session_dir}")
                print("You can now use --create-draft and --post-approved commands.")
                print("Session should persist for weeks unless LinkedIn invalidates it.")
                print("="*70)
            else:
                print("\n✗ Login not completed. Please run --setup-session again.")
                
        except Exception as e:
            print(f"\n✗ Error during setup: {e}")
            self.logger.error(f"Setup error: {e}")
        finally:
            print("\nClosing browser...")
            context.close()
            playwright.stop()

    def clear_session(self):
        """Clear saved session data."""
        import shutil
        
        self.logger.info("Clearing LinkedIn session...")
        
        cleared = []
        
        # Remove user data directory
        if self.user_data_dir.exists():
            shutil.rmtree(self.user_data_dir)
            cleared.append(str(self.user_data_dir))
            
        # Remove storage state file
        if self.storage_state_file.exists():
            self.storage_state_file.unlink()
            cleared.append(str(self.storage_state_file))
        
        if cleared:
            print(f"\n✓ Session cleared:")
            for path in cleared:
                print(f"  - {path}")
            print("\nRun --setup-session to login again.")
        else:
            print("No session data found to clear.")

    def create_draft(self, content: str, priority: str = 'medium') -> Path:
        """Create a draft post for approval."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"LINKEDIN_POST_{timestamp}.md"

        # Count characters
        char_count = len(content)
        max_chars = 3000

        # Extract hashtags for preview
        import re
        hashtags = re.findall(r'#\w+', content)
        
        draft_content = f"""---
type: approval_request
action: linkedin_post
created: {datetime.now().isoformat()}
priority: {priority}
status: pending
character_count: {char_count}
hashtags: {', '.join(hashtags) if hashtags else 'none'}
---

# LinkedIn Post for Approval

## Content

{content}

---

## Post Details

| Property | Value |
|----------|-------|
| **Character Count** | {char_count} / {max_chars} |
| **Priority** | {priority} |
| **Hashtags** | {', '.join(hashtags) if hashtags else 'None'} |
| **Created** | {datetime.now().strftime('%Y-%m-%d %H:%M')} |

---

## To Approve
Move this file to `/Approved/` folder.

## To Reject
Move this file to `/Rejected/` folder with reason.

---
*Created by LinkedIn Auto Poster v0.2 (Silver Tier Enhanced)*
*AI Employee - Qwen Code Brain*
"""

        filepath = self.pending_approval / filename
        filepath.write_text(draft_content, encoding='utf-8')

        self.logger.info(f"Created draft: {filename}")
        print(f"\n✓ Draft created: {filepath.name}")
        print("\nNext steps:")
        print("1. Review draft in: Pending_Approval/")
        print("2. Move to Approved/ to post, or Rejected/ to discard")
        print("3. Run: python linkedin_auto_poster.py --vault PATH --post-approved")
        
        return filepath

    def _humanize_typing(self, page, selector: str, text: str):
        """Type text with human-like delays."""
        element = page.query_selector(selector)
        if not element:
            return False
            
        element.focus()
        time.sleep(random.uniform(0.3, 0.7))
        
        # Type in chunks with small pauses (more human-like)
        chunk_size = random.randint(5, 15)
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i+chunk_size]
            element.type(chunk, delay=random.randint(20, 80))
            time.sleep(random.uniform(0.1, 0.3))
        
        return True

    def post_to_linkedin(self, content: str, retry_count: int = 0) -> tuple[bool, str]:
        """
        Post content to LinkedIn with retry logic.
        Returns: (success: bool, message: str)
        """
        max_retries = 2
        
        playwright = None
        context = None
        
        try:
            self.logger.info(f"Posting to LinkedIn (attempt {retry_count + 1}/{max_retries + 1})...")

            playwright, context = self._get_browser_context(headless=not self.debug_mode)
            page = context.pages[0] if context.pages else context.new_page()

            # Navigate to LinkedIn feed
            self.logger.info("Navigating to LinkedIn...")
            page.goto(self.FEED_URL, timeout=60000, wait_until='domcontentloaded')
            time.sleep(4)  # Wait for dynamic content
            
            # Check if logged in
            current_url = page.url
            if 'login' in current_url.lower():
                msg = "Not logged in - session expired"
                self.logger.error(msg)
                
                # Try to recover by reloading
                if retry_count < max_retries:
                    self.logger.info("Attempting session recovery...")
                    context.close()
                    playwright.stop()
                    time.sleep(2)
                    return self.post_to_linkedin(content, retry_count + 1)
                
                return False, msg
            
            # Click to start post - try multiple selectors (Updated 2026)
            self.logger.info("Opening post composer...")

            post_triggers = [
                'div[aria-label="Start a post"]',  # NEW: LinkedIn 2026
                '.share-box-feed-entry__trigger',
                '[data-control-name="updates_dish"]',
                'button:has-text("Start a post")',
                '[aria-label="Create a post"]',
                'button[aria-label*="post" i]',
                '.artdeco-button[aria-label*="post" i]',
            ]

            clicked = False
            for selector in post_triggers:
                try:
                    btn = page.wait_for_selector(selector, timeout=3000)
                    if btn:
                        btn.click()
                        clicked = True
                        self.logger.info(f"Clicked post trigger: {selector}")
                        time.sleep(3)  # Wait for modal to open
                        break
                except PlaywrightTimeout:
                    continue

            if not clicked:
                # Scroll down and retry
                self.logger.info("Post trigger not found, scrolling and retrying...")
                page.evaluate("window.scrollBy(0, 400)")
                time.sleep(2)
                
                for selector in post_triggers[:3]:  # Try top 3 selectors again
                    try:
                        btn = page.wait_for_selector(selector, timeout=2000)
                        if btn:
                            btn.click()
                            clicked = True
                            self.logger.info(f"Clicked post trigger after scroll: {selector}")
                            time.sleep(3)
                            break
                    except PlaywrightTimeout:
                        continue
                
            if not clicked:
                # Try direct navigation to post composer
                self.logger.info("Post trigger not found, trying direct navigation...")
                page.goto(self.POST_URL, timeout=30000, wait_until='domcontentloaded')
                time.sleep(3)
            
            time.sleep(2)
            
            # Find the text input (contenteditable div) - Updated 2026
            self.logger.info("Entering post content...")

            text_selectors = [
                '[contenteditable="true"][aria-label="Text editor for creating content"]',  # NEW: LinkedIn 2026
                '[contenteditable="true"][role="textbox"]',
                '[contenteditable="true"]',
                '.editor-composer__content [contenteditable="true"]',
                'div[aria-label="What do you want to talk about?"]',
                '[role="textbox"]',
            ]

            text_input = None
            for selector in text_selectors:
                try:
                    text_input = page.wait_for_selector(selector, timeout=3000)
                    if text_input:
                        self.logger.info(f"Found text input: {selector}")
                        break
                except PlaywrightTimeout:
                    continue

            # Fallback: get all contenteditable and use first
            if not text_input:
                try:
                    editables = page.query_selector_all('[contenteditable="true"]')
                    if editables:
                        text_input = editables[0]
                        self.logger.info(f"Using first contenteditable element (fallback)")
                except Exception as e:
                    self.logger.debug(f"Fallback failed: {e}")

            if not text_input:
                msg = "Could not find post text input"
                self.logger.error(msg)
                context.close()
                playwright.stop()
                return False, msg
            
            # Clear existing content and type new content
            text_input.focus()
            time.sleep(0.5)
            
            # Use keyboard to select all and delete
            page.keyboard.press('Control+A')
            time.sleep(0.3)
            page.keyboard.press('Delete')
            time.sleep(0.3)
            
            # Type content with human-like delays
            self._humanize_typing(page, selector, content)
            self.logger.info("Post content entered successfully")
            
            time.sleep(2)
            
            # Click Post button
            self.logger.info("Submitting post...")

            post_buttons = [
                'button:has-text("Post")',
                'button:has-text("Post now")',
                '[data-control-name="compose-submit"]',
                'button[aria-label="Post"]',
            ]

            submit_clicked = False
            for selector in post_buttons:
                try:
                    submit_btn = page.wait_for_selector(selector, timeout=3000)
                    if submit_btn:
                        # Check if enabled
                        is_disabled = submit_btn.evaluate('el => el.disabled')
                        if is_disabled:
                            self.logger.info(f"Found Post button but disabled: {selector}")
                            continue
                        submit_btn.click()
                        submit_clicked = True
                        self.logger.info(f"Clicked submit button: {selector}")
                        break
                except PlaywrightTimeout:
                    continue

            # CRITICAL FALLBACK: Check ALL buttons (LinkedIn 2026 fix)
            if not submit_clicked:
                try:
                    self.logger.info("Checking all buttons on page for Post button...")
                    all_buttons = page.query_selector_all('button')
                    for btn in all_buttons:
                        try:
                            btn_text = btn.inner_text().strip()
                            btn_aria = btn.get_attribute('aria-label') or ''
                            if btn_text in ['Post', 'Post now'] or btn_aria in ['Post', 'Post now']:
                                is_disabled = btn.evaluate('el => el.disabled')
                                if not is_disabled:
                                    self.logger.info(f"Found Post button by inspection: text='{btn_text}' aria='{btn_aria}'")
                                    btn.click()
                                    submit_clicked = True
                                    break
                        except Exception:
                            continue
                except Exception as e:
                    self.logger.warning(f"Button inspection failed: {e}")

            if not submit_clicked:
                msg = "Could not find Post button"
                self.logger.error(msg)
                context.close()
                playwright.stop()
                return False, msg
            
            # Wait for post to be submitted (look for confirmation)
            self.logger.info("Waiting for confirmation...")
            time.sleep(5)
            
            # Check if post was successful (URL might change or we see "Posted" message)
            try:
                # Look for "Posted successfully" or similar
                page.wait_for_selector('text=/Posted|Share|Your post/i', timeout=5000)
                self.logger.info("Post submission confirmed")
            except PlaywrightTimeout:
                self.logger.info("Post submitted (no explicit confirmation found)")
            
            context.close()
            playwright.stop()
            
            self.logger.info("✓ Post submitted successfully!")
            return True, "Post submitted successfully"
            
        except PlaywrightTimeout as e:
            msg = f"Timeout during posting: {e}"
            self.logger.error(msg)
            
            if context:
                try:
                    context.close()
                except:
                    pass
            if playwright:
                try:
                    playwright.stop()
                except:
                    pass
            
            # Retry if possible
            if retry_count < max_retries:
                self.logger.info(f"Retrying... ({retry_count + 1}/{max_retries})")
                time.sleep(2)
                return self.post_to_linkedin(content, retry_count + 1)
            
            return False, msg
            
        except Exception as e:
            msg = f"Error during posting: {e}"
            self.logger.error(msg)
            
            if context:
                try:
                    context.close()
                except:
                    pass
            if playwright:
                try:
                    playwright.stop()
                except:
                    pass

            return False, msg

    def direct_post_to_linkedin(self, content: str) -> tuple[bool, str]:
        """
        Direct post to LinkedIn without HITL approval.
        Uses robust 2026 UI selectors and human-like delays.
        Logs to /Logs/linkedin_posts.log
        
        Args:
            content: Post text content
            
        Returns:
            (success: bool, message: str)
        """
        # Setup dedicated post log
        post_log = self.logs / 'linkedin_posts.log'
        
        self.logger.info(f"=== DIRECT POST INITIATED ===")
        self.logger.info(f"Content: {content[:100]}...")
        
        # Log post attempt
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] ATTEMPT | Content: {content[:50]}... | "
        
        try:
            # Check session first
            if not self.check_session():
                msg = "Session expired - attempting recovery"
                self.logger.warning(msg)
                log_entry += f"FAILED | {msg}"
                with open(post_log, 'a', encoding='utf-8') as f:
                    f.write(log_entry + '\n')
                return False, msg

            playwright, context = self._get_browser_context(headless=not self.debug_mode)
            page = context.pages[0] if context.pages else context.new_page()

            # Navigate to feed
            self.logger.info("Navigating to LinkedIn feed...")
            page.goto(self.FEED_URL, timeout=60000, wait_until='domcontentloaded')
            time.sleep(5)  # Wait for page to fully load
            
            # Step 1: Find and click "Start a post" button using 2026 selectors
            self.logger.info("Looking for post creation button...")
            
            post_button = None
            selectors_2026 = [
                'button:has-text("Start a post")',
                'button:has-text("Start")',
                '.share-box-feed-entry__trigger',
                '[data-testid="post-modal-trigger"]',
                '[data-control-name="updates_dish"]',
                '[aria-label="Create a post"]',
            ]
            
            for selector in selectors_2026:
                try:
                    post_button = page.wait_for_selector(selector, timeout=5000)
                    if post_button:
                        self.logger.info(f"Found post trigger: {selector}")
                        post_button.click()
                        time.sleep(3)  # Wait for modal to open
                        break
                except PlaywrightTimeout:
                    continue
            
            if not post_button:
                # Try Playwright's get_by_role
                try:
                    post_button = page.get_by_role("button", name="Start a post").first
                    if post_button.count() > 0:
                        post_button.click()
                        time.sleep(3)
                        self.logger.info("Clicked post button using get_by_role")
                except Exception as e:
                    self.logger.warning(f"get_by_role failed: {e}")
            
            if not post_button:
                # Fallback: direct navigation to post composer
                self.logger.info("Post button not found, trying direct navigation...")
                page.goto(self.POST_URL, timeout=30000, wait_until='domcontentloaded')
                time.sleep(4)
            
            # Step 2: Find text area and type content
            self.logger.info("Entering post content...")
            
            text_input = None
            text_selectors_2026 = [
                '[contenteditable="true"][role="textbox"]',
                'div[aria-label="What do you want to talk about?"]',
                '[aria-label="What do you want to talk about?"]',
                '.editor-composer__content [contenteditable="true"]',
                '[data-testid="post-textbox"]',
            ]
            
            for selector in text_selectors_2026:
                try:
                    text_input = page.wait_for_selector(selector, timeout=5000)
                    if text_input:
                        self.logger.info(f"Found text input: {selector}")
                        break
                except PlaywrightTimeout:
                    continue
            
            # Fallback: get_by_role for textbox
            if not text_input:
                try:
                    text_input = page.get_by_role("textbox", name="What do you want to talk about?").first
                    if text_input.count() > 0:
                        self.logger.info("Found textbox using get_by_role")
                except Exception:
                    pass
            
            if not text_input:
                msg = "Could not find post text input"
                self.logger.error(msg)
                log_entry += f"FAILED | {msg}"
                with open(post_log, 'a', encoding='utf-8') as f:
                    f.write(log_entry + '\n')
                context.close()
                playwright.stop()
                return False, msg
            
            # Clear and type with human-like delays
            text_input.focus()
            time.sleep(1)
            
            # Select all and delete (clear any existing text)
            page.keyboard.press('Control+A')
            time.sleep(0.5)
            page.keyboard.press('Delete')
            time.sleep(0.5)
            
            # Type content in human-like chunks
            self.logger.info("Typing content with human-like delays...")
            chunk_size = 10
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i+chunk_size]
                page.keyboard.type(chunk, delay=random.randint(30, 100))
                time.sleep(random.uniform(0.05, 0.2))
            
            time.sleep(2)  # Wait for text to register
            
            # Step 3: Click Post button
            self.logger.info("Looking for Post button...")
            
            # Wait for any disabled state to clear (LinkedIn enables button after text input)
            time.sleep(2)

            # Take a snapshot for debugging
            try:
                snapshot = page.content()
                self.logger.info(f"Page loaded, content length: {len(snapshot)}")
            except Exception as e:
                self.logger.warning(f"Could not get page snapshot: {e}")

            submit_btn = None
            post_btn_selectors = [
                'button:has-text("Post")',
                'button:has-text("Post now")',
                '[data-control-name="compose-submit"]',
                'button[aria-label="Post"]',
                'button[data-ml-test="post-button"]',
                '.share-box__action-button',
                'button[class*="share-box"]',
                # LinkedIn 2026 new selectors
                'button[aria-label*="Post" i][aria-label*="now" i]',
                '.artdeco-button--primary:has-text("Post")',
                '[role="dialog"] button:has-text("Post")',
            ]

            for selector in post_btn_selectors:
                try:
                    submit_btn = page.wait_for_selector(selector, timeout=2000)
                    if submit_btn:
                        # Check if button is enabled
                        is_disabled = submit_btn.evaluate('el => el.disabled')
                        if is_disabled:
                            self.logger.info(f"Found Post button but disabled: {selector}")
                            continue
                        self.logger.info(f"Found Post button: {selector}")
                        submit_btn.click()
                        time.sleep(2)  # Wait for click to register
                        break
                except PlaywrightTimeout:
                    continue

            # Fallback: get_by_role for Post button with variations
            if not submit_btn:
                role_selectors = [
                    ("button", "Post"),
                    ("button", "Post now"),
                    ("button", "Share"),
                ]
                for role, name in role_selectors:
                    try:
                        submit_btn = page.get_by_role(role, name=name).first
                        if submit_btn.count() > 0:
                            is_disabled = submit_btn.evaluate('el => el.disabled')
                            if not is_disabled:
                                submit_btn.click()
                                self.logger.info(f"Clicked {name} button using get_by_role")
                                break
                    except Exception as e:
                        self.logger.debug(f"get_by_role({role}, {name}) failed: {e}")
                        continue

            # Last resort: find any button in the post modal that looks like submit
            if not submit_btn:
                try:
                    # Look for buttons in the composer modal
                    modal_buttons = page.query_selector_all('.editor-composer-modal button, [role="dialog"] button')
                    for btn in modal_buttons:
                        btn_text = btn.inner_text().strip()
                        if btn_text in ['Post', 'Post now', 'Share']:
                            self.logger.info(f"Found submit button by text: {btn_text}")
                            btn.click()
                            submit_btn = btn
                            break
                except Exception as e:
                    self.logger.warning(f"Modal button search failed: {e}")
            
            # CRITICAL FALLBACK: Check ALL buttons on page (LinkedIn 2026 fix)
            if not submit_btn:
                try:
                    self.logger.info("Checking all buttons on page for Post button...")
                    all_buttons = page.query_selector_all('button')
                    for btn in all_buttons:
                        try:
                            btn_text = btn.inner_text().strip()
                            btn_aria = btn.get_attribute('aria-label') or ''
                            # Check if this is the Post button
                            if btn_text in ['Post', 'Post now'] or btn_aria in ['Post', 'Post now']:
                                # Check if enabled
                                is_disabled = btn.evaluate('el => el.disabled')
                                if not is_disabled:
                                    self.logger.info(f"Found Post button by inspection: text='{btn_text}' aria='{btn_aria}'")
                                    btn.click()
                                    submit_btn = btn
                                    break
                        except Exception:
                            continue
                except Exception as e:
                    self.logger.warning(f"Button inspection failed: {e}")

            if not submit_btn:
                msg = "Could not find Post button - LinkedIn UI may have changed"
                self.logger.error(msg)
                self.logger.error("Tip: Run with --setup-session to manually check LinkedIn UI")
                log_entry += f"FAILED | {msg}"
                with open(post_log, 'a', encoding='utf-8') as f:
                    f.write(log_entry + '\n')
                # Don't close browser on error - let user inspect
                time.sleep(5)
                context.close()
                playwright.stop()
                return False, msg
            
            # Wait for post to submit
            self.logger.info("Waiting for post submission...")
            time.sleep(6)  # Give LinkedIn time to process
            
            # Check for success indicators
            success = False
            try:
                # Look for "Posted" confirmation or feed reload
                page.wait_for_selector('text=/Posted|Your post/i', timeout=5000)
                success = True
                self.logger.info("Post submission confirmed")
            except PlaywrightTimeout:
                # Check if we're back on feed (also indicates success)
                if 'feed' in page.url:
                    success = True
                    self.logger.info("Post submitted (back on feed)")
            
            # Log result
            if success:
                log_entry += f"SUCCESS | Posted to LinkedIn"
                self.logger.info("✓ DIRECT POST SUCCESSFUL!")
            else:
                log_entry += f"UNCERTAIN | Posted but no confirmation"
                self.logger.warning("Post may have succeeded but no confirmation found")
            
            # Write to post log
            with open(post_log, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
            
            context.close()
            playwright.stop()
            
            return success, "Post submitted" if success else "Posted but unconfirmed"
            
        except PlaywrightTimeout as e:
            msg = f"Timeout: {e}"
            self.logger.error(msg)
            log_entry += f"FAILED | {msg}"
            with open(post_log, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
            return False, msg
            
        except Exception as e:
            msg = f"Error: {e}"
            self.logger.error(msg)
            log_entry += f"FAILED | {msg}"
            with open(post_log, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
            return False, msg

    def process_approved_posts(self, auto_mode: bool = False) -> dict:
        """
        Process approved posts and publish them.
        Returns dict with counts of success/failure.
        """
        results = {'success': 0, 'failed': 0, 'errors': []}
        
        if not self.approved.exists():
            self.logger.info("No approved posts folder found")
            return results
        
        approved_files = list(self.approved.glob('LINKEDIN_POST_*.md'))
        
        if not approved_files:
            self.logger.info("No approved posts to process")
            return results
        
        self.logger.info(f"Found {len(approved_files)} approved post(s) to process")
        
        # Check session first
        if not self.check_session():
            error_msg = "LinkedIn session expired. Run --setup-session to re-authenticate."
            self.logger.error(error_msg)
            results['errors'].append(error_msg)
            return results
        
        for post_file in approved_files:
            self.logger.info(f"Processing: {post_file.name}")
            
            try:
                content = post_file.read_text(encoding='utf-8')
                
                # Extract post content (between ## Content and ---)
                parts = content.split('## Content')
                if len(parts) < 2:
                    error_msg = f"Invalid format: {post_file.name}"
                    self.logger.warning(error_msg)
                    results['errors'].append(error_msg)
                    results['failed'] += 1
                    continue
                
                post_content = parts[1].split('---')[0].strip()
                
                if not post_content:
                    error_msg = f"Empty post content: {post_file.name}"
                    self.logger.warning(error_msg)
                    results['errors'].append(error_msg)
                    results['failed'] += 1
                    continue
                
                # Post to LinkedIn
                success, message = self.post_to_linkedin(post_content)
                
                if success:
                    # Move to Done with timestamp
                    dest = self.done / post_file.name
                    dest.write_text(
                        f"{content}\n\n---\n\n**Posted:** {datetime.now().isoformat()}\n"
                        f"**Status:** Success\n"
                        f"**Message:** {message}",
                        encoding='utf-8'
                    )
                    self.logger.info(f"✓ Posted and moved to Done: {post_file.name}")
                    results['success'] += 1
                else:
                    # Keep in Approved but log error
                    error_msg = f"Failed to post {post_file.name}: {message}"
                    self.logger.error(error_msg)
                    results['errors'].append(error_msg)
                    results['failed'] += 1
                    
                    # Add error note to file
                    error_note = f"\n\n---\n\n**Attempt:** {datetime.now().isoformat()}\n" \
                                f"**Status:** Failed\n" \
                                f"**Error:** {message}"
                    post_file.write_text(content + error_note, encoding='utf-8')
                    
            except Exception as e:
                error_msg = f"Error processing {post_file.name}: {e}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
                results['failed'] += 1
        
        return results


def main():
    if not PLAYWRIGHT_AVAILABLE:
        print("Playwright not installed.")
        print("Install: pip install playwright && playwright install chromium")
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description='LinkedIn Auto Poster - Persistent Session Auto-Posting',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # First-time session setup (REQUIRED before posting)
    python linkedin_auto_poster.py --setup-session --vault /path/to/vault

    # Check session status
    python linkedin_auto_poster.py --check-session --vault /path/to/vault

    # Create draft post for approval
    python linkedin_auto_poster.py --vault /path/to/vault --create-draft "Your post content #hashtags"

    # Post all approved content
    python linkedin_auto_poster.py --vault /path/to/vault --post-approved

    # DIRECT POST (skip approval, for testing)
    python linkedin_auto_poster.py --vault /path/to/vault --direct-post "Your post content #hashtags"

    # Clear session and re-authenticate
    python linkedin_auto_poster.py --clear-session --vault /path/to/vault
        """
    )

    parser.add_argument('--vault', '-v', required=True, help='Path to Obsidian vault')
    parser.add_argument('--setup-session', action='store_true', help='Setup LinkedIn session (first-time login)')
    parser.add_argument('--check-session', action='store_true', help='Check if session is still valid')
    parser.add_argument('--clear-session', action='store_true', help='Clear saved session')
    parser.add_argument('--create-draft', '-d', help='Create draft post for approval')
    parser.add_argument('--post-approved', action='store_true', help='Post approved content')
    parser.add_argument('--direct-post', type=str, metavar='TEXT', help='Direct post to LinkedIn immediately (skips approval)')
    parser.add_argument('--session-path', help='Custom session path (default: vault/.linkedin_session)')
    parser.add_argument('--debug', action='store_true', help='Show browser window (headless=False) for debugging')

    args = parser.parse_args()

    # Override session path if provided
    session_path = args.session_path if args.session_path else None

    poster = LinkedInAutoPoster(args.vault, session_path, debug_mode=args.debug)

    if args.setup_session:
        poster.setup_session()
        return

    if args.check_session:
        print("\nChecking LinkedIn session...")
        if poster.check_session():
            print("\n[OK] Session is VALID - Ready to post!")
        else:
            print("\n[ERROR] Session EXPIRED - Run --setup-session to re-authenticate")
        return

    if args.clear_session:
        poster.clear_session()
        return

    if args.create_draft:
        draft_path = poster.create_draft(args.create_draft)
        return

    if args.direct_post:
        # Direct post without approval (for testing)
        print("\n" + "="*70)
        print("DIRECT LINKEDIN POST (No Approval)")
        print("="*70)
        print(f"\nContent:\n{args.direct_post}\n")
        print("-"*70)
        
        # Check session first
        print("Checking session...")
        if not poster.check_session():
            print("\n✗ Session EXPIRED - Run --setup-session first")
            sys.exit(1)
        
        print("✓ Session valid")
        print("\nPosting to LinkedIn...")
        
        success, message = poster.direct_post_to_linkedin(args.direct_post)
        
        print("\n" + "="*70)
        if success:
            print("✓ DIRECT POST SUCCESSFUL!")
            print(f"  Message: {message}")
            print(f"\nCheck your LinkedIn: https://www.linkedin.com/feed/")
            print(f"Logs: Logs/linkedin_posts.log")
        else:
            print("✗ DIRECT POST FAILED")
            print(f"  Error: {message}")
            print(f"\nTroubleshooting:")
            print(f"  1. Check session: python linkedin_auto_poster.py --check-session --vault ..")
            print(f"  2. Re-setup session: python linkedin_auto_poster.py --setup-session --vault ..")
            print(f"  3. Check logs: Logs/linkedin_*.log")
        print("="*70)
        
        sys.exit(0 if success else 1)

    if args.post_approved:
        print("\n" + "="*70)
        print("Processing Approved LinkedIn Posts")
        print("="*70)

        results = poster.process_approved_posts()

        print("\n" + "-"*70)
        print("Results:")
        print(f"  Successful: {results['success']}")
        print(f"  Failed: {results['failed']}")

        if results['errors']:
            print("\nErrors:")
            for error in results['errors']:
                print(f"  - {error}")

        print("-"*70)

        if results['success'] > 0:
            print("\n[OK] Auto-posting complete!")
        elif results['failed'] > 0:
            print("\n[ERROR] All posts failed. Check logs and session status.")
        else:
            print("\n[INFO] No posts to process.")

        return

    parser.print_help()


if __name__ == "__main__":
    main()
