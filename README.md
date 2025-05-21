# Gmail Server for Model Context Protocol (MCP)

This MCP server integrates with Gmail to enable sending, removing, reading, drafting, and responding to emails with enhanced security and features.

> **Security Note**: This server includes secure token storage with encryption and proper file permissions. The server prompts users before conducting sensitive operations.

https://github.com/user-attachments/assets/5794cd16-00d2-45a2-884a-8ba0c3a90c90

## Features

### Core Tools

- **send-email**: Send email to recipient
- **trash-email**: Move email to trash
- **mark-email-as-read**: Mark email as read
- **get-unread-emails**: Retrieve unread emails
- **read-email**: Retrieve email content
- **open-email**: Open email in browser
- **search-emails**: Search emails with custom queries
- **create-draft**: Create a draft email
- **list-drafts**: List email drafts

### Enhanced Tools (Available in Enhanced Server)

- **list-emails**: List emails with pagination support
- **download-attachment**: Download email attachments
- **send-email-with-attachment**: Send emails with attachments
- **manage-labels**: Add or remove labels from emails
- **list-labels**: List all available Gmail labels

### Security Features

- **Encrypted Token Storage**: OAuth tokens are encrypted using machine-specific keys
- **Secure File Permissions**: Token files are stored with 600 permissions
- **Fallback Compatibility**: Graceful fallback to plaintext for compatibility

### Prompts

The server includes specialized prompts for email management:
- **manage-email**: Act as an email administrator
- **draft-email**: Draft an email with content and recipient
- **edit-draft**: Edit an existing email draft

## Setup

### Gmail API Setup

1. [Create a new Google Cloud project](https://console.cloud.google.com/projectcreate)
2. [Enable the Gmail API](https://console.cloud.google.com/workspace-api/products)
3. [Configure an OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent) 
    - Choose "External" user type
    - Set the publishing status to **Testing** (not Production)
    - Fill in the required fields (app name, user support email, developer email)
    - Add your Gmail address as a **Test user** (this is crucial!)
4. Add OAuth scope `https://www.googleapis.com/auth/gmail.modify`
5. [Create an OAuth Client ID](https://console.cloud.google.com/apis/credentials/oauthclient) for application type "Desktop App"
6. Download the JSON file of your client's OAuth keys
7. Rename the key file and save it to your local machine in a secure location.

> **Important**: If you get an "Access blocked" error during authentication, make sure your OAuth consent screen is in "Testing" mode and your email is added as a test user. See [OAuth Troubleshooting](docs/OAUTH_TROUBLESHOOTING.md) for details.

### Installation

Using [uv](https://docs.astral.sh/uv/) is recommended:

```bash
# Clone the repository
git clone https://github.com/yourusername/gmail-mcp-server.git
cd gmail-mcp-server

# Install dependencies
uv pip install -e .

# For development
uv pip install -e ".[dev]"
```

### Usage with Claude Desktop

#### Standard Server
```json
{
  "mcpServers": {
    "gmail": {
      "command": "uv",
      "args": [
        "--directory",
        "[absolute-path-to-git-repo]",
        "run",
        "gmail",
        "--creds-file-path",
        "[absolute-path-to-credentials-file]",
        "--token-path",
        "[absolute-path-to-access-tokens-file]"
      ]
    }
  }
}
```

#### Enhanced Server (with all features)
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
        "[absolute-path-to-credentials-file]",
        "--token-path",
        "[absolute-path-to-access-tokens-file]"
      ]
    }
  }
}
```

### Authentication

When the server is started, an authentication flow will be launched in your system browser. 
Token credentials will be encrypted and securely saved in the specified token path.

| Parameter       | Example                                          |
|-----------------|--------------------------------------------------|
| `--creds-file-path` | `/[your-home-folder]/.google/client_creds.json` |
| `--token-path`      | `/[your-home-folder]/.google/app_tokens.json`    |

## API Reference

### Standard Tools

#### send-email
```typescript
{
  recipient_id: string,    // Recipient email address
  subject: string,         // Email subject
  message: string,         // Email content
  thread_id?: string       // Optional thread ID for replies
}
```

#### search-emails
```typescript
{
  query: string,           // Gmail search query
  max_results?: number     // Maximum results (default: 20)
}
```

### Enhanced Tools

#### list-emails (Pagination Support)
```typescript
{
  query?: string,          // Gmail search query (default: "in:inbox")
  page_size?: number,      // Results per page (default: 20)
  page_token?: string      // Token for next page
}
```

#### send-email-with-attachment
```typescript
{
  recipient_id: string,    // Recipient email address
  subject: string,         // Email subject
  message: string,         // Email content
  attachment_paths: string[], // Array of file paths to attach
  thread_id?: string       // Optional thread ID for replies
}
```

#### manage-labels
```typescript
{
  email_id: string,        // Email ID
  add_labels?: string[],   // Labels to add
  remove_labels?: string[] // Labels to remove
}
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=gmail --cov-report=html

# Run specific test file
uv run pytest tests/test_gmail_service.py
```

### Code Quality

```bash
# Format code
uv run black src/gmail tests

# Sort imports
uv run isort src/gmail tests

# Type checking
uv run mypy src/gmail

# Linting
uv run flake8 src/gmail tests
```

### Project Structure

```
gmail-mcp-server/
├── src/
│   └── gmail/
│       ├── __init__.py
│       ├── server.py                    # Standard server
│       ├── server_enhanced.py           # Enhanced server with all features
│       ├── constants.py
│       └── services/
│           ├── __init__.py
│           ├── gmail_service.py         # Core Gmail functionality
│           ├── gmail_service_enhanced.py # Extended features
│           └── security.py              # Token encryption utilities
├── tests/
│   ├── __init__.py
│   └── test_gmail_service.py
├── pyproject.toml
├── README.md
├── SECURITY.md
└── LICENSE
```

## Security Considerations

This server implements several security best practices:

1. **Token Encryption**: OAuth tokens are encrypted using Fernet encryption with machine-specific keys
2. **Secure File Permissions**: Token files are stored with restrictive permissions (600)
3. **No Hardcoded Secrets**: All sensitive data is provided via command-line arguments
4. **User Confirmation**: Sensitive operations require user confirmation
5. **Secure Defaults**: The server starts in safe mode, requiring explicit user action for sensitive operations

For more details, see [SECURITY.md](SECURITY.md).

## Troubleshooting

### OAuth Authentication Issues

If you encounter "Access blocked" or "Gmail MCP has not completed the Google verification process" errors:

1. Ensure your OAuth consent screen is in **Testing** mode
2. Add your email as a **Test user**
3. Clear existing tokens and re-authenticate

See [OAuth Troubleshooting Guide](docs/OAUTH_TROUBLESHOOTING.md) for detailed solutions.

### MCP Inspector

To test the server, use [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector):

```bash
# Standard server
npx @modelcontextprotocol/inspector uv run src/gmail/server.py --creds-file-path [path] --token-path [path]

# Enhanced server
npx @modelcontextprotocol/inspector uv run src/gmail/server_enhanced.py --creds-file-path [path] --token-path [path]
```

### Common Issues

1. **Access Denied Errors**: Check OAuth setup and test users - see [OAuth Troubleshooting](docs/OAUTH_TROUBLESHOOTING.md)
2. **Token Decryption Errors**: If you move between machines, tokens might fail to decrypt. Delete the token file and re-authenticate.
3. **Permission Errors**: Ensure the token directory has proper permissions
4. **API Limits**: Gmail API has rate limits. Implement exponential backoff for production use.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built for the Model Context Protocol (MCP)
- Uses Google Gmail API
- Inspired by the need for secure email automation
