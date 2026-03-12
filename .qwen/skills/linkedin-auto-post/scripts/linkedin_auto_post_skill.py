#!/usr/bin/env python3
"""
LinkedIn Auto-Post Agent Skill

This is the agent skill wrapper for LinkedIn auto-posting.
Qwen Code invokes this skill to post to LinkedIn autonomously.

Usage:
    # Via Qwen Code skill invocation
    skill: "linkedin-auto-post"
    
    # Direct command
    python linkedin_auto_post_skill.py --vault PATH --action post --content "Your post"
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Import the main poster
from linkedin_auto_poster import LinkedInAutoPoster


class LinkedInAutoPostSkill:
    """Agent skill wrapper for LinkedIn auto-posting."""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.poster = LinkedInAutoPoster(str(vault_path))
        
        # Setup skill-specific logging
        self.logs_dir = self.vault_path / 'Logs' / 'skills'
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = self.logs_dir / f"linkedin_skill_{datetime.now().strftime('%Y-%m-%d')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - SKILL - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def create_post(self, content: str, priority: str = 'medium') -> dict:
        """
        Create a LinkedIn post draft for approval.
        
        Args:
            content: Post text content
            priority: Priority level (low, medium, high)
            
        Returns:
            dict with status and draft path
        """
        self.logger.info(f"Creating LinkedIn post draft (priority: {priority})")
        
        try:
            draft_path = self.poster.create_draft(content, priority)
            
            return {
                'status': 'success',
                'action': 'draft_created',
                'draft_path': str(draft_path),
                'draft_name': draft_path.name,
                'next_step': 'Move file to Approved/ folder to publish',
                'character_count': len(content)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create draft: {e}")
            return {
                'status': 'error',
                'action': 'draft_created',
                'error': str(e)
            }
    
    def post_approved(self) -> dict:
        """
        Post all approved content to LinkedIn.
        
        Returns:
            dict with posting results
        """
        self.logger.info("Processing approved LinkedIn posts")
        
        try:
            # Check session first
            if not self.poster.check_session():
                return {
                    'status': 'error',
                    'action': 'post_approved',
                    'error': 'LinkedIn session expired. Run --setup-session to re-authenticate.',
                    'session_valid': False
                }
            
            # Process approved posts
            results = self.poster.process_approved_posts()
            
            return {
                'status': 'success' if results['success'] > 0 else 'partial',
                'action': 'post_approved',
                'successful': results['success'],
                'failed': results['failed'],
                'errors': results['errors'],
                'session_valid': True
            }
            
        except Exception as e:
            self.logger.error(f"Failed to post approved content: {e}")
            return {
                'status': 'error',
                'action': 'post_approved',
                'error': str(e)
            }
    
    def check_session(self) -> dict:
        """
        Check if LinkedIn session is valid.
        
        Returns:
            dict with session status
        """
        self.logger.info("Checking LinkedIn session status")
        
        is_valid = self.poster.check_session()
        
        return {
            'status': 'success',
            'action': 'check_session',
            'session_valid': is_valid,
            'message': 'Session is valid' if is_valid else 'Session expired - re-authentication needed'
        }
    
    def setup_session(self) -> dict:
        """
        Setup LinkedIn session (first-time login).
        
        Returns:
            dict with setup status
        """
        self.logger.info("Setting up LinkedIn session")
        
        try:
            self.poster.setup_session()
            
            return {
                'status': 'success',
                'action': 'setup_session',
                'message': 'LinkedIn session setup complete'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to setup session: {e}")
            return {
                'status': 'error',
                'action': 'setup_session',
                'error': str(e)
            }


def main():
    parser = argparse.ArgumentParser(
        description='LinkedIn Auto-Post Agent Skill',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Create a post draft
    python linkedin_auto_post_skill.py --vault PATH --action create --content "Your post content"

    # Post approved content
    python linkedin_auto_post_skill.py --vault PATH --action post

    # Check session status
    python linkedin_auto_post_skill.py --vault PATH --action check-session

    # Setup session (first-time)
    python linkedin_auto_post_skill.py --vault PATH --action setup
        """
    )
    
    parser.add_argument('--vault', '-v', required=True, help='Path to Obsidian vault')
    parser.add_argument('--action', '-a', required=True, 
                       choices=['create', 'post', 'check-session', 'setup'],
                       help='Action to perform')
    parser.add_argument('--content', '-c', help='Post content (for create action)')
    parser.add_argument('--priority', '-p', default='medium',
                       choices=['low', 'medium', 'high'],
                       help='Post priority (for create action)')
    
    args = parser.parse_args()
    
    # Initialize skill
    skill = LinkedInAutoPostSkill(args.vault)
    
    # Execute action
    if args.action == 'create':
        if not args.content:
            print("Error: --content required for create action")
            sys.exit(1)
        
        result = skill.create_post(args.content, args.priority)
        
    elif args.action == 'post':
        result = skill.post_approved()
        
    elif args.action == 'check-session':
        result = skill.check_session()
        
    elif args.action == 'setup':
        result = skill.setup_session()
    
    else:
        print(f"Unknown action: {args.action}")
        sys.exit(1)
    
    # Output result as JSON (for agent consumption)
    print("\n" + "="*60)
    print("LINKEDIN AUTO-POST SKILL RESULT")
    print("="*60)
    print(json.dumps(result, indent=2))
    print("="*60)
    
    # Exit with appropriate code
    sys.exit(0 if result['status'] == 'success' else 1)


if __name__ == "__main__":
    main()
