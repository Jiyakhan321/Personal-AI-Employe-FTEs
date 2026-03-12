#!/usr/bin/env python3
"""
Scheduler for AI Employee (Silver Tier)

Helper script for scheduling recurring tasks.
Supports Windows Task Scheduler and Linux/Mac cron.

Usage:
    # Show scheduling options
    python scheduler.py --show-config

    # Install scheduled tasks
    python scheduler.py --install --vault /path/to/vault

    # Remove scheduled tasks
    python scheduler.py --uninstall
"""

import argparse
import logging
import os
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class Scheduler:
    """Manage scheduled tasks for AI Employee."""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.scripts_folder = self.vault_path / 'scripts'
        self.python_executable = sys.executable
        self.is_windows = platform.system() == 'Windows'
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def get_tasks_config(self) -> list:
        """Get list of scheduled task configurations."""
        return [
            {
                'name': 'AI_Employee_Daily_Briefing',
                'description': 'Generate daily CEO briefing at 8 AM',
                'script': 'orchestrator.py',
                'args': ['--vault', str(self.vault_path), '--daily-briefing'],
                'schedule': 'daily_8am'
            },
            {
                'name': 'AI_Employee_Weekly_Audit',
                'description': 'Weekly business audit on Sunday at 10 PM',
                'script': 'orchestrator.py',
                'args': ['--vault', str(self.vault_path), '--weekly-audit'],
                'schedule': 'weekly_sunday_10pm'
            },
            {
                'name': 'AI_Employee_Watcher',
                'description': 'Continuous file watcher (every 5 minutes)',
                'script': 'filesystem_watcher.py',
                'args': ['--vault', str(self.vault_path), '--continuous'],
                'schedule': 'every_5min'
            }
        ]
        
    def install_windows(self) -> bool:
        """Install tasks using Windows Task Scheduler."""
        if not self.is_windows:
            self.logger.error("Not a Windows system")
            return False
            
        tasks = self.get_tasks_config()
        
        for task in tasks:
            try:
                # Build command
                script_path = self.scripts_folder / task['script']
                args = [self.python_executable, str(script_path)] + task['args']
                command = ' '.join(f'"{a}"' for a in args)
                
                # Determine trigger based on schedule
                if task['schedule'] == 'daily_8am':
                    trigger = f'/SC DAILY /MO 1 /ST 08:00'
                elif task['schedule'] == 'weekly_sunday_10pm':
                    trigger = f'/SC WEEKLY /D SUN /ST 22:00'
                elif task['schedule'] == 'every_5min':
                    trigger = f'/SC MINUTE /MO 5'
                else:
                    continue
                
                # Create task using schtasks
                cmd = f'schtasks /Create /TN "{task["name"]}" /TR "{command}" {trigger} ' \
                      f'/RL HIGHEST /F /SC {trigger} /IT /Z'
                
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.logger.info(f"Installed: {task['name']}")
                else:
                    self.logger.error(f"Failed: {task['name']} - {result.stderr}")
                    
            except Exception as e:
                self.logger.error(f"Error installing {task['name']}: {e}")
                
        return True
        
    def uninstall_windows(self) -> bool:
        """Remove tasks from Windows Task Scheduler."""
        if not self.is_windows:
            return False
            
        tasks = self.get_tasks_config()
        
        for task in tasks:
            try:
                cmd = f'schtasks /Delete /TN "{task["name"]}" /F'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.logger.info(f"Removed: {task['name']}")
                else:
                    self.logger.warning(f"Could not remove: {task['name']}")
                    
            except Exception as e:
                self.logger.error(f"Error removing {task['name']}: {e}")
                
        return True
        
    def install_cron(self) -> bool:
        """Install tasks using cron."""
        if self.is_windows:
            self.logger.error("Use install_windows() for Windows")
            return False
            
        tasks = self.get_tasks_config()
        cron_lines = []
        
        for task in tasks:
            script_path = self.scripts_folder / task['script']
            args = [self.python_executable, str(script_path)] + task['args']
            command = ' '.join(f'"{a}"' for a in args)
            
            # Determine cron expression
            if task['schedule'] == 'daily_8am':
                cron_expr = '0 8 * * *'
            elif task['schedule'] == 'weekly_sunday_10pm':
                cron_expr = '0 22 * * 0'
            elif task['schedule'] == 'every_5min':
                cron_expr = '*/5 * * * *'
            else:
                continue
                
            cron_line = f'{cron_expr} cd {self.vault_path} && {command}'
            cron_lines.append(cron_line)
            
        # Add to crontab
        cron_content = '\n'.join(cron_lines)
        
        try:
            # Get current crontab
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            current_crontab = result.stdout if result.returncode == 0 else ''
            
            # Add new entries (avoid duplicates)
            for line in cron_lines:
                if line not in current_crontab:
                    current_crontab += f'\n{line}'
                    
            # Install new crontab
            proc = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
            proc.communicate(input=current_crontab)
            
            self.logger.info(f"Installed {len(cron_lines)} cron job(s)")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install cron jobs: {e}")
            return False
            
    def uninstall_cron(self) -> bool:
        """Remove AI Employee tasks from crontab."""
        if self.is_windows:
            return False
            
        try:
            # Get current crontab
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.info("No crontab installed")
                return True
                
            # Filter out AI Employee tasks
            lines = result.stdout.split('\n')
            filtered = [l for l in lines if 'AI_Employee' not in l and 
                       str(self.vault_path) not in l]
            
            # Install filtered crontab
            new_crontab = '\n'.join(filtered)
            proc = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
            proc.communicate(input=new_crontab)
            
            self.logger.info("Removed AI Employee cron jobs")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to uninstall cron jobs: {e}")
            return False
            
    def show_config(self):
        """Display scheduling configuration."""
        tasks = self.get_tasks_config()
        
        print("\n=== AI Employee Scheduled Tasks ===\n")
        print(f"Vault: {self.vault_path}")
        print(f"Python: {self.python_executable}")
        print(f"Platform: {'Windows' if self.is_windows else 'Linux/Mac'}")
        print()
        
        for task in tasks:
            print(f"Task: {task['name']}")
            print(f"  Description: {task['description']}")
            print(f"  Schedule: {task['schedule']}")
            print(f"  Script: {task['script']}")
            print(f"  Args: {' '.join(task['args'])}")
            print()
            
    def show_cron_output(self):
        """Show cron configuration output."""
        tasks = self.get_tasks_config()
        
        print("\n=== Cron Configuration ===\n")
        print("# Add these lines to your crontab (run: crontab -e)\n")
        
        for task in tasks:
            script_path = self.scripts_folder / task['script']
            args = [self.python_executable, str(script_path)] + task['args']
            command = ' '.join(f'"{a}"' for a in args)
            
            if task['schedule'] == 'daily_8am':
                cron_expr = '0 8 * * *'
            elif task['schedule'] == 'weekly_sunday_10pm':
                cron_expr = '0 22 * * 0'
            elif task['schedule'] == 'every_5min':
                cron_expr = '*/5 * * * *'
            else:
                continue
                
            print(f"{cron_expr} cd {self.vault_path} && {command}")
            
        print()


