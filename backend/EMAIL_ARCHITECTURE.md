# Email Service Architecture

This document describes the email service architecture implemented for Go Postal SD, following the same design patterns as the storage and third-party services.

## 🏗️ Architecture Overview

The email system follows a **Factory Pattern** with **Strategy Pattern** implementation, similar to the storage service architecture:

```
BaseEmailService (Abstract Base Class)
├── SMTPEmailService (SMTP Implementation)
├── SendGridEmailServiceWrapper (SendGrid Wrapper)
└── MailerSendEmailServiceWrapper (MailerSend Wrapper)

EmailServiceFactory (Factory for creating instances)
├── Auto-detection based on environment variables
├── Provider validation
└── Configuration management
```

## 📁 File Structure

### Core Services
- **`server/services/email_service.py`** - Abstract base class with common email methods
- **`server/services/smtp_email_service.py`** - SMTP implementation
- **`server/services/sendgrid_email_service.py`** - SendGrid wrapper
- **`server/services/mailersend_email_service.py`** - MailerSend wrapper

### Third-Party Integrations
- **`server/thirdparty/sendgrid.py`** - SendGrid API integration
- **`server/thirdparty/mailersend.py`** - MailerSend API integration

### Factory Pattern
- **`server/factories/email_factory.py`** - Email service factory
- **`server/factories/service_factory.py`** - Updated to use email factory

## 🔧 Email Providers

### 1. SMTP (Gmail/Generic SMTP)
**File:** `server/services/smtp_email_service.py`
**Third-party:** Built-in Python `smtplib`

**Configuration:**
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

**Pros:**
- ✅ No external dependencies
- ✅ Works with any SMTP server
- ✅ Good for development and small production

**Cons:**
- ❌ Limited deliverability features
- ❌ No analytics or tracking
- ❌ Manual rate limiting needed

### 2. SendGrid
**File:** `server/thirdparty/sendgrid.py` + `server/services/sendgrid_email_service.py`
**Third-party:** `sendgrid` Python library

**Configuration:**
```bash
SENDGRID_API_KEY=your-sendgrid-api-key
```

**Pros:**
- ✅ High deliverability
- ✅ Analytics and tracking
- ✅ Professional features
- ✅ Scalable

**Cons:**
- ❌ Paid service (but generous free tier)
- ❌ External dependency

### 3. MailerSend
**File:** `server/thirdparty/mailersend.py` + `server/services/mailersend_email_service.py`
**Third-party:** `mailersend` Python library

**Configuration:**
```bash
MAILERSEND_API_KEY=your-mailersend-api-key
```

**Pros:**
- ✅ High deliverability
- ✅ Good pricing
- ✅ Professional features
- ✅ Good documentation

**Cons:**
- ❌ External dependency
- ❌ Less popular than SendGrid

## 🚀 Usage Examples

### Basic Usage
```python
from server.factories.email_factory import EmailServiceFactory

# Auto-detect provider based on environment variables
email_service = EmailServiceFactory.create_email_service()
email_service.init_app(app)

# Send verification email
result = email_service.send_verification_email(
    email="user@example.com",
    first_name="John",
    token="verification-token-123"
)
```

### Specific Provider
```python
# Force specific provider
email_service = EmailServiceFactory.create_email_service('sendgrid')
email_service.init_app(app)
```

### Configuration Validation
```python
# Check available providers
providers = EmailServiceFactory.get_available_providers()
print(f"Available providers: {providers}")

# Validate specific provider
validation = EmailServiceFactory.validate_provider_config('sendgrid')
if validation['valid']:
    print("SendGrid is properly configured")
else:
    print(f"Missing variables: {validation['missing_vars']}")
```

## 🔄 Factory Pattern Implementation

### EmailServiceFactory
The factory automatically detects the best available email provider:

1. **Priority Order:**
   - SendGrid (if `SENDGRID_API_KEY` is set)
   - MailerSend (if `MAILERSEND_API_KEY` is set)
   - SMTP (if `SMTP_USERNAME` and `SMTP_PASSWORD` are set)

