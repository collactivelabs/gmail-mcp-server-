# Migration Guide

## Upgrading from v0.1.0 to v0.2.0

### Token Storage Changes

Version 0.2.0 introduces encrypted token storage. Your existing plaintext tokens will continue to work through a compatibility layer.

#### Automatic Migration
- The new version will automatically detect plaintext tokens
- On first use, tokens will be encrypted and saved securely
- No action required from users

#### Manual Migration (Optional)
If you want to force re-encryption of your tokens:

1. Delete your existing token file
2. Run the server to trigger re-authentication
3. New tokens will be encrypted automatically

### New Features

#### Using the Enhanced Server
To access new features like attachments and labels, use the enhanced server:

```json
{
  "mcpServers": {
    "gmail": {
      "command": "uv",
      "args": [
        "--directory",
        "[absolute-path-to-git-repo]",
        "run",
        "python",
        "src/gmail/server_enhanced.py",
        "--creds-file-path",
        "[path-to-credentials]",
        "--token-path",
        "[path-to-token]"
      ]
    }
  }
}
```

#### New Tools Available
- `list-emails`: Paginated email listing
- `download-attachment`: Download email attachments
- `send-email-with-attachment`: Send emails with files
- `manage-labels`: Add/remove Gmail labels
- `list-labels`: List available labels

### Breaking Changes

None. All existing functionality remains compatible.

### Configuration Changes

No configuration changes required. The same command-line arguments work with both versions.

### Development Changes

#### New Dependencies
```bash
# Required for encryption
cryptography>=41.0.0

# Development tools (optional)
pytest>=7.4.0
black>=23.7.0
mypy>=1.5.1
```

#### Project Structure
```
src/gmail/
├── services/           # New directory
│   ├── gmail_service.py
│   ├── gmail_service_enhanced.py
│   └── security.py
├── server.py          # Original server
├── server_enhanced.py # Enhanced server
└── constants.py       # New file
```

### Troubleshooting

#### Token Decryption Errors
If you encounter decryption errors after moving between machines:

1. Delete the token file
2. Re-authenticate through the OAuth flow
3. New encrypted tokens will be created

#### Permission Errors
Ensure proper permissions on token files:
```bash
chmod 600 /path/to/your/app_token.json
```

### Getting Help

If you encounter issues during migration:

1. Check the [troubleshooting section](README.md#troubleshooting)
2. Review the [security documentation](SECURITY.md)
3. Open an issue on GitHub
