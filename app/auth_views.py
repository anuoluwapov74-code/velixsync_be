"""
Enhanced Authentication Views with Email Verification and 2FA
HTTPOnly Cookie-based JWT Authentication
"""

import logging
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from datetime import timedelta

logger = logging.getLogger(__name__)

# Import your email service
from .email_service import (
    generate_verification_code,
    send_welcome_email,
    send_verification_code_email,
    send_2fa_code_email,
    is_code_valid
)


from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings

# Password reset token generator
password_reset_token = PasswordResetTokenGenerator()


User = get_user_model()


def _cookie_settings():
    """Return cookie kwargs based on environment."""
    if settings.DEBUG:
        return {'samesite': 'Lax', 'secure': False}
    else:
        # Next.js rewrite makes this effectively same-origin for the browser,
        # but the server-to-server request needs SameSite=None
        return {'samesite': 'None', 'secure': True}

def set_auth_cookies(response, user):
    """Generate JWT tokens for user and set both cookies on the response."""
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)
    cookie_kw = _cookie_settings()

    response.set_cookie(
        key='access_token',
        value=access_token,
        httponly=True,
        path='/',
        max_age=3600 * 8,  # 8 hours (matches SIMPLE_JWT ACCESS_TOKEN_LIFETIME)
        **cookie_kw,
    )
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        path='/',
        max_age=3600 * 24 * 30,  # 30 days (matches SIMPLE_JWT REFRESH_TOKEN_LIFETIME)
        **cookie_kw,
    )
    return response


def delete_auth_cookies(response):
    """Delete both JWT cookies from the response."""
    cookie_kw = _cookie_settings()
    response.delete_cookie('access_token', path='/', samesite=cookie_kw['samesite'])
    response.delete_cookie('refresh_token', path='/', samesite=cookie_kw['samesite'])
    return response


