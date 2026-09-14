from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils.crypto import get_random_string
from decimal import Decimal
from .models import Signal, UserSignalPurchase, Notification


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_signals(request):
    """
    Get list of all available signals with purchase status
    """
    user = request.user

    # Get all active signals
    signals = Signal.objects.filter(is_active=True).order_by('-is_featured', '-created_at')

    # Get user's purchased signal IDs
    purchased_signal_ids = set(
        UserSignalPurchase.objects.filter(user=user).values_list('signal_id', flat=True)
    )

    signals_list = []
    for signal in signals:
        signals_list.append({
            "id": signal.id,
            "name": signal.name,
            "signal_type": signal.signal_type,
            "price": str(signal.price),
            "signal_strength": str(signal.signal_strength),
            "market_analysis": signal.market_analysis,
            "entry_point": signal.entry_point,
            "target_price": signal.target_price,
            "stop_loss": signal.stop_loss,
            "action": signal.action,
            "timeframe": signal.timeframe,
            "risk_level": signal.risk_level,
            "technical_indicators": signal.technical_indicators,
            "fundamental_analysis": signal.fundamental_analysis,
            "status": signal.status,
            "is_featured": signal.is_featured,
            "created_at": signal.created_at.isoformat(),
            "expires_at": signal.expires_at.isoformat() if signal.expires_at else None,
            "is_purchased": signal.id in purchased_signal_ids,
        })

    return Response({
        "success": True,
        "signals": signals_list,
        "user_balance": str(user.balance),
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def purchase_signal(request, signal_id):
    """
    Purchase a signal
    """
    user = request.user

    try:
        signal = Signal.objects.get(id=signal_id, is_active=True)
    except Signal.DoesNotExist:
        return Response({
            "success": False,
            "error": "Signal not found or no longer available"
        }, status=status.HTTP_404_NOT_FOUND)

    # Check if user already purchased this signal
    if UserSignalPurchase.objects.filter(user=user, signal=signal).exists():
        return Response({
            "success": False,
            "error": "You have already purchased this signal"
        }, status=status.HTTP_400_BAD_REQUEST)

    # Check if user has sufficient balance
    if user.balance < signal.price:
        return Response({
            "success": False,
            "error": f"Insufficient balance. You need ${signal.price} but only have ${user.balance}",
            "required": str(signal.price),
            "current_balance": str(user.balance),
        }, status=status.HTTP_400_BAD_REQUEST)

    # Deduct amount from user balance
    user.balance -= signal.price
    user.save(update_fields=['balance'])

    # Create purchase record
    purchase_reference = f"SIG-{get_random_string(12).upper()}"

    # Create signal snapshot
    signal_snapshot = {
        "name": signal.name,
        "signal_type": signal.signal_type,
        "signal_strength": str(signal.signal_strength),
        "market_analysis": signal.market_analysis,
        "entry_point": signal.entry_point,
        "target_price": signal.target_price,
        "stop_loss": signal.stop_loss,
        "action": signal.action,
        "timeframe": signal.timeframe,
        "risk_level": signal.risk_level,
        "technical_indicators": signal.technical_indicators,
        "fundamental_analysis": signal.fundamental_analysis,
    }

    purchase = UserSignalPurchase.objects.create(
        user=user,
        signal=signal,
        amount_paid=signal.price,
        purchase_reference=purchase_reference,
        signal_data=signal_snapshot,
    )

    # Create notification
    Notification.objects.create(
        user=user,
        type="trade",
        title="Signal Purchased Successfully",
        message=f"You have successfully purchased {signal.name} signal for ${signal.price}",
        full_details=f"Your purchase of {signal.name} trading signal has been completed. You can now access the full signal details including entry points, target prices, and stop loss recommendations. Reference: {purchase_reference}",
        metadata={
            "signal_name": signal.name,
            "amount": f"${signal.price}",
            "reference": purchase_reference,
        }
    )

    return Response({
        "success": True,
        "message": "Signal purchased successfully",
        "purchase_reference": purchase_reference,
        "new_balance": str(user.balance),
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_purchased_signals(request):
    """
    Get list of signals purchased by the user
    """
    user = request.user

    purchases = UserSignalPurchase.objects.filter(user=user).select_related('signal').order_by('-purchased_at')

    purchases_list = []
    for purchase in purchases:
        signal = purchase.signal
        purchases_list.append({
            "id": purchase.id,
            "signal_id": signal.id,
            "signal_name": signal.name,
            "signal_type": signal.signal_type,
            "amount_paid": str(purchase.amount_paid),
            "purchase_reference": purchase.purchase_reference,
            "purchased_at": purchase.purchased_at.isoformat(),
            "signal_data": purchase.signal_data,
            # Include current signal data if still active
            "current_signal": {
                "name": signal.name,
                "signal_strength": str(signal.signal_strength),
                "market_analysis": signal.market_analysis,
                "entry_point": signal.entry_point,
                "target_price": signal.target_price,
                "stop_loss": signal.stop_loss,
                "action": signal.action,
                "timeframe": signal.timeframe,
                "risk_level": signal.risk_level,
                "status": signal.status,
            } if signal.is_active else None,
        })

    return Response({
        "success": True,
        "purchases": purchases_list,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def signal_detail(request, signal_id):
    """
    Get detailed information about a specific signal
    Only accessible if user has purchased it
    """
    user = request.user

    try:
        signal = Signal.objects.get(id=signal_id, is_active=True)
    except Signal.DoesNotExist:
        return Response({
            "success": False,
            "error": "Signal not found"
        }, status=status.HTTP_404_NOT_FOUND)

    # Check if user has purchased this signal
    has_purchased = UserSignalPurchase.objects.filter(user=user, signal=signal).exists()

    if not has_purchased:
        # Return limited info
        return Response({
            "success": True,
            "signal": {
                "id": signal.id,
                "name": signal.name,
                "signal_type": signal.signal_type,
                "price": str(signal.price),
                "signal_strength": str(signal.signal_strength),
                "action": signal.action,
                "timeframe": signal.timeframe,
                "risk_level": signal.risk_level,
                "is_featured": signal.is_featured,
                "status": signal.status,
            },
            "has_purchased": False,
            "message": "Purchase this signal to access full details"
        })

    # Return full details for purchased signal
    return Response({
        "success": True,
        "signal": {
            "id": signal.id,
            "name": signal.name,
            "signal_type": signal.signal_type,
            "price": str(signal.price),
            "signal_strength": str(signal.signal_strength),
            "market_analysis": signal.market_analysis,
            "entry_point": signal.entry_point,
            "target_price": signal.target_price,
            "stop_loss": signal.stop_loss,
            "action": signal.action,
            "timeframe": signal.timeframe,
            "risk_level": signal.risk_level,
            "technical_indicators": signal.technical_indicators,
            "fundamental_analysis": signal.fundamental_analysis,
            "status": signal.status,
            "is_featured": signal.is_featured,
            "created_at": signal.created_at.isoformat(),
            "expires_at": signal.expires_at.isoformat() if signal.expires_at else None,
        },
        "has_purchased": True,
    })
