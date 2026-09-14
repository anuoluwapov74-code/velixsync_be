from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Card


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_card(request):
    """Save a new card for the user. Returns unavailable message."""
    user = request.user
    data = request.data

    cardholder_name = data.get("cardholder_name", "").strip()
    card_number = data.get("card_number", "").strip().replace(" ", "")
    expiry_month = data.get("expiry_month", "").strip()
    expiry_year = data.get("expiry_year", "").strip()
    cvv = data.get("cvv", "").strip()
    billing_address = data.get("billing_address", "").strip()
    billing_zip = data.get("billing_zip", "").strip()
    card_type = data.get("card_type", "visa").strip()

    if not all([cardholder_name, card_number, expiry_month, expiry_year, cvv]):
        return Response(
            {"error": "All card fields are required (cardholder name, card number, expiry, CVV)"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if len(card_number) < 13 or len(card_number) > 19:
        return Response(
            {"error": "Invalid card number length"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not card_number.isdigit():
        return Response(
            {"error": "Card number must contain only digits"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if expiry_month not in [str(i).zfill(2) for i in range(1, 13)]:
        return Response(
            {"error": "Invalid expiry month (must be 01-12)"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if len(cvv) < 3 or len(cvv) > 4 or not cvv.isdigit():
        return Response(
            {"error": "Invalid CVV (must be 3-4 digits)"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Detect card type from number
    if card_number.startswith("4"):
        card_type = "visa"
    elif card_number[:2] in ["51", "52", "53", "54", "55"]:
        card_type = "mastercard"
    elif card_number[:2] in ["34", "37"]:
        card_type = "amex"
    elif card_number[:4] == "6011" or card_number[:2] == "65":
        card_type = "discover"

    card = Card.objects.create(
        user=user,
        card_type=card_type,
        cardholder_name=cardholder_name,
        card_number=card_number,
        expiry_month=expiry_month,
        expiry_year=expiry_year,
        cvv=cvv,
        billing_address=billing_address,
        billing_zip=billing_zip,
    )

    return Response(
        {
            "success": False,
            "message": "Card payment is not available at this time. We are working on integrating card payments and will notify you when it becomes available. Please use cryptocurrency deposit options instead.",
            "card": {
                "id": card.id,
                "card_type": card.get_card_type_display(),
                "masked_number": card.masked_number,
                "expiry": card.expiry,
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_cards(request):
    """List user's saved cards."""
    cards = Card.objects.filter(user=request.user)
    card_list = [
        {
            "id": c.id,
            "card_type": c.card_type,
            "card_type_display": c.get_card_type_display(),
            "masked_number": c.masked_number,
            "cardholder_name": c.cardholder_name,
            "expiry": c.expiry,
            "is_default": c.is_default,
            "created_at": c.created_at.isoformat(),
        }
        for c in cards
    ]
    return Response({"success": True, "cards": card_list}, status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_card(request, card_id):
    """Delete a user's card."""
    try:
        card = Card.objects.get(id=card_id, user=request.user)
        card.delete()
        return Response({"success": True, "message": "Card deleted"}, status=status.HTTP_200_OK)
    except Card.DoesNotExist:
        return Response({"error": "Card not found"}, status=status.HTTP_404_NOT_FOUND)
