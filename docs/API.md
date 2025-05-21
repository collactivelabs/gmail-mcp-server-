# Gmail MCP Server API Reference

Complete API documentation for all available tools and prompts.

## Table of Contents

- [Core Tools](#core-tools)
- [Enhanced Tools](#enhanced-tools)
- [Prompts](#prompts)
- [Types](#types)
- [Error Handling](#error-handling)

## Core Tools

### send-email

Send an email to a recipient.

```typescript
interface SendEmailParams {
  recipient_id: string;    // Email address of the recipient
  subject: string;         // Email subject line
  message: string;         // Email body content
  thread_id?: string;      // Optional: Thread ID for replies
}

interface SendEmailResponse {
  status: "success" | "error";
  message_id?: string;     // ID of sent message (on success)
  error_message?: string;  // Error description (on failure)
}
```

**Example:**
```json
{
  "recipient_id": "john@example.com",
  "subject": "Meeting Tomorrow",
  "message": "Let's meet at 10 AM tomorrow.",
  "thread_id": "thread_123"
}
```

### get-unread-emails

Retrieve unread emails from the inbox.

```typescript
interface GetUnreadEmailsParams {
  query?: string;        // Additional search filters
  max_results?: number;  // Maximum results to return (default: 20)
}

interface GetUnreadEmailsResponse {
  emails: Array<{
    id: string;
    threadId: string;
  }>;
}
```

### read-email

Read the content of a specific email.

```typescript
interface ReadEmailParams {
  email_id: string;      // Email ID to read
}

interface ReadEmailResponse {
  subject: string;       // Email subject
  from: string;          // Sender email
  to: string;            // Recipient email
  date: string;          // Date sent
  content: string;       // Email body
  content_type: "text" | "html";
  thread_id: string;     // Thread ID for replies
  message_id: string;    // Message ID
  attachments?: Array<{  // Available in enhanced version
    filename: string;
    mime_type: string;
    size: number;
    attachment_id: string;
  }>;
}
```

### search-emails

Search emails using Gmail query syntax.

```typescript
interface SearchEmailsParams {
  query: string;         // Gmail search query
  max_results?: number;  // Maximum results (default: 20)
}

interface SearchEmailsResponse {
  emails: Array<{
    id: string;
    threadId: string;
  }>;
}
```

**Query Examples:**
- `from:john@example.com`
- `subject:meeting`
- `is:unread`
- `has:attachment`
- `after:2024/1/1`

### trash-email

Move an email to trash.

```typescript
interface TrashEmailParams {
  email_id: string;      // Email ID to trash
}

interface TrashEmailResponse {
  message: string;       // Success/error message
}
```

### mark-email-as-read

Mark an email as read.

```typescript
interface MarkAsReadParams {
  email_id: string;      // Email ID to mark as read
}

interface MarkAsReadResponse {
  message: string;       // Success/error message
}
```

### open-email

Open an email in the default browser.

```typescript
interface OpenEmailParams {
  email_id: string;      // Email ID to open
}

interface OpenEmailResponse {
  message: string;       // Success/error message
}
```

### create-draft

Create a new email draft.

```typescript
interface CreateDraftParams {
  recipient: string;     // Recipient email address
  subject: string;       // Draft subject
  message: string;       // Draft content
}

interface CreateDraftResponse {
  status: "success" | "error";
  draft_id?: string;     // Draft ID (on success)
  error_message?: string; // Error description (on failure)
}
```

### list-drafts

List all email drafts.

```typescript
interface ListDraftsParams {
  max_results?: number;  // Maximum results (default: 10)
}

interface ListDraftsResponse {
  drafts: Array<{
    id: string;
    message: {
      id: string;
    };
  }>;
}
```

## Enhanced Tools

Available only in the enhanced server (`server_enhanced.py`).

### list-emails

List emails with full pagination support.

```typescript
interface ListEmailsParams {
  query?: string;        // Gmail search query (default: "in:inbox")
  page_size?: number;    // Results per page (default: 20)
  page_token?: string;   // Token for next page
}

interface ListEmailsResponse {
  emails: Array<{
    id: string;
    threadId: string;
  }>;
  next_page_token?: string; // Token for next page
}
```

### download-attachment

Download an attachment from an email.

```typescript
interface DownloadAttachmentParams {
  email_id: string;      // Email containing the attachment
  attachment_id: string; // Attachment ID to download
  save_path: string;     // Local path to save file
}

interface DownloadAttachmentResponse {
  status: "success" | "error";
  message: string;       // Status message
  error_message?: string; // Error description (on failure)
}
```

### send-email-with-attachment

Send an email with attachments.

```typescript
interface SendEmailWithAttachmentParams {
  recipient_id: string;      // Recipient email address
  subject: string;           // Email subject
  message: string;           // Email body
  attachment_paths: string[]; // Local paths to files to attach
  thread_id?: string;        // Optional: Thread ID for replies
}

interface SendEmailWithAttachmentResponse {
  status: "success" | "error";
  message_id?: string;       // ID of sent message (on success)
  error_message?: string;    // Error description (on failure)
}
```

### manage-labels

Add or remove labels from an email.

```typescript
interface ManageLabelsParams {
  email_id: string;          // Email to modify
  add_labels?: string[];     // Label IDs to add
  remove_labels?: string[];  // Label IDs to remove
}

interface ManageLabelsResponse {
  status: "success" | "error";
  message: string;           // Status message
  error_message?: string;    // Error description (on failure)
}
```

### list-labels

List all available Gmail labels.

```typescript
interface ListLabelsParams {
  // No parameters required
}

interface ListLabelsResponse {
  labels: Array<{
    id: string;              // Label ID
    name: string;            // Label name
    type: "system" | "user"; // Label type
    messageListVisibility?: "show" | "hide";
    labelListVisibility?: "labelShow" | "labelShowIfUnread" | "labelHide";
  }>;
}
```

## Prompts

### manage-email

Provides instructions for email management.

```typescript
interface ManageEmailPrompt {
  name: "manage-email";
  arguments: null;
}
```

Returns a system prompt with email management instructions.

### draft-email

Create an email draft with guided prompts.

```typescript
interface DraftEmailPrompt {
  name: "draft-email";
  arguments: {
    content: string;        // What the email is about
    recipient: string;      // Who should receive it
    recipient_email: string; // Recipient's email address
  };
}
```

### edit-draft

Edit an existing email draft.

```typescript
interface EditDraftPrompt {
  name: "edit-draft";
  arguments: {
    changes: string;        // What changes to make
    current_draft: string;  // Current draft content
  };
}
```

## Types

### Email Object

```typescript
interface Email {
  id: string;               // Unique email ID
  threadId: string;         // Thread ID
  labelIds: string[];       // Applied labels
  snippet: string;          // Email preview
}
```

### Label Object

```typescript
interface Label {
  id: string;               // Label ID
  name: string;             // Label name
  type: "system" | "user";  // Label type
  color?: {
    textColor: string;      // Text color code
    backgroundColor: string; // Background color code
  };
}
```

### Thread Object

```typescript
interface Thread {
  id: string;               // Thread ID
  messages: Email[];        // Messages in thread
  snippet: string;          // Thread preview
}
```

## Error Handling

All tools return consistent error responses:

```typescript
interface ErrorResponse {
  status: "error";
  error_message: string;    // Human-readable error description
  error_code?: string;      // Optional error code
  error_details?: any;      // Optional additional details
}
```

### Common Error Codes

- `AUTH_ERROR`: Authentication failure
- `NOT_FOUND`: Email or resource not found
- `QUOTA_EXCEEDED`: API quota exceeded
- `INVALID_PARAMS`: Invalid parameters provided
- `PERMISSION_DENIED`: Insufficient permissions

### Error Examples

```json
{
  "status": "error",
  "error_message": "Email not found",
  "error_code": "NOT_FOUND",
  "error_details": {
    "email_id": "invalid_id_123"
  }
}
```

## Rate Limits

Gmail API has the following limits:
- Daily quota: 1,000,000,000 quota units
- Per-user rate limit: 250 quota units per user per second
- Sending limits: Varies by account type

### Quota Costs

| Operation | Quota Cost |
|-----------|------------|
| messages.send | 100 units |
| messages.get | 5 units |
| messages.list | 5 units |
| messages.modify | 5 units |
| messages.trash | 5 units |

## Best Practices

1. **Batch Operations**: Use batch requests for multiple operations
2. **Pagination**: Always implement pagination for list operations
3. **Error Handling**: Implement exponential backoff for rate limits
4. **Caching**: Cache frequently accessed data like labels
5. **Scopes**: Request minimal required OAuth scopes

## Examples

### Complete Email Workflow

```python
# Search for unread emails
search_result = await search_emails({
  "query": "is:unread from:important@example.com"
})

# Read first email
if search_result.emails:
    email_content = await read_email({
        "email_id": search_result.emails[0].id
    })
    
    # Reply to email
    reply_result = await send_email({
        "recipient_id": email_content.from,
        "subject": f"Re: {email_content.subject}",
        "message": "Thank you for your email...",
        "thread_id": email_content.thread_id
    })
```

### Attachment Handling

```python
# Read email with attachments
email = await read_email_with_attachments({
    "email_id": "email_123"
})

# Download all attachments
for attachment in email.attachments:
    await download_attachment({
        "email_id": "email_123",
        "attachment_id": attachment.attachment_id,
        "save_path": f"/tmp/{attachment.filename}"
    })
```
