"""Tests for Gmail service"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import base64
from email.message import EmailMessage

from gmail.services import GmailService


class TestGmailService(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.creds_file_path = "/tmp/test_creds.json"
        self.token_path = "/tmp/test_token.json"
        
        # Mock the Google API client
        self.mock_service = MagicMock()
        self.mock_credentials = MagicMock()
        
        # Patch the Google API methods
        self.patches = [
            patch('gmail.services.gmail_service.InstalledAppFlow'),
            patch('gmail.services.gmail_service.Credentials'),
            patch('gmail.services.gmail_service.build'),
            patch('os.path.exists'),
        ]
        
        for p in self.patches:
            p.start()
            
    def tearDown(self):
        """Clean up after tests"""
        for p in self.patches:
            p.stop()
    
    def test_send_email(self):
        """Test sending an email"""
        # Create a Gmail service instance
        service = GmailService(self.creds_file_path, self.token_path)
        service.service = self.mock_service
        service.user_email = "test@example.com"
        
        # Mock the API response
        self.mock_service.users().messages().send().execute.return_value = {
            "id": "test_message_id"
        }
        
        # Test sending email
        result = service.send_email(
            "recipient@example.com",
            "Test Subject",
            "Test message body"
        )
        
        # Verify the result
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message_id"], "test_message_id")
        
        # Verify the API was called correctly
        self.mock_service.users().messages().send.assert_called_once()
    
    def test_read_email(self):
        """Test reading an email"""
        service = GmailService(self.creds_file_path, self.token_path)
        service.service = self.mock_service
        
        # Create a test email message
        test_email = EmailMessage()
        test_email.set_content("Test email content")
        test_email['Subject'] = "Test Subject"
        test_email['From'] = "sender@example.com"
        test_email['To'] = "recipient@example.com"
        
        # Encode the message as base64
        raw_message = base64.urlsafe_b64encode(test_email.as_bytes()).decode()
        
        # Mock the API response
        self.mock_service.users().messages().get().execute.return_value = {
            "id": "test_email_id",
            "raw": raw_message,
            "threadId": "test_thread_id"
        }
        
        # Test reading email
        result = service.read_email("test_email_id")
        
        # Verify the result
        self.assertEqual(result["subject"], "Test Subject")
        self.assertEqual(result["from"], "sender@example.com")
        self.assertEqual(result["to"], "recipient@example.com")
        self.assertIn("Test email content", result["content"])
    
    def test_error_handling(self):
        """Test error handling in Gmail service"""
        from googleapiclient.errors import HttpError
        
        service = GmailService(self.creds_file_path, self.token_path)
        service.service = self.mock_service
        
        # Mock an HTTP error
        http_error = HttpError(
            resp=MagicMock(status=403),
            content=b"Access denied"
        )
        self.mock_service.users().messages().send().execute.side_effect = http_error
        
        # Test error handling
        result = service.send_email(
            "recipient@example.com",
            "Test Subject",
            "Test message"
        )
        
        # Verify error response
        self.assertEqual(result["status"], "error")
        self.assertIn("error_message", result)


if __name__ == '__main__':
    unittest.main()
