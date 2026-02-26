#!/usr/bin/env python3
"""
File System Watcher for AI Employee (Bronze Tier)

Monitors a drop folder for new files and creates action files in Needs_Action.
This is the simplest watcher implementation for the Bronze tier.

Usage:
    python filesystem_watcher.py /path/to/vault /path/to/drop_folder

Or run continuously:
    python filesystem_watcher.py --vault /path/to/vault --drop /path/to/drop_folder --continuous
"""

import argparse
import hashlib
import logging
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

# Optional: watchdog for efficient file system monitoring
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = None
    print("Note: watchdog not installed. Using polling mode instead.")
    print("Install with: pip install watchdog")


class DropFolderHandler:
    """Handles file drops by copying to Needs_Action and creating metadata."""
    
    def __init__(self, vault_path: str, drop_path: str = None):
        self.vault_path = Path(vault_path)
        self.drop_path = Path(drop_path) if drop_path else self.vault_path / 'Inbox'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.processed_files = set()
        
        # Ensure directories exist
        self.drop_path.mkdir(parents=True, exist_ok=True)
        self.needs_action.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def get_file_hash(self, filepath: Path) -> str:
        """Generate a unique hash for a file."""
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def process_file(self, filepath: Path) -> Path:
        """Process a single dropped file."""
        if filepath.is_dir():
            return None
            
        # Skip already processed files
        file_hash = self.get_file_hash(filepath)
        if file_hash in self.processed_files:
            return None
            
        self.logger.info(f"Processing new file: {filepath.name}")
        
        # Copy file to Needs_Action
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dest_name = f"FILE_{filepath.stem}_{timestamp}{filepath.suffix}"
        dest_path = self.needs_action / dest_name
        
        try:
            shutil.copy2(filepath, dest_path)
            self.logger.info(f"Copied to: {dest_path}")
        except Exception as e:
            self.logger.error(f"Failed to copy file: {e}")
            return None
            
        # Create metadata file
        meta_path = dest_path.with_suffix('.md')
        file_size = filepath.stat().st_size
        file_type = filepath.suffix.lower()
        
        content = f"""---
type: file_drop
original_name: {filepath.name}
dropped_name: {dest_name}
size: {file_size} bytes
file_type: {file_type}
received: {datetime.now().isoformat()}
priority: medium
status: pending
---

# File Drop for Processing

**Original File:** `{filepath.name}`

**File Size:** {file_size} bytes

**File Type:** {file_type}

## Suggested Actions
- [ ] Review file content
- [ ] Categorize and file appropriately
- [ ] Take any required action
- [ ] Move to /Done when complete

---
*Created by File System Watcher v0.1*
"""
        
        try:
            meta_path.write_text(content)
            self.logger.info(f"Created metadata: {meta_path.name}")
            
            # Mark as processed
            self.processed_files.add(file_hash)
            
            # Optionally remove original from drop folder
            # filepath.unlink()  # Uncomment to auto-delete after processing
            
            return meta_path
        except Exception as e:
            self.logger.error(f"Failed to create metadata: {e}")
            return None
    
    def scan_drop_folder(self) -> list:
        """Scan drop folder for new files."""
        new_files = []
        
        if not self.drop_path.exists():
            return new_files
            
        for filepath in self.drop_path.iterdir():
            if filepath.is_file() and filepath.suffix not in ['.md', '.tmp']:
                result = self.process_file(filepath)
                if result:
                    new_files.append(result)
                    
        return new_files
    
    def run_continuous(self, check_interval: int = 30):
        """Run watcher continuously."""
        self.logger.info(f"Starting File System Watcher")
        self.logger.info(f"Monitoring: {self.drop_path}")
        self.logger.info(f"Output: {self.needs_action}")
        self.logger.info(f"Check interval: {check_interval}s")
        
        while True:
            try:
                new_files = self.scan_drop_folder()
                if new_files:
                    self.logger.info(f"Processed {len(new_files)} file(s)")
            except Exception as e:
                self.logger.error(f"Error during scan: {e}")
            
            time.sleep(check_interval)


# Watchdog-based handler (only defined if watchdog is available)
if WATCHDOG_AVAILABLE:
    class WatchdogHandler(FileSystemEventHandler):
        """Watchdog-based event handler for efficient file monitoring."""

        def __init__(self, watcher: DropFolderHandler):
            self.watcher = watcher

        def on_created(self, event):
            if event.is_directory:
                return
            filepath = Path(event.src_path)
            if filepath.parent == self.watcher.drop_path:
                # Small delay to ensure file is fully written
                time.sleep(0.5)
                self.watcher.process_file(filepath)


def main():
    parser = argparse.ArgumentParser(
        description='File System Watcher for AI Employee',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # One-time scan
    python filesystem_watcher.py /path/to/vault
    
    # Continuous monitoring with custom drop folder
    python filesystem_watcher.py --vault /path/to/vault --drop /path/to/drop --continuous
    
    # Custom check interval
    python filesystem_watcher.py /path/to/vault --interval 60
        """
    )
    
    parser.add_argument('vault', nargs='?', help='Path to Obsidian vault')
    parser.add_argument('--vault', '-v', dest='vault_opt', help='Path to Obsidian vault (named)')
    parser.add_argument('--drop', '-d', help='Path to drop folder (default: vault/Inbox)')
    parser.add_argument('--continuous', '-c', action='store_true', help='Run continuously')
    parser.add_argument('--interval', '-i', type=int, default=30, help='Check interval in seconds')
    
    args = parser.parse_args()
    
    # Get vault path
    vault_path = args.vault_opt or args.vault
    if not vault_path:
        # Try to auto-detect vault in current directory
        possible_vaults = list(Path('.').glob('*/Dashboard.md'))
        if possible_vaults:
            vault_path = possible_vaults[0].parent
            print(f"Auto-detected vault: {vault_path}")
        else:
            parser.error("Vault path required. Provide as argument or use --vault")
    
    # Create watcher
    watcher = DropFolderHandler(vault_path, args.drop)
    
    if args.continuous:
        if WATCHDOG_AVAILABLE:
            # Use watchdog for efficient monitoring
            observer = Observer()
            handler = WatchdogHandler(watcher)
            observer.schedule(handler, str(watcher.drop_path), recursive=False)
            observer.start()
            print(f"File System Watcher started (watchdog mode)")
            print(f"Monitoring: {watcher.drop_path}")
            print("Press Ctrl+C to stop...")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
                print("\nWatcher stopped")
            observer.join()
        else:
            # Fall back to polling mode
            watcher.run_continuous(args.interval)
    else:
        # One-time scan
        print("Running one-time scan...")
        new_files = watcher.scan_drop_folder()
        if new_files:
            print(f"Processed {len(new_files)} file(s):")
            for f in new_files:
                print(f"  - {f.name}")
        else:
            print("No new files found")


if __name__ == "__main__":
    main()
