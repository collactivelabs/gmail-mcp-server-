# Security Documentation

This document outlines the security measures implemented in the Gmail MCP Server.

## Token Security

### Encryption
- OAuth tokens are encrypted using the `cryptography` library's Fernet encryption
- Encryption keys are derived from machine-specific information (username + hostname)
- PBKDF2HMAC with SHA256 is used for key derivation with 100,000 iterations

### Storage
- Encrypted tokens are stored with restrictive file permissions (600)
- Token files are readable and writable only by the owner
- Parent directories are created with secure defaults if they don't exist

### Implementation Details

```python
# Key derivation
salt = (os.getenv("USER", "") + os.uname().nodename).encode()
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100000,
)
key = base64.urlsafe_b64encode(kdf.derive(b"gmail-mcp-token-key"))

# Encryption
fernet = Fernet(key)
encrypted_token = fernet.encrypt(token_json.encode())
```

## OAuth Security

### Scopes
- Default scope: `https://www.googleapis.com/auth/gmail.modify`
- Minimal permissions required for functionality
- Users can configure additional scopes if needed

### Authentication Flow
- Uses Google's official OAuth 2.0 flow
- Tokens are refreshed automatically when expired
- No credentials are stored in code or configuration files

## API Security

### Request Validation
- All API requests are authenticated with OAuth tokens
- Input validation on all tool parameters
- Error handling prevents information leakage

### User Confirmation
- Sensitive operations (send, trash) require user confirmation
- Clear prompts explain what actions will be taken
- No automatic execution of destructive operations

## Best Practices

### Development
1. Never commit credentials or tokens
2. Use environment variables for sensitive configuration
3. Regular security audits of dependencies
4. Keep dependencies updated

### Deployment
1. Use secure token storage locations
2. Restrict file permissions appropriately
3. Monitor for unusual API usage
4. Implement rate limiting for production use

### User Guidelines
1. Store credentials in secure locations
2. Regularly review OAuth permissions
3. Revoke access for unused applications
4. Use strong authentication for Google account

## Security Checklist

- [ ] Credentials file has restrictive permissions
- [ ] Token file is encrypted and has 600 permissions
- [ ] No sensitive data in logs
- [ ] All user inputs are validated
- [ ] Error messages don't leak sensitive information
- [ ] OAuth scopes are minimal
- [ ] Dependencies are up to date

## Reporting Security Issues

If you discover a security vulnerability, please:

1. Do NOT open a public issue
2. Email the maintainers directly
3. Provide detailed information about the vulnerability
4. Allow time for a fix before public disclosure

## Security Updates

| Version | Date | Description |
|---------|------|-------------|
| 0.2.0   | 2024 | Added token encryption and secure storage |
| 0.1.0   | 2024 | Initial release with basic OAuth flow |

## References

- [Google OAuth 2.0 Security Best Practices](https://developers.google.com/identity/protocols/oauth2/security)
- [OWASP Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)
- [Python Security Best Practices](https://docs.python.org/3/library/secrets.html)
