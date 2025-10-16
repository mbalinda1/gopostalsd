# Email Service Setup Guide

This guide walks you through setting up the email service for the Go Postal SD application using MailerSend.

## 🚀 Quick Start

### 1. Create MailerSend Account
1. Go to [MailerSend](https://www.mailersend.com/)
2. Sign up for a free account
3. Verify your email address

### 2. Get API Key
1. Go to [API Tokens](https://app.mailersend.com/api-tokens)
2. Click "Create API Token"
3. Give it a name like "Go Postal SD"
4. Copy the generated API key

### 3. Set Environment Variables
Create a `.env` file in the `backend/` directory:

```bash
# MailerSend Configuration
MAILERSEND_API_KEY=your-mailersend-api-key-here

# Email Settings
FROM_EMAIL=noreply@gopostalsd.com
FROM_NAME=Go Postal SD
FRONTEND_URL=http://localhost:3000

# Other required variables
ENVIRONMENT=development
DATABASE_URL=postgresql://username:password@localhost:5432/gopostalsd
JWT_SECRET_KEY=your-super-secret-jwt-key-here
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=604800
SINALITE_API_URL=https://api.sinaliteuppy.com
SINALITE_API_KEY=your-sinalite-api-key
```

### 4. Test Configuration
```bash
cd backend
python test_email.py
```

## 🔧 MailerSend Features

### Free Tier
- ✅ 3,000 emails/month
- ✅ 100 emails/day
- ✅ SMTP and API access
- ✅ Email templates
- ✅ Analytics

### Production Features
- ✅ High deliverability
- ✅ Domain authentication
- ✅ Bounce handling
- ✅ Unsubscribe management
- ✅ Email tracking

## 📧 Email Types Supported

The system automatically handles these email types:

1. **Email Verification** - When users register
2. **Password Reset** - When users request password reset
3. **Contact Form** - When users submit contact form
4. **Custom Emails** - For any other email needs

## 🛡️ Security Best Practices

### 1. API Key Security
- Never commit API keys to version control
- Use different keys for development/production
- Rotate keys regularly

### 2. Domain Authentication
For production, set up domain authentication:
1. Go to [Domains](https://app.mailersend.com/domains)
2. Add your domain (e.g., gopostalsd.com)
3. Add the required DNS records
4. Verify domain ownership

### 3. Rate Limiting
MailerSend has built-in rate limiting:
- Free tier: 100 emails/day
- Paid tiers: Higher limits

## 🧪 Testing

### Test Script
```bash
cd backend
python test_email.py
```

### Manual Testing
```python
from server.services.email_service import EmailService

email_service = EmailService()
email_service.init_app(app)

result = email_service.send_verification_email(
    email="test@example.com",
    first_name="Test",
    token="test-token"
)
print(f"Email sent: {result['success']}")
```

## 🚨 Troubleshooting

### Common Issues

1. **"MailerSend not configured"**
   - Check if `MAILERSEND_API_KEY` is set
   - Verify the API key is correct
   - Check if the key has proper permissions

2. **"API error"**
   - Check MailerSend service status
   - Verify API key permissions
   - Check rate limits

3. **"Email not delivered"**
   - Check spam folder
   - Verify recipient email address
   - Check domain authentication

### Debug Mode
```python
import logging
logging.getLogger('server.thirdparty.mailersend').setLevel(logging.DEBUG)
```

## 📊 Monitoring

### MailerSend Dashboard
- Go to [MailerSend Dashboard](https://app.mailersend.com/)
- View email statistics
- Monitor delivery rates
- Check bounce rates

### Application Logs
All email operations are logged:
- Success/failure status
- Error details
- Recipient information (email only)

## 🚀 Production Setup

### 1. Domain Authentication
1. Add your domain in MailerSend
2. Add DNS records
3. Verify domain ownership
4. Update `FROM_EMAIL` to use your domain

### 2. Environment Variables
```bash
# Production example
MAILERSEND_API_KEY=your-production-api-key
FROM_EMAIL=noreply@gopostalsd.com
FROM_NAME=Go Postal SD
FRONTEND_URL=https://gopostalsd.com
```

### 3. Monitoring
- Set up alerts for failed emails
- Monitor delivery rates
- Track bounce rates
- Watch for spam complaints

## 📈 Scaling

### Upgrade Tiers
- **Free**: 3,000 emails/month
- **Starter**: $9/month for 10,000 emails
- **Pro**: $25/month for 50,000 emails
- **Business**: Custom pricing

### Best Practices
- Use email templates for consistency
- Implement proper error handling
- Monitor delivery rates
- Set up proper bounce handling

## 🔄 Migration from Other Providers

If migrating from another email provider:

1. **Export your email list** (if applicable)
2. **Set up MailerSend** with your domain
3. **Update environment variables**
4. **Test thoroughly** before going live
5. **Monitor delivery rates** after migration

## 📚 Additional Resources

- [MailerSend Documentation](https://developers.mailersend.com/)
- [API Reference](https://developers.mailersend.com/api/)
- [Email Templates](https://app.mailersend.com/templates)
- [Analytics](https://app.mailersend.com/analytics)

This setup provides a robust, scalable email solution for Go Postal SD! 🎉
