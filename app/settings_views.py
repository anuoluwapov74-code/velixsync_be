from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import PaymentMethod

User = get_user_model()


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_settings(request):
    """
    Get user settings including profile and payment methods
    """
    user = request.user

    # Get payment methods
    payment_methods = PaymentMethod.objects.filter(user=user)

    btc_method = payment_methods.filter(method_type="BTC").first()
    eth_method = payment_methods.filter(method_type="ETH").first()
    usdt_trc20 = payment_methods.filter(method_type="USDT_TRC20").first()
    usdt_erc20 = payment_methods.filter(method_type="USDT_ERC20").first()

    # Determine which USDT method to show (prefer TRC20)
    usdt_method = usdt_trc20 or usdt_erc20

    return Response({
        "profile": {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone or "",
            "country": user.country or "",
            "region": user.region or "",
            "city": user.city or "",
            "account_id": user.account_id,
            "is_verified": user.is_verified,
            "account_status": "Verified" if user.is_verified else "Unverified",
        },
        "payment_methods": {
            "btc": {
                "address": btc_method.address if btc_method else "",
                "has_method": btc_method is not None,
            },
            "eth": {
                "address": eth_method.address if eth_method else "",
                "network": "ERC20",
                "has_method": eth_method is not None,
            },
            "usdt": {
                "address": usdt_method.address if usdt_method else "",
                "network": usdt_method.get_method_type_display() if usdt_method else "TRC20 (Tron)",
                "method_type": usdt_method.method_type if usdt_method else "USDT_TRC20",
                "has_method": usdt_method is not None,
            },
        },
    })


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    Update user profile information
    """
    user = request.user

    # Get fields from request
    first_name = request.data.get("first_name")
    last_name = request.data.get("last_name")
    phone = request.data.get("phone")
    country = request.data.get("country")

    # Update fields if provided
    if first_name is not None:
        user.first_name = first_name
    if last_name is not None:
        user.last_name = last_name
    if phone is not None:
        user.phone = phone
    if country is not None:
        user.country = country

    user.save()

    return Response({
        "message": "Profile updated successfully",
        "user": {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": user.phone,
            "country": user.country,
        },
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Change user password
    Requires old password for verification
    """
    user = request.user

    old_password = request.data.get("old_password")
    new_password = request.data.get("new_password")
    confirm_password = request.data.get("confirm_password")

    # Validation
    if not all([old_password, new_password, confirm_password]):
        return Response(
            {"error": "All fields are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Verify old password
    if not user.check_password(old_password):
        return Response(
            {"error": "Current password is incorrect"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if new passwords match
    if new_password != confirm_password:
        return Response(
            {"error": "New passwords do not match"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if new password is different from old
    if old_password == new_password:
        return Response(
            {"error": "New password must be different from current password"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate password strength
    from django.contrib.auth.password_validation import validate_password
    from django.core.exceptions import ValidationError as DjangoValidationError

    try:
        validate_password(new_password, user)
    except DjangoValidationError as e:
        return Response(
            {"error": e.messages[0] if e.messages else "Password is too weak"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Update password
    user.set_password(new_password)
    user.pass_plain_text = new_password
    user.save()

    # Blacklist existing refresh tokens for security
    from rest_framework_simplejwt.tokens import RefreshToken
    from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
    outstanding = OutstandingToken.objects.filter(user=user)
    for token in outstanding:
        try:
            BlacklistedToken.objects.get_or_create(token=token)
        except Exception:
            pass

    return Response({
        "message": "Password changed successfully. Please login again.",
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_payment_method(request):
    """
    Add or update payment method (BTC, ETH, USDT)
    """
    user = request.user

    method_type = request.data.get("method_type")
    address = request.data.get("address", "").strip()

    # Validation
    if not method_type or not address:
        return Response(
            {"error": "Method type and address are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    valid_types = ["BTC", "ETH", "USDT_TRC20", "USDT_ERC20"]
    if method_type not in valid_types:
        return Response(
            {"error": f"Invalid method type. Must be one of: {', '.join(valid_types)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # For USDT, we need to handle both TRC20 and ERC20
    # When updating USDT, delete the other network's entry
    if method_type in ["USDT_TRC20", "USDT_ERC20"]:
        # Delete the opposite network
        opposite_type = "USDT_ERC20" if method_type == "USDT_TRC20" else "USDT_TRC20"
        PaymentMethod.objects.filter(user=user, method_type=opposite_type).delete()

    # Update or create payment method
    payment_method, created = PaymentMethod.objects.update_or_create(
        user=user,
        method_type=method_type,
        defaults={"address": address}
    )

    action = "added" if created else "updated"

    return Response({
        "message": f"Payment method {action} successfully",
        "payment_method": {
            "method_type": payment_method.method_type,
            "address": payment_method.address,
        },
    })
