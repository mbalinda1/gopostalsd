import os
import logging
from typing import Dict, Any
from flask import Flask
from server.thirdparty.mailersend import MailerSend

logger = logging.getLogger(__name__)

class EmailService:
    """MailerSend email service implementation."""
    
    def __init__(self):
        self.client = None
        self.base_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    
    def init_app(self, app: Flask):
        """Initialize MailerSend with Flask app."""
        try:
            self.client = MailerSend()
            if self.client.is_configured:
                logger.info("Email service initialized successfully")
            else:
                logger.warning("Email service initialized but not configured")
        except Exception as e:
            logger.error(f"Failed to initialize MailerSend: {str(e)}")
            self.client = None
    
    def send_email(self, to_email: str, subject: str, text_content: str, html_content: str = None) -> Dict[str, Any]:
        """
        Send email using MailerSend.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            text_content: Plain text content
            html_content: HTML content (optional)
        
        Returns:
            Dict containing send result
        """
        if not self.client:
            return {
                'success': False, 
                'error': 'Email service not configured. Set EMAIL_API_KEY environment variable.'
            }
        
        return self.client.send_email(to_email, subject, text_content, html_content)
    
    @property
    def is_configured(self) -> bool:
        """Check if MailerSend is properly configured."""
        return self.client and self.client.is_configured
    
    def send_verification_email(self, email: str, first_name: str, token: str) -> Dict[str, Any]:
        """Send email verification email."""
        subject = "Verify Your Email - Go Postal SD"
        
        verification_url = f"{self.base_url}/verify-email?token={token}"
        
        text_content = f"""
                Hello {first_name},

                Welcome to Go Postal SD! Please verify your email address to complete your registration.

                Click the link below to verify your email:
                {verification_url}

                If you didn't create an account with us, please ignore this email.

                Best regards,
                Go Postal SD Team
                        """.strip()
                        
                        html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>Verify Your Email</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                        .header {{ background-color: #1976d2; color: white; padding: 20px; text-align: center; }}
                        .content {{ padding: 20px; background-color: #f9f9f9; }}
                        .button {{ display: inline-block; background-color: #1976d2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 20px 0; }}
                        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 14px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>Welcome to Go Postal SD!</h1>
                        </div>
                        <div class="content">
                            <p>Hello {first_name},</p>
                            <p>Thank you for registering with Go Postal SD! To complete your registration, please verify your email address.</p>
                            <p style="text-align: center;">
                                <a href="{verification_url}" class="button">Verify Email Address</a>
                            </p>
                            <p>If the button doesn't work, you can also copy and paste this link into your browser:</p>
                            <p style="word-break: break-all; color: #1976d2;">{verification_url}</p>
                            <p>If you didn't create an account with us, please ignore this email.</p>
                        </div>
                        <div class="footer">
                            <p>Best regards,<br>Go Postal SD Team</p>
                        </div>
                    </div>
                </body>
                </html>
                """.strip()
        
        return self.send_email(email, subject, text_content, html_content)
    
    def send_password_reset_email(self, email: str, first_name: str, token: str) -> Dict[str, Any]:
        """Send password reset email."""
        subject = "Reset Your Password - Go Postal SD"
        
        reset_url = f"{self.base_url}/reset-password?token={token}"
        
        text_content = f"""
            Hello {first_name},

            You requested to reset your password for your Go Postal SD account.

            Click the link below to reset your password:
            {reset_url}

            This link will expire in 1 hour for security reasons.

            If you didn't request a password reset, please ignore this email.

            Best regards,
            Go Postal SD Team
                    """.strip()
                    
                    html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Reset Your Password</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #8B0000; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f9f9f9; }}
                    .button {{ display: inline-block; background-color: #8B0000; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 20px 0; }}
                    .footer {{ text-align: center; padding: 20px; color: #666; font-size: 14px; }}
                    .warning {{ background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 4px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Password Reset Request</h1>
                    </div>
                    <div class="content">
                        <p>Hello {first_name},</p>
                        <p>You requested to reset your password for your Go Postal SD account.</p>
                        <p style="text-align: center;">
                            <a href="{reset_url}" class="button">Reset Password</a>
                        </p>
                        <div class="warning">
                            <strong>Security Notice:</strong> This link will expire in 1 hour for security reasons.
                        </div>
                        <p>If the button doesn't work, you can also copy and paste this link into your browser:</p>
                        <p style="word-break: break-all; color: #8B0000;">{reset_url}</p>
                        <p>If you didn't request a password reset, please ignore this email.</p>
                    </div>
                    <div class="footer">
                        <p>Best regards,<br>Go Postal SD Team</p>
                    </div>
                </div>
            </body>
            </html>
                """.strip()
        
        return self.send_email(email, subject, text_content, html_content)
    
    def send_contact_email(self, name: str, email: str, phone: str, subject: str, message: str) -> bool:
        """Send contact form email to Go Postal."""
        email_subject = f"Contact Form: {subject}"
        
        text_content = f"""
            New contact form submission from Go Postal SD website:

            Name: {name}
            Email: {email}
            Phone: {phone or 'Not provided'}
            Subject: {subject}

            Message:
            {message}

            ---
            This message was sent from the Go Postal SD contact form.
                    """.strip()
                    
                    html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Contact Form Submission</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #1976d2; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f9f9f9; }}
                    .field {{ margin-bottom: 15px; }}
                    .label {{ font-weight: bold; color: #1976d2; }}
                    .message {{ background-color: white; padding: 15px; border-left: 4px solid #1976d2; margin: 15px 0; }}
                    .footer {{ text-align: center; padding: 20px; color: #666; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>New Contact Form Submission</h1>
                    </div>
                    <div class="content">
                        <div class="field">
                            <span class="label">Name:</span> {name}
                        </div>
                        <div class="field">
                            <span class="label">Email:</span> {email}
                        </div>
                        <div class="field">
                            <span class="label">Phone:</span> {phone or 'Not provided'}
                        </div>
                        <div class="field">
                            <span class="label">Subject:</span> {subject}
                        </div>
                        <div class="field">
                            <span class="label">Message:</span>
                            <div class="message">{message}</div>
                        </div>
                    </div>
                    <div class="footer">
                        <p>This message was sent from the Go Postal SD contact form.</p>
                    </div>
                </div>
            </body>
            </html>
            """.strip()
        
        result = self.send_email(
            to_email=self.from_email,  # Send to Go Postal email
            subject=email_subject,
            text_content=text_content,
            html_content=html_content
        )
        
        if result.get('success'):
            # Send confirmation to customer
            self._send_contact_confirmation(name, email, subject)
            return True
        else:
            logger.error(f"Failed to send contact email: {result.get('error')}")
            return False
    
    def _send_contact_confirmation(self, name: str, email: str, subject: str):
        """Send confirmation email to customer."""
        confirmation_subject = "Message Received - Go Postal SD"
        
        text_content = f"""
            Hello {name},

            Thank you for contacting Go Postal SD! We have received your message regarding "{subject}".

            Our team will review your message and get back to you as soon as possible.

            If you have any urgent questions, please call us at (619) 237-0374.

            Best regards,
            Go Postal SD Team

            Go Postal
            1501 India St Suite 103
            San Diego, CA 92101
            Phone: (619) 237-0374
            Email: gopostalsd@gmail.com
                    """.strip()
                    
                    html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Message Received</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #1976d2; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f9f9f9; }}
                    .footer {{ text-align: center; padding: 20px; color: #666; font-size: 14px; }}
                    .contact-info {{ background-color: white; padding: 15px; border-radius: 4px; margin: 15px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Message Received!</h1>
                    </div>
                    <div class="content">
                        <p>Hello {name},</p>
                        <p>Thank you for contacting Go Postal SD! We have received your message regarding <strong>"{subject}"</strong>.</p>
                        <p>Our team will review your message and get back to you as soon as possible.</p>
                        <p>If you have any urgent questions, please call us at <strong>(619) 237-0374</strong>.</p>
                        
                        <div class="contact-info">
                            <h3>Go Postal SD</h3>
                            <p>1501 India St Suite 103<br>
                            San Diego, CA 92101<br>
                            Phone: (619) 237-0374<br>
                            Email: gopostalsd@gmail.com</p>
                        </div>
                    </div>
                    <div class="footer">
                        <p>Best regards,<br>Go Postal SD Team</p>
                    </div>
                </div>
            </body>
            </html>
            """.strip()
        
        self.send_email(
            to_email=email,
            subject=confirmation_subject,
            text_content=text_content,
            html_content=html_content
        )
