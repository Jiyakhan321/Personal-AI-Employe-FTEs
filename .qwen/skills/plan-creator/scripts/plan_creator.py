#!/usr/bin/env python3
"""
Plan Creator for AI Employee (Silver Tier)

Creates structured Plan.md files for multi-step task processing.
Used by orchestrator to track AI reasoning progress.

Usage:
    python plan_creator.py --vault /path/to/vault --create "Plan objective"
"""

import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional


class PlanCreator:
    """Create and manage action plans."""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.plans_folder = self.vault_path / 'Plans'
        
        # Ensure folder exists
        self.plans_folder.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def create_plan(self, objective: str, source_file: str = None,
                    steps: List[str] = None, priority: str = 'medium',
                    context: dict = None) -> Path:
        """Create a new action plan."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_objective = "".join(c if c.isalnum() else '_' for c in objective[:30])
        filename = f"PLAN_{safe_objective}_{timestamp}.md"
        
        # Default steps if none provided
        if not steps:
            steps = [
                "Review task details",
                "Identify required actions",
                "Execute actions",
                "Verify completion",
                "Move to /Done"
            ]
            
        # Build plan content
        content = f"""---
created: {datetime.now().isoformat()}
type: plan
status: pending
objective: {objective}
priority: {priority}
"""
        if source_file:
            content += f"source: {source_file}\n"
        content += "---\n\n"
        
        content += f"# Action Plan: {objective}\n\n"
        
        if context:
            content += "## Context\n\n"
            for key, value in context.items():
                content += f"- **{key}:** {value}\n"
            content += "\n"
            
        content += "## Steps\n\n"
        for i, step in enumerate(steps, 1):
            content += f"- [ ] {step}\n"
            
        content += "\n## Resources Needed\nNone\n"
        content += "\n## Blockers\nNone\n"
        content += "\n## Notes\n\n---\n"
        content += "*Created by Plan Creator v0.1 (Silver Tier)*\n"
        
        filepath = self.plans_folder / filename
        filepath.write_text(content, encoding='utf-8')
        
        self.logger.info(f"Created plan: {filename}")
        return filepath
        
    def update_step(self, plan_file: Path, step_number: int, completed: bool) -> bool:
        """Update a step's completion status."""
        try:
            content = plan_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Find steps section
            in_steps = False
            step_count = 0
            
            for i, line in enumerate(lines):
                if '## Steps' in line:
                    in_steps = True
                    continue
                elif line.startswith('## ') and in_steps:
                    break
                    
                if in_steps and line.strip().startswith('- ['):
                    step_count += 1
                    if step_count == step_number:
                        if completed:
                            lines[i] = line.replace('- [ ]', '- [x]')
                        else:
                            lines[i] = line.replace('- [x]', '- [ ]')
                        break
                        
            plan_file.write_text('\n'.join(lines), encoding='utf-8')
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update step: {e}")
            return False
            
    def set_status(self, plan_file: Path, status: str) -> bool:
        """Update plan status."""
        try:
            content = plan_file.read_text(encoding='utf-8')
            
            # Update status in frontmatter
            if 'status: pending' in content:
                content = content.replace('status: pending', f'status: {status}')
            elif 'status: in_progress' in content:
                content = content.replace('status: in_progress', f'status: {status}')
            elif 'status: blocked' in content:
                content = content.replace('status: blocked', f'status: {status}')
            elif 'status: completed' in content:
                content = content.replace('status: completed', f'status: {status}')
                
            plan_file.write_text(content, encoding='utf-8')
            self.logger.info(f"Set status to: {status}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update status: {e}")
            return False
            
    def complete_plan(self, plan_file: Path, notes: str = None) -> bool:
        """Mark plan as completed."""
        try:
            # Set all steps as completed
            content = plan_file.read_text(encoding='utf-8')
            content = content.replace('- [ ]', '- [x]')
            
            # Add completion timestamp
            if notes:
                content = content.replace(
                    '*Created by Plan Creator v0.1*',
                    f'*Created by Plan Creator v0.1*\n\n**Completed:** {datetime.now().isoformat()}\n\n**Notes:** {notes}'
                )
            else:
                content = content.replace(
                    '*Created by Plan Creator v0.1*',
                    f'*Created by Plan Creator v0.1*\n\n**Completed:** {datetime.now().isoformat()}'
                )
                
            # Update status
            content = content.replace('status: in_progress', 'status: completed')
            content = content.replace('status: pending', 'status: completed')
            
            plan_file.write_text(content, encoding='utf-8')
            self.logger.info(f"Completed plan: {plan_file.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to complete plan: {e}")
            return False
            
    def get_active_plans(self) -> List[Path]:
        """Get all active (non-completed) plans."""
        if not self.plans_folder.exists():
            return []
            
        active = []
        for plan_file in self.plans_folder.glob('*.md'):
            content = plan_file.read_text(encoding='utf-8')
            if 'status: completed' not in content and 'status: cancelled' not in content:
                active.append(plan_file)
                
        return active
        
    def get_plan_status(self, plan_file: Path) -> dict:
        """Get plan status summary."""
        content = plan_file.read_text(encoding='utf-8')
        
        # Extract metadata
        status = 'unknown'
        objective = ''
        total_steps = 0
        completed_steps = 0
        
        lines = content.split('\n')
        in_frontmatter = False
        in_steps = False
        
        for line in lines:
            if line.strip() == '---':
                if not in_frontmatter:
                    in_frontmatter = True
                    continue
                else:
                    in_frontmatter = False
                    continue
                    
            if in_frontmatter:
                if line.startswith('status:'):
                    status = line.split(':')[1].strip()
                elif line.startswith('objective:'):
                    objective = line.split(':')[1].strip()
                    
            if '## Steps' in line:
                in_steps = True
                continue
                
            if in_steps and line.strip().startswith('- ['):
                total_steps += 1
                if '- [x]' in line:
                    completed_steps += 1
                    
        return {
            'file': plan_file.name,
            'status': status,
            'objective': objective,
            'total_steps': total_steps,
            'completed_steps': completed_steps,
            'progress': f"{completed_steps}/{total_steps}"
        }


def main():
    parser = argparse.ArgumentParser(description='Plan Creator')
    parser.add_argument('--vault', '-v', required=True, help='Path to Obsidian vault')
    parser.add_argument('--create', '-c', help='Create new plan with objective')
    parser.add_argument('--steps', '-s', nargs='+', help='Plan steps')
    parser.add_argument('--priority', '-p', default='medium', help='Priority level')
    parser.add_argument('--status', action='store_true', help='Show active plans status')
    
    args = parser.parse_args()
    
    creator = PlanCreator(args.vault)
    
    if args.create:
        plan_path = creator.create_plan(
            objective=args.create,
            steps=args.steps,
            priority=args.priority
        )
        print(f"Plan created: {plan_path.name}")
        
    elif args.status:
        active_plans = creator.get_active_plans()
        if active_plans:
            print(f"Active Plans ({len(active_plans)}):")
            for plan in active_plans:
                status = creator.get_plan_status(plan)
                print(f"  - {status['file']}: {status['progress']} steps")
        else:
            print("No active plans")
            
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
