#!/usr/bin/env python3
"""
Orchestrator for AI Employee (Silver Tier)

Main orchestration script that:
1. Scans Needs_Action folder for pending tasks
2. Creates Plan.md files for multi-step tasks (Silver Tier feature)
3. Triggers Qwen Code to process tasks
4. Manages approval workflow (HITL)
5. Updates Dashboard.md with current status
6. Logs all actions

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
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict


class Orchestrator:
    """Main orchestrator for AI Employee (Silver Tier)."""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans = self.vault_path / 'Plans'
        self.done = self.vault_path / 'Done'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.logs = self.vault_path / 'Logs'
        self.dashboard = self.vault_path / 'Dashboard.md'
        
        # Ensure directories exist
        for directory in [self.needs_action, self.plans, self.done,
                          self.pending_approval, self.approved, self.rejected, self.logs]:
            directory.mkdir(parents=True, exist_ok=True)
            
        # Setup logging
        log_file = self.logs / f"{datetime.now().strftime('%Y-%m-%d')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def count_files(self, directory: Path) -> int:
        """Count .md files in a directory."""
        if not directory.exists():
            return 0
        return len([f for f in directory.iterdir() if f.suffix == '.md'])
    
    def get_pending_tasks(self) -> List[Path]:
        """Get list of pending task files."""
        if not self.needs_action.exists():
            return []
        return [f for f in self.needs_action.iterdir() if f.suffix == '.md']
    
    def create_plan(self, task_file: Path) -> Path:
        """Create a Plan.md file for a task (Silver Tier feature)."""
        content = task_file.read_text(encoding='utf-8')
        
        # Extract metadata
        metadata = self.extract_frontmatter(content)
        task_type = metadata.get('type', 'general')
        priority = metadata.get('priority', 'medium')
        subject = metadata.get('subject', metadata.get('original_name', 'Task'))
        
        # Generate plan steps based on task type
        steps = self.generate_steps(task_type, content)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_subject = "".join(c if (c.isalnum() or c in '._-') else '_' for c in str(subject)[:30])
        plan_filename = f"PLAN_{safe_subject}_{timestamp}.md"
        
        plan_content = f"""---
created: {datetime.now().isoformat()}
type: plan
status: pending
objective: Process {task_type}: {subject}
priority: {priority}
source: {task_file.name}
---

# Action Plan: {subject}

## Task Type
{task_type.replace('_', ' ').title()}

## Context
- **Source File:** {task_file.name}
- **Priority:** {priority}
- **Created:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Steps

"""
        # Add steps
        for i, step in enumerate(steps, 1):
            plan_content += f"- [ ] {step}\n"
            
        plan_content += f"""
## Resources Needed
- Access to relevant systems
- Qwen Code for processing

## Blockers
None

## Notes