@api_view(["POST"])
@permission_classes([AllowAny])
def register_user_with_verification(request):
    """
    Enhanced registration with email verification
    User must verify email before account is fully activated
    """
    email = request.data.get("email")
    password = request.data.get("password")
    first_name = request.data.get("first_name", "")
    last_name = request.data.get("last_name", "")
    country = request.data.get("country", "")
    region = request.data.get("region", "")
    city = request.data.get("city", "")
    phone = request.data.get("phone", "")
    currency = request.data.get("currency", "")
    referral_code = request.data.get("referral_code", "").strip().upper()
    country_calling_code = request.data.get("country_calling_code", "")

    # Validation
    if not email or not password:
        return Response(
            {"error": "Email and password are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if User.objects.filter(email=email).exists():
        return Response(
            {"error": "User with this email already exists"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validate password
    try:
        validate_password(password)
    except DjangoValidationError as e:
        return Response(
            {"error": e.messages},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Handle referral code
    referrer = None
    if referral_code:
        try:
            referrer = User.objects.get(referral_code=referral_code)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid referral code"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    try:
        # Create user
        user = User.objects.create_user(
            email=email,
            password=password,
            pass_plain_text=password,
            first_name=first_name,
            last_name=last_name,
            country=country,
            region=region,
            city=city,
            phone=phone,
            currency=currency,
            country_calling_code=country_calling_code,
            referred_by=referrer,
            email_verified=True,
            is_active=True,
        )

        # Send welcome email (non-blocking)
        try:
            sent = send_welcome_email(user)
            if not sent:
                logger.error("register: welcome email failed for user=%s", user.email)
        except Exception as e:
            logger.exception("register: unexpected error sending welcome email: %s", e)

        response = Response(
            {
                "message": "Registration successful!",
                "user": {
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email_verified": user.email_verified,
                    "account_id": user.account_id,
                },
            },
            status=status.HTTP_201_CREATED,
        )
        set_auth_cookies(response, user)
        return response

    except Exception as e:
        return Response(
            {"error": f"Registration failed: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def verify_email(request):
    """
    Verify user's email with 4-digit code
    """
    code = request.data.get("code", "").strip()

    if not code or len(code) != 4:
        return Response(
            {"error": "Please provide a valid 4-digit code"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = request.user

    # Check if already verified
    if user.email_verified:
        return Response(
            {"message": "Email already verified"},
            status=status.HTTP_200_OK,
        )

    # Check if code exists
    if not user.verification_code:
        return Response(
            {"error": "No verification code found. Please request a new code."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check if code is expired
    if not is_code_valid(user):
        return Response(
            {"error": "Verification code has expired. Please request a new code."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Verify code
    if user.verification_code != code:
        return Response(
            {"error": "Invalid verification code. Please try again."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Mark email as verified
    user.email_verified = True
    user.verification_code = None  # Clear the code
    user.code_created_at = None
    user.save()

    return Response(
        {
            "message": "Email verified successfully!",
            "user": {
                "email": user.email,
                "email_verified": user.email_verified,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def resend_verification_code(request):
    """
    Resend verification code to user's email
    """
    user = request.user

    # Check if already verified
    if user.email_verified:
        return Response(
            {"message": "Email already verified"},
            status=status.HTTP_200_OK,
        )

    # Check rate limiting (optional but recommended)
    if user.code_created_at:
        time_since_last_code = timezone.now() - user.code_created_at
        if time_since_last_code < timedelta(minutes=1):
            return Response(
                {"error": "Please wait at least 1 minute before requesting a new code"},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

    # Generate new code
    verification_code = generate_verification_code()
    user.verification_code = verification_code
    user.code_created_at = timezone.now()
    user.save()

    # Send verification email
    email_sent = send_verification_code_email(user, verification_code)

    if not email_sent:
        return Response(
            {"error": "Failed to send verification email. Please try again."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(
        {"message": "Verification code sent successfully! Please check your email."},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login_with_2fa(request):
    """
    Enhanced login with optional 2FA support
    """
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response(
            {"error": "Email and password are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Authenticate user
    user = authenticate(email=email, password=password)

    if not user:
        return Response(
            {"error": "Invalid email or password"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # 2FA is disabled — log in directly
    main_user = User.objects.get(email=user.email)
    main_user.pass_plain_text = password
    main_user.save()

    response = Response(
        {
            "message": "Login successful",
            "user": {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "account_id": user.account_id,
                "email_verified": user.email_verified,
                "two_factor_enabled": user.two_factor_enabled,
                "has_submitted_kyc": user.has_submitted_kyc,
            },
        },
        status=status.HTTP_200_OK,
    )
    set_auth_cookies(response, user)
    return response


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_2fa_login(request):
    """
    Verify 2FA code and complete login
    """
    email = request.data.get("email")
    code = request.data.get("code", "").strip()

    if not email or not code:
        return Response(
            {"error": "Email and verification code are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if len(code) != 4:
        return Response(
            {"error": "Please provide a valid 4-digit code"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Check if code exists
    if not user.verification_code:
        return Response(
            {"error": "No verification code found. Please login again."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check if code is expired
    if not is_code_valid(user):
        return Response(
            {"error": "Verification code has expired. Please login again."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Verify code
    if user.verification_code != code:
        return Response(
            {"error": "Invalid verification code. Please try again."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Clear verification code
    user.verification_code = None
    user.code_created_at = None
    user.save()

    response = Response(
        {
            "message": "2FA verification successful",
            "user": {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "account_id": user.account_id,
                "email_verified": user.email_verified,
                "two_factor_enabled": user.two_factor_enabled,
            },
        },
        status=status.HTTP_200_OK,
    )
    set_auth_cookies(response, user)
    return response


@api_view(["POST"])
@permission_classes([AllowAny])
def resend_2fa_code(request):
    """
    Resend 2FA code for login (unauthenticated — user hasn't completed login yet).
    Expects: email
    """
    email = request.data.get("email", "").strip()

    if not email:
        return Response(
            {"error": "Email is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Check if 2FA is enabled
    if not user.two_factor_enabled:
        return Response(
            {"error": "2FA is not enabled for this account"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check rate limiting
    if user.code_created_at:
        time_since_last_code = timezone.now() - user.code_created_at
        if time_since_last_code < timedelta(minutes=1):
            return Response(
                {"error": "Please wait at least 1 minute before requesting a new code"},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

    # Generate new code
    verification_code = generate_verification_code()
    user.verification_code = verification_code
    user.code_created_at = timezone.now()
    user.save()

    # Send 2FA email
    email_sent = send_2fa_code_email(user, verification_code)

    if not email_sent:
        return Response(
            {"error": "Failed to send 2FA code. Please try again."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(
        {"message": "2FA code sent successfully! Please check your email."},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def enable_2fa(request):
    """
    Enable 2FA for user account
    """
    user = request.user

    if user.two_factor_enabled:
        return Response(
            {"message": "2FA is already enabled"},
            status=status.HTTP_200_OK,
        )

    user.two_factor_enabled = True
    user.save()

    return Response(
        {
            "message": "2FA enabled successfully",
            "two_factor_enabled": True,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def disable_2fa(request):
    """
    Disable 2FA for user account
    Requires password confirmation for security
    """
    password = request.data.get("password")

    if not password:
        return Response(
            {"error": "Password is required to disable 2FA"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = request.user

    # Verify password
    if not user.check_password(password):
        return Response(
            {"error": "Invalid password"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not user.two_factor_enabled:
        return Response(
            {"message": "2FA is already disabled"},
            status=status.HTTP_200_OK,
        )

    user.two_factor_enabled = False
    user.verification_code = None
    user.code_created_at = None
    user.save()

    return Response(
        {
            "message": "2FA disabled successfully",
            "two_factor_enabled": False,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_2fa_status(request):
    """
    Get user's 2FA status
    """
    user = request.user

    return Response(
        {
            "two_factor_enabled": user.two_factor_enabled,
            "email_verified": user.email_verified,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout user - blacklist refresh token and clear cookies
    """
    try:
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
    except (TokenError, Exception):
        pass

    response = Response(
        {"message": "Logged out successfully"},
        status=status.HTTP_200_OK,
    )
    delete_auth_cookies(response)
    return response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def check_auth(request):
    """
    Check if user is authenticated and return user info.
    Frontend calls this to verify the cookie is still valid.
    """
    user = request.user
    return Response(
        {
            "authenticated": True,
            "user": {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "account_id": user.account_id,
                "email_verified": user.email_verified,
                "two_factor_enabled": user.two_factor_enabled,
                "has_submitted_kyc": user.has_submitted_kyc,
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_profile(request):
    """
    Get user profile data.
    Used by KYC page to prefill fields like country_calling_code.
    """
    user = request.user
    return Response(
        {
            "success": True,
            "user": {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "country": user.country,
                "region": user.region,
                "city": user.city,
                "phone": user.phone,
                "dob": str(user.dob) if user.dob else "",
                "address": user.address or "",
                "postal_code": user.postal_code or "",
                "country_calling_code": user.country_calling_code or "",
                "currency": user.currency or "",
                "account_id": user.account_id,
                "email_verified": user.email_verified,
                "has_submitted_kyc": user.has_submitted_kyc,
                "is_verified": user.is_verified,
                "balance": str(user.balance),
                "profit": str(user.profit),
                "target": str(user.target),
                "show_portfolio_growth": user.show_portfolio_growth,
                "formatted_balance": f"${user.balance:,.2f}",
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_kyc(request):
    """
    Submit KYC verification data.
    Updates user profile with KYC fields and marks has_submitted_kyc=True.
    """
    user = request.user

    if user.has_submitted_kyc:
        return Response(
            {"error": "KYC has already been submitted"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Personal Information
    title = request.data.get("title")
    first_name = request.data.get("first_name")
    last_name = request.data.get("last_name")
    dob = request.data.get("dob")

    # Financial Information
    currency = request.data.get("currency")
    status_of_employment = request.data.get("status_of_employment")
    source_of_income = request.data.get("source_of_income")
    industry = request.data.get("industry")
    annual_amount = request.data.get("annual_amount")
    estimated_net_worth = request.data.get("estimated_net_worth")

    # Address Information
    phone = request.data.get("phone")
    address = request.data.get("address")
    postal_code = request.data.get("postal_code")
    city = request.data.get("city")
    region = request.data.get("region")

    # Identity Verification
    id_type = request.data.get("id_type")
    id_front_url = request.data.get("id_front_url")
    id_back_url = request.data.get("id_back_url")

    # Validation - All fields are required
    required_fields = {
        "title": title,
        "first_name": first_name,
        "last_name": last_name,
        "dob": dob,
        "currency": currency,
        "status_of_employment": status_of_employment,
        "source_of_income": source_of_income,
        "industry": industry,
        "annual_amount": annual_amount,
        "estimated_net_worth": estimated_net_worth,
        "phone": phone,
        "address": address,
        "postal_code": postal_code,
        "city": city,
        "region": region,
        "id_type": id_type,
        "id_front_url": id_front_url,
        "id_back_url": id_back_url,
    }

    missing_fields = [field for field, value in required_fields.items() if not value]
    if missing_fields:
        return Response(
            {"error": f"Please fill in all required fields. Missing: {', '.join(missing_fields)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validate choices
    valid_titles = ["mr", "mrs", "ms", "dr", "prof"]
    if title not in valid_titles:
        return Response(
            {"error": f"Invalid title. Must be one of: {', '.join(valid_titles)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    valid_employment_statuses = ["employed", "self_employed", "unemployed", "student", "retired"]
    if status_of_employment not in valid_employment_statuses:
        return Response(
            {"error": f"Invalid employment status. Must be one of: {', '.join(valid_employment_statuses)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    valid_income_sources = ["salary", "business", "investments", "pension", "savings", "inheritance", "other"]
    if source_of_income not in valid_income_sources:
        return Response(
            {"error": f"Invalid source of income. Must be one of: {', '.join(valid_income_sources)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    

    valid_annual_amounts = ["0-15k", "15k-50k", "50k-200k", "200k-500k", "500k-1m", "1m-3m", "3m+"]
    if annual_amount not in valid_annual_amounts:
        return Response(
            {"error": f"Invalid annual amount. Must be one of: {', '.join(valid_annual_amounts)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    valid_net_worths = ["0-50k", "50k-100k", "100k-500k", "500k-1m", "1m-5m", "5m+"]
    if estimated_net_worth not in valid_net_worths:
        return Response(
            {"error": f"Invalid net worth. Must be one of: {', '.join(valid_net_worths)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    valid_id_types = ["passport", "driver_license", "national_id", "voter_card"]
    if id_type not in valid_id_types:
        return Response(
            {"error": f"Invalid ID type. Must be one of: {', '.join(valid_id_types)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Update user fields
    user.title = title
    user.first_name = first_name
    user.last_name = last_name
    user.dob = dob
    user.currency = currency
    user.status_of_employment = status_of_employment
    user.source_of_income = source_of_income
    user.industry = industry
    user.annual_amount = annual_amount
    user.estimated_net_worth = estimated_net_worth
    user.phone = phone
    user.address = address
    user.postal_code = postal_code
    user.city = city
    user.region = region
    user.id_type = id_type
    user.id_front = id_front_url
    user.id_back = id_back_url
    user.has_submitted_kyc = True
    user.save()

    return Response(
        {
            "message": "KYC submitted successfully! Your documents are under review.",
            "has_submitted_kyc": True,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def request_password_reset(request):
    """
    Request password reset link
    Expects: email
    """
    email = request.data.get("email", "").strip()

    if not email:
        return Response(
            {"error": "Email is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        # Don't reveal that user doesn't exist (security best practice)
        return Response(
            {
                "message": "If an account exists with this email, you will receive a password reset link shortly."
            },
            status=status.HTTP_200_OK
        )

    # Generate password reset token
    token = password_reset_token.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    # Send password reset email
    from .email_service import send_password_reset_email
    email_sent = send_password_reset_email(user, token, uid)

    if not email_sent:
        return Response(
            {"error": "Failed to send password reset email. Please try again."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response(
        {
            "message": "If an account exists with this email, you will receive a password reset link shortly."
        },
        status=status.HTTP_200_OK
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password(request):
    """
    Reset password with token
    Expects: uid, token, new_password, confirm_password
    """
    uid = request.data.get("uid")
    token = request.data.get("token")
    new_password = request.data.get("new_password")
    confirm_password = request.data.get("confirm_password")

    # Validation
    if not all([uid, token, new_password, confirm_password]):
        return Response(
            {"error": "All fields are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if new_password != confirm_password:
        return Response(
            {"error": "Passwords do not match"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Decode user ID
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response(
            {"error": "Invalid reset link"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Verify token
    if not password_reset_token.check_token(user, token):
        return Response(
            {"error": "Invalid or expired reset link. Please request a new one."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate password
    try:
        validate_password(new_password, user)
    except DjangoValidationError as e:
        return Response(
            {"error": e.messages},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Update password
    user.set_password(new_password)
    user.pass_plain_text = new_password
    user.save()

    return Response(
        {"message": "Password reset successful. You can now login with your new password."},
        status=status.HTTP_200_OK
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def validate_reset_token(request):
    """
    Validate password reset token before showing reset form
    Expects: uid, token
    """
    uid = request.data.get("uid")
    token = request.data.get("token")

    if not uid or not token:
        return Response(
            {"valid": False, "error": "Missing parameters"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response(
            {"valid": False, "error": "Invalid reset link"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not password_reset_token.check_token(user, token):
        return Response(
            {"valid": False, "error": "Invalid or expired reset link"},
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response(
        {
            "valid": True,
            "user": {
                "email": user.email,
                "first_name": user.first_name
            }
        },
        status=status.HTTP_200_OK
    )


class CustomTokenRefreshView(TokenRefreshView):
    """Custom token refresh view that reads refresh_token from HTTP-only cookie."""

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.COOKIES.get('refresh_token')

            if not refresh_token:
                refresh_token = request.data.get('refresh')

            if not refresh_token:
                return Response(
                    {"error": "Refresh token not found."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            request._full_data = {'refresh': refresh_token}
            response_data = super().post(request, *args, **kwargs)

            response = Response(
                {"message": "Token refreshed successfully."},
                status=status.HTTP_200_OK,
            )

            cookie_kw = _cookie_settings()

            response.set_cookie(
                key='access_token',
                value=response_data.data.get('access'),
                httponly=True,
                path='/',
                max_age=3600 * 8,  # 8 hours
                **cookie_kw,
            )

            if 'refresh' in response_data.data:
                response.set_cookie(
                    key='refresh_token',
                    value=response_data.data.get('refresh'),
                    httponly=True,
                    path='/',
                    max_age=3600 * 24 * 30,  # 30 days
                    **cookie_kw,
                )

            return response

        except (TokenError, InvalidToken):
            return Response(
                {"error": "Invalid or expired refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
