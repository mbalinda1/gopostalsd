# Documentation Changelog

## Recent Updates

### 2024-01-XX - Reply-To Email Support Added

**Changes Made:**
- Added reply-to functionality to all email adapters and services
- MailerSendAdapter now supports `reply_to` parameter in `send_email()` method
- SMTPAdapter now supports `reply_to` parameter in `send_email()` method
- EmailService updated to pass through reply-to parameter to all email methods
- Reply-to defaults to `FROM_EMAIL` environment variable when not specified
- Contact form emails now use customer's email as reply-to for better communication

**Technical Implementation:**
- MailerSendAdapter: Uses `email.set_reply_to(reply_to_email)` method
- SMTPAdapter: Sets `msg['Reply-To'] = reply_to_email` header
- EmailService: All methods (`send_verification_email`, `send_password_reset_email`, `send_contact_email`) now support `reply_to` parameter
- Contact emails: Reply-to defaults to customer's email for direct communication

**Documentation Updated:**
- `docs/mailersend-adapter.md` - Added reply-to examples and technical implementation
- `docs/smtp-adapter.md` - Added reply-to functionality section with examples
- `docs/CHANGELOG.md` - Documented the new feature

**Files Modified:**
- `backend/server/thirdparty/mailersend.py` - Added reply-to support
- `backend/server/thirdparty/smtp.py` - Added reply-to support  
- `backend/server/services/email_service.py` - Updated all email methods
- `docs/mailersend-adapter.md` - Updated documentation
- `docs/smtp-adapter.md` - Updated documentation

**Impact:**
- Better email communication flow
- Replies go to appropriate addresses (customer email for contact forms)
- Maintains FROM_EMAIL as default when no reply-to specified
- Consistent behavior across all email providers

---

### 2024-01-XX - MailerSendAdapter API Update

**Changes Made:**
- Updated MailerSendAdapter to use correct MailerSend Python SDK API
- Changed from `MailerSendSDK` to `MailerSendClient` and `Email` classes
- Fixed import statements: `from mailersend import MailerSendClient, Email`
- Updated email sending method to use proper SDK methods:
  - `email.set_from()`, `email.set_to()`, `email.set_subject()`, etc.
  - `client.send(email)` instead of `client.send(email_data)`

**Documentation Updated:**
- `docs/mailersend-adapter.md` - Updated technical implementation section
- `docs/mailersend-adapter.md` - Updated testing examples
- `docs/mailersend-adapter.md` - Added note about official SDK usage

**Files Modified:**
- `backend/server/thirdparty/mailersend.py` - Core adapter implementation
- `docs/mailersend-adapter.md` - Documentation updates

**Impact:**
- MailerSend integration now uses the correct official SDK
- Better error handling and response management
- More reliable email delivery
- Updated documentation reflects actual implementation

---

## Documentation Maintenance Guidelines

When making changes to the backend:

1. **Update relevant adapter documentation** in `docs/` folder
2. **Update API examples** to match actual implementation
3. **Update testing examples** to reflect new API usage
4. **Add changelog entries** for significant changes
5. **Verify documentation accuracy** by testing examples

### Files to Update When Making Changes:

- **SinaliteAdapter changes** → Update `docs/sinalite-adapter.md`
- **MailerSendAdapter changes** → Update `docs/mailersend-adapter.md`
- **SMTPAdapter changes** → Update `docs/smtp-adapter.md`
- **SupabaseAdapter changes** → Update `docs/supabase-adapter.md`
- **Server architecture changes** → Update `docs/server-architecture.md`
- **API endpoint changes** → Update `docs/api-endpoints.md`
