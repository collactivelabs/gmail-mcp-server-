#!/usr/bin/env python3
"""Gmail MCP Server"""
import argparse
import asyncio
import logging
from typing import Any

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

from .services import GmailService
from .constants import (
    EMAIL_ADMIN_PROMPTS,
    TOOL_SEND_EMAIL,
    TOOL_TRASH_EMAIL,
    TOOL_GET_UNREAD_EMAILS,
    TOOL_READ_EMAIL,
    TOOL_MARK_EMAIL_AS_READ,
    TOOL_OPEN_EMAIL,
    TOOL_SEARCH_EMAILS,
    TOOL_CREATE_DRAFT,
    TOOL_LIST_DRAFTS
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define available prompts
PROMPTS = {
    "manage-email": types.Prompt(
        name="manage-email",
        description="Act like an email administrator",
        arguments=None,
    ),
    "draft-email": types.Prompt(
        name="draft-email",
        description="Draft an email with content and recipient",
        arguments=[
            types.PromptArgument(
                name="content",
                description="What the email is about",
                required=True
            ),
            types.PromptArgument(
                name="recipient",
                description="Who should the email be addressed to",
                required=True
            ),
            types.PromptArgument(
                name="recipient_email",
                description="Recipient's email address",
                required=True
            ),
        ],
    ),
    "edit-draft": types.Prompt(
        name="edit-draft",
        description="Edit the existing email draft",
        arguments=[
            types.PromptArgument(
                name="changes",
                description="What changes should be made to the draft",
                required=True
            ),
            types.PromptArgument(
                name="current_draft",
                description="The current draft to edit",
                required=True
            ),
        ],
    ),
}


async def main(creds_file_path: str, token_path: str):
    """Main entry point for the MCP server"""
    
    gmail_service = GmailService(creds_file_path, token_path)
    server = Server("gmail")

    @server.list_prompts()
    async def list_prompts() -> list[types.Prompt]:
        return list(PROMPTS.values())

    @server.get_prompt()
    async def get_prompt(
        name: str, arguments: dict[str, str] | None = None
    ) -> types.GetPromptResult:
        if name not in PROMPTS:
            raise ValueError(f"Prompt not found: {name}")

        if name == "manage-email":
            return types.GetPromptResult(
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text=EMAIL_ADMIN_PROMPTS,
                        )
                    )
                ]
            )

        if name == "draft-email":
            content = arguments.get("content", "")
            recipient = arguments.get("recipient", "")
            recipient_email = arguments.get("recipient_email", "")
            
            return types.GetPromptResult(
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text=f"""Please draft an email about {content} for {recipient} ({recipient_email}).
                            Include a subject line starting with 'Subject:' on the first line.
                            Do not send the email yet, just draft it and ask the user for their thoughts."""
                        )
                    )
                ]
            )
        
        elif name == "edit-draft":
            changes = arguments.get("changes", "")
            current_draft = arguments.get("current_draft", "")
            
            return types.GetPromptResult(
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text=f"""Please revise the current email draft:
                            {current_draft}
                            
                            Requested changes:
                            {changes}
                            
                            Please provide the updated draft."""
                        )
                    )
                ]
            )

        raise ValueError("Prompt implementation not found")

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name=TOOL_SEND_EMAIL,
                description="""Sends email to recipient. 
                Do not use if user only asked to draft email. 
                Drafts must be approved before sending.""",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "recipient_id": {
                            "type": "string",
                            "description": "Recipient email address",
                        },
                        "subject": {
                            "type": "string",
                            "description": "Email subject",
                        },
                        "message": {
                            "type": "string",
                            "description": "Email content text",
                        },
                        "thread_id": {
                            "type": "string",
                            "description": "Thread ID for replies",
                        },
                    },
                    "required": ["recipient_id", "subject", "message"],
                },
            ),
            types.Tool(
                name=TOOL_TRASH_EMAIL,
                description="""Moves email to trash. 
                Confirm before moving email to trash.""",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "email_id": {
                            "type": "string",
                            "description": "Email ID",
                        },
                    },
                    "required": ["email_id"],
                },
            ),
            types.Tool(
                name=TOOL_GET_UNREAD_EMAILS,
                description="Retrieve unread emails",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Additional search query",
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 20,
                        },
                    },
                    "required": []
                },
            ),
            types.Tool(
                name=TOOL_READ_EMAIL,
                description="Retrieves given email content",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "email_id": {
                            "type": "string",
                            "description": "Email ID",
                        },
                    },
                    "required": ["email_id"],
                },
            ),
            types.Tool(
                name=TOOL_MARK_EMAIL_AS_READ,
                description="Marks given email as read",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "email_id": {
                            "type": "string",
                            "description": "Email ID",
                        },
                    },
                    "required": ["email_id"],
                },
            ),
            types.Tool(
                name=TOOL_OPEN_EMAIL,
                description="Open email in browser",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "email_id": {
                            "type": "string",
                            "description": "Email ID",
                        },
                    },
                    "required": ["email_id"],
                },
            ),
            types.Tool(
                name=TOOL_SEARCH_EMAILS,
                description="Search emails with custom query",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Gmail search query",
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 20,
                        },
                    },
                    "required": ["query"],
                },
            ),
            types.Tool(
                name=TOOL_CREATE_DRAFT,
                description="Create a draft email",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "recipient": {
                            "type": "string",
                            "description": "Recipient email address",
                        },
                        "subject": {
                            "type": "string",
                            "description": "Email subject",
                        },
                        "message": {
                            "type": "string",
                            "description": "Email content",
                        },
                    },
                    "required": ["recipient", "subject", "message"],
                },
            ),
            types.Tool(
                name=TOOL_LIST_DRAFTS,
                description="List email drafts",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 10,
                        },
                    },
                    "required": []
                },
            ),
        ]

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:

        if name == TOOL_SEND_EMAIL:
            recipient = arguments.get("recipient_id")
            if not recipient:
                raise ValueError("Missing recipient parameter")
            subject = arguments.get("subject")
            if not subject:
                raise ValueError("Missing subject parameter")
            message = arguments.get("message")
            if not message:
                raise ValueError("Missing message parameter")
            thread_id = arguments.get("thread_id")
                
            # Extract subject if included in message
            email_lines = message.split('\n')
            if email_lines[0].startswith('Subject:'):
                subject = email_lines[0][8:].strip()
                message_content = '\n'.join(email_lines[1:]).strip()
            else:
                message_content = message
                
            send_response = await gmail_service.send_email(
                recipient, 
                subject, 
                message_content,
                thread_id
            )
            
            if send_response["status"] == "success":
                response_text = f"Email sent successfully. Message ID: {send_response['message_id']}"
            else:
                response_text = f"Failed to send email: {send_response['error_message']}"
            return [types.TextContent(type="text", text=response_text)]

        elif name == TOOL_GET_UNREAD_EMAILS:
            query = arguments.get("query")
            max_results = arguments.get("max_results", 20)
            
            unread_emails = await gmail_service.get_unread_emails(query, max_results)
            return [types.TextContent(
                type="text", 
                text=str(unread_emails),
                artifact={"type": "json", "data": unread_emails}
            )]
        
        elif name == TOOL_READ_EMAIL:
            email_id = arguments.get("email_id")
            if not email_id:
                raise ValueError("Missing email ID parameter")
                
            retrieved_email = await gmail_service.read_email(email_id)
            return [types.TextContent(
                type="text", 
                text=str(retrieved_email),
                artifact={"type": "dictionary", "data": retrieved_email}
            )]
            
        elif name == TOOL_OPEN_EMAIL:
            email_id = arguments.get("email_id")
            if not email_id:
                raise ValueError("Missing email ID parameter")
                
            msg = await gmail_service.open_email(email_id)
            return [types.TextContent(type="text", text=str(msg))]
            
        elif name == TOOL_TRASH_EMAIL:
            email_id = arguments.get("email_id")
            if not email_id:
                raise ValueError("Missing email ID parameter")
                
            msg = await gmail_service.trash_email(email_id)
            return [types.TextContent(type="text", text=str(msg))]
            
        elif name == TOOL_MARK_EMAIL_AS_READ:
            email_id = arguments.get("email_id")
            if not email_id:
                raise ValueError("Missing email ID parameter")
                
            msg = await gmail_service.mark_email_as_read(email_id)
            return [types.TextContent(type="text", text=str(msg))]
            
        elif name == TOOL_SEARCH_EMAILS:
            query = arguments.get("query")
            if not query:
                raise ValueError("Missing query parameter")
            max_results = arguments.get("max_results", 20)
            
            search_results = await gmail_service.search_emails(query, max_results)
            return [types.TextContent(
                type="text", 
                text=str(search_results),
                artifact={"type": "json", "data": search_results}
            )]
            
        elif name == TOOL_CREATE_DRAFT:
            recipient = arguments.get("recipient")
            subject = arguments.get("subject")
            message = arguments.get("message")
            
            if not all([recipient, subject, message]):
                raise ValueError("Missing required parameters")
                
            draft_response = await gmail_service.create_draft(recipient, subject, message)
            if draft_response["status"] == "success":
                response_text = f"Draft created successfully. Draft ID: {draft_response['draft_id']}"
            else:
                response_text = f"Failed to create draft: {draft_response['error_message']}"
            return [types.TextContent(type="text", text=response_text)]
            
        elif name == TOOL_LIST_DRAFTS:
            max_results = arguments.get("max_results", 10)
            drafts = await gmail_service.list_drafts(max_results)
            return [types.TextContent(
                type="text", 
                text=str(drafts),
                artifact={"type": "json", "data": drafts}
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
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Gmail API MCP Server')
    parser.add_argument('--creds-file-path',
                        required=True,
                       help='OAuth 2.0 credentials file path')
    parser.add_argument('--token-path',
                        required=True,
                       help='File location to store and retrieve access and refresh tokens for application')
    
    args = parser.parse_args()
    asyncio.run(main(args.creds_file_path, args.token_path))
