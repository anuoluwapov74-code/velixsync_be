"""
Email service for VelixSync
Professional trading firm email templates
"""

import resend
import random
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


def generate_verification_code():
    """Generate a random 4-digit verification code"""
    return str(random.randint(1000, 9999))


def send_email(to_email, subject, html_content):
    """Send HTML email using Resend API"""
    try:
        api_key = settings.RESEND_API_KEY
        if not api_key:
            logger.error("send_email: RESEND_API_KEY is not set — email not sent to %s", to_email)
            return False

        resend.api_key = api_key

        resend.Emails.send({
            "from": settings.DEFAULT_FROM_EMAIL,
            "to": to_email,
            "subject": subject,
            "html": html_content,
        })

        logger.info("send_email: sent '%s' to %s", subject, to_email)
        return True

    except Exception as e:
        logger.error(
            "send_email: FAILED to send '%s' to %s — %s: %s",
            subject, to_email, type(e).__name__, e,
        )
        return False


# ─────────────────────────────────────────────────────────────
# Shared base template
# ─────────────────────────────────────────────────────────────

def _base_styles():
    return """
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #1a1a2e;
            margin: 0;
            padding: 0;
            background-color: #f0f2f5;
            -webkit-font-smoothing: antialiased;
        }
        .wrapper {
            max-width: 600px;
            margin: 40px auto;
            background-color: #ffffff;
            border-radius: 2px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        }
        .header {
            background-color: #001a0f;
            padding: 32px 40px;
        }
        .header-logo {
            font-size: 20px;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: 0.5px;
        }
        .header-logo span {
            color: #00C9A7;
        }
        .header-divider {
            width: 40px;
            height: 2px;
            background-color: #00C9A7;
            margin-top: 16px;
        }
        .body-content {
            padding: 40px;
        }
        .greeting {
            font-size: 15px;
            color: #64748b;
            margin-bottom: 24px;
            font-weight: 400;
        }
        .heading {
            font-size: 22px;
            font-weight: 600;
            color: #0a1628;
            margin-bottom: 16px;
            line-height: 1.3;
        }
        .text {
            font-size: 14px;
            color: #475569;
            margin-bottom: 24px;
            line-height: 1.7;
        }
        .divider {
            height: 1px;
            background-color: #e2e8f0;
            margin: 32px 0;
        }
        .footer {
            background-color: #f8fafc;
            padding: 28px 40px;
            border-top: 1px solid #e2e8f0;
        }
        .footer-text {
            font-size: 12px;
            color: #94a3b8;
            line-height: 1.6;
        }
        .footer-links {
            margin-top: 12px;
        }
        .footer-links a {
            color: #64748b;
            text-decoration: none;
            font-size: 12px;
            margin-right: 16px;
        }
        .btn {
            display: inline-block;
            padding: 12px 32px;
            background-color: #00C9A7;
            color: #001a0f;
            text-decoration: none;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 600;
            letter-spacing: 0.3px;
        }
        .info-box {
            background-color: #f0fdf9;
            border-left: 3px solid #00C9A7;
            padding: 16px 20px;
            margin: 24px 0;
        }
        .info-box p {
            font-size: 13px;
            color: #475569;
            margin: 0;
        }
        .code-container {
            background-color: #f1f5f9;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 28px;
            margin: 28px 0;
            text-align: center;
        }
        .code-value {
            font-size: 40px;
            font-weight: 700;
            color: #00C9A7;
            letter-spacing: 12px;
            font-family: 'SF Mono', 'Fira Code', 'Courier New', monospace;
        }
        .code-label {
            font-size: 12px;
            color: #94a3b8;
            margin-top: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .notice {
            background-color: #fffbeb;
            border-left: 3px solid #f59e0b;
            padding: 14px 18px;
            margin: 24px 0;
        }
        .notice p {
            font-size: 13px;
            color: #92400e;
            margin: 0;
        }
        .detail-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        .detail-table td {
            padding: 10px 0;
            font-size: 13px;
            border-bottom: 1px solid #f1f5f9;
        }
        .detail-table .label {
            color: #94a3b8;
            width: 40%;
            font-weight: 500;
        }
        .detail-table .value {
            color: #1e293b;
            font-weight: 500;
            text-align: right;
        }
    """