def main():
    parser = argparse.ArgumentParser(description='AI Employee Scheduler')
    parser.add_argument('--vault', '-v', help='Path to Obsidian vault')
    parser.add_argument('--install', action='store_true', help='Install scheduled tasks')
    parser.add_argument('--uninstall', action='store_true', help='Remove scheduled tasks')
    parser.add_argument('--show-config', action='store_true', help='Show configuration')
    parser.add_argument('--show-cron', action='store_true', help='Show cron output')
    
    args = parser.parse_args()
    
    if args.show_cron:
        if args.vault:
            scheduler = Scheduler(args.vault)
            scheduler.show_cron_output()
        else:
            print("--vault is required")
            sys.exit(1)
        return
        
    if not args.vault:
        # Try to auto-detect
        possible_vaults = list(Path('.').glob('*/Dashboard.md'))
        if possible_vaults:
            args.vault = str(possible_vaults[0].parent)
            print(f"Auto-detected vault: {args.vault}")
        else:
            print("--vault is required (or run from vault directory)")
            sys.exit(1)
            
    scheduler = Scheduler(args.vault)
    
    if args.show_config:
        scheduler.show_config()
        
    elif args.install:
        if scheduler.is_windows:
            scheduler.install_windows()
        else:
            scheduler.install_cron()
            
    elif args.uninstall:
        if scheduler.is_windows:
            scheduler.uninstall_windows()
        else:
            scheduler.uninstall_cron()
            
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
