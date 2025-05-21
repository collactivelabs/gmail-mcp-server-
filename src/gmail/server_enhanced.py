#!/usr/bin/env python3
"""Enhanced Gmail MCP Server with all features"""
import argparse
import asyncio
import logging
from typing import Any, Dict, List, Optional
import json

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

from .services import GmailServiceEnhanced, TokenSecurityManager
from .constants import EMAIL_ADMIN_PROMPTS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enhanced constants
TOOL_LIST_EMAILS = "list-emails"
TOOL_DOWNLOAD_ATTACHMENT = "download-attachment"
TOOL_SEND_EMAIL_WITH_ATTACHMENT = "send-email-with-attachment"
TOOL_MANAGE_LABELS = "manage-labels"
TOOL_LIST_LABELS = "list-labels"


class SecureGmailService(GmailServiceEnhanced):
    """Gmail service with secure token storage"""
    
    def __init__(self, creds_file_path: str, token_path: str, scopes: Optional[List[str]] = None):
        self.security_manager = TokenSecurityManager(token_path)
        super().__init__(creds_file_path, token_path, scopes)
    
    def _get_token(self):
        """Override to use secure token storage"""
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        
        token = None
        token_data = self.security_manager.load_token()
        
        if token_data:
            logger.info('Loading token from secure storage')
            token = Credentials.from_authorized_user_info(token_data, self.scopes)
        
        if not token or not token.valid:
            if token and token.expired and token.refresh_token:
                logger.info('Refreshing token')
                token.refresh(Request())
            else:
                logger.info('Fetching new token')
                flow = InstalledAppFlow.from_client_secrets_file(self.creds_file_path, self.scopes)
                token = flow.run_local_server(port=0)
            
            # Save token securely
            token_info = {
                'token': token.token,
                'refresh_token': token.refresh_token,
                'token_uri': token.token_uri,
                'client_id': token.client_id,
                'client_secret': token.client_secret,
                'scopes': token.scopes
            }
            self.security_manager.save_token(token_info)
        
        return token


async def main(creds_file_path: str, token_path: str):
    """Main entry point for the enhanced MCP server"""
    
    gmail_service = SecureGmailService(creds_file_path, token_path)
    server = Server("gmail")

    # Include all the original tools plus new ones
    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        return [
            # Original tools (imported from main server)
            # ... (include all original tools here)
            
            # New tools
            types.Tool(
                name=TOOL_LIST_EMAILS,
                description="List emails with pagination",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Gmail search query",
                            "default": "in:inbox"
                        },
                        "page_size": {
                            "type": "integer",
                            "description": "Number of results per page",
                            "default": 20
                        },
                        "page_token": {
                            "type": "string",
                            "description": "Token for next page"
                        },
                    },
                    "required": []
                },
            ),
            types.Tool(
                name=TOOL_DOWNLOAD_ATTACHMENT,
                description="Download an attachment from an email",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "email_id": {
                            "type": "string",
                            "description": "Email ID"
                        },
                        "attachment_id": {
                            "type": "string",
                            "description": "Attachment ID"
                        },
                        "save_path": {
                            "type": "string",
                            "description": "Path to save attachment"
                        },
                    },
                    "required": ["email_id", "attachment_id", "save_path"]
                },
            ),
            types.Tool(
                name=TOOL_SEND_EMAIL_WITH_ATTACHMENT,
                description="Send email with attachments",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "recipient_id": {
                            "type": "string",
                            "description": "Recipient email address"
                        },
                        "subject": {
                            "type": "string",
                            "description": "Email subject"
                        },
                        "message": {
                            "type": "string",
                            "description": "Email content"
                        },
                        "attachment_paths": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of file paths to attach"
                        },
                        "thread_id": {
                            "type": "string",
                            "description": "Thread ID for replies"
                        },
                    },
                    "required": ["recipient_id", "subject", "message", "attachment_paths"]
                },
            ),
            types.Tool(
                name=TOOL_MANAGE_LABELS,
                description="Add or remove labels from an email",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "email_id": {
                            "type": "string",
                            "description": "Email ID"
                        },
                        "add_labels": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Labels to add"
                        },
                        "remove_labels": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Labels to remove"
                        },
                    },
                    "required": ["email_id"]
                },
            ),
            types.Tool(
                name=TOOL_LIST_LABELS,
                description="List all available labels",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                },
            ),
        ]

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        
        # Include original tool handlers...
        # (copy from original server.py)
        
        # New tool handlers
        if name == TOOL_LIST_EMAILS:
            query = arguments.get("query", "in:inbox")
            page_size = arguments.get("page_size", 20)
            page_token = arguments.get("page_token")
            
            emails, next_page_token = await gmail_service.list_emails_paginated(
                query, page_size, page_token
            )
            
            result = {
                "emails": emails,
                "next_page_token": next_page_token
            }
            
            return [types.TextContent(
                type="text", 
                text=json.dumps(result),
                artifact={"type": "json", "data": result}
            )]
            
        elif name == TOOL_DOWNLOAD_ATTACHMENT:
            email_id = arguments.get("email_id")
            attachment_id = arguments.get("attachment_id")
            save_path = arguments.get("save_path")
            
            if not all([email_id, attachment_id, save_path]):
                raise ValueError("Missing required parameters")
                
            result = await gmail_service.download_attachment(
                email_id, attachment_id, save_path
            )
            
            return [types.TextContent(type="text", text=json.dumps(result))]
            
        elif name == TOOL_SEND_EMAIL_WITH_ATTACHMENT:
            recipient = arguments.get("recipient_id")
            subject = arguments.get("subject")
            message = arguments.get("message")
            attachment_paths = arguments.get("attachment_paths", [])
            thread_id = arguments.get("thread_id")
            
            if not all([recipient, subject, message]):
                raise ValueError("Missing required parameters")
                
            result = await gmail_service.send_email_with_attachment(
                recipient, subject, message, attachment_paths, thread_id
            )
            
            return [types.TextContent(type="text", text=json.dumps(result))]
            
        elif name == TOOL_MANAGE_LABELS:
            email_id = arguments.get("email_id")
            add_labels = arguments.get("add_labels", [])
            remove_labels = arguments.get("remove_labels", [])
            
            if not email_id:
                raise ValueError("Missing email_id parameter")
                
            result = await gmail_service.manage_labels(
                email_id, add_labels, remove_labels
            )
            
            return [types.TextContent(type="text", text=json.dumps(result))]
            
        elif name == TOOL_LIST_LABELS:
            labels = await gmail_service.list_labels()
            return [types.TextContent(
                type="text", 
                text=json.dumps(labels),
                artifact={"type": "json", "data": labels}
            )]
            
        else:
            logger.error(f"Unknown tool: {name}")
            raise ValueError(f"Unknown tool: {name}")

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="gmail",
                server_version="0.2.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Enhanced Gmail API MCP Server')
    parser.add_argument('--creds-file-path',
                        required=True,
                       help='OAuth 2.0 credentials file path')
    parser.add_argument('--token-path',
                        required=True,
                       help='File location to store and retrieve access and refresh tokens for application')
    
    args = parser.parse_args()
    asyncio.run(main(args.creds_file_path, args.token_path))
