#!/usr/bin/env python3
"""
Test Runner for AI Employee (Bronze Tier)

Verifies all Bronze tier components are working correctly.

Usage:
    python test_bronze_tier.py /path/to/vault
"""

import os
import sys
from pathlib import Path


def check_directory(path: Path, name: str) -> bool:
    """Check if directory exists."""
    if path.exists() and path.is_dir():
        print(f"  [OK] {name}: {path}")
        return True
    else:
        print(f"  [MISSING] {name}: {path}")
        return False


def check_file(path: Path, name: str) -> bool:
    """Check if file exists."""
    if path.exists() and path.is_file():
        print(f"  [OK] {name}: {path}")
        return True
    else:
        print(f"  [MISSING] {name}: {path}")
        return False


def check_python_dependency(package: str, import_name: str = None) -> bool:
    """Check if Python package is installed."""
    import_name = import_name or package
    try:
        __import__(import_name)
        print(f"  [OK] Python package: {package}")
        return True
    except ImportError:
        print(f"  [MISSING] Python package: {package}")
        print(f"    Install with: pip install {package}")
        return False


def check_command(command: str) -> bool:
    """Check if command is available."""
    import subprocess
    try:
        result = subprocess.run(
            [command, '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0]
            print(f"  [OK] {command}: {version}")
            return True
        else:
            print(f"  [ERROR] {command} installed but not working")
            return False
    except FileNotFoundError:
        print(f"  [NOT FOUND] {command}")
        return False
    except subprocess.TimeoutExpired:
        print(f"  [OK] {command}: installed (version check timed out)")
        return True


def run_tests(vault_path: Path):
    """Run all Bronze tier verification tests."""
    
    print("=" * 60)
    print("AI Employee - Bronze Tier Verification")
    print("=" * 60)
    print()
    
    all_passed = True
    
    # 1. Check Vault Structure
    print("1. Vault Structure")
    print("-" * 40)
    
    required_dirs = [
        'Inbox',
        'Needs_Action',
        'Plans',
        'Done',
        'Pending_Approval',
        'Approved',
        'Rejected',
        'Logs',
        'Accounting',
        'Invoices',
        'Briefings',
        'scripts'
    ]
    
    for dir_name in required_dirs:
        if not check_directory(vault_path / dir_name, dir_name):
            all_passed = False
    
    print()
    
    # 2. Check Core Files
    print("2. Core Files")
    print("-" * 40)
    
    required_files = [
        'Dashboard.md',
        'Company_Handbook.md',
        'Business_Goals.md',
        'README.md',
        'scripts/filesystem_watcher.py',
        'scripts/orchestrator.py'
    ]
    
    for file_name in required_files:
        if not check_file(vault_path / file_name, file_name):
            all_passed = False
    
    print()
    
    # 3. Check Python Dependencies
    print("3. Python Dependencies")
    print("-" * 40)

    # watchdog is optional - don't fail if missing
    check_python_dependency('watchdog')
    print("    Note: watchdog is optional (enables efficient file monitoring)")
    print("    Without it, the watcher uses polling mode")

    print()

    # 4. Check System Commands
    print("4. System Commands")
    print("-" * 40)

    if not check_command('python'):
        all_passed = False

    # Claude Code is required for full automation but optional for Bronze tier
    if not check_command('claude'):
        print("    [INFO] Claude Code CLI is required for full automation")
        print("    Install with: npm install -g @anthropic/claude-code")
        print("    For Bronze tier, you can process tasks manually in Claude Code")

    print()

    # 5. Test File System Watcher
    print("5. File System Watcher Test")
    print("-" * 40)

    test_file = vault_path / 'scripts' / 'sample_test_drop.txt'
    if test_file.exists():
        print(f"  [OK] Sample test file exists")

        # Simulate dropping file to Inbox
        inbox_test = vault_path / 'Inbox' / 'test_drop.txt'
        try:
            import shutil
            shutil.copy2(test_file, inbox_test)
            print(f"  [OK] Copied test file to Inbox/")

            # Run watcher
            print("  Running filesystem watcher...")
            sys.path.insert(0, str(vault_path / 'scripts'))
            
            # Import and run the watcher (works without watchdog)
            from filesystem_watcher import DropFolderHandler

            watcher = DropFolderHandler(str(vault_path))
            result = watcher.process_file(inbox_test)

            if result:
                print(f"  [OK] Watcher processed file: {result.name}")
            else:
                print(f"  [ERROR] Watcher failed to process file")
                all_passed = False

        except Exception as e:
            print(f"  [ERROR] Watcher test failed: {e}")
            all_passed = False
    else:
        print(f"  [MISSING] Sample test file")
        all_passed = False
    
    print()
    
    # 6. Test Orchestrator
    print("6. Orchestrator Test")
    print("-" * 40)
    
    try:
        sys.path.insert(0, str(vault_path / 'scripts'))
        from orchestrator import Orchestrator
        
        orchestrator = Orchestrator(str(vault_path))
        orchestrator.update_dashboard()
        print(f"  [OK] Orchestrator can update dashboard")
        
    except Exception as e:
        print(f"  [ERROR] Orchestrator test failed: {e}")
        all_passed = False
    
    print()
    
    # Final Summary
    print("=" * 60)
    if all_passed:
        print("[SUCCESS] ALL TESTS PASSED - Bronze Tier Ready!")
        print()
        print("Next Steps:")
        print("1. Open Dashboard.md in Obsidian")
        print("2. Drop a test file into Inbox/")
        print("3. Run: python scripts/orchestrator.py .")
        print("4. Check Needs_Action/ for processed tasks")
    else:
        print("[FAILED] SOME TESTS FAILED - Review output above")
        print()
        print("Common fixes:")
        print("- Install missing Python packages: pip install watchdog")
        print("- Create missing directories manually")
        print("- Install Claude Code: npm install -g @anthropic/claude-code")
    print("=" * 60)
    
    return all_passed


def main():
    if len(sys.argv) > 1:
        vault_path = Path(sys.argv[1])
    else:
        # Try to auto-detect vault
        vault_path = Path(__file__).parent
        if not (vault_path / 'Dashboard.md').exists():
            print("Error: Could not find vault.")
            print("Usage: python test_bronze_tier.py /path/to/vault")
            sys.exit(1)
    
    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    success = run_tests(vault_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
