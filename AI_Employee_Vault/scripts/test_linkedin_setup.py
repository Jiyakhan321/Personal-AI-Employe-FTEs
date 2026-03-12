#!/usr/bin/env python3
"""
LinkedIn Auto-Poster - Installation Test & Setup Wizard

This script verifies all components are ready and guides through first-time setup.

Usage:
    python test_linkedin_setup.py /path/to/vault
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime


def print_header(text: str):
    """Print formatted header."""
    print("\n" + "="*70)
    print(f" {text}")
    print("="*70 + "\n")


def print_success(text: str):
    """Print success message."""
    print(f"[OK] {text}")


def print_error(text: str):
    """Print error message."""
    print(f"[ERROR] {text}")


def print_warning(text: str):
    """Print warning message."""
    print(f"[WARN] {text}")


def check_python_version() -> bool:
    """Check Python version."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} installed")
        return True
    else:
        print_error(f"Python 3.10+ required, found {version.major}.{version.minor}")
        return False


def check_playwright() -> bool:
    """Check if Playwright is installed."""
    try:
        import playwright
        print_success("Playwright installed")
        return True
    except ImportError:
        print_error("Playwright not installed")
        print("\nInstall with:")
        print("  pip install playwright")
        print("  playwright install chromium")
        return False


def check_chromium() -> bool:
    """Check if Chromium browser is installed."""
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            # Try to launch
            browser = p.chromium.launch()
            browser.close()
        
        print_success("Chromium browser installed")
        return True
    except Exception as e:
        print_error("Chromium browser not found or not working")
        print(f"\nInstall with: playwright install chromium")
        print(f"Error: {e}")
        return False


def check_vault_structure(vault_path: Path) -> bool:
    """Check if vault has required structure."""
    required_dirs = [
        'Pending_Approval',
        'Approved',
        'Done',
        'Logs',
        'scripts'
    ]
    
    all_exist = True
    for dir_name in required_dirs:
        dir_path = vault_path / dir_name
        if dir_path.exists() and dir_path.is_dir():
            print_success(f"Directory exists: {dir_name}/")
        else:
            print_error(f"Missing directory: {dir_name}/")
            all_exist = False
    
    return all_exist


def check_linkedin_script(vault_path: Path) -> bool:
    """Check if linkedin_auto_poster.py exists."""
    script_path = vault_path / 'scripts' / 'linkedin_auto_poster.py'
    
    if script_path.exists():
        print_success(f"linkedin_auto_poster.py found")
        return True
    else:
        print_error(f"linkedin_auto_poster.py not found at {script_path}")
        return False


def test_session(vault_path: Path) -> bool:
    """Test LinkedIn session."""
    print("\nTesting LinkedIn session...")
    
    try:
        sys.path.insert(0, str(vault_path / 'scripts'))
        from linkedin_auto_poster import LinkedInAutoPoster
        
        poster = LinkedInAutoPoster(str(vault_path))
        is_valid = poster.check_session()
        
        if is_valid:
            print_success("LinkedIn session is VALID")
            return True
        else:
            print_warning("LinkedIn session EXPIRED or not found")
            return False
            
    except Exception as e:
        print_error(f"Session test failed: {e}")
        return False


def run_setup_wizard(vault_path: Path):
    """Run interactive setup wizard."""
    print_header("LinkedIn Session Setup Wizard")
    
    print("This wizard will help you log in to LinkedIn.")
    print("Your session will be saved for automatic posting.")
    print("\nInstructions:")
    print("1. A browser window will open")
    print("2. Log in to your LinkedIn account")
    print("3. Wait until you see your feed/homepage")
    print("4. The browser will close automatically")
    print("5. Session will be saved for future use")
    
    response = input("\nReady to proceed? (y/n): ").strip().lower()
    
    if response != 'y':
        print("\nSetup cancelled. Run again when ready.")
        return False
    
    print("\nStarting LinkedIn login...")
    
    try:
        sys.path.insert(0, str(vault_path / 'scripts'))
        from linkedin_auto_poster import LinkedInAutoPoster
        
        poster = LinkedInAutoPoster(str(vault_path))
        poster.setup_session()
        
        # Verify
        print("\nVerifying session...")
        time.sleep(2)
        
        if poster.check_session():
            print_success("Session setup SUCCESSFUL!")
            print("\nYou can now create and post to LinkedIn:")
            print("\n1. Create draft post:")
            print(f'   python linkedin_auto_poster.py --vault .. --create-draft "Your content"')
            print("\n2. Move draft from Pending_Approval/ to Approved/")
            print("\n3. Post:")
            print('   python linkedin_auto_poster.py --vault .. --post-approved')
            return True
        else:
            print_warning("Session setup may have failed. Try again.")
            return False
            
    except Exception as e:
        print_error(f"Setup failed: {e}")
        return False