def _header_html():
    return """
    <div class="header">
        <div class="header-logo">HEDGE<span>SYNC</span></div>
        <div class="header-divider"></div>
    </div>
    """


def _footer_html(user_email):
    frontend = settings.FRONTEND_URL
    return f"""
    <div class="footer">
        <div class="footer-text">
            This is an automated message from VelixSync. Please do not reply directly to this email.
        </div>
        <div class="footer-links">
            <a href="{frontend}/privacy-policy">Privacy Policy</a>
            <a href="{frontend}/terms-of-service">Terms of Service</a>
        </div>
        <div class="footer-text" style="margin-top: 16px;">
            Sent to {user_email} &middot; &copy; {timezone.now().year} VelixSync. All rights reserved.
        </div>
    </div>
    """


# ─────────────────────────────────────────────────────────────
# Welcome Email
# ─────────────────────────────────────────────────────────────

def send_welcome_email(user):
    subject = "Welcome to VelixSync"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>{_base_styles()}</style>
    </head>
    <body>
        <div class="wrapper">
            {_header_html()}

            <div class="body-content">
                <div class="greeting">Hello {user.first_name or 'Trader'},</div>

                <div class="heading">Your account has been created</div>

                <div class="text">
                    Thank you for choosing VelixSync. Your account has been successfully registered and is ready for setup.
                </div>

                <div class="info-box">
                    <p><strong>Next steps to get started:</strong></p>
                    <p>1. Complete identity verification (KYC)</p>
                    <p>2. Fund your account and begin trading</p>
                </div>

                <div class="text">
                    Once that is done, you'll have access to copy trading, premium signals, and our full suite of trading instruments including stocks, forex, and commodities.
                </div>

                <div class="divider"></div>

                <div class="text" style="font-size: 13px; color: #94a3b8;">
                    If you have any questions, our support team is available around the clock to assist you.
                </div>
            </div>

            {_footer_html(user.email)}
        </div>
    </body>
    </html>
    """

    return send_email(user.email, subject, html_content)


# ─────────────────────────────────────────────────────────────
# Email Verification Code
# ─────────────────────────────────────────────────────────────

def send_verification_code_email(user, code):
    subject = "Email Verification \u2014 VelixSync"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>{_base_styles()}</style>
    </head>
    <body>
        <div class="wrapper">
            {_header_html()}

            <div class="body-content">
                <div class="greeting">Hello {user.first_name or 'Trader'},</div>

                <div class="heading">Verify your email address</div>

                <div class="text">
                    To complete your account registration, please enter the verification code below. This code is valid for 10 minutes.
                </div>

                <div class="code-container">
                    <div class="code-value">{code}</div>
                    <div class="code-label">Verification Code</div>
                </div>

                <div class="notice">
                    <p><strong>Security:</strong> Never share this code with anyone. VelixSync will never ask for your verification code via phone or chat.</p>
                </div>

                <div class="divider"></div>

                <div class="text" style="font-size: 13px; color: #94a3b8;">
                    If you did not create a VelixSync account, you can safely ignore this email.
                </div>
            </div>

            {_footer_html(user.email)}
        </div>
    </body>
    </html>
    """

    return send_email(user.email, subject, html_content)


# ─────────────────────────────────────────────────────────────
# 2FA Login Code
# ─────────────────────────────────────────────────────────────

