"""Security utilities for Gmail MCP server"""
import os
import json
import base64
import logging
from pathlib import Path
from typing import Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)


class TokenSecurityManager:
    """Manages secure token storage with encryption"""
    
    def __init__(self, token_path: str):
        self.token_path = Path(token_path)
        self._ensure_secure_permissions()
        
    def _ensure_secure_permissions(self):
        """Ensure token file has secure permissions (600)"""
        if self.token_path.exists():
            self.token_path.chmod(0o600)
        else:
            # Create parent directory if needed
            self.token_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _get_encryption_key(self) -> bytes:
        """Generate encryption key from machine-specific info"""
        # Use machine-specific info as salt
        salt = (os.getenv("USER", "") + os.uname().nodename).encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(b"gmail-mcp-token-key"))
        return key
    
    def save_token(self, token_data: Dict[str, Any]):
        """Save token with encryption"""
        try:
            # Convert token to JSON
            token_json = json.dumps(token_data)
            
            # Encrypt the token
            fernet = Fernet(self._get_encryption_key())
            encrypted_token = fernet.encrypt(token_json.encode())
            
            # Save encrypted token
            self.token_path.write_bytes(encrypted_token)
            self._ensure_secure_permissions()
            
            logger.info(f"Token saved securely to {self.token_path}")
        except Exception as e:
            logger.error(f"Failed to save token securely: {e}")
            # Fallback to plaintext for compatibility
            self.token_path.write_text(token_json)
    
    def load_token(self) -> Dict[str, Any]:
        """Load and decrypt token"""
        try:
            if not self.token_path.exists():
                return None
                
            # Read encrypted token
            encrypted_token = self.token_path.read_bytes()
            
            # Decrypt token
            try:
                fernet = Fernet(self._get_encryption_key())
                decrypted_token = fernet.decrypt(encrypted_token)
                return json.loads(decrypted_token.decode())
            except:
                # Fallback: try reading as plaintext
                token_text = self.token_path.read_text()
                return json.loads(token_text)
                
        except Exception as e:
            logger.error(f"Failed to load token: {e}")
            return None
