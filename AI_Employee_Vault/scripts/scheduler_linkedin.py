#!/usr/bin/env python3
"""
Scheduler Integration for LinkedIn Auto-Posting

Creates scheduled tasks for recurring LinkedIn posts.
Supports Windows Task Scheduler and cron.

Usage:
    # Install scheduled task
    python scheduler_linkedin.py --vault PATH --install

    # Remove scheduled task
    python scheduler_linkedin.py --vault PATH --uninstall

    # Check status
    python scheduler_linkedin.py --vault PATH --status
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def get_script_dir() -> Path:
    """Get directory of this script."""
    return Path(__file__).parent.absolute()


def get_vault_path(custom_path: str = None) -> Path:
    """Get vault path."""
    if custom_path:
        return Path(custom_path)
    # Auto-detect
    possible = list(Path('.').glob('*/Dashboard.md'))
    if possible:
        return possible[0].parent
    return None


def create_windows_task(task_name: str, script_path: Path, vault_path: Path, 
                        schedule: str = 'daily', time: str = '09:00') -> bool:
    """Create Windows Task Scheduler task."""
    
    bat_file = script_path / 'post-to-linkedin.bat'
    
    if not bat_file.exists():
        print(f"Error: {bat_file} not found")
        return False
    
    # Build schtasks command
    if schedule == 'daily':
        schedule_type = 'DAILY'
        interval = '/MO 1'  # Every day
    elif schedule == 'weekly':
        schedule_type = 'WEEKLY'
        interval = '/MO 1 /D MON'  # Every Monday
    else:
        schedule_type = 'DAILY'
        interval = '/MO 1'
    
    cmd = (
        f'schtasks /Create /TN "{task_name}" '
        f'/TR "cmd.exe /c cd /d {script_path} && {bat_file}" '
        f'/SC {schedule_type} {interval} /ST {time} '
        f'/RL HIGHEST /F'
    )
    
    print(f"Creating scheduled task: {task_name}")
    print(f"Schedule: {schedule_type} at {time}")
    print(f"Command: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ Task created successfully")
            return True
        else:
            print(f"✗ Failed to create task")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def delete_windows_task(task_name: str) -> bool:
    """Delete Windows Task Scheduler task."""
    cmd = f'schtasks /Delete /TN "{task_name}" /F'
    
    print(f"Deleting scheduled task: {task_name}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ Task deleted successfully")
            return True
        else:
            print(f"Task not found or deletion failed")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def check_task_status(task_name: str) -> bool:
    """Check if scheduled task exists and is enabled."""
    cmd = f'schtasks /Query /TN "{task_name}"'
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ Task '{task_name}' is installed and enabled")
            return True
        else:
            print(f"✗ Task '{task_name}' not found")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def create_cron_job(script_path: Path, vault_path: Path, 
                   schedule: str = 'daily', time: str = '09:00') -> bool:
    """Create cron job (Linux/Mac)."""
    
    py_file = script_path / 'linkedin_auto_poster.py'
    
    # Build cron expression
    if schedule == 'daily':
        hour, minute = time.split(':')
        cron_line = f'{minute} {hour} * * * cd {script_path} && python {py_file} --vault {vault_path} --post-approved\n'
    elif schedule == 'weekly':
        hour, minute = time.split(':')
        cron_line = f'{minute} {hour} * * 1 cd {script_path} && python {py_file} --vault {vault_path} --post-approved\n'
    else:
        cron_line = f'0 9 * * * cd {script_path} && python {py_file} --vault {vault_path} --post-approved\n'
    
    print("To install cron job, add this line to your crontab:")
    print(f"  {cron_line.strip()}")
    print("\nRun 'crontab -e' and add the line above.")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Scheduler for LinkedIn Auto-Posting',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Install daily task at 9 AM
    python scheduler_linkedin.py --vault PATH --install

    # Install weekly task (Monday at 9 AM)
    python scheduler_linkedin.py --vault PATH --install --schedule weekly

    # Remove scheduled task
    python scheduler_linkedin.py --vault PATH --uninstall

    # Check task status
    python scheduler_linkedin.py --vault PATH --status
        """
    )
    
    parser.add_argument('--vault', '-v', required=True, help='Path to Obsidian vault')
    parser.add_argument('--install', action='store_true', help='Install scheduled task')
    parser.add_argument('--uninstall', action='store_true', help='Remove scheduled task')
    parser.add_argument('--status', action='store_true', help='Check task status')
    parser.add_argument('--schedule', default='daily', choices=['daily', 'weekly'],
                       help='Schedule frequency')
    parser.add_argument('--time', default='09:00', help='Time to run (HH:MM, default: 09:00)')
    parser.add_argument('--name', default='LinkedInAutoPost', 
                       help='Task name (default: LinkedInAutoPost)')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault)
    script_path = get_script_dir()
    task_name = args.name
    
    if not vault_path.exists():
        print(f"Error: Vault not found: {vault_path}")
        sys.exit(1)
    
    # Determine OS
    is_windows = os.name == 'nt'
    
    if args.install:
        print("\n" + "="*70)
        print("Install LinkedIn Auto-Post Scheduler")
        print("="*70)
        
        if is_windows:
            success = create_windows_task(task_name, script_path, vault_path, 
                                         args.schedule, args.time)
        else:
            success = create_cron_job(script_path, vault_path, args.schedule, args.time)
        
        if success:
            print("\n✓ Scheduler installed successfully!")
            print(f"\nTask will run: {args.schedule} at {args.time}")
            print(f"Check Logs/ folder for results")
        else:
            print("\n✗ Failed to install scheduler")
            sys.exit(1)
    
    elif args.uninstall:
        print("\n" + "="*70)
        print("Remove LinkedIn Auto-Post Scheduler")
        print("="*70)
        
        if is_windows:
            success = delete_windows_task(task_name)
        else:
            print("Manual removal required:")
            print(f"  Run 'crontab -e' and remove LinkedIn auto-post line")
            success = True
        
        if success:
            print("\n✓ Scheduler removed successfully!")
        else:
            print("\n✗ Failed to remove scheduler")
            sys.exit(1)
    
    elif args.status:
        print("\n" + "="*70)
        print("LinkedIn Auto-Post Scheduler Status")
        print("="*70)
        
        if is_windows:
            exists = check_task_status(task_name)
        else:
            print("Check cron jobs with: crontab -l")
            exists = True
        
        if exists:
            print(f"\nTask: {task_name}")
            print(f"Schedule: {args.schedule} at {args.time}")
            print(f"Vault: {vault_path}")
        else:
            print("\nScheduler not installed")
            print("Install with: python scheduler_linkedin.py --vault PATH --install")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
