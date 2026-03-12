#!/usr/bin/env python3
"""
Approval Workflow Manager for AI Employee (Silver Tier)

Manages human-in-the-loop approval requests.
Monitors Pending_Approval/, Approved/, and Rejected/ folders.

Usage:
    # One-time check
    python approval_manager.py --vault /path/to/vault

    # Continuous monitoring
    python approval_manager.py --vault /path/to/vault --continuous

    # Check expired approvals
    python approval_manager.py --vault /path/to/vault --check-expired
"""

import argparse
import json
import logging
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any


class ApprovalWorkflow:
    """Manage approval requests."""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        
        # Ensure directories exist
        for directory in [self.pending_approval, self.approved, 
                          self.rejected, self.done, self.logs]:
            directory.mkdir(parents=True, exist_ok=True)
            
        # Default expiration (24 hours)
        self.default_expiration_hours = 24
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def create_approval_request(self, action_type: str, details: Dict[str, Any],
                                 expiration_hours: int = None) -> Path:
        """Create a new approval request."""
        if expiration_hours is None:
            expiration_hours = self.default_expiration_hours
            
        now = datetime.now()
        expires = now + timedelta(hours=expiration_hours)
        timestamp = now.strftime('%Y%m%d_%H%M%S')
        
        filename = f"APPROVAL_{action_type}_{timestamp}.md"
        
        content = f"""---
type: approval_request
action: {action_type}
created: {now.isoformat()}
expires: {expires.isoformat()}
priority: {details.get('priority', 'medium')}
status: pending
---

# Approval Request

## Action Details
- **Type:** {action_type.replace('_', ' ').title()}
- **Created:** {now.strftime('%Y-%m-%d %H:%M')}
- **Expires:** {expires.strftime('%Y-%m-%d %H:%M')}

## Details

"""
        # Add details
        for key, value in details.items():
            if key != 'priority':
                content += f"- **{key.replace('_', ' ').title()}:** {value}\n"
                
        content += f"""
---

## To Approve
Move this file to `/Approved/` folder.

## To Reject
Move this file to `/Rejected/` folder and add reason.

---
*Created by Approval Workflow v0.1 (Silver Tier)*
"""
        
        filepath = self.pending_approval / filename
        filepath.write_text(content, encoding='utf-8')
        
        self.logger.info(f"Created approval request: {filename}")
        self.log_approval_event('created', action_type, filepath.name)
        
        return filepath
        
    def check_approved(self) -> list:
        """Check for approved actions and return list."""
        if not self.approved.exists():
            return []
            
        approved_files = [f for f in self.approved.iterdir() if f.suffix == '.md']
        
        if approved_files:
            self.logger.info(f"Found {len(approved_files)} approved action(s)")
            
        return approved_files
        
    def process_approved(self, approved_file: Path) -> bool:
        """Process an approved action."""
        try:
            content = approved_file.read_text(encoding='utf-8')
            
            # Extract action type from frontmatter
            action_type = self.extract_metadata(content).get('action', 'unknown')
            
            self.logger.info(f"Processing approved action: {action_type}")
            
            # Log the execution
            self.log_approval_event('executed', action_type, approved_file.name)
            
            # Move to Done
            dest = self.done / approved_file.name
            shutil.move(str(approved_file), str(dest))
            
            self.logger.info(f"Moved to Done: {dest.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to process approval: {e}")
            return False
            
    def check_expired(self) -> list:
        """Check for expired approvals and move to Rejected."""
        if not self.pending_approval.exists():
            return []
            
        now = datetime.now()
        expired = []
        
        for approval_file in self.pending_approval.glob('*.md'):
            content = approval_file.read_text(encoding='utf-8')
            metadata = self.extract_metadata(content)
            
            expires_str = metadata.get('expires')
            if expires_str:
                try:
                    expires = datetime.fromisoformat(expires_str)
                    if expires < now:
                        expired.append(approval_file)
                        
                        # Add expiration notice
                        content += f"\n\n**EXPIRED:** {expires_str}"
                        approval_file.write_text(content, encoding='utf-8')
                        
                        # Move to Rejected
                        dest = self.rejected / approval_file.name
                        shutil.move(str(approval_file), str(dest))
                        
                        self.logger.info(f"Expired approval moved to Rejected: {approval_file.name}")
                        self.log_approval_event('expired', metadata.get('action', 'unknown'), 
                                               approval_file.name)
                        
                except ValueError:
                    self.logger.warning(f"Invalid expires date in {approval_file.name}")
                    
        return expired
        
    def extract_metadata(self, content: str) -> dict:
        """Extract metadata from frontmatter."""
        metadata = {}
        
        if not content.startswith('---'):
            return metadata
            
        # Parse frontmatter
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
        
    def log_approval_event(self, event_type: str, action_type: str, filename: str):
        """Log approval event."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event': event_type,
            'action_type': action_type,
            'file': filename
        }
        
        log_file = self.logs / f"approvals_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
            
    def get_status(self) -> dict:
        """Get current approval status."""
        return {
            'pending': len(list(self.pending_approval.glob('*.md'))) if self.pending_approval.exists() else 0,
            'approved': len(list(self.approved.glob('*.md'))) if self.approved.exists() else 0,
            'rejected': len(list(self.rejected.glob('*.md'))) if self.rejected.exists() else 0,
            'done_today': len([f for f in self.done.glob('*.md') if f.stat().st_mtime > 
                              (datetime.now() - timedelta(days=1)).timestamp()]) if self.done.exists() else 0
        }
        
    def run_cycle(self):
        """Run one approval processing cycle."""
        self.logger.info("Starting approval cycle")
        
        # Check for expired approvals
        expired = self.check_expired()
        if expired:
            self.logger.info(f"Processed {len(expired)} expired approval(s)")
            
        # Process approved actions
        approved = self.check_approved()
        for approved_file in approved:
            self.process_approved(approved_file)
            
        # Log status
        status = self.get_status()
        self.logger.info(f"Status: {status['pending']} pending, {status['approved']} approved, "
                        f"{status['rejected']} rejected")


def main():
    parser = argparse.ArgumentParser(description='Approval Workflow Manager')
    parser.add_argument('--vault', '-v', required=True, help='Path to Obsidian vault')
    parser.add_argument('--continuous', '-c', action='store_true', help='Run continuously')
    parser.add_argument('--interval', '-i', type=int, default=60, help='Check interval (seconds)')
    parser.add_argument('--check-expired', action='store_true', help='Check and expire old approvals')
    parser.add_argument('--status', action='store_true', help='Show current status')
    
    args = parser.parse_args()
    
    workflow = ApprovalWorkflow(args.vault)
    
    if args.status:
        status = workflow.get_status()
        print(f"Approval Status:")
        print(f"  Pending:  {status['pending']}")
        print(f"  Approved: {status['approved']}")
        print(f"  Rejected: {status['rejected']}")
        print(f"  Done (24h): {status['done_today']}")
        return
        
    if args.check_expired:
        expired = workflow.check_expired()
        print(f"Found and processed {len(expired)} expired approval(s)")
        return
        
    if args.continuous:
        print(f"Starting Approval Workflow (interval: {args.interval}s)")
        while True:
            try:
                workflow.run_cycle()
            except Exception as e:
                print(f"Error: {e}")
            time.sleep(args.interval)
    else:
        workflow.run_cycle()
        print("Approval cycle complete")


if __name__ == "__main__":
    import time
    main()