2. **Auto-detection:**
   ```python
   provider = EmailServiceFactory._detect_provider()
   ```

3. **Manual Selection:**
   ```python
   email_service = EmailServiceFactory.create_email_service('smtp')
   ```

## 📧 Email Types Supported

All email services support these common email types:

### 1. Email Verification
```python
email_service.send_verification_email(email, first_name, token)
```

### 2. Password Reset
```python
email_service.send_password_reset_email(email, first_name, token)
```

### 3. Contact Form
```python
email_service.send_contact_email(name, email, phone, subject, message)
```

### 4. Custom Email
```python
email_service.send_email(to_email, subject, text_content, html_content)
```

## 🛡️ Security Features

### 1. Environment Variable Management
- All credentials stored in environment variables
- No hardcoded secrets
- Proper `.gitignore` configuration

### 2. Configuration Validation
- Automatic validation of required variables
- Clear error messages for missing configuration
- Provider-specific validation

### 3. Error Handling
- Graceful fallback between providers
- Comprehensive error logging
- User-friendly error messages

## 🧪 Testing

### Test Configuration
```bash
cd backend
python test_email_config.py
```

This script will:
- ✅ Check email configuration
- ✅ Validate provider setup
- ✅ Test email sending
- ✅ Show available providers

### Manual Testing
```python
# Test specific provider
email_service = EmailServiceFactory.create_email_service('smtp')
email_service.init_app(app)

# Send test email
result = email_service.send_verification_email(
    email="test@example.com",
    first_name="Test",
    token="test-token"
)
print(f"Email sent: {result['success']}")
```

## 🔄 Migration from Old System

The new email system is **backward compatible** with the existing authentication system:

1. **No API Changes:** All existing email calls work unchanged
2. **Same Interface:** `send_verification_email`, `send_password_reset_email`, etc.
3. **Automatic Detection:** System automatically uses the best available provider

### Migration Steps
1. Install new dependencies: `pip install sendgrid mailersend`
2. Set up environment variables for your chosen provider
3. Restart the application
4. Test email functionality

## 📊 Monitoring and Logging

### Logging
All email operations are logged with:
- Provider used
- Recipient (email address only)
- Success/failure status
- Error details (if any)

### Monitoring
- Email delivery success rates
- Provider performance
- Error frequency
- Configuration validation

## 🚀 Production Recommendations

### Development
- Use **SMTP (Gmail)** for development
- Set up app passwords for Gmail
- Use manual verification endpoint for testing

### Production
- Use **SendGrid** or **MailerSend** for production
- Set up proper domain authentication
- Monitor delivery rates and bounces
- Implement rate limiting

### Environment Variables
```bash
# Production example
SENDGRID_API_KEY=your-production-api-key
FROM_EMAIL=noreply@gopostalsd.com
FROM_NAME=Go Postal SD
FRONTEND_URL=https://gopostalsd.com
```

## 🔧 Troubleshooting

### Common Issues

1. **"Email service not configured"**
   - Check environment variables
   - Run `python test_email_config.py`
   - Verify provider-specific configuration

2. **"Provider not available"**
   - Check if required environment variables are set
   - Verify API keys are valid
   - Check provider service status

3. **"Email sending failed"**
   - Check provider logs
   - Verify recipient email address
   - Check rate limits

### Debug Mode
```python
import logging
logging.getLogger('server.services.email_service').setLevel(logging.DEBUG)
logging.getLogger('server.thirdparty.sendgrid').setLevel(logging.DEBUG)
```

## 📈 Future Enhancements

### Planned Features
- Email templates management
- Delivery tracking
- Bounce handling
- Unsubscribe management
- A/B testing for email content

### Extensibility
The architecture makes it easy to add new email providers:
1. Create third-party integration in `server/thirdparty/`
2. Create service wrapper in `server/services/`
3. Update `EmailServiceFactory` to include new provider
4. Add configuration validation

This architecture provides a robust, scalable, and maintainable email system that follows the same patterns as the rest of the Go Postal SD application.

