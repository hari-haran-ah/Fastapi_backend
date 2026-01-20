import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from app.core.config import settings


class EmailService:
    """
    Production-ready email service using SMTP
    """

    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.email_from = settings.EMAIL_FROM

    def _send_email(self, to_email: str, subject: str, html_content: str) -> None:
        """
        Internal method to send email
        """
        try:
            message = MIMEMultipart("alternative")
            message["From"] = self.email_from
            message["To"] = to_email
            message["Subject"] = subject

            message.attach(MIMEText(html_content, "html"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.email_from, to_email, message.as_string())

            print(f"📧 Email sent to {to_email}")

        except Exception as e:
            print(f"❌ Email sending failed: {e}")

    def send_otp_email(self, to_email: str, otp: str) -> None:
        subject = "Verify your email - OTP"
        html = f"""
        <html>
            <body>
                <h2>Email Verification</h2>
                <p>Your OTP is:</p>
                <h1>{otp}</h1>
                <p>This OTP is valid for {settings.OTP_EXPIRE_MINUTES} minutes.</p>
            </body>
        </html>
        """
        self._send_email(to_email, subject, html)

    def send_login_alert(self, to_email: str) -> None:
        subject = "New Login Detected"
        html = """
        <html>
            <body>
                <h3>Login Alert</h3>
                <p>Your account was just logged in.</p>
                <p>If this was not you, please reset your password immediately.</p>
            </body>
        </html>
        """
        self._send_email(to_email, subject, html)

    def send_password_reset_email(self, to_email: str, reset_link: str) -> None:
        subject = "Password Reset Request"
        html = f"""
        <html>
            <body>
                <h3>Password Reset</h3>
                <p>Click the link below to reset your password:</p>
                <a href="{reset_link}">Reset Password</a>
            </body>
        </html>
        """
        self._send_email(to_email, subject, html)

    def send_account_status_email(self, to_email: str, is_active: bool) -> None:
        status = "Activated" if is_active else "Deactivated"
        subject = f"Account {status}"
        html = f"""
        <html>
            <body>
                <h3>Account Status Update</h3>
                <p>Your account has been <strong>{status}</strong> by the administrator.</p>
                <p>If you have questions, contact support.</p>
            </body>
        </html>
        """
        self._send_email(to_email, subject, html)