def create_test_post(vault_path: Path) -> Path:
    """Create a test draft post."""
    print("\nCreating test draft post...")
    
    try:
        sys.path.insert(0, str(vault_path / 'scripts'))
        from linkedin_auto_poster import LinkedInAutoPoster
        
        poster = LinkedInAutoPoster(str(vault_path))
        
        test_content = "Test auto post from AI Employee Hackathon project! 🚀\n\n" \
                      "Building autonomous agents with local-first AI. " \
                      "This post was created automatically to test the LinkedIn integration.\n\n" \
                      "#AIEmployee #Hackathon2026 #Panaversity #Automation #Test"
        
        draft_path = poster.create_draft(test_content, priority='low')
        
        print_success(f"Test draft created: {draft_path.name}")
        print(f"\nLocation: Pending_Approval/{draft_path.name}")
        print("\nNext steps:")
        print("1. Open the file to review content")
        print("2. Move to Approved/ folder to publish")
        print("3. Run: python linkedin_auto_poster.py --vault .. --post-approved")
        
        return draft_path
        
    except Exception as e:
        print_error(f"Failed to create test post: {e}")
        return None


def run_all_tests(vault_path: Path) -> bool:
    """Run all installation tests."""
    print_header("LinkedIn Auto-Poster - Installation Test")
    
    results = []
    
    # Test 1: Python version
    print("\n[Test 1/6] Checking Python version...")
    results.append(check_python_version())
    
    # Test 2: Playwright
    print("\n[Test 2/6] Checking Playwright...")
    results.append(check_playwright())
    
    # Test 3: Chromium
    print("\n[Test 3/6] Checking Chromium browser...")
    results.append(check_chromium())
    
    # Test 4: Vault structure
    print("\n[Test 4/6] Checking vault structure...")
    results.append(check_vault_structure(vault_path))
    
    # Test 5: Script exists
    print("\n[Test 5/6] Checking linkedin_auto_poster.py...")
    results.append(check_linkedin_script(vault_path))
    
    # Test 6: Session (optional)
    print("\n[Test 6/6] Checking LinkedIn session...")
    session_valid = test_session(vault_path)
    results.append(session_valid)  # This one is optional for first run
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(results[:-1])  # Exclude session check
    total = len(results) - 1  # Exclude session check
    
    print(f"Core Tests: {passed}/{total} passed")
    
    if session_valid:
        print("Session: [VALID] Ready to post")
    else:
        print("Session: [NOT CONFIGURED] Run setup")
    
    print("\n" + "-"*70)
    
    if passed == total:
        print_success("ALL CORE TESTS PASSED!")
        
        if not session_valid:
            print("\n" + "="*70)
            print("NEXT STEP: Setup LinkedIn Session")
            print("="*70)
            
            # Check if running interactively
            try:
                response = input("\nRun setup wizard now? (y/n): ").strip().lower()
                if response == 'y':
                    run_setup_wizard(vault_path)
                    
                    # After setup, offer to create test post
                    response2 = input("\nCreate a test draft post? (y/n): ").strip().lower()
                    if response2 == 'y':
                        create_test_post(vault_path)
            except EOFError:
                # Non-interactive mode
                print("\nRun setup wizard manually:")
                print("  python linkedin_auto_poster.py --setup-session --vault ..")
        
        return True
    else:
        print_error("SOME TESTS FAILED - Review output above")
        print("\nFix the issues and run again:")
        print("  python test_linkedin_setup.py ..")
        return False


def main():
    """Main entry point."""
    print_header("LinkedIn Auto-Poster Setup & Test")
    
    # Get vault path
    if len(sys.argv) > 1:
        vault_path = Path(sys.argv[1])
    else:
        # Try to auto-detect
        possible_vaults = list(Path('.').glob('*/Dashboard.md'))
        if possible_vaults:
            vault_path = possible_vaults[0].parent
            print(f"Auto-detected vault: {vault_path}")
        else:
            print("Error: Could not find vault.")
            print("Usage: python test_linkedin_setup.py /path/to/vault")
            sys.exit(1)
    
    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    # Run tests
    success = run_all_tests(vault_path)
    
    print("\n" + "="*70)
    print("For detailed setup guide, see:")
    print("  LINKEDIN_AUTO_POST_SETUP.md")
    print("="*70 + "\n")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
