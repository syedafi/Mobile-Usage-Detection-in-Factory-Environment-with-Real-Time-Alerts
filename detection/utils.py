import random
from django.core.mail import send_mail

def generate_otp():
    """Generate a 6-digit OTP."""
    return str(random.randint(100000, 999999))

from django.core.mail import send_mail

def send_otp_email(email, otp):
    """Send OTP to the provided email address."""
    subject = "Your OTP for Verification"
    message = f"""
    Dear Team,

    Your OTP for verification is: {otp}.
    Please keep it confidential. If you didn't request this, contact support.

    Thank you,
    Team LivNSense Technologies Pvt Ltd
    """
    from_email = "noreply@example.com"
    send_mail(subject, message, from_email, [email])