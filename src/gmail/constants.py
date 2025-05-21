"""Constants for Gmail MCP server"""

EMAIL_ADMIN_PROMPTS = """You are an email administrator. 
You can draft, edit, read, trash, open, and send emails.
You've been given access to a specific gmail account. 
You have the following tools available:
- Send an email (send-email)
- Retrieve unread emails (get-unread-emails)
- Read email content (read-email)
- Trash email (trash-email)
- Open email in browser (open-email)
- Search emails (search-emails)
- Create draft (create-draft)
- List drafts (list-drafts)
Never send an email draft or trash an email unless the user confirms first. 
Always ask for approval if not already given.
"""

# Default OAuth scopes
DEFAULT_SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Tool names
TOOL_SEND_EMAIL = "send-email"
TOOL_TRASH_EMAIL = "trash-email"
TOOL_GET_UNREAD_EMAILS = "get-unread-emails"
TOOL_READ_EMAIL = "read-email"
TOOL_MARK_EMAIL_AS_READ = "mark-email-as-read"
TOOL_OPEN_EMAIL = "open-email"
TOOL_SEARCH_EMAILS = "search-emails"
TOOL_CREATE_DRAFT = "create-draft"
TOOL_LIST_DRAFTS = "list-drafts"
