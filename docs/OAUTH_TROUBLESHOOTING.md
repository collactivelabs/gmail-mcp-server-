# OAuth Authentication Troubleshooting

## Error: "Gmail MCP has not completed the Google verification process"

This error occurs when the OAuth consent screen is misconfigured. Follow these steps to resolve it:

### Quick Fix: Configure for Testing

1. **Set OAuth Consent Screen to Testing Mode**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Navigate to "APIs & Services" → "OAuth consent screen"
   - Set the publishing status to **Testing** (not Production)
   - Save changes

2. **Add Test Users**
   - In the OAuth consent screen, scroll to "Test users"
   - Click "Add Users"
   - Add your Gmail email address
   - Add any other email addresses you'll use for testing
   - Save changes

3. **Verify OAuth Client Settings**
   - Go to "APIs & Services" → "Credentials"
   - Click on your OAuth 2.0 Client ID
   - Ensure:
     - Application type: "Desktop app"
     - Name: Your app name (e.g., "Gmail MCP Server")
   - Download the JSON file again if needed

### Alternative: Use Internal App Type

If you're using this for a Google Workspace account:

1. Go to OAuth consent screen
2. Choose "Internal" instead of "External"
3. This bypasses the verification requirement
4. Only available for Google Workspace accounts

### Clear Existing Tokens

After making these changes, clear any existing tokens:

```bash
# Remove the existing token file
rm /path/to/your/app_token.json

# Restart Claude Desktop
# The authentication flow will start fresh
```

### Common Issues and Solutions

#### Issue: Still Getting Access Denied
- Ensure you're logged in with the correct Google account
- The account must be listed as a test user
- Clear browser cookies and try again

#### Issue: Consent Screen Shows Warnings
- This is normal for unverified apps in testing mode
- Click "Continue" when prompted
- The warning appears because the app isn't verified

#### Issue: Can't Add Test Users
- Make sure the OAuth consent screen is in "Testing" mode
- You can add up to 100 test users
- Test users must have valid Google accounts

### Long-term Solution: App Verification

For production use with multiple users:

1. Complete the [Google OAuth verification process](https://support.google.com/cloud/answer/7454865)
2. Provide required information:
   - Privacy policy URL
   - Terms of service URL
   - Authorized domains
   - App logo
3. Wait for Google's review (can take several days)

### Development Best Practices

1. **Use Testing Mode for Development**
   - Always start in testing mode
   - Only move to production when needed
   - Keep test user list updated

2. **Separate Development and Production**
   - Use different projects for dev/prod
   - Maintain separate OAuth clients
   - Use environment-specific credentials

3. **Security Considerations**
   - Never share OAuth client secrets
   - Use secure token storage
   - Rotate credentials periodically

### Need More Help?

If you're still experiencing issues:

1. Check the [Google OAuth 2.0 documentation](https://developers.google.com/identity/protocols/oauth2)
2. Review the [Gmail API documentation](https://developers.google.com/gmail/api/guides)
3. Open an issue on the [Gmail MCP Server repository](https://github.com/yourusername/gmail-mcp-server/issues)

### Related Documentation

- [Quick Start Guide](QUICKSTART.md)
- [Security Guide](../SECURITY.md)
- [API Reference](API.md)
