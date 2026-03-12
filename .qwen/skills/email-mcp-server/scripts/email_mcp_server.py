#!/usr/bin/env python3
"""
Email MCP Server for AI Employee (Silver Tier)

Provides email sending capabilities via Gmail API using Model Context Protocol.

Usage:
    # First-time authentication
    python email_mcp_server.py --authenticate

    # Start MCP server
    python email_mcp_server.py --serve --port 8809
"""

import argparse
import base64
import json
import logging
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# Google API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False


SCOPES = ['https://www.googleapis.com/auth/gmail.send', 
          'https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.draft']


class EmailMCPServer:
    """MCP server for email operations."""
    
    def __init__(self, credentials_path: str = None, token_path: str = None):
        self.credentials_path = Path(credentials_path) if credentials_path else None
        self.token_path = Path(token_path) if token_path else None
        self.service = None
        self.logger = logging.getLogger(__name__)
        
    def get_credentials(self):
        """Get or refresh OAuth credentials."""
        creds = None
        
        if self.token_path and self.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)
            
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                creds_path = self.credentials_path or Path('scripts/credentials.json')
                if not creds_path.exists():
                    self.logger.error("credentials.json not found")
                    return None
                flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
                creds = flow.run_local_server(port=0)
                
            if self.token_path:
                self.token_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.token_path, 'w') as f:
                    f.write(creds.to_json())
                    
        return creds
        
    def connect(self):
        """Connect to Gmail API."""
        if not GMAIL_AVAILABLE:
            return False
            
        creds = self.get_credentials()
        if not creds:
            return False
            
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            self.logger.info("Connected to Gmail API")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect: {e}")
            return False
            
    def authenticate(self):
        """Perform OAuth authentication."""
        creds_path = self.credentials_path or Path('scripts/credentials.json')
        
        if not creds_path.exists():
            print(f"Error: credentials.json not found at {creds_path}")
            return False
            
        flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
        creds = flow.run_local_server(port=0)
        
        self.token_path = self.token_path or Path('scripts/token.json')
        self.token_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.token_path, 'w') as f:
            f.write(creds.to_json())
            
        print("Authentication successful!")
        return True
        
    def send_email(self, to: str, subject: str, body: str, 
                   cc: str = None, bcc: str = None, attachment: str = None) -> dict:
        """Send an email."""
        if not self.service:
            self.connect()
            
        try:
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            from email.mime.base import MIMEBase
            from email import encoders
            
            # Create message
            if attachment:
                message = MIMEMultipart()
                message.attach(MIMEText(body, 'plain'))
                
                with open(attachment, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename={Path(attachment).name}'
                    )
                    message.attach(part)
            else:
                message = MIMEText(body, 'plain')
                
            message['to'] = to
            message['subject'] = subject
            if cc:
                message['cc'] = cc
                
            # Send
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            result = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            self.logger.info(f"Email sent: {result['id']}")
            return {'success': True, 'message_id': result['id']}
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return {'success': False, 'error': str(e)}
            
    def draft_email(self, to: str, subject: str, body: str,
                    cc: str = None, attachment: str = None) -> dict:
        """Create a draft email."""
        if not self.service:
            self.connect()
            
        try:
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            if attachment:
                message = MIMEMultipart()
                message.attach(MIMEText(body, 'plain'))
            else:
                message = MIMEText(body, 'plain')
                
            message['to'] = to
            message['subject'] = subject
            if cc:
                message['cc'] = cc
                
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            result = self.service.users().drafts().create(
                userId='me',
                body={'message': {'raw': raw_message}}
            ).execute()
            
            self.logger.info(f"Draft created: {result['id']}")
            return {'success': True, 'draft_id': result['id']}
            
        except Exception as e:
            self.logger.error(f"Failed to create draft: {e}")
            return {'success': False, 'error': str(e)}
            
    def search_emails(self, query: str, max_results: int = 10) -> list:
        """Search for emails."""
        if not self.service:
            self.connect()
            
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            return [{'id': m['id']} for m in messages]
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return []
            
    def mark_read(self, message_id: str) -> dict:
        """Mark email as read."""
        if not self.service:
            self.connect()
            
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            
            self.logger.info(f"Marked {message_id} as read")
            return {'success': True}
            
        except Exception as e:
            self.logger.error(f"Failed to mark read: {e}")
            return {'success': False, 'error': str(e)}


