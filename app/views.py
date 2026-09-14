"""
Deposit & Withdrawal Views
HTTPOnly Cookie-based Token Authentication
"""

import random
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from .models import AdminWallet, Transaction, PaymentMethod, Notification, Stock
from .email_service import (
    send_admin_payment_intent_notification,
    send_admin_deposit_notification,
    send_admin_withdrawal_notification,
)


# ============================================================
# SYNC TRIGGER (called by cron-job.com)
# ============================================================

@api_view(["POST"])
@permission_classes([AllowAny])
def sync_trigger(request, sync_type):
    """
    Called by cron-job.com to run scheduled management commands.
    Protected by X-Sync-Secret header matching SYNC_SECRET env var.
    sync_type: 'prices' | 'rates' | 'news' | 'treemap' | 'profiles' | 'history'
    """
    from decouple import config
    from django.core.management import call_command

    secret = config("SYNC_SECRET", default="")
    if not secret or request.headers.get("X-Sync-Secret") != secret:
        return Response({"success": False, "error": "Unauthorized"}, status=401)

    ALLOWED = {
        "prices":   "sync_stock_prices",
        "rates":    "sync_crypto_rates",
        "news":     "fetch_fmp_news",
        "treemap":  "sync_treemap_stocks",
        "profiles": "sync_stock_profiles",
        "history":  "sync_stock_history",
    }
    cmd = ALLOWED.get(sync_type)
    if not cmd:
        return Response({"success": False, "error": "Unknown sync type"}, status=400)

    try:
        call_command(cmd)
        return Response({"success": True, "synced": sync_type})
    except Exception as exc:
        return Response({"success": False, "error": str(exc)}, status=500)


# ============================================================
# DEPOSIT VIEWS
# ============================================================

