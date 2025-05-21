"""Gmail service implementation"""
import os
import asyncio
import logging
import base64
from email.message import EmailMessage
from email.header import decode_header
from base64 import urlsafe_b64decode
from email import message_from_bytes
import webbrowser
from typing import Any, Dict, List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


def decode_mime_header(header: str) -> str:
    """Helper function to decode encoded email headers"""
    decoded_parts = decode_header(header)
    decoded_string = ''
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            decoded_string += part.decode(encoding or 'utf-8')
        else:
            decoded_string += part
    return decoded_string


class GmailService:
    """Gmail service wrapper for MCP server"""
    
    def __init__(self,
                 creds_file_path: str,
                 token_path: str,
                 scopes: Optional[List[str]] = None):
        logger.info(f"Initializing GmailService with creds file: {creds_file_path}")
        self.creds_file_path = creds_file_path
        self.token_path = token_path
        self.scopes = scopes or ['https://www.googleapis.com/auth/gmail.modify']
        self.token = self._get_token()
        logger.info("Token retrieved successfully")
        self.service = self._get_service()
        logger.info("Gmail service initialized")
        self.user_email = self._get_user_email()
        logger.info(f"User email retrieved: {self.user_email}")

    def _get_token(self) -> Credentials:
        """Get or refresh Google API token"""
        token = None
    
        if os.path.exists(self.token_path):
            logger.info('Loading token from file')
            token = Credentials.from_authorized_user_file(self.token_path, self.scopes)

        if not token or not token.valid:
            if token and token.expired and token.refresh_token:
                logger.info('Refreshing token')
                token.refresh(Request())
            else:
                logger.info('Fetching new token')
                flow = InstalledAppFlow.from_client_secrets_file(self.creds_file_path, self.scopes)
                token = flow.run_local_server(port=0)

            with open(self.token_path, 'w') as token_file:
                token_file.write(token.to_json())
                logger.info(f'Token saved to {self.token_path}')

        return token

    def _get_service(self) -> Any:
        """Initialize Gmail API service"""
        try:
            service = build('gmail', 'v1', credentials=self.token)
            return service
        except HttpError as error:
            logger.error(f'An error occurred building Gmail service: {error}')
            raise ValueError(f'An error occurred: {error}')
    
    def _get_user_email(self) -> str:
        """Get user email address"""
        profile = self.service.users().getProfile(userId='me').execute()
        user_email = profile.get('emailAddress', '')
        return user_email
    
    async def send_email(self, 
                        recipient_id: str, 
                        subject: str, 
                        message: str,
                        thread_id: Optional[str] = None) -> Dict[str, str]:
        """Creates and sends an email message"""
        try:
            message_obj = EmailMessage()
            message_obj.set_content(message)
            
            message_obj['To'] = recipient_id
            message_obj['From'] = self.user_email
            message_obj['Subject'] = subject

            encoded_message = base64.urlsafe_b64encode(message_obj.as_bytes()).decode()
            create_message = {'raw': encoded_message}
            
            if thread_id:
                create_message['threadId'] = thread_id
            
            send_message = await asyncio.to_thread(
                self.service.users().messages().send(userId="me", body=create_message).execute
            )
            logger.info(f"Message sent: {send_message['id']}")
            return {"status": "success", "message_id": send_message["id"]}
        except HttpError as error:
            logger.error(f"Error sending email: {error}")
            return {"status": "error", "error_message": str(error)}

    async def open_email(self, email_id: str) -> str:
        """Opens email in browser given ID."""
        try:
            url = f"https://mail.google.com/mail/u/0/#inbox/{email_id}"
            webbrowser.open(url, new=0, autoraise=True)
            return "Email opened in browser successfully."
        except Exception as error:
            return f"An error occurred: {str(error)}"

    async def get_unread_emails(self, 
                              query: Optional[str] = None,
                              max_results: int = 20) -> List[Dict[str, str]]:
        """Retrieves unread messages from mailbox."""
        try:
            user_id = 'me'
            if query:
                search_query = f'in:inbox is:unread {query}'
            else:
                search_query = 'in:inbox is:unread category:primary'

            response = self.service.users().messages().list(
                userId=user_id,
                q=search_query,
                maxResults=max_results
            ).execute()
            
            messages = response.get('messages', [])
            return messages

        except HttpError as error:
            logger.error(f"Error getting unread emails: {error}")
            return []

    async def search_emails(self, 
                          query: str,
                          max_results: int = 20) -> List[Dict[str, str]]:
        """Search emails with custom query"""
        try:
            response = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = response.get('messages', [])
            return messages

        except HttpError as error:
            logger.error(f"Error searching emails: {error}")
            return []

    async def read_email(self, email_id: str) -> Dict[str, str]:
        """Retrieves email contents including metadata and body"""
        try:
            msg = self.service.users().messages().get(
                userId="me", 
                id=email_id, 
                format='raw'
            ).execute()
            
            email_metadata = {}

            # Decode the base64URL encoded raw content
            raw_data = msg['raw']
            decoded_data = urlsafe_b64decode(raw_data)

            # Parse the RFC 2822 email
            mime_message = message_from_bytes(decoded_data)

            # Extract the email body
            body_text = None
            body_html = None
            
            if mime_message.is_multipart():
                for part in mime_message.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain" and not body_text:
                        body_text = part.get_payload(decode=True).decode()
                    elif content_type == "text/html" and not body_html:
                        body_html = part.get_payload(decode=True).decode()
            else:
                content_type = mime_message.get_content_type()
                payload = mime_message.get_payload(decode=True).decode()
                if content_type == "text/plain":
                    body_text = payload
                elif content_type == "text/html":
                    body_html = payload
            
            email_metadata['content'] = body_text or body_html or ""
            email_metadata['content_type'] = 'text' if body_text else 'html'
            
            # Extract metadata
            email_metadata['subject'] = decode_mime_header(mime_message.get('subject', ''))
            email_metadata['from'] = mime_message.get('from', '')
            email_metadata['to'] = mime_message.get('to', '')
            email_metadata['date'] = mime_message.get('date', '')
            email_metadata['message_id'] = mime_message.get('message-id', '')
            
            # Get thread ID for replies
            email_metadata['thread_id'] = msg.get('threadId', '')
            
            logger.info(f"Email read: {email_id}")
            
            # Mark email as read
            await self.mark_email_as_read(email_id)

            return email_metadata
        except HttpError as error:
            logger.error(f"Error reading email: {error}")
            return {"error": str(error)}
        
    async def trash_email(self, email_id: str) -> str:
        """Moves email to trash given ID."""
        try:
            self.service.users().messages().trash(userId="me", id=email_id).execute()
            logger.info(f"Email moved to trash: {email_id}")
            return "Email moved to trash successfully."
        except HttpError as error:
            return f"An HttpError occurred: {str(error)}"
        
    async def mark_email_as_read(self, email_id: str) -> str:
        """Marks email as read given ID."""
        try:
            self.service.users().messages().modify(
                userId="me", 
                id=email_id, 
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            logger.info(f"Email marked as read: {email_id}")
            return "Email marked as read."
        except HttpError as error:
            return f"An HttpError occurred: {str(error)}"

    async def create_draft(self, 
                          recipient: str, 
                          subject: str, 
                          message: str) -> Dict[str, str]:
        """Create a draft email"""
        try:
            message_obj = EmailMessage()
            message_obj.set_content(message)
            message_obj['To'] = recipient
            message_obj['From'] = self.user_email
            message_obj['Subject'] = subject

            encoded_message = base64.urlsafe_b64encode(message_obj.as_bytes()).decode()
            draft_body = {'message': {'raw': encoded_message}}
            
            draft = self.service.users().drafts().create(
                userId="me", 
                body=draft_body
            ).execute()
            
            logger.info(f"Draft created: {draft['id']}")
            return {"status": "success", "draft_id": draft["id"]}
        except HttpError as error:
            logger.error(f"Error creating draft: {error}")
            return {"status": "error", "error_message": str(error)}

    async def list_drafts(self, max_results: int = 10) -> List[Dict[str, str]]:
        """List email drafts"""
        try:
            response = self.service.users().drafts().list(
                userId='me',
                maxResults=max_results
            ).execute()
            
            drafts = response.get('drafts', [])
            return drafts
        except HttpError as error:
            logger.error(f"Error listing drafts: {error}")
            return []