def send_2fa_code_email(user, code):
    subject = "Login Verification \u2014 VelixSync"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>{_base_styles()}</style>
    </head>
    <body>
        <div class="wrapper">
            {_header_html()}

            <div class="body-content">
                <div class="greeting">Hello {user.first_name or 'Trader'},</div>

                <div class="heading">Two-factor authentication</div>

                <div class="text">
                    A sign-in attempt was detected on your account. Enter the code below to complete authentication. This code expires in 10 minutes.
                </div>

                <div class="code-container">
                    <div class="code-value">{code}</div>
                    <div class="code-label">Authentication Code</div>
                </div>

                <table class="detail-table">
                    <tr>
                        <td class="label">Account</td>
                        <td class="value">{user.email}</td>
                    </tr>
                    <tr>
                        <td class="label">Timestamp</td>
                        <td class="value">{timezone.now().strftime('%b %d, %Y at %I:%M %p UTC')}</td>
                    </tr>
                </table>

                <div class="notice">
                    <p><strong>Unrecognized activity?</strong> If you did not attempt to sign in, change your password immediately and contact support.</p>
                </div>
            </div>

            {_footer_html(user.email)}
        </div>
    </body>
    </html>
    """

    return send_email(user.email, subject, html_content)


def is_code_valid(user):
    """Check if verification code is still valid (within 10 minutes)"""
    if not user.code_created_at or not user.verification_code:
        return False

    expiry_time = user.code_created_at + timedelta(minutes=10)
    return timezone.now() < expiry_time


# ─────────────────────────────────────────────────────────────
# Admin: Payment Intent Notification
# ─────────────────────────────────────────────────────────────

def send_admin_payment_intent_notification(user, currency, dollar_amount, currency_unit):
    admin_email = settings.ADMIN_NOTIFICATION_EMAIL if hasattr(settings, 'ADMIN_NOTIFICATION_EMAIL') else settings.EMAIL_HOST_USER

    subject = f"Payment Intent — {user.email} — ${dollar_amount}"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            {_base_styles()}
            .amount-display {{
                background-color: #f0fdf9;
                border: 1px solid #99f6e4;
                border-radius: 6px;
                padding: 24px;
                text-align: center;
                margin: 24px 0;
            }}
            .amount-display .amount {{
                font-size: 32px;
                font-weight: 700;
                color: #00A88C;
            }}
            .amount-display .label {{
                font-size: 12px;
                color: #64748b;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-top: 4px;
            }}
            .status-badge {{
                display: inline-block;
                padding: 4px 12px;
                background-color: #f0fdf9;
                color: #00796B;
                border-radius: 2px;
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .section-title {{
                font-size: 11px;
                font-weight: 600;
                color: #94a3b8;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 12px;
                margin-top: 28px;
            }}
        </style>
    </head>
    <body>
        <div class="wrapper">
            {_header_html()}

            <div class="body-content">
                <div style="margin-bottom: 20px;">
                    <span class="status-badge">Payment Intent</span>
                </div>

                <div class="heading">Deposit Intent Received</div>

                <div class="text">A user has indicated intent to deposit funds. They have entered an amount and are proceeding to the payment step. Follow up if no deposit is completed.</div>

                <div class="amount-display">
                    <div class="amount">${dollar_amount}</div>
                    <div class="label">{currency_unit} {currency}</div>
                </div>

                <div class="section-title">Intent Details</div>
                <table class="detail-table">
                    <tr><td class="label">Currency</td><td class="value">{currency}</td></tr>
                    <tr><td class="label">USD Amount</td><td class="value">${dollar_amount}</td></tr>
                    <tr><td class="label">Crypto Amount</td><td class="value">{currency_unit}</td></tr>
                    <tr><td class="label">Timestamp</td><td class="value">{timezone.now().strftime('%b %d, %Y at %I:%M %p UTC')}</td></tr>
                </table>

                <div class="section-title">User Information</div>
                <table class="detail-table">
                    <tr><td class="label">Name</td><td class="value">{user.first_name} {user.last_name}</td></tr>
                    <tr><td class="label">Email</td><td class="value">{user.email}</td></tr>
                    <tr><td class="label">Account ID</td><td class="value">{user.account_id}</td></tr>
                    <tr><td class="label">Balance</td><td class="value">${user.balance}</td></tr>
                    <tr><td class="label">KYC</td><td class="value">{'Verified' if user.is_verified else ('Pending' if user.has_submitted_kyc else 'Not Submitted')}</td></tr>
                </table>

                <div class="notice">
                    <p><strong>Note:</strong> This is a payment intent notification, not a confirmed deposit. The user may or may not complete the payment. Staff should follow up if no deposit is received.</p>
                </div>
            </div>

            <div class="footer">
                <div class="footer-text">Admin notification &middot; Payment intent &middot; {timezone.now().strftime('%b %d, %Y at %I:%M %p UTC')}</div>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(admin_email, subject, html_content)


# ─────────────────────────────────────────────────────────────
# Admin: Deposit Notification
# ─────────────────────────────────────────────────────────────

def send_admin_deposit_notification(user, transaction):
    admin_email = settings.ADMIN_NOTIFICATION_EMAIL if hasattr(settings, 'ADMIN_NOTIFICATION_EMAIL') else settings.EMAIL_HOST_USER

    subject = f"Deposit Request \u2014 {user.email} \u2014 ${transaction.amount}"

    receipt_row = ""
    if transaction.receipt:
        receipt_row = f"""
        <tr>
            <td class="label">Receipt</td>
            <td class="value"><a href="{transaction.receipt.url}" target="_blank" style="color: #3b82f6; text-decoration: none;">View Receipt</a></td>
        </tr>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            {_base_styles()}
            .amount-display {{
                background-color: #f0fdf4;
                border: 1px solid #bbf7d0;
                border-radius: 6px;
                padding: 24px;
                text-align: center;
                margin: 24px 0;
            }}
            .amount-display .amount {{
                font-size: 32px;
                font-weight: 700;
                color: #16a34a;
            }}
            .amount-display .label {{
                font-size: 12px;
                color: #64748b;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-top: 4px;
            }}
            .status-badge {{
                display: inline-block;
                padding: 4px 12px;
                background-color: #fef3c7;
                color: #92400e;
                border-radius: 2px;
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .section-title {{
                font-size: 11px;
                font-weight: 600;
                color: #94a3b8;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 12px;
                margin-top: 28px;
            }}
        </style>
    </head>
    <body>
        <div class="wrapper">
            {_header_html()}

            <div class="body-content">
                <div style="margin-bottom: 20px;">
                    <span class="status-badge">Pending Approval</span>
                </div>

                <div class="heading">New Deposit Request</div>

                <div class="text">A deposit request has been submitted and requires review.</div>

                <div class="amount-display">
                    <div class="amount">${transaction.amount}</div>
                    <div class="label">{transaction.unit} {transaction.currency}</div>
                </div>

                <div class="section-title">Transaction Details</div>
                <table class="detail-table">
                    <tr><td class="label">Reference</td><td class="value">{transaction.reference}</td></tr>
                    <tr><td class="label">Status</td><td class="value">{transaction.status.upper()}</td></tr>
                    <tr><td class="label">Date</td><td class="value">{transaction.created_at.strftime('%b %d, %Y at %I:%M %p UTC')}</td></tr>
                    <tr><td class="label">Currency</td><td class="value">{transaction.currency}</td></tr>
                    {receipt_row}
                </table>

                <div class="section-title">User Information</div>
                <table class="detail-table">
                    <tr><td class="label">Name</td><td class="value">{user.first_name} {user.last_name}</td></tr>
                    <tr><td class="label">Email</td><td class="value">{user.email}</td></tr>
                    <tr><td class="label">Account ID</td><td class="value">{user.account_id}</td></tr>
                    <tr><td class="label">Balance</td><td class="value">${user.balance}</td></tr>
                    <tr><td class="label">KYC</td><td class="value">{'Verified' if user.is_verified else ('Pending' if user.has_submitted_kyc else 'Not Submitted')}</td></tr>
                </table>
            </div>

            <div class="footer">
                <div class="footer-text">Admin notification &middot; Action required &middot; {timezone.now().strftime('%b %d, %Y at %I:%M %p UTC')}</div>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(admin_email, subject, html_content)


# ─────────────────────────────────────────────────────────────
# Admin: Withdrawal Notification
# ─────────────────────────────────────────────────────────────

def send_admin_withdrawal_notification(user, transaction, method_type=None, address=None):
    admin_email = settings.ADMIN_NOTIFICATION_EMAIL if hasattr(settings, 'ADMIN_NOTIFICATION_EMAIL') else settings.EMAIL_HOST_USER

    subject = f"Withdrawal Request \u2014 {user.email} \u2014 ${transaction.amount}"

    payment_method_info = method_type or transaction.currency or "Not specified"
    payment_address = address or "N/A"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            {_base_styles()}
            .amount-display {{
                background-color: #fef2f2;
                border: 1px solid #fecaca;
                border-radius: 6px;
                padding: 24px;
                text-align: center;
                margin: 24px 0;
            }}
            .amount-display .amount {{
                font-size: 32px;
                font-weight: 700;
                color: #dc2626;
            }}
            .amount-display .label {{
                font-size: 12px;
                color: #64748b;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-top: 4px;
            }}
            .status-badge {{
                display: inline-block;
                padding: 4px 12px;
                background-color: #fef2f2;
                color: #991b1b;
                border-radius: 2px;
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .section-title {{
                font-size: 11px;
                font-weight: 600;
                color: #94a3b8;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 12px;
                margin-top: 28px;
            }}
        </style>
    </head>
    <body>
        <div class="wrapper">
            {_header_html()}

            <div class="body-content">
                <div style="margin-bottom: 20px;">
                    <span class="status-badge">Urgent \u2014 Approval Required</span>
                </div>

                <div class="heading">Withdrawal Request</div>

                <div class="text">A withdrawal request has been submitted and requires immediate processing.</div>

                <div class="amount-display">
                    <div class="amount">${transaction.amount}</div>
                    <div class="label">Withdrawal Amount</div>
                </div>

                <div class="notice">
                    <p><strong>Note:</strong> The user's balance has NOT been deducted yet — it will only be deducted once this withdrawal is approved. Approve or reject from the admin dashboard.</p>
                </div>

                <div class="section-title">Transaction Details</div>
                <table class="detail-table">
                    <tr><td class="label">Reference</td><td class="value">{transaction.reference}</td></tr>
                    <tr><td class="label">Status</td><td class="value">{transaction.status.upper()}</td></tr>
                    <tr><td class="label">Source</td><td class="value">{transaction.get_source_display()}</td></tr>
                    <tr><td class="label">Date</td><td class="value">{transaction.created_at.strftime('%b %d, %Y at %I:%M %p UTC')}</td></tr>
                </table>

                <div class="section-title">Payment Destination</div>
                <table class="detail-table">
                    <tr><td class="label">Method</td><td class="value">{payment_method_info}</td></tr>
                    <tr><td class="label">Address / Account</td><td class="value" style="font-size: 12px;">{payment_address}</td></tr>
                </table>

                <div class="section-title">User Information</div>
                <table class="detail-table">
                    <tr><td class="label">Name</td><td class="value">{user.first_name} {user.last_name}</td></tr>
                    <tr><td class="label">Email</td><td class="value">{user.email}</td></tr>
                    <tr><td class="label">Account ID</td><td class="value">{user.account_id}</td></tr>
                    <tr><td class="label">Current Balance</td><td class="value">${user.balance}</td></tr>
                    <tr><td class="label">KYC</td><td class="value">{'Verified' if user.is_verified else ('Pending' if user.has_submitted_kyc else 'Not Submitted')}</td></tr>
                </table>
            </div>

            <div class="footer">
                <div class="footer-text">Admin notification &middot; Urgent action required &middot; {timezone.now().strftime('%b %d, %Y at %I:%M %p UTC')}</div>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(admin_email, subject, html_content)


# ─────────────────────────────────────────────────────────────
# Password Reset
# ─────────────────────────────────────────────────────────────

def send_password_reset_email(user, token, uid):
    reset_link = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"

    subject = "Password Reset \u2014 VelixSync"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            {_base_styles()}
            .link-fallback {{
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                padding: 12px 16px;
                margin: 20px 0;
                word-break: break-all;
                font-size: 12px;
                color: #64748b;
                font-family: monospace;
            }}
        </style>
    </head>
    <body>
        <div class="wrapper">
            {_header_html()}

            <div class="body-content">
                <div class="greeting">Hello {user.first_name or 'Trader'},</div>

                <div class="heading">Reset your password</div>

                <div class="text">
                    We received a request to reset the password associated with your VelixSync account. Click the button below to set a new password.
                </div>

                <div style="text-align: center; margin: 32px 0;">
                    <a href="{reset_link}" class="btn">Reset Password</a>
                </div>

                <div class="text" style="font-size: 13px; color: #94a3b8;">
                    This link will expire in 1 hour. If the button above doesn't work, copy and paste this URL into your browser:
                </div>

                <div class="link-fallback">{reset_link}</div>

                <div class="notice">
                    <p><strong>Didn't request this?</strong> If you did not initiate a password reset, no action is needed. Your current password remains unchanged.</p>
                </div>
            </div>

            {_footer_html(user.email)}
        </div>
    </body>
    </html>
    """

    return send_email(user.email, subject, html_content)
