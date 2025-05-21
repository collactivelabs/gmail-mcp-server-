"""Enhanced Gmail service with additional features"""
from typing import List, Dict, Optional, Tuple
import base64
import mimetypes
from pathlib import Path

from .gmail_service import GmailService, logger


class GmailServiceEnhanced(GmailService):
    """Enhanced Gmail service with additional features"""
    
    async def read_email_with_attachments(self, email_id: str) -> Dict[str, any]:
        """Retrieves email with attachments"""
        try:
            msg = self.service.users().messages().get(
                userId="me", 
                id=email_id, 
                format='full'
            ).execute()
            
            email_data = await self.read_email(email_id)
            email_data['attachments'] = []
            
            # Process attachments
            if 'payload' in msg and 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part.get('filename'):
                        attachment = {
                            'filename': part['filename'],
                            'mime_type': part.get('mimeType', ''),
                            'size': part.get('body', {}).get('size', 0),
                            'attachment_id': part.get('body', {}).get('attachmentId', '')
                        }
                        email_data['attachments'].append(attachment)
            
            return email_data
        except Exception as e:
            logger.error(f"Error reading email with attachments: {e}")
            return {"error": str(e)}
    
    async def download_attachment(self, 
                                 email_id: str, 
                                 attachment_id: str, 
                                 save_path: str) -> Dict[str, str]:
        """Download an attachment from an email"""
        try:
            attachment = self.service.users().messages().attachments().get(
                userId='me',
                messageId=email_id,
                id=attachment_id
            ).execute()
            
            # Decode attachment data
            file_data = base64.urlsafe_b64decode(
                attachment['data'].encode('UTF-8')
            )
            
            # Save to file
            path = Path(save_path)
            path.write_bytes(file_data)
            
            return {
                "status": "success",
                "message": f"Attachment saved to {save_path}"
            }
        except Exception as e:
            logger.error(f"Error downloading attachment: {e}")
            return {
                "status": "error",
                "error_message": str(e)
            }
    
    async def send_email_with_attachment(self, 
                                       recipient_id: str, 
                                       subject: str, 
                                       message: str,
                                       attachment_paths: List[str],
                                       thread_id: Optional[str] = None) -> Dict[str, str]:
        """Send email with attachments"""
        try:
            import email.mime.multipart
            import email.mime.text
            import email.mime.base
            
            # Create message container
            message_obj = email.mime.multipart.MIMEMultipart()
            message_obj['to'] = recipient_id
            message_obj['from'] = self.user_email
            message_obj['subject'] = subject
            
            # Add message body
            body = email.mime.text.MIMEText(message)
            message_obj.attach(body)
            
            # Add attachments
            for file_path in attachment_paths:
                path = Path(file_path)
                if not path.exists():
                    continue
                    
                # Guess mime type
                content_type, _ = mimetypes.guess_type(str(path))
                if content_type is None:
                    content_type = 'application/octet-stream'
                    
                main_type, sub_type = content_type.split('/', 1)
                
                # Read file
                with open(path, 'rb') as f:
                    file_data = f.read()
                
                # Create attachment
                attachment = email.mime.base.MIMEBase(main_type, sub_type)
                attachment.set_payload(file_data)
                email.encoders.encode_base64(attachment)
                attachment.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{path.name}"'
                )
                message_obj.attach(attachment)
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(
                message_obj.as_bytes()
            ).decode('utf-8')
            
            body = {'raw': raw_message}
            if thread_id:
                body['threadId'] = thread_id
                
            # Send message
            send_message = self.service.users().messages().send(
                userId="me", 
                body=body
            ).execute()
            
            logger.info(f"Message with attachments sent: {send_message['id']}")
            return {"status": "success", "message_id": send_message["id"]}
            
        except Exception as e:
            logger.error(f"Error sending email with attachments: {e}")
            return {"status": "error", "error_message": str(e)}
    
    async def list_emails_paginated(self, 
                                   query: str = "in:inbox",
                                   page_size: int = 20,
                                   page_token: Optional[str] = None) -> Tuple[List[Dict], Optional[str]]:
        """List emails with pagination support"""
        try:
            params = {
                'userId': 'me',
                'q': query,
                'maxResults': page_size
            }
            if page_token:
                params['pageToken'] = page_token
                
            response = self.service.users().messages().list(**params).execute()
            
            messages = response.get('messages', [])
            next_page_token = response.get('nextPageToken')
            
            return messages, next_page_token
            
        except Exception as e:
            logger.error(f"Error listing emails: {e}")
            return [], None
    
    async def manage_labels(self, email_id: str, 
                          add_labels: Optional[List[str]] = None,
                          remove_labels: Optional[List[str]] = None) -> Dict[str, str]:
        """Add or remove labels from an email"""
        try:
            body = {}
            if add_labels:
                body['addLabelIds'] = add_labels
            if remove_labels:
                body['removeLabelIds'] = remove_labels
                
            self.service.users().messages().modify(
                userId="me", 
                id=email_id, 
                body=body
            ).execute()
            
            return {
                "status": "success",
                "message": "Labels updated successfully"
            }
        except Exception as e:
            logger.error(f"Error managing labels: {e}")
            return {
                "status": "error",
                "error_message": str(e)
            }
    
    async def list_labels(self) -> List[Dict[str, str]]:
        """List all available labels"""
        try:
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            return labels
        except Exception as e:
            logger.error(f"Error listing labels: {e}")
            return []
