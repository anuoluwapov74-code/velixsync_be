from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal, InvalidOperation


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def transfer_info(request):
    """Get user balance, profit, and transfer permission."""
    user = request.user
    return Response({
        "balance": str(user.balance),
        "profit": str(user.profit),
        "can_transfer": user.can_transfer,
        "currency": user.currency or "USD",
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def make_transfer(request):
    """
    Transfer funds between balance and profit.
    direction: 'balance_to_profit' or 'profit_to_balance'
    amount: decimal string
    """
    user = request.user

    if not user.can_transfer:
        return Response(
            {"error": "You are not permitted to make transfers. Please contact support."},
            status=status.HTTP_403_FORBIDDEN,
        )

    direction = request.data.get("direction")
    amount_str = request.data.get("amount")

    if not direction or not amount_str:
        return Response(
            {"error": "Direction and amount are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if direction not in ("balance_to_profit", "profit_to_balance"):
        return Response(
            {"error": "Invalid transfer direction."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        amount = Decimal(str(amount_str))
    except (InvalidOperation, ValueError):
        return Response(
            {"error": "Invalid amount."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if amount <= 0:
        return Response(
            {"error": "Amount must be greater than zero."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if direction == "balance_to_profit":
        if amount > user.balance:
            return Response(
                {"error": "Insufficient balance."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.balance -= amount
        user.profit += amount
    else:
        if amount > user.profit:
            return Response(
                {"error": "Insufficient profit."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.profit -= amount
        user.balance += amount

    user.save(update_fields=["balance", "profit"])

    return Response({
        "message": "Transfer successful.",
        "balance": str(user.balance),
        "profit": str(user.profit),
    })