# MCP Protocol Handler
class MCPRequestHandler(BaseHTTPRequestHandler):
    """HTTP handler for MCP requests."""
    
    server_instance = None
    
    def log_message(self, format, *args):
        logging.info(f"MCP: {args[0]}")
        
    def do_POST(self):
        """Handle MCP tool calls."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            request = json.loads(post_data.decode('utf-8'))
            method = request.get('method')
            params = request.get('params', {})
            
            if method == 'tools/list':
                tools = [
                    {
                        'name': 'send_email',
                        'description': 'Send an email via Gmail',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'to': {'type': 'string'},
                                'subject': {'type': 'string'},
                                'body': {'type': 'string'},
                                'cc': {'type': 'string'},
                                'attachment': {'type': 'string'}
                            },
                            'required': ['to', 'subject', 'body']
                        }
                    },
                    {
                        'name': 'draft_email',
                        'description': 'Create a draft email',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'to': {'type': 'string'},
                                'subject': {'type': 'string'},
                                'body': {'type': 'string'},
                                'cc': {'type': 'string'},
                                'attachment': {'type': 'string'}
                            },
                            'required': ['to', 'subject', 'body']
                        }
                    },
                    {
                        'name': 'search_emails',
                        'description': 'Search for emails',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'query': {'type': 'string'},
                                'max_results': {'type': 'number'}
                            },
                            'required': ['query']
                        }
                    },
                    {
                        'name': 'mark_read',
                        'description': 'Mark email as read',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'message_id': {'type': 'string'}
                            },
                            'required': ['message_id']
                        }
                    }
                ]
                response = {'result': {'tools': tools}}
                
            elif method == 'tools/call':
                tool_name = params.get('name')
                args = params.get('arguments', {})
                
                if tool_name == 'send_email':
                    result = self.server_instance.send_email(
                        args.get('to'),
                        args.get('subject'),
                        args.get('body'),
                        args.get('cc'),
                        args.get('attachment')
                    )
                elif tool_name == 'draft_email':
                    result = self.server_instance.draft_email(
                        args.get('to'),
                        args.get('subject'),
                        args.get('body'),
                        args.get('cc'),
                        args.get('attachment')
                    )
                elif tool_name == 'search_emails':
                    result = self.server_instance.search_emails(
                        args.get('query'),
                        args.get('max_results', 10)
                    )
                elif tool_name == 'mark_read':
                    result = self.server_instance.mark_read(args.get('message_id'))
                else:
                    result = {'error': f'Unknown tool: {tool_name}'}
                    
                response = {'result': result}
                
            elif method == 'initialize':
                response = {
                    'result': {
                        'protocolVersion': '2024-11-05',
                        'capabilities': {'tools': {}},
                        'serverInfo': {'name': 'email-mcp-server', 'version': '0.1'}
                    }
                }
                
            else:
                response = {'error': {'message': f'Unknown method: {method}'}}
                
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))


def main():
    parser = argparse.ArgumentParser(description='Email MCP Server')
    parser.add_argument('--authenticate', '-a', action='store_true', help='Authenticate with Gmail')
    parser.add_argument('--serve', '-s', action='store_true', help='Start MCP server')
    parser.add_argument('--port', '-p', type=int, default=8809, help='Server port')
    parser.add_argument('--credentials', help='Path to credentials.json')
    parser.add_argument('--token', help='Path to token.json')
    
    args = parser.parse_args()
    
    if not GMAIL_AVAILABLE:
        print("Gmail API libraries not installed.")
        print("Install: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        sys.exit(1)
        
    server = EmailMCPServer(args.credentials, args.token)
    
    if args.authenticate:
        if server.authenticate():
            print("Authentication successful!")
        else:
            print("Authentication failed.")
            sys.exit(1)
            
    elif args.serve:
        logging.basicConfig(level=logging.INFO)
        
        MCPRequestHandler.server_instance = server
        
        httpd = HTTPServer(('localhost', args.port), MCPRequestHandler)
        print(f"Email MCP Server running on http://localhost:{args.port}")
        print("Press Ctrl+C to stop")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")
            httpd.shutdown()
            
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
