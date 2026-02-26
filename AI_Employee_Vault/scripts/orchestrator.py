#!/usr/bin/env python3
"""
Orchestrator for AI Employee (Bronze Tier)

Main orchestration script that:
1. Scans Needs_Action folder for pending tasks
2. Triggers Qwen Code to process tasks
3. Updates Dashboard.md with current status
4. Logs all actions

Usage:
    python orchestrator.py /path/to/vault

Or for continuous operation:
    python orchestrator.py /path/to/vault --continuous --interval 60
"""

import argparse
import json
import logging
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional


class Orchestrator:
    """Main orchestrator for AI Employee."""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans = self.vault_path / 'Plans'
        self.done = self.vault_path / 'Done'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.logs = self.vault_path / 'Logs'
        self.dashboard = self.vault_path / 'Dashboard.md'
        
        # Ensure directories exist
        for directory in [self.needs_action, self.plans, self.done, 
                          self.pending_approval, self.approved, self.logs]:
            directory.mkdir(parents=True, exist_ok=True)
            
        # Setup logging
        log_file = self.logs / f"{datetime.now().strftime('%Y-%m-%d')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def count_files(self, directory: Path) -> int:
        """Count .md files in a directory."""
        if not directory.exists():
            return 0
        return len([f for f in directory.iterdir() if f.suffix == '.md'])
    
    def get_pending_tasks(self) -> list:
        """Get list of pending task files."""
        if not self.needs_action.exists():
            return []
        return [f for f in self.needs_action.iterdir() if f.suffix == '.md']
    
    def update_dashboard(self):
        """Update Dashboard.md with current status."""
        if not self.dashboard.exists():
            self.logger.warning("Dashboard.md not found")
            return

        # Count files in each folder
        pending_count = self.count_files(self.needs_action)
        approval_count = self.count_files(self.pending_approval)
        done_count = self.count_files(self.done)

        # Read current dashboard with UTF-8 encoding
        content = self.dashboard.read_text(encoding='utf-8')

        # Update timestamp
        timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        content = content.replace(
            'last_updated: 2026-02-26T00:00:00Z',
            f'last_updated: {timestamp}'
        )

        # Update stats (simple replacement for Bronze tier)
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if line.strip().startswith('| Pending Tasks |'):
                new_lines.append(f'| Pending Tasks | {pending_count} |')
            elif line.strip().startswith('| Awaiting Approval |'):
                new_lines.append(f'| Awaiting Approval | {approval_count} |')
            elif line.strip().startswith('| Completed Today |'):
                new_lines.append(f'| Completed Today | {done_count} |')
            else:
                new_lines.append(line)

        self.dashboard.write_text('\n'.join(new_lines), encoding='utf-8')
        self.logger.info(f"Dashboard updated: {pending_count} pending, {approval_count} awaiting approval")
    
    def process_tasks_with_qwen(self) -> bool:
        """
        Process pending tasks using Qwen Code.

        For Bronze tier, this creates a summary prompt for Qwen to process.
        In a real implementation, you would call Qwen Code API or CLI.
        """
        pending_tasks = self.get_pending_tasks()

        if not pending_tasks:
            self.logger.info("No pending tasks to process")
            return False

        self.logger.info(f"Found {len(pending_tasks)} pending task(s)")

        # Read all pending tasks
        task_contents = []
        for task_file in pending_tasks:
            content = task_file.read_text()
            task_contents.append(f"### {task_file.name}\n\n{content}\n")

        # Create a processing prompt for Qwen
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        plan_file = self.plans / f"PLAN_batch_{timestamp}.md"

        prompt = f"""---
created: {datetime.now().isoformat()}
type: batch_processing
status: pending
tasks_count: {len(pending_tasks)}
---

# Batch Task Processing

## Tasks to Process

{''.join(task_contents)}

## Instructions for Qwen Code

Run the following command to process these tasks:

```bash
qwen "Review all files in /Needs_Action folder. For each task:
1. Read the task file and understand what's needed
2. Create a plan for how to handle it
3. If approval is needed, create a file in /Pending_Approval
4. If no approval needed, complete the task and move to /Done
5. Update Dashboard.md with progress

Refer to Company_Handbook.md for rules and guidelines."
```

## Status
- [ ] Tasks reviewed
- [ ] Plans created
- [ ] Approvals requested (if needed)
- [ ] Tasks completed

---
*Created by Orchestrator v0.1*
"""

        plan_file.write_text(prompt)
        self.logger.info(f"Created processing plan: {plan_file.name}")

        # For Bronze tier, we just create the plan file
        # In Silver/Gold tier, you would actually invoke Qwen here
        # Example (requires qwen-code CLI):
        # self.invoke_qwen(plan_file)

        return True

    def invoke_qwen(self, plan_file: Path):
        """
        Invoke Qwen Code to process tasks.

        This is a placeholder for Bronze tier.
        In production, you would:
        1. Check if qwen-code CLI is installed
        2. Build the appropriate prompt
        3. Execute and capture output
        4. Handle errors gracefully
        """
        try:
            # Check if qwen-code is available
            result = subprocess.run(
                ['qwen', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                self.logger.info("Qwen Code CLI found")
                # Build and execute Qwen command
                # This is a simplified example
                prompt = f"Process tasks defined in {plan_file}"
                # subprocess.run(['qwen', prompt], timeout=300)
            else:
                self.logger.warning("Qwen Code CLI not available - plan file created for manual processing")

        except FileNotFoundError:
            self.logger.warning("Qwen Code CLI not installed - plan file created for manual processing")
        except subprocess.TimeoutExpired:
            self.logger.error("Qwen Code execution timed out")
        except Exception as e:
            self.logger.error(f"Error invoking Qwen Code: {e}")
    
    def check_approvals(self):
        """Check for approved actions and execute them."""
        if not self.approved.exists():
            return
            
        approved_files = [f for f in self.approved.iterdir() if f.suffix == '.md']
        
        for approved_file in approved_files:
            self.logger.info(f"Processing approved action: {approved_file.name}")
            # For Bronze tier, just log and move to Done
            # In Silver/Gold tier, execute the actual action via MCP
            
            # Move to Done
            dest = self.done / approved_file.name
            shutil.move(str(approved_file), str(dest))
            self.logger.info(f"Moved to Done: {dest.name}")
    
    def run_cycle(self):
        """Run one complete orchestration cycle."""
        self.logger.info("Starting orchestration cycle")

        try:
            # Step 1: Process pending tasks
            self.process_tasks_with_qwen()

            # Step 2: Check and execute approvals
            self.check_approvals()

            # Step 3: Update dashboard
            self.update_dashboard()

            self.logger.info("Orchestration cycle complete")

        except Exception as e:
            self.logger.error(f"Error in orchestration cycle: {e}")
    
    def run_continuous(self, check_interval: int = 60):
        """Run orchestrator continuously."""
        self.logger.info(f"Starting Orchestrator (interval: {check_interval}s)")
        self.logger.info(f"Vault: {self.vault_path}")
        
        while True:
            try:
                self.run_cycle()
            except Exception as e:
                self.logger.error(f"Error in cycle: {e}")
            
            time.sleep(check_interval)


def main():
    import time  # Import here for continuous mode
    
    parser = argparse.ArgumentParser(
        description='AI Employee Orchestrator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # One-time processing cycle
    python orchestrator.py /path/to/vault
    
    # Continuous operation
    python orchestrator.py /path/to/vault --continuous --interval 60
    
    # With custom log level
    python orchestrator.py /path/to/vault --verbose
        """
    )
    
    parser.add_argument('vault', nargs='?', help='Path to Obsidian vault')
    parser.add_argument('--vault', '-v', dest='vault_opt', help='Path to Obsidian vault (named)')
    parser.add_argument('--continuous', '-c', action='store_true', help='Run continuously')
    parser.add_argument('--interval', '-i', type=int, default=60, help='Check interval in seconds')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
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
    
    # Create orchestrator
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    orchestrator = Orchestrator(vault_path)
    
    if args.continuous:
        orchestrator.run_continuous(args.interval)
    else:
        orchestrator.run_cycle()
        print("Orchestration cycle complete. Check logs for details.")


if __name__ == "__main__":
    main()
