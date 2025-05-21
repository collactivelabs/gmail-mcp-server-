# Quick Start Guide

Get up and running with the Gmail MCP Server in 5 minutes!

## Prerequisites

- Python 3.12+
- A Google account
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Step 1: Gmail API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable the Gmail API:
   ```
   APIs & Services → Library → Search "Gmail API" → Enable
   ```
4. Create credentials:
   ```
   APIs & Services → Credentials → Create Credentials → OAuth client ID
   ```
5. Select "Desktop app" as the application type
6. Download the JSON file and save it securely

## Step 2: Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/gmail-mcp-server.git
cd gmail-mcp-server

# Install with uv (recommended)
uv pip install -e .

# Or with pip
pip install -e .
```

## Step 3: Configuration

### For Claude Desktop

1. Find your Claude configuration file:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. Add the Gmail server configuration:

```json
{
  "mcpServers": {
    "gmail": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/gmail-mcp-server",
        "run",
        "gmail",
        "--creds-file-path",
        "/path/to/your/credentials.json",
        "--token-path",
        "/path/to/store/app_token.json"
      ]
    }
  }
}
```

3. Restart Claude Desktop

## Step 4: First Run

1. Start Claude Desktop
2. The first time you use Gmail commands, a browser window will open
3. Authenticate with your Google account
4. Grant the requested permissions
5. The token will be saved and encrypted automatically

## Step 5: Test It Out

Try these commands in Claude:

```
"Show me my unread emails"
"Search for emails from john@example.com"
"Draft an email to alice@example.com about the meeting tomorrow"
```

## Common Issues

### Browser doesn't open for authentication
- Check if your default browser is set correctly
- Try manually copying the URL from the console

### Permission denied errors
```bash
chmod 600 /path/to/your/app_token.json
```

### Can't find unread emails
- Make sure you're checking the right inbox (primary by default)
- Try using the search function: "search for emails with subject meeting"

## Next Steps

- Read the [full documentation](../README.md)
- Explore [advanced features](../README.md#enhanced-tools)
- Check [security best practices](../SECURITY.md)

## Need Help?

- Review the [troubleshooting guide](../README.md#troubleshooting)
- Check [open issues](https://github.com/yourusername/gmail-mcp-server/issues)
- Open a new issue with detailed information