---
*Created by Orchestrator v0.2 (Silver Tier)*
*AI Employee - Qwen Code Brain*
"""
        
        plan_file = self.plans / plan_filename
        plan_file.write_text(plan_content, encoding='utf-8')
        
        self.logger.info(f"Created plan: {plan_filename}")
        return plan_file
        
    def generate_steps(self, task_type: str, content: str) -> List[str]:
        """Generate action steps based on task type."""
        default_steps = [
            "Read and understand task details",
            "Identify required actions",
            "Execute actions or create approval request",
            "Verify completion",
            "Move to /Done"
        ]

        if task_type == 'email':
            return [
                "Read email content thoroughly",
                "Identify sender intent and urgency",
                "Check if response is needed",
                "Draft response if required",
                "Create approval request for sending (HITL)",
                "Send email after approval",
                "Archive or move to /Done"
            ]
        elif task_type == 'whatsapp':
            return [
                "Read WhatsApp message",
                "Check for keywords (urgent, payment, etc.)",
                "Draft appropriate response",
                "Create approval request (HITL)",
                "Send via WhatsApp after approval",
                "Move to /Done"
            ]
        elif task_type in ['linkedin_message', 'linkedin_connection']:
            return [
                "Review LinkedIn notification",
                "Check sender profile if needed",
                "Draft professional response",
                "Create approval request (HITL)",
                "Send via LinkedIn after approval",
                "Move to /Done"
            ]
        elif task_type == 'linkedin_post':
            return [
                "Review LinkedIn post content",
                "Check character count and hashtags",
                "Verify content aligns with business goals",
                "Create approval request (HITL)",
                "Post to LinkedIn after approval",
                "Verify post published successfully",
                "Move to /Done"
            ]
        elif task_type == 'file_drop':
            return [
                "Review dropped file content",
                "Categorize file type and purpose",
                "Determine required action",
                "Process file accordingly",
                "Move to appropriate folder or /Done"
            ]
        elif task_type == 'approval_request':
            return [
                "Wait for human decision",
                "Check if moved to /Approved or /Rejected",
                "Execute if approved",
                "Log and move to /Done"
            ]

        return default_steps
        
    def extract_frontmatter(self, content: str) -> dict:
        """Extract metadata from frontmatter."""
        metadata = {}
        
        if not content.startswith('---'):
            return metadata
            
        lines = content.split('\n')
        in_frontmatter = False
        
        for line in lines:
            if line.strip() == '---':
                if not in_frontmatter:
                    in_frontmatter = True
                    continue
                else:
                    break
                    
            if ':' in line and in_frontmatter:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()
                
        return metadata
        
    def check_approval_workflow(self) -> int:
        """Check and process approved actions (HITL)."""
        if not self.approved.exists():
            return 0

        approved_files = [f for f in self.approved.iterdir() if f.suffix == '.md']
        processed = 0

        for approved_file in approved_files:
            try:
                self.logger.info(f"Processing approved action: {approved_file.name}")

                # Check if it's a LinkedIn post approval
                content = approved_file.read_text(encoding='utf-8')
                metadata = self.extract_frontmatter(content)
                
                if metadata.get('action') == 'linkedin_post':
                    # Execute LinkedIn post
                    if self.execute_linkedin_post(approved_file, content):
                        processed += 1
                    else:
                        self.logger.warning(f"LinkedIn post failed: {approved_file.name}")
                else:
                    # Generic approval - just move to Done
                    self.log_event('approval_executed', approved_file.name)
                    dest = self.done / approved_file.name
                    shutil.move(str(approved_file), str(dest))
                    self.logger.info(f"Moved to Done: {dest.name}")
                    processed += 1

            except Exception as e:
                self.logger.error(f"Failed to process approval: {e}")

        return processed

    def execute_linkedin_post(self, approved_file: Path, content: str) -> bool:
        """
        Execute LinkedIn post using linkedin_auto_poster.py
        Returns True if successful, False otherwise.
        """
        self.logger.info(f"Executing LinkedIn post: {approved_file.name}")
        
        try:
            # Import the poster
            sys.path.insert(0, str(self.vault_path / 'scripts'))
            from linkedin_auto_poster import LinkedInAutoPoster
            
            poster = LinkedInAutoPoster(str(self.vault_path))
            
            # Extract post content (between ## Content and ---)
            parts = content.split('## Content')
            if len(parts) < 2:
                self.logger.error(f"Invalid LinkedIn post format: {approved_file.name}")
                return False
            
            post_content = parts[1].split('---')[0].strip()
            
            if not post_content:
                self.logger.error(f"Empty post content: {approved_file.name}")
                return False
            
            # Post to LinkedIn
            success, message = poster.post_to_linkedin(post_content)
            
            if success:
                # Move to Done with timestamp
                dest = self.done / approved_file.name
                dest.write_text(
                    f"{content}\n\n---\n\n**Posted:** {datetime.now().isoformat()}\n"
                    f"**Status:** Success\n"
                    f"**Message:** {message}",
                    encoding='utf-8'
                )
                self.logger.info(f"✓ LinkedIn post successful: {approved_file.name}")
                self.log_event('linkedin_post_success', approved_file.name)
                return True
            else:
                # Log error
                self.logger.error(f"LinkedIn post failed: {message}")
                self.log_event('linkedin_post_failed', f"{approved_file.name}: {message}")
                
                # Add error note to file
                error_note = f"\n\n---\n\n**Attempt:** {datetime.now().isoformat()}\n" \
                            f"**Status:** Failed\n" \
                            f"**Error:** {message}"
                approved_file.write_text(content + error_note, encoding='utf-8')
                return False
                
        except ImportError:
            self.logger.error("linkedin_auto_poster.py not found in scripts/")
            self.log_event('linkedin_post_error', 'Module not found')
            return False
        except Exception as e:
            self.logger.error(f"Error executing LinkedIn post: {e}")
            self.log_event('linkedin_post_error', str(e))
            return False
        
    def check_expired_approvals(self) -> int:
        """Move expired approvals to Rejected."""
        if not self.pending_approval.exists():
            return 0
            
        now = datetime.now()
        expired = 0
        
        for approval_file in self.pending_approval.glob('*.md'):
            content = approval_file.read_text(encoding='utf-8')
            metadata = self.extract_frontmatter(content)
            
            expires_str = metadata.get('expires')
            if expires_str:
                try:
                    expires = datetime.fromisoformat(expires_str)
                    if expires < now:
                        # Add expiration notice
                        content += f"\n\n**EXPIRED:** {expires_str}"
                        approval_file.write_text(content, encoding='utf-8')
                        
                        # Move to Rejected
                        dest = self.rejected / approval_file.name
                        shutil.move(str(approval_file), str(dest))
                        
                        self.logger.info(f"Expired approval moved to Rejected: {approval_file.name}")
                        self.log_event('approval_expired', approval_file.name)
                        expired += 1
                        
                except ValueError:
                    pass
                    
        return expired
        
    def update_dashboard(self):
        """Update Dashboard.md with current status."""
        if not self.dashboard.exists():
            self.logger.warning("Dashboard.md not found")
            return
            
        # Count files in each folder
        pending_count = self.count_files(self.needs_action)
        plans_count = self.count_files(self.plans)
        approval_count = self.count_files(self.pending_approval)
        approved_count = self.count_files(self.approved)
        done_count = self.count_files(self.done)
        
        # Read current dashboard
        content = self.dashboard.read_text(encoding='utf-8')
        
        # Update timestamp
        timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        if 'last_updated:' in content:
            content = content.replace(
                content.split('last_updated:')[1].split('\n')[0].strip(),
                timestamp
            )
        else:
            # Add last_updated if not present
            content = f"---\nlast_updated: {timestamp}\n---\n" + content
        
        # Update stats
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if '| Pending Tasks |' in line:
                new_lines.append(f'| Pending Tasks | {pending_count} |')
            elif '| Awaiting Approval |' in line:
                new_lines.append(f'| Awaiting Approval | {approval_count + approved_count} |')
            elif '| Completed Today |' in line:
                new_lines.append(f'| Completed Today | {done_count} |')
            elif '| Active Plans |' in line:
                new_lines.append(f'| Active Plans | {plans_count} |')
            else:
                new_lines.append(line)
                
        self.dashboard.write_text('\n'.join(new_lines), encoding='utf-8')
        self.logger.info(f"Dashboard updated: {pending_count} pending, {plans_count} plans, {approval_count} awaiting approval")
        
    def process_tasks(self) -> bool:
        """Process pending tasks and create plans."""
        pending_tasks = self.get_pending_tasks()
        
        if not pending_tasks:
            self.logger.info("No pending tasks to process")
            return False
            
        self.logger.info(f"Found {len(pending_tasks)} pending task(s)")
        
        # Create plans for each task
        for task_file in pending_tasks:
            try:
                plan_file = self.create_plan(task_file)
                self.logger.info(f"Created plan for: {task_file.name}")
            except Exception as e:
                self.logger.error(f"Failed to create plan for {task_file.name}: {e}")
                
        return True
        
    def log_event(self, event_type: str, details: str):
        """Log an event to the logs folder."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event': event_type,
            'details': details
        }
        
        log_file = self.logs / f"{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
            
    def run_cycle(self):
        """Run one complete orchestration cycle (Silver Tier)."""
        self.logger.info("Starting Silver Tier orchestration cycle")
        
        try:
            # Step 1: Check for expired approvals
            expired = self.check_expired_approvals()
            if expired:
                self.logger.info(f"Processed {expired} expired approval(s)")
            
            # Step 2: Process pending tasks and create plans
            self.process_tasks()
            
            # Step 3: Check and execute approved actions (HITL)
            approved = self.check_approval_workflow()
            if approved:
                self.logger.info(f"Executed {approved} approved action(s)")
            
            # Step 4: Update dashboard
            self.update_dashboard()
            
            self.logger.info("Orchestration cycle complete")
            
        except Exception as e:
            self.logger.error(f"Error in orchestration cycle: {e}")
            
    def run_continuous(self, check_interval: int = 60):
        """Run orchestrator continuously."""
        self.logger.info(f"Starting Orchestrator (interval: {check_interval}s)")
        self.logger.info(f"Vault: {self.vault_path}")
        
        print("\n" + "="*60)
        print("AI Employee Orchestrator (Silver Tier)")
        print("="*60)
        print(f"Vault: {self.vault_path}")
        print(f"Interval: {check_interval} seconds")
        print("Press Ctrl+C to stop")
        print("="*60 + "\n")
        
        while True:
            try:
                self.run_cycle()
            except Exception as e:
                self.logger.error(f"Error in cycle: {e}")
                
            time.sleep(check_interval)


def main():
    parser = argparse.ArgumentParser(
        description='AI Employee Orchestrator (Silver Tier)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # One-time processing cycle
    python orchestrator.py /path/to/vault
    
    # Continuous operation (every 60 seconds)
    python orchestrator.py /path/to/vault --continuous --interval 60
    
    # With verbose logging
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
        # Try to auto-detect
        possible_vaults = list(Path('.').glob('*/Dashboard.md'))
        if possible_vaults:
            vault_path = str(possible_vaults[0].parent)
            print(f"Auto-detected vault: {vault_path}")
        else:
            print("Error: Vault path required")
            print("\nUsage: python orchestrator.py /path/to/vault")
            print("       python orchestrator.py --vault /path/to/vault")
            sys.exit(1)
    
    # Create orchestrator
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    orchestrator = Orchestrator(vault_path)
    
    if args.continuous:
        orchestrator.run_continuous(args.interval)
    else:
        orchestrator.run_cycle()
        print("\n" + "-"*60)
        print("✓ Orchestration cycle complete")
        print(f"✓ Check {orchestrator.logs} for details")
        print("-"*60)


if __name__ == "__main__":
    main()
