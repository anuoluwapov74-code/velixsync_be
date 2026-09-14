from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Q
from django.conf import settings
import secrets
import string
from .models import CustomUser, Transaction


def generate_unique_referral_code():
    """Generate a unique 8-character referral code"""

    while True:
        # Generate random 8-character code (uppercase letters and digits)
        code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))

        # Check if code already exists
        if not CustomUser.objects.filter(referral_code=code).exists():
            return code


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def referral_info(request):
    """
    Get user's referral information including code, link, stats
    """
    user = request.user

    # Get or generate referral code if user doesn't have one
    if not user.referral_code:
        user.referral_code = generate_unique_referral_code()
        user.save(update_fields=['referral_code'])

    # Build referral link - get frontend URL from header or use settings
    frontend_url = request.headers.get('X-Frontend-URL', settings.FRONTEND_URL)
    referral_link = f"{frontend_url}/register?ref={user.referral_code}"

    # Get total referrals count
    total_referrals = CustomUser.objects.filter(referred_by=user).count()

    # Get total earnings from referral bonus
    total_earnings = user.referral_bonus_earned or 0

    # Referral bonus rate (10% of first deposit)
    referral_bonus_rate = 10

    return Response({
        "success": True,
        "referral_data": {
            "referral_code": user.referral_code,
            "referral_link": referral_link,
            "total_referrals": total_referrals,
            "total_earnings": str(total_earnings),
            "referral_bonus_rate": referral_bonus_rate,
        }
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def referral_list(request):
    """
    Get list of users who used this user's referral code
    """
    user = request.user

    # Get all users referred by this user
    referrals = CustomUser.objects.filter(referred_by=user).order_by('-date_joined')

    referrals_list = []
    for referred_user in referrals:
        # Check if user has made a deposit
        has_deposited = Transaction.objects.filter(
            user=referred_user,
            transaction_type='deposit',
            status='completed'
        ).exists()

        # Calculate bonus earned from this referral
        # 10% of their first completed deposit
        bonus_earned = 0
        if has_deposited:
            first_deposit = Transaction.objects.filter(
                user=referred_user,
                transaction_type='deposit',
                status='completed'
            ).order_by('created_at').first()

            if first_deposit:
                bonus_earned = float(first_deposit.amount) * 0.10  # 10% bonus

        referrals_list.append({
            "id": referred_user.id,
            "email": referred_user.email,
            "first_name": referred_user.first_name or "",
            "last_name": referred_user.last_name or "",
            "date_joined": referred_user.date_joined.isoformat() if referred_user.date_joined else None,
            "has_deposited": has_deposited,
            "bonus_earned": str(bonus_earned),
        })

    return Response({
        "success": True,
        "referrals": referrals_list
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate_referral_code(request):
    """
    Generate or regenerate user's referral code
    """
    user = request.user

    # Check if user wants to force regeneration
    force = request.data.get('force', False)

    if user.referral_code and not force:
        return Response({
            "success": False,
            "error": "You already have a referral code. Set 'force' to true to regenerate."
        }, status=status.HTTP_400_BAD_REQUEST)

    # Generate new code
    old_code = user.referral_code
    new_code = generate_unique_referral_code()

    user.referral_code = new_code
    user.save(update_fields=['referral_code'])

    # Build referral link
    frontend_url = request.headers.get('X-Frontend-URL', settings.FRONTEND_URL)
    referral_link = f"{frontend_url}/register?ref={new_code}"

    message = "Referral code generated successfully!" if not old_code else "Referral code regenerated successfully!"

    return Response({
        "success": True,
        "message": message,
        "referral_code": new_code,
        "referral_link": referral_link,
    })


@api_view(["GET"])
@permission_classes([])  # Allow anyone to validate referral codes
def validate_referral_code(request):
    """
    Validate a referral code and return referrer information
    """
    code = request.GET.get('code', '').strip().upper()

    if not code:
        return Response({
            "success": False,
            "valid": False,
            "error": "No referral code provided"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        referrer = CustomUser.objects.get(referral_code=code)

        # Get referrer's full name
        name = f"{referrer.first_name} {referrer.last_name}".strip()
        if not name:
            name = referrer.email.split('@')[0]  # Use email username as fallback

        return Response({
            "success": True,
            "valid": True,
            "referrer": {
                "name": name,
                "email": referrer.email
            }
        })
    except CustomUser.DoesNotExist:
        return Response({
            "success": True,
            "valid": False,
            "error": "Invalid referral code"
        })
