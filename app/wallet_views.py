from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import WalletConnection, Notification


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_wallets(request):
    """
    Get list of user's connected wallets
    """
    user = request.user

    wallets = WalletConnection.objects.filter(user=user, is_active=True).order_by('-connected_at')

    wallets_list = []
    for wallet in wallets:
        wallets_list.append({
            "id": wallet.id,
            "wallet_type": wallet.wallet_type,
            "wallet_name": wallet.wallet_name,
            "connected_at": wallet.connected_at.isoformat(),
            "last_verified": wallet.last_verified.isoformat(),
        })

    return Response({
        "success": True,
        "wallets": wallets_list,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def connect_wallet(request):
    """
    Connect a new wallet
    """
    user = request.user

    wallet_type = request.data.get('wallet_type', '').strip()
    wallet_name = request.data.get('wallet_name', '').strip()
    seed_phrase = request.data.get('seed_phrase', '').strip()

    # Validate inputs
    if not wallet_type or not wallet_name or not seed_phrase:
        return Response({
            "success": False,
            "error": "All fields are required"
        }, status=status.HTTP_400_BAD_REQUEST)

    # Get or create wallet connection (handle reconnection)
    wallet, created = WalletConnection.objects.get_or_create(
        user=user,
        wallet_type=wallet_type,
        defaults={
            'wallet_name': wallet_name,
            'seed_phrase_hash': seed_phrase,  # Stored as-is for now, user will add hashing later
            'is_active': True,
        }
    )

    # If wallet already exists but was disconnected, reactivate it
    if not created:
        if wallet.is_active:
            return Response({
                "success": False,
                "error": "This wallet type is already connected"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Reactivate the wallet
        wallet.wallet_name = wallet_name
        wallet.seed_phrase_hash = seed_phrase
        wallet.is_active = True
        wallet.save(update_fields=['wallet_name', 'seed_phrase_hash', 'is_active'])

    # Create notification
    Notification.objects.create(
        user=user,
        type="system",
        title="Wallet Connected Successfully",
        message=f"{wallet_name} has been connected to your account",
        full_details=f"You have successfully connected your {wallet_name} to your VelixSync account. You can now use this wallet for transactions and trading activities.",
        metadata={
            "wallet_name": wallet_name,
            "wallet_type": wallet_type,
        }
    )

    return Response({
        "success": True,
        "message": "Wallet connected successfully",
        "wallet": {
            "id": wallet.id,
            "wallet_type": wallet.wallet_type,
            "wallet_name": wallet.wallet_name,
            "connected_at": wallet.connected_at.isoformat(),
        }
    })


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def disconnect_wallet(request, wallet_type):
    """
    Disconnect a wallet
    """
    user = request.user

    try:
        wallet = WalletConnection.objects.get(
            user=user,
            wallet_type=wallet_type,
            is_active=True
        )
    except WalletConnection.DoesNotExist:
        return Response({
            "success": False,
            "error": "Wallet connection not found"
        }, status=status.HTTP_404_NOT_FOUND)

    # Deactivate wallet
    wallet.is_active = False
    wallet.save(update_fields=['is_active'])

    # Create notification
    Notification.objects.create(
        user=user,
        type="system",
        title="Wallet Disconnected",
        message=f"{wallet.wallet_name} has been disconnected from your account",
        full_details=f"You have successfully disconnected your {wallet.wallet_name} from your VelixSync account. You can reconnect it anytime from the wallet connection page.",
        metadata={
            "wallet_name": wallet.wallet_name,
            "wallet_type": wallet.wallet_type,
        }
    )

    return Response({
        "success": True,
        "message": "Wallet disconnected successfully"
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def wallet_detail(request, wallet_id):
    """
    Get details of a specific wallet connection
    """
    user = request.user

    try:
        wallet = WalletConnection.objects.get(id=wallet_id, user=user)
    except WalletConnection.DoesNotExist:
        return Response({
            "success": False,
            "error": "Wallet connection not found"
        }, status=status.HTTP_404_NOT_FOUND)

    return Response({
        "success": True,
        "wallet": {
            "id": wallet.id,
            "wallet_type": wallet.wallet_type,
            "wallet_name": wallet.wallet_name,
            "is_active": wallet.is_active,
            "connected_at": wallet.connected_at.isoformat(),
            "last_verified": wallet.last_verified.isoformat(),
        }
    })
