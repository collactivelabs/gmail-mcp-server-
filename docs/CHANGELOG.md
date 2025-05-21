# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2024-XX-XX

### Added
- Token encryption using Fernet with machine-specific keys
- Secure file permissions (600) for token storage
- Support for email attachments (download and send)
- Full pagination support with page tokens
- Label management functionality
- Enhanced server implementation with all features
- Comprehensive test suite with pytest
- Security documentation
- Development tools configuration (black, isort, mypy, flake8)

### Changed
- Restructured code into modular services
- Improved email parsing with HTML support
- Enhanced error handling throughout
- Updated documentation with new features

### Fixed
- Typo in tool description ("tras-email" → "trash-email")
- Improved handling of multipart email messages
- Better error messages for failed operations

### Security
- Implemented encrypted token storage
- Added secure file permissions
- Machine-specific encryption keys
- Fallback compatibility for existing plaintext tokens

## [0.1.0] - 2024-XX-XX

### Added
- Initial release
- Basic Gmail operations (send, read, trash)
- OAuth 2.0 authentication
- MCP server implementation
- Basic documentation
- Claude Desktop integration support

### Features
- Send emails
- Read emails
- Mark emails as read
- Get unread emails
- Trash emails
- Open emails in browser
- Draft management
- Basic prompts for email operations