@api_view(["GET"])
@permission_classes([AllowAny])
def get_deposit_options(request):
    """
    Get all active admin wallets (deposit payment methods).
    Rates are sourced live from the Stock table (populated by sync_crypto_rates).
    Falls back to the manually-set AdminWallet.amount if not found.
    Public endpoint - no auth required.
    """
    # Map AdminWallet currency labels to FMP Stock symbols
    CURRENCY_TO_SYMBOL = {
        "BTC":         "BTCUSD",
        "ETH":         "ETHUSD",
        "SOL":         "SOLUSD",
        "BNB":         "BNBUSD",
        "XRP":         "XRPUSD",
        "TRX":         "TRXUSD",
        "USDT ERC20":  None,   # stablecoin — always 1:1
        "USDT TRC20":  None,
        "USDC":        None,
    }

    # Fetch live prices for all relevant symbols in one query
    symbols = [s for s in CURRENCY_TO_SYMBOL.values() if s]
    live_prices = {
        s.symbol: s.price
        for s in Stock.objects.filter(symbol__in=symbols, is_active=True)
    }

    wallets = AdminWallet.objects.filter(is_active=True)
    wallet_list = []
    for w in wallets:
        qr_code_url = None
        if w.qr_code:
            try:
                qr_code_url = w.qr_code.url
            except Exception:
                qr_code_url = None

        # Resolve live rate
        stock_sym = CURRENCY_TO_SYMBOL.get(w.currency)
        if stock_sym is None:
            # Stablecoin: 1 USD = 1 unit
            live_rate = "1.000000"
        elif stock_sym in live_prices and live_prices[stock_sym]:
            live_rate = str(live_prices[stock_sym])
        else:
            # Fallback to manually-set rate
            live_rate = str(w.amount)

        wallet_list.append({
            "id": w.id,
            "currency": w.currency,
            "currency_display": w.get_currency_display(),
            "amount": live_rate,
            "wallet_address": w.wallet_address,
            "qr_code_url": qr_code_url,
            "is_active": w.is_active,
        })

    return Response({
        "success": True,
        "wallets": wallet_list,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def create_deposit(request):
    """
    Create a new deposit transaction.
    Does NOT touch user balance - admin will approve later.
    """
    user = request.user
    currency = request.data.get("currency")
    dollar_amount = request.data.get("dollar_amount")
    currency_unit = request.data.get("currency_unit", "0")
    receipt = request.FILES.get("receipt")

    if not currency or not dollar_amount:
        return Response({
            "success": False,
            "error": "Currency and amount are required.",
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        amount = float(dollar_amount)
        if amount <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return Response({
            "success": False,
            "error": "Please enter a valid amount.",
        }, status=status.HTTP_400_BAD_REQUEST)

    # Create transaction (status=pending, balance NOT touched)
    reference = f"DEP-{random.randint(100000, 999999)}-{user.id}"

    transaction = Transaction.objects.create(
        user=user,
        transaction_type="deposit",
        amount=amount,
        currency=currency,
        unit=float(currency_unit) if currency_unit else 0,
        status="pending",
        reference=reference,
        description=f"Deposit of ${amount} via {currency}",
        receipt=receipt,
    )

    # Create notification
    Notification.objects.create(
        user=user,
        type="deposit",
        title="Deposit Request Submitted",
        message=f"Your deposit of ${amount:.2f} via {currency} is pending approval.",
        full_details=f"Deposit reference: {reference}. Amount: ${amount:.2f}. Currency: {currency}. Unit: {currency_unit}. This deposit is pending verification.",
        metadata={
            "amount": str(amount),
            "currency": currency,
            "reference": reference,
        },
    )

    # Notify admin (non-blocking — deposit is already recorded regardless of email outcome)
    try:
        sent = send_admin_deposit_notification(user, transaction)
        if not sent:
            logger.error(
                "create_deposit: admin email failed for user=%s reference=%s",
                user.email, reference,
            )
    except Exception as exc:
        logger.exception("create_deposit: unexpected error sending admin deposit email: %s", exc)

    return Response({
        "success": True,
        "message": "Deposit request submitted successfully!",
        "transaction": {
            "id": transaction.id,
            "reference": transaction.reference,
            "amount": str(transaction.amount),
            "currency": transaction.currency,
            "status": transaction.status,
            "created_at": transaction.created_at.isoformat(),
        },
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def deposit_payment_intent(request):
    """
    Notify admin that a user intends to make a deposit.
    Sends an email so staff can follow up if the deposit is not completed.
    """
    user = request.user
    currency = request.data.get("currency")
    dollar_amount = request.data.get("dollar_amount")
    currency_unit = request.data.get("currency_unit", "0")

    if not currency or not dollar_amount:
        return Response({
            "success": False,
            "error": "Currency and amount are required.",
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        sent = send_admin_payment_intent_notification(user, currency, dollar_amount, currency_unit)
        if not sent:
            logger.error(
                "deposit_payment_intent: email failed for user=%s currency=%s amount=%s",
                user.email, currency, dollar_amount,
            )
    except Exception as exc:
        logger.exception("deposit_payment_intent: unexpected error sending intent email: %s", exc)

    return Response({
        "success": True,
        "message": "Payment intent recorded.",
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_deposit_history(request):
    """Get user's deposit transaction history."""
    user = request.user
    limit = int(request.GET.get("limit", 10))

    transactions = Transaction.objects.filter(
        user=user,
        transaction_type="deposit",
    ).order_by("-created_at")[:limit]

    transaction_list = []
    for t in transactions:
        receipt_url = None
        if t.receipt:
            try:
                receipt_url = t.receipt.url
            except Exception:
                receipt_url = None

        transaction_list.append({
            "id": t.id,
            "reference": t.reference,
            "transaction_type": t.transaction_type,
            "transaction_type_display": t.get_transaction_type_display(),
            "amount": str(t.amount),
            "currency": t.currency,
            "unit": str(t.unit),
            "status": t.status,
            "status_display": t.get_status_display(),
            "created_at": t.created_at.isoformat(),
            "receipt_url": receipt_url,
        })

    return Response({
        "success": True,
        "transactions": transaction_list,
    })


# ============================================================
# WITHDRAWAL VIEWS
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_withdrawal_profile(request):
    """Get user profile info for withdrawal page."""
    user = request.user

    return Response({
        "success": True,
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "full_name": f"{user.first_name or ''} {user.last_name or ''}".strip() or user.email,
            "account_id": user.account_id or "",
            "balance": str(user.balance),
            "formatted_balance": f"${user.balance:,.2f}",
            "profit": str(user.profit),
            "formatted_profit": f"${user.profit:,.2f}",
            "is_verified": user.is_verified,
        },
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_withdrawal_methods(request):
    """Get user's saved payment/withdrawal methods."""
    user = request.user

    methods = PaymentMethod.objects.filter(user=user)

    method_list = []
    for m in methods:
        # Determine address based on method type
        address = ""
        if m.method_type in ("ETH", "BTC", "SOL", "USDT_ERC20", "USDT_TRC20"):
            address = m.address or ""
        elif m.method_type == "BANK":
            address = m.bank_account_number or ""
        elif m.method_type == "CASHAPP":
            address = m.cashapp_id or ""
        elif m.method_type == "PAYPAL":
            address = m.paypal_email or ""

        method_list.append({
            "id": m.id,
            "method_type": m.method_type,
            "display_name": m.get_method_type_display(),
            "address": address,
        })

    return Response({
        "success": True,
        "methods": method_list,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_withdrawal(request):
    """
    Create a new withdrawal transaction.
    Does NOT touch user balance - admin will approve later.
    """
    user = request.user
    method_type = request.data.get("method_type")
    amount = request.data.get("amount")
    withdrawal_address = request.data.get("withdrawal_address", "")
    source = request.data.get("source", "balance")

    if source not in ("balance", "profit"):
        source = "balance"

    if not method_type or not amount:
        return Response({
            "success": False,
            "error": "Method and amount are required.",
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        amount_val = float(amount)
        if amount_val <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return Response({
            "success": False,
            "error": "Please enter a valid amount.",
        }, status=status.HTTP_400_BAD_REQUEST)

    # Check correct source balance
    if source == "profit":
        available = float(user.profit)
        if amount_val > available:
            return Response({
                "success": False,
                "error": f"Insufficient profit. Your profit balance is ${user.profit:,.2f}",
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        available = float(user.balance)
        if amount_val > available:
            return Response({
                "success": False,
                "error": f"Insufficient balance. Your balance is ${user.balance:,.2f}",
            }, status=status.HTTP_400_BAD_REQUEST)

    # Create transaction (status=pending, balance NOT touched yet)
    reference = f"WDR-{random.randint(100000, 999999)}-{user.id}"

    transaction = Transaction.objects.create(
        user=user,
        transaction_type="withdrawal",
        amount=amount_val,
        currency=method_type,
        status="pending",
        reference=reference,
        source=source,
        description=f"Withdrawal of ${amount_val} via {method_type} to {withdrawal_address} (from {source})",
    )

    source_label = "profit" if source == "profit" else "main balance"

    # Create notification
    Notification.objects.create(
        user=user,
        type="withdrawal",
        title="Withdrawal Request Submitted",
        message=f"Your withdrawal of ${amount_val:.2f} from {source_label} via {method_type} is pending approval.",
        full_details=f"Withdrawal reference: {reference}. Amount: ${amount_val:.2f}. Source: {source_label}. Method: {method_type}. Address: {withdrawal_address}. This withdrawal is pending verification.",
        metadata={
            "amount": str(amount_val),
            "source": source,
            "method": method_type,
            "reference": reference,
            "address": withdrawal_address,
        },
    )

    # Notify admin (non-blocking — withdrawal is already recorded regardless of email outcome)
    try:
        sent = send_admin_withdrawal_notification(
            user, transaction, method_type=method_type, address=withdrawal_address,
        )
        if not sent:
            logger.error(
                "create_withdrawal: admin email failed for user=%s reference=%s",
                user.email, reference,
            )
    except Exception as exc:
        logger.exception("create_withdrawal: unexpected error sending admin withdrawal email: %s", exc)

    return Response({
        "success": True,
        "message": "Withdrawal request submitted successfully!",
        "transaction": {
            "id": transaction.id,
            "reference": transaction.reference,
            "amount": str(transaction.amount),
            "currency": transaction.currency,
            "status": transaction.status,
            "source": transaction.source,
            "new_balance": str(user.balance),
            "formatted_new_balance": f"${user.balance:,.2f}",
            "new_profit": str(user.profit),
            "formatted_new_profit": f"${user.profit:,.2f}",
            "created_at": transaction.created_at.isoformat(),
        },
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_withdrawal_history(request):
    """Get user's withdrawal transaction history."""
    user = request.user
    limit = int(request.GET.get("limit", 10))

    transactions = Transaction.objects.filter(
        user=user,
        transaction_type="withdrawal",
    ).order_by("-created_at")[:limit]

    transaction_list = []
    for t in transactions:
        transaction_list.append({
            "id": t.id,
            "reference": t.reference,
            "transaction_type": t.transaction_type,
            "transaction_type_display": t.get_transaction_type_display(),
            "amount": str(t.amount),
            "currency": t.currency,
            "unit": str(t.unit),
            "status": t.status,
            "status_display": t.get_status_display(),
            "created_at": t.created_at.isoformat(),
        })

    return Response({
        "success": True,
        "transactions": transaction_list,
    })


# ============================================================
# COMBINED TRANSACTION HISTORY
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_transaction_history(request):
    """Get all user transactions (both deposits and withdrawals)."""
    user = request.user
    limit = int(request.GET.get("limit", 20))
    tx_type = request.GET.get("type", "all")

    transactions = Transaction.objects.filter(user=user)

    if tx_type == "deposit":
        transactions = transactions.filter(transaction_type="deposit")
    elif tx_type == "withdrawal":
        transactions = transactions.filter(transaction_type="withdrawal")

    transactions = transactions.order_by("-created_at")[:limit]

    transaction_list = []
    for t in transactions:
        receipt_url = None
        if t.receipt:
            try:
                receipt_url = t.receipt.url
            except Exception:
                receipt_url = None

        transaction_list.append({
            "id": t.id,
            "reference": t.reference,
            "transaction_type": t.transaction_type,
            "transaction_type_display": t.get_transaction_type_display(),
            "amount": str(t.amount),
            "currency": t.currency,
            "unit": str(t.unit),
            "status": t.status,
            "status_display": t.get_status_display(),
            "created_at": t.created_at.isoformat(),
            "receipt_url": receipt_url,
        })

    return Response({
        "success": True,
        "transactions": transaction_list,
    })
