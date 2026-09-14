from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from decimal import Decimal

from app.models import (
    CustomUser, Transaction, Stock, AdminWallet,
    Portfolio, Notification, UserStockPosition,
    Trader, UserCopyTraderHistory, UserTraderCopy,
    WalletConnection, Card,
)
from .forms import (
    AddTradeForm, AddEarningsForm, ApproveDepositForm,
    ApproveWithdrawalForm, ApproveKYCForm, AddCopyTradeForm,
    EditCopyTradeForm, AddTraderForm, EditTraderForm, EditDepositForm,
    AdminWalletForm, CardEditForm, AddUserDirectTradeForm, StockForm,
    UserEditForm,
)
from .decorators import admin_required


# ---------------------------------------------------------------------------
# FMP Symbol Search API
# ---------------------------------------------------------------------------

def fmp_symbol_search(request):
    """FMP symbol search endpoint for admin autocomplete. Returns JSON."""
    from app import fmp_client
    q = request.GET.get("q", "").strip()
    if len(q) < 1:
        return JsonResponse([], safe=False)
    results = fmp_client.search_symbols(q, limit=15)
    return JsonResponse(results, safe=False)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _paginate(queryset_or_list, request, per_page=20):
    """Return a Page object and metadata dict."""
    paginator = Paginator(queryset_or_list, per_page)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return page_obj, paginator


def _resolve_range(exact, range_val, mapping, fallback=0):
    """Pick exact value, mapped range mid-point, or fallback."""
    if exact:
        return exact
    if range_val and range_val in mapping:
        return mapping[range_val]
    return fallback


_COPIERS_MAP = {'1-10': 5, '11-20': 15, '21-30': 25, '31-50': 40, '51-100': 75, '101-200': 150, '201-300': 250, '300+': 350}
_TRADES_MAP = {'1-50': 25, '51-100': 75, '101-200': 150, '201-300': 250, '301-500': 400, '500+': 600}
_SUBS_MAP = {'0': 0, '1-10': 5, '11-25': 18, '26-50': 38, '51-100': 75, '101-200': 150, '200+': 250}
_POS_MAP = {'0': 0, '1-5': 3, '6-10': 8, '11-20': 15, '20+': 25}


def _pick(custom, dropdown, fallback):
    """Return custom value if truthy, else dropdown, else fallback."""
    if custom:
        return custom
    if dropdown:
        return Decimal(dropdown) if isinstance(fallback, Decimal) else dropdown
    return fallback


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard:dashboard')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, f'Welcome back, {user.email}!')
            return redirect('dashboard:dashboard')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions.')
    return render(request, 'dashboard/login.html')


@admin_required
def admin_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('dashboard:login')


# ---------------------------------------------------------------------------
# Dashboard Overview
# ---------------------------------------------------------------------------

@admin_required
def dashboard(request):
    total_users = CustomUser.objects.filter(is_active=True).count()
    verified_users = CustomUser.objects.filter(is_verified=True).count()
    pending_kyc = CustomUser.objects.filter(has_submitted_kyc=True, is_verified=False).count()
    pending_deposits = Transaction.objects.filter(transaction_type='deposit', status='pending').count()
    pending_withdrawals = Transaction.objects.filter(transaction_type='withdrawal', status='pending').count()
    total_deposits = Transaction.objects.filter(transaction_type='deposit', status='completed').aggregate(t=Sum('amount'))['t'] or Decimal('0.00')
    total_withdrawals = Transaction.objects.filter(transaction_type='withdrawal', status='completed').aggregate(t=Sum('amount'))['t'] or Decimal('0.00')
    recent_transactions = Transaction.objects.select_related('user').order_by('-created_at')[:10]
    recent_users = CustomUser.objects.filter(is_active=True).order_by('-date_joined')[:5]

    return render(request, 'dashboard/dashboard.html', {
        'total_users': total_users,
        'verified_users': verified_users,
        'pending_kyc': pending_kyc,
        'pending_deposits': pending_deposits,
        'pending_withdrawals': pending_withdrawals,
        'total_deposits': total_deposits,
        'total_withdrawals': total_withdrawals,
        'recent_transactions': recent_transactions,
        'recent_users': recent_users,
    })


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

@admin_required
def users_list(request):
    search_query = request.GET.get('search', '')
    filter_status = request.GET.get('status', '')
    users = CustomUser.objects.all().order_by('-date_joined')

    if search_query:
        users = users.filter(
            Q(email__icontains=search_query) | Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) | Q(account_id__icontains=search_query)
        )
    if filter_status == 'verified':
        users = users.filter(is_verified=True)
    elif filter_status == 'unverified':
        users = users.filter(is_verified=False)
    elif filter_status == 'kyc_pending':
        users = users.filter(has_submitted_kyc=True, is_verified=False)

    page_obj, paginator = _paginate(users, request, 20)
    return render(request, 'dashboard/users.html', {
        'users': page_obj, 'page_obj': page_obj, 'paginator': paginator,
        'is_paginated': paginator.num_pages > 1,
        'search_query': search_query, 'filter_status': filter_status,
    })


@admin_required
def user_detail(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'verify':
            user.is_verified = True
            user.save()
            messages.success(request, f'{user.email} has been verified.')
        elif action == 'unverify':
            user.is_verified = False
            user.save()
            messages.success(request, f'{user.email} verification removed.')
        elif action == 'activate':
            user.is_active = True
            user.save()
            messages.success(request, f'{user.email} has been activated.')
        elif action == 'deactivate':
            user.is_active = False
            user.save()
            messages.success(request, f'{user.email} has been deactivated.')
        elif action == 'update_balance':
            new_balance = request.POST.get('balance')
            if new_balance:
                user.balance = Decimal(new_balance)
                user.save()
                messages.success(request, f'Balance updated to ${user.balance}')
        elif action == 'update_profit':
            new_profit = request.POST.get('profit')
            if new_profit:
                user.profit = Decimal(new_profit)
                user.save()
                messages.success(request, f'Profit updated to ${user.profit}')
        elif action == 'update_target':
            new_target = request.POST.get('target')
            if new_target:
                user.target = Decimal(new_target)
                user.save()
                messages.success(request, f'Portfolio target updated to ${user.target}')
        elif action == 'toggle_transfer':
            user.can_transfer = not user.can_transfer
            user.save(update_fields=['can_transfer'])
            status = 'enabled' if user.can_transfer else 'disabled'
            messages.success(request, f'Transfer {status} for {user.email}')
        elif action == 'toggle_portfolio_growth':
            user.show_portfolio_growth = not user.show_portfolio_growth
            user.save(update_fields=['show_portfolio_growth'])
            status = 'enabled' if user.show_portfolio_growth else 'disabled'
            messages.success(request, f'Portfolio Growth {status} for {user.email}')
        elif action == 'delete_portfolio':
            portfolio_id = request.POST.get('portfolio_id')
            if portfolio_id:
                Portfolio.objects.filter(id=portfolio_id, user=user).delete()
                messages.success(request, 'Portfolio entry deleted.')
        elif action == 'update_portfolio':
            portfolio_id = request.POST.get('portfolio_id')
            if portfolio_id:
                try:
                    p = Portfolio.objects.get(id=portfolio_id, user=user)
                    p.invested = Decimal(request.POST.get('invested', p.invested))
                    p.profit_loss = Decimal(request.POST.get('profit_loss', p.profit_loss))
                    p.value = p.invested + p.profit_loss
                    p.is_active = request.POST.get('is_active') == 'on'
                    p.save()
                    messages.success(request, 'Portfolio updated.')
                except Portfolio.DoesNotExist:
                    messages.error(request, 'Portfolio not found.')
        elif action == 'generate_reset_link':
            # Support fallback for when the automated reset email bounces/is
            # throttled (e.g. Microsoft consumer domains via Resend/SES).
            # Uses the exact same token mechanism as the emailed link — same
            # 1-hour expiry, same /reset-password page — just skips sending
            # it so an admin can hand it to the client directly.
            from django.conf import settings
            from django.utils.http import urlsafe_base64_encode
            from django.utils.encoding import force_bytes
            from app.auth_views import password_reset_token

            token = password_reset_token.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"

            transactions = Transaction.objects.filter(user=user).order_by('-created_at')[:20]
            portfolios = Portfolio.objects.filter(user=user).order_by('-is_active', '-opened_at')
            return render(request, 'dashboard/user_detail.html', {
                'view_user': user, 'transactions': transactions, 'portfolios': portfolios,
                'generated_reset_link': reset_link,
            })
        return redirect('dashboard:user_detail', user_id=user.id)

    transactions = Transaction.objects.filter(user=user).order_by('-created_at')[:20]
    portfolios = Portfolio.objects.filter(user=user).order_by('-is_active', '-opened_at')

    return render(request, 'dashboard/user_detail.html', {
        'view_user': user, 'transactions': transactions, 'portfolios': portfolios,
    })


@admin_required
def user_edit(request, user_id):
    obj = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        form = UserEditForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            obj.first_name            = d['first_name']
            obj.last_name             = d['last_name']
            obj.email                 = d['email']
            obj.phone                 = d['phone']
            obj.country               = d['country']
            obj.region                = d['region']
            obj.city                  = d['city']
            obj.address               = d['address']
            obj.postal_code           = d['postal_code']
            obj.currency              = d['currency']
            obj.dob                   = d['dob']
            obj.balance               = d['balance']
            obj.profit                = d['profit']
            obj.target                = d['target']
            obj.title                 = d['title']
            obj.id_type               = d['id_type']
            obj.status_of_employment  = d['status_of_employment']
            obj.source_of_income      = d['source_of_income']
            obj.industry              = d['industry']
            obj.level_of_education    = d['level_of_education']
            obj.annual_amount         = d['annual_amount']
            obj.estimated_net_worth   = d['estimated_net_worth']
            obj.current_loyalty_status = d['current_loyalty_status']
            obj.next_loyalty_status   = d['next_loyalty_status']
            obj.next_amount_to_upgrade = d['next_amount_to_upgrade']
            obj.is_active             = d['is_active']
            obj.is_verified           = d['is_verified']
            obj.email_verified        = d['email_verified']
            obj.can_transfer          = d['can_transfer']
            obj.two_factor_enabled    = d['two_factor_enabled']
            obj.is_staff              = d['is_staff']
            obj.show_portfolio_growth = d['show_portfolio_growth']
            plain = d.get('new_password', '').strip()
            if plain:
                obj.set_password(plain)
                obj.pass_plain_text = plain
            obj.save()
            messages.success(request, f'{obj.email} updated successfully.')
            return redirect('dashboard:user_detail', user_id=obj.id)
    else:
        initial = {
            'first_name': obj.first_name, 'last_name': obj.last_name,
            'email': obj.email, 'phone': obj.phone, 'country': obj.country,
            'region': obj.region, 'city': obj.city, 'address': obj.address,
            'postal_code': obj.postal_code, 'currency': obj.currency, 'dob': obj.dob,
            'balance': obj.balance, 'profit': obj.profit, 'target': obj.target,
            'title': obj.title or '', 'id_type': obj.id_type or '',
            'status_of_employment': obj.status_of_employment or '',
            'source_of_income': obj.source_of_income or '',
            'industry': obj.industry or '',
            'level_of_education': obj.level_of_education or '',
            'annual_amount': obj.annual_amount or '',
            'estimated_net_worth': obj.estimated_net_worth or '',
            'current_loyalty_status': obj.current_loyalty_status,
            'next_loyalty_status': obj.next_loyalty_status,
            'next_amount_to_upgrade': obj.next_amount_to_upgrade,
            'is_active': obj.is_active, 'is_verified': obj.is_verified,
            'email_verified': obj.email_verified, 'can_transfer': obj.can_transfer,
            'two_factor_enabled': obj.two_factor_enabled, 'is_staff': obj.is_staff,
            'show_portfolio_growth': obj.show_portfolio_growth,
        }
        form = UserEditForm(initial=initial)

    return render(request, 'dashboard/edit_user.html', {'form': form, 'view_user': obj})


@admin_required
def delete_user(request, user_id):
    view_user = get_object_or_404(CustomUser, id=user_id)

    if view_user.is_superuser:
        messages.error(request, "Superuser accounts cannot be deleted.")
        return redirect('dashboard:user_detail', user_id=user_id)

    if request.user.id == view_user.id:
        messages.error(request, "You cannot delete your own account.")
        return redirect('dashboard:user_detail', user_id=user_id)

    if request.method == 'POST':
        email = view_user.email
        try:
            with transaction.atomic():
                # ── 1. JWT token blacklist (BlacklistedToken → OutstandingToken chain) ──
                try:
                    from rest_framework_simplejwt.token_blacklist.models import (
                        BlacklistedToken, OutstandingToken,
                    )
                    BlacklistedToken.objects.filter(token__user=view_user).delete()
                    OutstandingToken.objects.filter(user=view_user).delete()
                except Exception:
                    pass

                # ── 2. All user-related records (explicit order avoids SQLite FK issues) ──
                view_user.portfolios.all().delete()
                view_user.direct_trade_history.all().delete()
                view_user.copied_traders.all().delete()
                view_user.transactions.all().delete()
                view_user.notifications.all().delete()
                view_user.stock_positions.all().delete()
                view_user.wallet_connections.all().delete()
                view_user.cards.all().delete()
                view_user.tickets.all().delete()
                view_user.payment_methods.all().delete()
                view_user.signal_purchases.all().delete()
                view_user.trades.all().delete()

                # ── 3. Admin action log entries ──
                try:
                    from django.contrib.admin.models import LogEntry
                    LogEntry.objects.filter(user=view_user).delete()
                except Exception:
                    pass

                # ── 4. Clear self-referential referred_by FK on other users ──
                CustomUser.objects.filter(referred_by=view_user).update(referred_by=None)

                # ── 5. Delete the user (no FK children remain) ──
                view_user.delete()

            messages.success(request, f"User {email} has been permanently deleted.")
            return redirect('dashboard:users_list')
        except Exception as e:
            messages.error(request, f"Could not delete user: {e}")
            return redirect('dashboard:user_detail', user_id=user_id)

    return render(request, 'dashboard/delete_user.html', {'view_user': view_user})


# ---------------------------------------------------------------------------
# KYC
# ---------------------------------------------------------------------------

@admin_required
def kyc_requests(request):
    status_filter = request.GET.get('status', 'pending')
    search_query = request.GET.get('search', '').strip()

    if status_filter == 'pending':
        users = CustomUser.objects.filter(has_submitted_kyc=True, is_verified=False)
    elif status_filter == 'approved':
        users = CustomUser.objects.filter(has_submitted_kyc=True, is_verified=True)
    else:
        users = CustomUser.objects.filter(has_submitted_kyc=True)

    if search_query:
        users = users.filter(
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    users = users.order_by('-date_joined')

    page_obj, paginator = _paginate(users, request, 15)
    return render(request, 'dashboard/kyc_requests.html', {
        'kyc_requests': page_obj, 'page_obj': page_obj, 'paginator': paginator,
        'is_paginated': paginator.num_pages > 1, 'status_filter': status_filter,
        'search_query': search_query,
    })


@admin_required
def kyc_detail(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id, has_submitted_kyc=True)
    if request.method == 'POST':
        form = ApproveKYCForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            admin_notes = form.cleaned_data['admin_notes']
            if action == 'approve':
                user.is_verified = True
                user.save()
                Notification.objects.create(user=user, type='system', title='KYC Approved',
                    message='Your KYC verification has been approved!',
                    full_details='Your account is now fully verified. You can access all features.')
                messages.success(request, f'KYC approved for {user.email}')
            else:
                user.is_verified = False
                user.has_submitted_kyc = False
                user.save()
                Notification.objects.create(user=user, type='alert', title='KYC Rejected',
                    message='Your KYC verification was not approved.',
                    full_details=admin_notes or 'Please review your documents and submit again.')
                messages.warning(request, f'KYC rejected for {user.email}')
            return redirect('dashboard:kyc_requests')
    else:
        form = ApproveKYCForm()
    return render(request, 'dashboard/kyc_detail.html', {'view_user': user, 'form': form})


# ---------------------------------------------------------------------------
# Deposits
# ---------------------------------------------------------------------------

@admin_required
def deposits(request):
    status_filter = request.GET.get('status', 'pending')
    qs = Transaction.objects.filter(transaction_type='deposit').select_related('user').order_by('-created_at')
    if status_filter and status_filter != 'all':
        qs = qs.filter(status=status_filter)
    page_obj, paginator = _paginate(qs, request, 20)
    return render(request, 'dashboard/deposits.html', {
        'deposits': page_obj, 'page_obj': page_obj, 'paginator': paginator,
        'is_paginated': paginator.num_pages > 1, 'status_filter': status_filter,
    })


@admin_required
def deposit_detail(request, transaction_id):
    deposit = get_object_or_404(Transaction, id=transaction_id, transaction_type='deposit')
    if request.method == 'POST':
        form = ApproveDepositForm(request.POST)
        if form.is_valid():
            status = form.cleaned_data['status']
            admin_notes = form.cleaned_data['admin_notes']
            deposit.status = status
            deposit.save()
            if status == 'completed':
                deposit.user.balance += deposit.amount
                deposit.user.save()
                deposit.user.update_loyalty_tier()
                Notification.objects.create(user=deposit.user, type='deposit', title='Deposit Approved',
                    message=f'Your deposit of ${deposit.amount} has been approved.',
                    full_details=f'Amount: ${deposit.amount}\nReference: {deposit.reference}')
                messages.success(request, f'Deposit approved — ${deposit.amount} credited to {deposit.user.email}')
            else:
                Notification.objects.create(user=deposit.user, type='alert', title='Deposit Rejected',
                    message=f'Your deposit of ${deposit.amount} was not approved.',
                    full_details=admin_notes or 'Please contact support.')
                messages.warning(request, f'Deposit rejected for {deposit.user.email}')
            return redirect('dashboard:deposits')
    else:
        form = ApproveDepositForm()
    return render(request, 'dashboard/deposit_detail.html', {'deposit': deposit, 'form': form})


@admin_required
def edit_deposit(request, transaction_id):
    deposit = get_object_or_404(Transaction, id=transaction_id, transaction_type='deposit')
    if request.method == 'POST':
        form = EditDepositForm(request.POST, request.FILES)
        if form.is_valid():
            old_amount, old_status = deposit.amount, deposit.status
            deposit.amount = form.cleaned_data['amount']
            deposit.currency = form.cleaned_data['currency']
            deposit.unit = form.cleaned_data['unit']
            deposit.status = form.cleaned_data['status']
            deposit.description = form.cleaned_data['description']
            deposit.reference = form.cleaned_data['reference']
            if form.cleaned_data.get('receipt'):
                deposit.receipt = form.cleaned_data['receipt']
            deposit.save()

            # Balance adjustments
            if old_status != deposit.status:
                if old_status == 'completed' and deposit.status != 'completed':
                    deposit.user.balance -= old_amount
                    deposit.user.save()
                    messages.warning(request, f'${old_amount} deducted from {deposit.user.email} balance.')
                elif old_status != 'completed' and deposit.status == 'completed':
                    deposit.user.balance += deposit.amount
                    deposit.user.save()
                    deposit.user.update_loyalty_tier()
                    messages.success(request, f'${deposit.amount} credited to {deposit.user.email} balance.')
            elif deposit.status == 'completed' and old_amount != deposit.amount:
                diff = deposit.amount - old_amount
                deposit.user.balance += diff
                deposit.user.save()
                if diff > 0:
                    messages.success(request, f'Additional ${diff} credited.')
                else:
                    messages.warning(request, f'${abs(diff)} deducted.')

            Notification.objects.create(user=deposit.user, type='deposit', title='Deposit Updated',
                message='Your deposit has been updated.',
                full_details=f'Amount: ${deposit.amount}\nCurrency: {deposit.currency}\nStatus: {deposit.status}\nRef: {deposit.reference}')
            messages.success(request, 'Deposit updated successfully!')
            return redirect('dashboard:deposit_detail', transaction_id=deposit.id)
    else:
        form = EditDepositForm(initial={
            'amount': deposit.amount, 'currency': deposit.currency, 'unit': deposit.unit,
            'status': deposit.status, 'description': deposit.description or '', 'reference': deposit.reference,
        })
    return render(request, 'dashboard/edit_deposit.html', {'form': form, 'deposit': deposit})


# ---------------------------------------------------------------------------
# Withdrawals
# ---------------------------------------------------------------------------

@admin_required
def withdrawals(request):
    status_filter = request.GET.get('status', 'pending')
    qs = Transaction.objects.filter(transaction_type='withdrawal').select_related('user').order_by('-created_at')
    if status_filter and status_filter != 'all':
        qs = qs.filter(status=status_filter)
    page_obj, paginator = _paginate(qs, request, 20)
    return render(request, 'dashboard/withdrawals.html', {
        'withdrawals': page_obj, 'page_obj': page_obj, 'paginator': paginator,
        'is_paginated': paginator.num_pages > 1, 'status_filter': status_filter,
    })


@admin_required
def withdrawal_detail(request, transaction_id):
    withdrawal = get_object_or_404(Transaction, id=transaction_id, transaction_type='withdrawal')
    if request.method == 'POST':
        form = ApproveWithdrawalForm(request.POST)
        if form.is_valid():
            status = form.cleaned_data['status']
            admin_notes = form.cleaned_data['admin_notes']
            withdrawal.status = status
            withdrawal.save()
            source = withdrawal.source or 'balance'
            if status == 'completed':
                # Deduct from the correct source
                if source == 'profit':
                    withdrawal.user.profit -= withdrawal.amount
                else:
                    withdrawal.user.balance -= withdrawal.amount
                withdrawal.user.save()
                source_label = 'profit' if source == 'profit' else 'main balance'
                Notification.objects.create(user=withdrawal.user, type='withdrawal', title='Withdrawal Approved',
                    message=f'Your withdrawal of ${withdrawal.amount} from {source_label} has been processed.',
                    full_details=f'Amount: ${withdrawal.amount}\nSource: {source_label}\nReference: {withdrawal.reference}')
                messages.success(request, f'Withdrawal approved for {withdrawal.user.email}')
            else:
                Notification.objects.create(user=withdrawal.user, type='alert', title='Withdrawal Rejected',
                    message=f'Your withdrawal of ${withdrawal.amount} was not processed.',
                    full_details=admin_notes or 'Your withdrawal request has been rejected.')
                messages.warning(request, f'Withdrawal rejected for {withdrawal.user.email}')
            return redirect('dashboard:withdrawals')
    else:
        form = ApproveWithdrawalForm()
    return render(request, 'dashboard/withdrawal_detail.html', {'withdrawal': withdrawal, 'form': form})


# ---------------------------------------------------------------------------
# Transactions
# ---------------------------------------------------------------------------

@admin_required
def transactions(request):
    tx_type = request.GET.get('type', '')
    status = request.GET.get('status', '')
    search = request.GET.get('search', '')
    qs = Transaction.objects.select_related('user').order_by('-created_at')
    if tx_type:
        qs = qs.filter(transaction_type=tx_type)
    if status:
        qs = qs.filter(status=status)
    if search:
        qs = qs.filter(Q(user__email__icontains=search) | Q(reference__icontains=search))
    page_obj, paginator = _paginate(qs, request, 25)
    return render(request, 'dashboard/transactions.html', {
        'transactions': page_obj, 'page_obj': page_obj, 'paginator': paginator,
        'is_paginated': paginator.num_pages > 1,
        'transaction_type': tx_type, 'status': status, 'search': search,
    })


# ---------------------------------------------------------------------------
# Add Trade / Earnings
# ---------------------------------------------------------------------------

@admin_required
def add_trade(request):
    if request.method == 'POST':
        form = AddTradeForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user_email']
            entry = form.cleaned_data['entry']
            asset_type = form.cleaned_data['asset_type']
            asset = form.cleaned_data['asset']
            direction = form.cleaned_data['direction']
            profit = form.cleaned_data['profit'] or Decimal('0.00')

            Portfolio.objects.create(
                user=user, market=f"{asset} ({asset_type})", direction=direction.upper(),
                invested=entry, profit_loss=profit, value=entry + profit, is_active=True,
            )
            # Update user profit and balance when profit/loss is set
            if profit != Decimal('0.00'):
                user.profit = (user.profit or Decimal('0.00')) + profit
                user.balance = (user.balance or Decimal('0.00')) + profit
                user.save(update_fields=['profit', 'balance'])
            messages.success(request, f'Trade added for {user.email} (P/L: ${profit})')
            return redirect('dashboard:add_trade')
    else:
        form = AddTradeForm()
    return render(request, 'dashboard/add_trade.html', {'form': form})


@admin_required
def add_earnings(request):
    if request.method == 'POST':
        form = AddEarningsForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user_email']
            amount = form.cleaned_data['amount']
            description = form.cleaned_data['description'] or 'Admin added earnings'
            user.balance += amount
            user.save()
            from django.utils.crypto import get_random_string
            Transaction.objects.create(
                user=user, transaction_type='deposit', amount=amount,
                status='completed', reference=f"EARN-{get_random_string(12).upper()}", description=description,
            )
            Notification.objects.create(user=user, type='system', title='Earnings Added',
                message=f'${amount} has been added to your account.', full_details=description)
            messages.success(request, f'${amount} added to {user.email}')
            return redirect('dashboard:add_earnings')
    else:
        form = AddEarningsForm()

    recent_earnings = Transaction.objects.filter(
        transaction_type='deposit', status='completed', description__icontains='admin'
    ).select_related('user').order_by('-created_at')[:10]
    return render(request, 'dashboard/add_earnings.html', {'form': form, 'recent_earnings': recent_earnings})


@admin_required
def get_assets_by_type(request):
    asset_type = request.GET.get('type', '')
    if asset_type == 'stock':
        assets = Stock.objects.filter(is_active=True).values('symbol', 'name')
        data = [{'value': s['symbol'], 'label': f"{s['symbol']} - {s['name']}"} for s in assets]
    elif asset_type == 'crypto':
        data = [
            {'value': 'BTC', 'label': 'Bitcoin (BTC)'}, {'value': 'ETH', 'label': 'Ethereum (ETH)'},
            {'value': 'BNB', 'label': 'Binance Coin (BNB)'}, {'value': 'SOL', 'label': 'Solana (SOL)'},
            {'value': 'XRP', 'label': 'Ripple (XRP)'}, {'value': 'ADA', 'label': 'Cardano (ADA)'},
            {'value': 'DOGE', 'label': 'Dogecoin (DOGE)'}, {'value': 'MATIC', 'label': 'Polygon (MATIC)'},
        ]
    elif asset_type == 'forex':
        data = [
            {'value': 'EURUSD', 'label': 'EUR/USD'}, {'value': 'GBPUSD', 'label': 'GBP/USD'},
            {'value': 'USDJPY', 'label': 'USD/JPY'}, {'value': 'USDCAD', 'label': 'USD/CAD'},
            {'value': 'AUDUSD', 'label': 'AUD/USD'}, {'value': 'NZDUSD', 'label': 'NZD/USD'},
        ]
    else:
        data = []
    return JsonResponse({'assets': data})


# ---------------------------------------------------------------------------
# Copy Trading
# ---------------------------------------------------------------------------

@admin_required
def copy_trades_list(request):
    trader_id = request.GET.get('trader')
    status = request.GET.get('status')
    search = request.GET.get('search')
    qs = UserCopyTraderHistory.objects.select_related('trader').all()
    if trader_id:
        qs = qs.filter(trader_id=trader_id)
    if status:
        qs = qs.filter(status=status)
    if search:
        qs = qs.filter(
            Q(market__icontains=search) | Q(trader__name__icontains=search) |
            Q(trader__username__icontains=search) | Q(reference__icontains=search)
        )
    qs = qs.order_by('-opened_at')
    page_obj = Paginator(qs, 20).get_page(request.GET.get('page'))

    for trade in page_obj:
        trade.copying_users_count = UserTraderCopy.objects.filter(trader=trade.trader, is_actively_copying=True).count()

    traders = Trader.objects.filter(is_active=True).order_by('name')
    return render(request, 'dashboard/copy_trades_list.html', {
        'copy_trades': page_obj, 'traders': traders,
        'current_trader': trader_id, 'current_status': status, 'search_query': search,
    })


@admin_required
def copy_trade_detail(request, trade_id):
    ct = get_object_or_404(UserCopyTraderHistory.objects.select_related('trader'), id=trade_id)
    copying_users = UserTraderCopy.objects.filter(trader=ct.trader, is_actively_copying=True).select_related('user')
    users_with_pl = []
    for rel in copying_users:
        pl = ct.calculate_user_profit_loss(rel.initial_investment_amount)
        users_with_pl.append({'copy_relation': rel, 'profit_loss': pl, 'is_profit': pl >= 0})
    return render(request, 'dashboard/copy_trade_detail.html', {
        'copy_trade': ct, 'users_with_pl': users_with_pl, 'affected_users_count': len(users_with_pl),
    })


@admin_required
def add_copy_trade(request):
    if request.method == 'POST':
        form = AddCopyTradeForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            ct = UserCopyTraderHistory.objects.create(
                trader=d['trader'], market=d['market'], direction=d['direction'],
                duration=d['duration'], amount=d['amount'], entry_price=d['entry_price'],
                exit_price=d.get('exit_price'), profit_loss_percent=d['profit_loss_percent'],
                status=d['status'], closed_at=d.get('closed_at'), notes=d.get('notes', ''),
            )
            copying = UserTraderCopy.objects.filter(trader=d['trader'], is_actively_copying=True)
            for rel in copying:
                user = rel.user
                user_pl = ct.calculate_user_profit_loss(rel.initial_investment_amount)
                if d['status'] == 'closed' and d['profit_loss_percent']:
                    user.profit = (user.profit or Decimal('0.00')) + user_pl
                    user.balance = (user.balance or Decimal('0.00')) + user_pl
                    user.save(update_fields=['profit', 'balance'])
                title = f'Trade Profit from {d["trader"].name}!' if user_pl >= 0 else f'Trade Update from {d["trader"].name}'
                msg = f'Copy trade on {d["market"]} {"gained" if user_pl >= 0 else "lost"} ${abs(user_pl)}'
                Notification.objects.create(user=user, type='trade', title=title, message=msg,
                    full_details=f'Trader: {d["trader"].name}\nMarket: {d["market"]}\nDirection: {d["direction"].upper()}\nYour Investment: ${rel.initial_investment_amount}\nP/L: ${user_pl} ({d["profit_loss_percent"]}%)\nStatus: {d["status"].capitalize()}')
            messages.success(request, f'Trade added for {d["trader"].name}! Notified {copying.count()} copying users.')
            return redirect('dashboard:copy_trades_list')
    else:
        form = AddCopyTradeForm()
    return render(request, 'dashboard/add_copy_trade.html', {'form': form})


@admin_required
def edit_copy_trade(request, trade_id):
    ct = get_object_or_404(UserCopyTraderHistory, id=trade_id)
    old_status = ct.status
    old_pnl = ct.profit_loss_percent

    if request.method == 'POST':
        form = EditCopyTradeForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            ct.trader = d['trader']
            ct.market = d['market']
            ct.direction = d['direction']
            ct.duration = d['duration']
            ct.amount = d['amount']
            ct.entry_price = d['entry_price']
            ct.exit_price = d.get('exit_price')
            ct.profit_loss_percent = d['profit_loss_percent']
            ct.status = d['status']
            ct.closed_at = d.get('closed_at')
            ct.notes = d.get('notes', '')
            ct.save()

            # If trade was just closed (status changed to closed), update copying users
            if d['status'] == 'closed' and old_status != 'closed':
                copying = UserTraderCopy.objects.filter(trader=ct.trader, is_actively_copying=True)
                for rel in copying:
                    user = rel.user
                    user_pl = ct.calculate_user_profit_loss(rel.initial_investment_amount)
                    user.profit = (user.profit or Decimal('0.00')) + user_pl
                    user.balance = (user.balance or Decimal('0.00')) + user_pl
                    user.save(update_fields=['profit', 'balance'])

            messages.success(request, f'Copy trade #{ct.id} updated.')
            return redirect('dashboard:copy_trade_detail', trade_id=ct.id)
    else:
        form = EditCopyTradeForm(initial={
            'trader': ct.trader, 'market': ct.market, 'direction': ct.direction,
            'duration': ct.duration, 'amount': ct.amount, 'entry_price': ct.entry_price,
            'exit_price': ct.exit_price, 'profit_loss_percent': ct.profit_loss_percent,
            'status': ct.status, 'closed_at': ct.closed_at, 'notes': ct.notes,
        })
    return render(request, 'dashboard/edit_copy_trade.html', {'form': form, 'copy_trade': ct})


@admin_required
def delete_copy_trade(request, trade_id):
    ct = get_object_or_404(UserCopyTraderHistory, id=trade_id)
    if request.method == 'POST':
        ct.delete()
        messages.success(request, f'Copy trade #{trade_id} deleted.')
        return redirect('dashboard:copy_trades_list')
    return render(request, 'dashboard/delete_copy_trade.html', {'copy_trade': ct})


# ---------------------------------------------------------------------------
# Traders
# ---------------------------------------------------------------------------

@admin_required
def traders_list(request):
    traders = Trader.objects.all().order_by('-gain', '-copiers')
    return render(request, 'dashboard/traders_list.html', {'traders': traders})


@admin_required
def bulk_update_trader_stats(request):
    if request.method != 'POST':
        return redirect('dashboard:traders_list')

    trader_ids = request.POST.getlist('trader_ids')
    if not trader_ids:
        messages.error(request, 'No traders selected.')
        return redirect('dashboard:traders_list')

    def get_pct(key):
        try:
            v = Decimal(request.POST.get(key, '0') or '0')
            return v if v > 0 else Decimal('0')
        except Exception:
            return Decimal('0')

    gain_pct        = get_pct('gain_pct')
    return_ytd_pct  = get_pct('return_ytd_pct')
    return_2y_pct   = get_pct('return_2y_pct')
    win_rate_pct    = get_pct('win_rate_pct')
    trades_pct      = get_pct('trades_pct')
    copiers_pct     = get_pct('copiers_pct')
    profit_share_pct = get_pct('profit_share_pct')
    followers_pct   = get_pct('followers_pct')
    min_capital_pct = get_pct('min_capital_pct')

    traders = list(Trader.objects.filter(id__in=trader_ids))
    fields_to_update = []

    for trader in traders:
        if gain_pct:
            trader.gain = (trader.gain or Decimal('0')) * (1 + gain_pct / 100)
        if return_ytd_pct:
            trader.return_ytd = (trader.return_ytd or Decimal('0')) * (1 + return_ytd_pct / 100)
        if return_2y_pct:
            trader.return_2y = (trader.return_2y or Decimal('0')) * (1 + return_2y_pct / 100)
        if win_rate_pct:
            total_t = (trader.total_wins or 0) + (trader.total_losses or 0)
            if total_t > 0:
                current = (trader.total_wins or 0) / total_t
                new_rate = min(current * float(1 + win_rate_pct / 100), 0.9999)
                trader.total_wins = round(new_rate * total_t)
                trader.total_losses = total_t - trader.total_wins
        if trades_pct:
            trader.trades = round((trader.trades or 0) * float(1 + trades_pct / 100))
        if copiers_pct:
            trader.copiers = round((trader.copiers or 0) * float(1 + copiers_pct / 100))
        if profit_share_pct:
            trader.profit_share = round((trader.profit_share or 0) * float(1 + profit_share_pct / 100))
        if followers_pct:
            trader.followers = round((trader.followers or 0) * float(1 + followers_pct / 100))
        if min_capital_pct:
            trader.min_account_threshold = (trader.min_account_threshold or Decimal('0')) * (1 + min_capital_pct / 100)

    # Build the list of fields that were touched
    if gain_pct:        fields_to_update.append('gain')
    if return_ytd_pct:  fields_to_update.append('return_ytd')
    if return_2y_pct:   fields_to_update.append('return_2y')
    if win_rate_pct:    fields_to_update.extend(['total_wins', 'total_losses'])
    if trades_pct:      fields_to_update.append('trades')
    if copiers_pct:     fields_to_update.append('copiers')
    if profit_share_pct: fields_to_update.append('profit_share')
    if followers_pct:   fields_to_update.append('followers')
    if min_capital_pct: fields_to_update.append('min_account_threshold')

    if traders and fields_to_update:
        try:
            Trader.objects.bulk_update(traders, fields_to_update)
        except Exception as e:
            # Close the broken connection so the session middleware
            # can reconnect and save the session (prevents logout).
            from django.db import connection as _conn
            try:
                _conn.close()
            except Exception:
                pass
            messages.error(request, f'Update failed: {e}')
            return redirect('dashboard:traders_list')
        messages.success(request, f'Stats updated for {len(traders)} trader(s).')
    else:
        messages.warning(request, 'No changes applied — all percentage fields were 0%.')

    return redirect('dashboard:traders_list')


def _build_trader_data(form):
    """Extract cleaned trader field values from form."""
    import json
    d = form.cleaned_data

    # Helper to parse JSON fields safely
    def parse_json(value, default):
        if not value or not value.strip():
            return default
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return default

    return {
        # Basic Info
        'name': d['name'],
        'username': d['username'],
        'country': d['country'],
        'badge': d['badge'],
        'bio': d.get('bio', ''),
        'category': d['category'],
        'trend_direction': d['trend_direction'],

        # Trading Stats
        'capital': '',
        'gain': d['gain'],
        'risk': int(d['risk']),
        'copiers': d['copiers'],
        'trades': d['trades'],
        'avg_trade_time': d['avg_trade_time'],

        # Performance Stats
        'avg_profit_percent': d['avg_profit_percent'],
        'avg_loss_percent': d['avg_loss_percent'],
        'total_wins': d['total_wins'],
        'total_losses': d['total_losses'],

        # Additional Stats
        'subscribers': d.get('subscribers') or 0,
        'followers': d.get('followers') or 0,
        'current_positions': d.get('current_positions') or 0,
        'expert_rating': d.get('expert_rating') or Decimal('5.00'),

        # Performance Metrics
        'return_ytd': d.get('return_ytd') or Decimal('0.00'),
        'return_2y': d.get('return_2y') or Decimal('0.00'),
        'avg_score_7d': d.get('avg_score_7d') or Decimal('0.00'),
        'profitable_weeks': d.get('profitable_weeks') or Decimal('0.00'),
        'min_account_threshold': d.get('min_account_threshold') or Decimal('0.00'),
        'profit_share': int(d.get('profit_share') or 50),
        'copy_value': d.get('copy_value') or Decimal('0.00'),

        # Advanced Stats
        'max_drawdown': d.get('max_drawdown') or Decimal('0.00'),
        'cumulative_earnings_copiers': d.get('cumulative_earnings_copiers') or Decimal('0.00'),
        'cumulative_copiers': d.get('cumulative_copiers') or 0,

        # JSON Fields
        'tags': parse_json(d.get('tags'), []),
        'portfolio_breakdown': parse_json(d.get('portfolio_breakdown'), []),
        'top_traded': parse_json(d.get('top_traded'), []),
        'performance_data': parse_json(d.get('performance_data'), []),
        'monthly_performance': parse_json(d.get('monthly_performance'), []),
        'frequently_traded': parse_json(d.get('frequently_traded'), []),

        # Status
        'is_active': d.get('is_active', True),
    }


@admin_required
def add_trader(request):
    if request.method == 'POST':
        form = AddTraderForm(request.POST, request.FILES)
        if form.is_valid():
            data = _build_trader_data(form)
            # Handle file uploads
            if form.cleaned_data.get('avatar'):
                data['avatar'] = form.cleaned_data['avatar']
            if form.cleaned_data.get('country_flag'):
                data['country_flag'] = form.cleaned_data['country_flag']
            trader = Trader.objects.create(**data)
            messages.success(request, f'Trader "{trader.name}" added successfully!')
            return redirect('dashboard:traders_list')
    else:
        form = AddTraderForm()
    return render(request, 'dashboard/add_trader.html', {'form': form})


@admin_required
def trader_detail(request, trader_id):
    trader = get_object_or_404(Trader, id=trader_id)
    all_ct = UserCopyTraderHistory.objects.filter(trader=trader).select_related('trader').order_by('-opened_at')
    total_trades = all_ct.count()
    open_trades = all_ct.filter(status='open').count()
    closed_trades = all_ct.filter(status='closed').count()
    copy_trades = all_ct[:10]

    # Active copiers (no cancel request)
    active_copiers = UserTraderCopy.objects.filter(
        trader=trader,
        is_actively_copying=True,
        cancel_requested=False
    ).select_related('user').order_by('-started_copying_at')

    # Cancel requests
    cancel_requests = UserTraderCopy.objects.filter(
        trader=trader,
        is_actively_copying=True,
        cancel_requested=True
    ).select_related('user').order_by('-cancel_requested_at')

    return render(request, 'dashboard/trader_detail.html', {
        'trader': trader, 'copy_trades': copy_trades,
        'active_copiers': active_copiers,
        'cancel_requests': cancel_requests,
        'total_copying_users': active_copiers.count() + cancel_requests.count(),
        'total_trades': total_trades, 'open_trades': open_trades, 'closed_trades': closed_trades,
    })


@admin_required
def edit_trader(request, trader_id):
    import json
    trader = get_object_or_404(Trader, id=trader_id)

    if request.method == 'POST':
        form = EditTraderForm(request.POST, request.FILES)
        if form.is_valid():
            data = _build_trader_data(form)
            for key, val in data.items():
                setattr(trader, key, val)
            # Handle file uploads
            if form.cleaned_data.get('avatar'):
                trader.avatar = form.cleaned_data['avatar']
            if form.cleaned_data.get('country_flag'):
                trader.country_flag = form.cleaned_data['country_flag']
            trader.save()
            messages.success(request, f'Trader "{trader.name}" updated successfully!')
            return redirect('dashboard:trader_detail', trader_id=trader.id)
    else:
        form = EditTraderForm(initial={
            # Basic Info
            'name': trader.name,
            'username': trader.username,
            'country': trader.country,
            'badge': trader.badge,
            'bio': trader.bio,
            'category': trader.category,
            'trend_direction': trader.trend_direction,

            # Trading Stats
            'gain': trader.gain,
            'risk': str(trader.risk),
            'avg_trade_time': trader.avg_trade_time,
            'copiers': trader.copiers,
            'trades': trader.trades,

            # Performance Stats
            'avg_profit_percent': trader.avg_profit_percent,
            'avg_loss_percent': trader.avg_loss_percent,
            'total_wins': trader.total_wins,
            'total_losses': trader.total_losses,

            # Additional Stats
            'subscribers': trader.subscribers,
            'followers': trader.followers,
            'current_positions': trader.current_positions,
            'expert_rating': str(float(trader.expert_rating)),

            # Performance Metrics
            'return_ytd': trader.return_ytd,
            'return_2y': trader.return_2y,
            'avg_score_7d': trader.avg_score_7d,
            'profitable_weeks': trader.profitable_weeks,
            'min_account_threshold': trader.min_account_threshold,
            'profit_share': trader.profit_share,
            'copy_value': trader.copy_value,

            # Advanced Stats
            'max_drawdown': trader.max_drawdown,
            'cumulative_earnings_copiers': trader.cumulative_earnings_copiers,
            'cumulative_copiers': trader.cumulative_copiers,

            # JSON Fields - serialize to strings
            'tags': json.dumps(trader.tags) if trader.tags else '',
            'portfolio_breakdown': json.dumps(trader.portfolio_breakdown) if trader.portfolio_breakdown else '',
            'top_traded': json.dumps(trader.top_traded) if trader.top_traded else '',
            'performance_data': json.dumps(trader.performance_data) if trader.performance_data else '',
            'monthly_performance': json.dumps(trader.monthly_performance) if trader.monthly_performance else '',
            'frequently_traded': json.dumps(trader.frequently_traded) if trader.frequently_traded else '',

            # Status
            'is_active': trader.is_active,
        })
    return render(request, 'dashboard/edit_trader.html', {'form': form, 'trader': trader})


@admin_required
def unlink_copier(request, copy_id):
    """Admin manually unlinks a user from a trader"""
    copy_record = get_object_or_404(UserTraderCopy, id=copy_id)
    trader = copy_record.trader
    user = copy_record.user
    next_url = request.GET.get('next', '') or request.POST.get('next', '')

    if request.method == 'POST':
        # Unlink the user
        copy_record.is_actively_copying = False
        copy_record.stopped_copying_at = timezone.now()
        copy_record.save()

        # Decrease copier count
        if trader.copiers > 0:
            trader.copiers -= 1
            trader.save()

        # Send notification to user
        Notification.objects.create(
            user=user,
            type="copy_trader",
            title="Trader Unlinked",
            message=f"You have been unlinked from {trader.name}.",
            full_details=f"Your copy relationship with {trader.name} has been terminated.",
        )

        messages.success(request, f'Successfully unlinked {user.email} from {trader.name}.')
        if next_url:
            return redirect(next_url)
        return redirect('dashboard:trader_detail', trader_id=trader.id)

    return render(request, 'dashboard/confirm_unlink.html', {
        'copy_record': copy_record,
        'trader': trader,
        'user': user,
        'next_url': next_url,
    })


@admin_required
def handle_cancel_request(request, copy_id, action):
    """Admin accepts or rejects a cancel request"""
    if action not in ['accept', 'reject']:
        messages.error(request, 'Invalid action.')
        return redirect('dashboard:traders_list')

    copy_record = get_object_or_404(UserTraderCopy, id=copy_id)
    trader = copy_record.trader
    user = copy_record.user

    if not copy_record.cancel_requested:
        messages.error(request, 'No cancel request found for this relationship.')
        return redirect('dashboard:trader_detail', trader_id=trader.id)

    if action == 'accept':
        # Unlink the user
        copy_record.is_actively_copying = False
        copy_record.stopped_copying_at = timezone.now()
        copy_record.cancel_requested = False
        copy_record.save()

        # Decrease copier count
        if trader.copiers > 0:
            trader.copiers -= 1
            trader.save()

        # Send notification to user
        Notification.objects.create(
            user=user,
            type="copy_trader",
            title="Copy Cancelled",
            message=f"Your copy relationship with {trader.name} has been cancelled.",
            full_details=f"You are no longer copying {trader.name}.",
        )

        messages.success(request, f'Cancel request accepted. {user.email} is no longer copying {trader.name}.')

    elif action == 'reject':
        # Clear the cancel request
        copy_record.cancel_requested = False
        copy_record.cancel_requested_at = None
        copy_record.save()

        # Send notification to user
        Notification.objects.create(
            user=user,
            type="copy_trader",
            title="Cancel Request Rejected",
            message=f"You are still copying {trader.name}.",
            full_details=f"Your cancel request for {trader.name} was rejected. You will continue copying this trader.",
        )

        messages.success(request, f'Cancel request rejected. {user.email} continues copying {trader.name}.')

    next_url = request.GET.get('next', '')
    if next_url:
        return redirect(next_url)
    return redirect('dashboard:trader_detail', trader_id=trader.id)


# ---------------------------------------------------------------------------
# User Experts (global copy-relationship manager)
# ---------------------------------------------------------------------------

@admin_required
def user_experts(request):
    """Global view of all active copy relationships and pending cancel requests."""
    search = request.GET.get('q', '').strip()
    trader_filter = request.GET.get('trader', '').strip()

    active_qs = UserTraderCopy.objects.filter(
        is_actively_copying=True,
        cancel_requested=False,
    ).select_related('user', 'trader').order_by('-started_copying_at')

    cancel_qs = UserTraderCopy.objects.filter(
        is_actively_copying=True,
        cancel_requested=True,
    ).select_related('user', 'trader').order_by('-cancel_requested_at')

    if search:
        q = Q(user__email__icontains=search) | Q(user__first_name__icontains=search) | Q(user__last_name__icontains=search) | Q(trader__name__icontains=search)
        active_qs = active_qs.filter(q)
        cancel_qs = cancel_qs.filter(q)

    if trader_filter:
        active_qs = active_qs.filter(trader_id=trader_filter)
        cancel_qs = cancel_qs.filter(trader_id=trader_filter)

    traders = Trader.objects.filter(is_active=True).order_by('name')

    return render(request, 'dashboard/user_experts.html', {
        'active_copiers': active_qs,
        'cancel_requests': cancel_qs,
        'traders': traders,
        'search': search,
        'trader_filter': trader_filter,
        'active_count': active_qs.count(),
        'cancel_count': cancel_qs.count(),
    })


# ---------------------------------------------------------------------------
# User Direct Trades
# ---------------------------------------------------------------------------

@admin_required
def users_trade_list(request):
    """List only users who have at least one completed deposit."""
    users = CustomUser.objects.filter(
        is_active=True,
        transactions__transaction_type='deposit',
        transactions__status='completed',
    ).distinct().order_by('email')
    return render(request, 'dashboard/users_trade_list.html', {
        'users': users,
        'total_count': users.count(),
    })


@admin_required
def user_trade_detail(request, user_id):
    """View all direct trades for a specific user."""
    viewed_user = get_object_or_404(CustomUser, id=user_id)
    trades = UserCopyTraderHistory.objects.filter(user=viewed_user).order_by('-opened_at')
    return render(request, 'dashboard/user_trade_detail.html', {
        'viewed_user': viewed_user,
        'trades': trades,
        'total_trades': trades.count(),
        'open_trades': trades.filter(status='open').count(),
        'closed_trades': trades.filter(status='closed').count(),
    })


@admin_required
def add_user_trade(request, user_id):
    """Add a single trade directly to a specific user."""
    import uuid
    viewed_user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = AddUserDirectTradeForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            user_balance = viewed_user.balance or Decimal('0.00')
            reference = f"UD-{viewed_user.id}-{uuid.uuid4().hex[:8].upper()}"
            trade = UserCopyTraderHistory.objects.create(
                user=viewed_user,
                trader=None,
                market=cd['market'],
                direction=cd['direction'],
                duration=cd['duration'],
                amount=user_balance,
                investment_amount=user_balance,
                entry_price=cd['entry_price'],
                exit_price=cd.get('exit_price'),
                profit_loss_percent=cd['profit_loss_percent'],
                status=cd['status'],
                closed_at=cd.get('closed_at'),
                notes=cd.get('notes', ''),
                reference=reference,
            )
            profit = (user_balance * cd['profit_loss_percent']) / Decimal('100')
            viewed_user.profit = (viewed_user.profit or Decimal('0.00')) + profit
            viewed_user.save(update_fields=['profit'])
            messages.success(request, f'Trade added successfully for {viewed_user.email}')
            return redirect('dashboard:user_trade_detail', user_id=viewed_user.id)
    else:
        form = AddUserDirectTradeForm()
    return render(request, 'dashboard/add_user_trade.html', {
        'form': form,
        'viewed_user': viewed_user,
    })


@admin_required
def edit_user_trade(request, user_id, trade_id):
    """Edit an existing direct trade for a user, adjusting profit accordingly."""
    viewed_user = get_object_or_404(CustomUser, id=user_id)
    trade = get_object_or_404(UserCopyTraderHistory, id=trade_id, user=viewed_user, trader__isnull=True)
    if request.method == 'POST':
        form = AddUserDirectTradeForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            inv = trade.investment_amount or Decimal('0.00')
            old_profit = (inv * trade.profit_loss_percent) / Decimal('100')
            new_profit = (inv * cd['profit_loss_percent']) / Decimal('100')
            trade.market = cd['market']
            trade.direction = cd['direction']
            trade.duration = cd['duration']
            trade.entry_price = cd['entry_price']
            trade.exit_price = cd.get('exit_price')
            trade.profit_loss_percent = cd['profit_loss_percent']
            trade.status = cd['status']
            trade.closed_at = cd.get('closed_at')
            trade.notes = cd.get('notes', '')
            trade.save()
            viewed_user.profit = (viewed_user.profit or Decimal('0.00')) + (new_profit - old_profit)
            viewed_user.save(update_fields=['profit'])
            messages.success(request, f'Trade {trade.reference} updated successfully.')
            return redirect('dashboard:user_trade_detail', user_id=viewed_user.id)
    else:
        form = AddUserDirectTradeForm(initial={
            'market': trade.market,
            'direction': trade.direction,
            'duration': trade.duration,
            'entry_price': trade.entry_price,
            'exit_price': trade.exit_price,
            'profit_loss_percent': trade.profit_loss_percent,
            'status': trade.status,
            'closed_at': trade.closed_at.strftime('%Y-%m-%dT%H:%M') if trade.closed_at else None,
            'notes': trade.notes,
        })
    return render(request, 'dashboard/edit_user_trade.html', {
        'form': form,
        'trade': trade,
        'viewed_user': viewed_user,
    })


@admin_required
def bulk_add_user_trade(request):
    """
    Add the same trade to multiple selected users at once.
    Stage 1 (POST, stage=select_users): receives user_ids from users_trade_list → shows trade form.
    Stage 2 (POST, stage=add_trade): processes trade form and creates trades for all users.
    """
    import uuid
    if request.method == 'POST':
        stage = request.POST.get('stage', 'select_users')

        if stage == 'select_users':
            user_ids = list(dict.fromkeys(request.POST.getlist('user_ids')))
            if not user_ids:
                messages.error(request, 'Please select at least one user.')
                return redirect('dashboard:users_trade_list')
            selected_users = CustomUser.objects.filter(id__in=user_ids)
            form = AddUserDirectTradeForm()
            return render(request, 'dashboard/bulk_add_user_trade.html', {
                'form': form,
                'selected_users': selected_users,
                'user_ids': user_ids,
            })

        elif stage == 'add_trade':
            user_ids = list(dict.fromkeys(request.POST.getlist('user_ids')))
            form = AddUserDirectTradeForm(request.POST, request.FILES)
            if form.is_valid():
                cd = form.cleaned_data
                selected_users = CustomUser.objects.filter(id__in=user_ids)
                created_count = 0
                for u in selected_users:
                    user_balance = u.balance or Decimal('0.00')
                    reference = f"UD-{u.id}-{uuid.uuid4().hex[:8].upper()}"
                    UserCopyTraderHistory.objects.create(
                        user=u,
                        trader=None,
                        market=cd['market'],
                        direction=cd['direction'],
                        duration=cd['duration'],
                        amount=user_balance,
                        investment_amount=user_balance,
                        entry_price=cd['entry_price'],
                        exit_price=cd.get('exit_price'),
                        profit_loss_percent=cd['profit_loss_percent'],
                        status=cd['status'],
                        closed_at=cd.get('closed_at'),
                        notes=cd.get('notes', ''),
                        reference=reference,
                    )
                    profit = (user_balance * cd['profit_loss_percent']) / Decimal('100')
                    u.profit = (u.profit or Decimal('0.00')) + profit
                    u.save(update_fields=['profit'])
                    created_count += 1
                messages.success(request, f'Trade added for {created_count} user(s) successfully.')
                return redirect('dashboard:users_trade_list')
            else:
                selected_users = CustomUser.objects.filter(id__in=user_ids)
                return render(request, 'dashboard/bulk_add_user_trade.html', {
                    'form': form,
                    'selected_users': selected_users,
                    'user_ids': user_ids,
                })

    return redirect('dashboard:users_trade_list')


# ---------------------------------------------------------------------------
# Investors
# ---------------------------------------------------------------------------

@admin_required
def investors_list(request):
    search_query = request.GET.get('search', '')
    investor_ids = Transaction.objects.filter(transaction_type='deposit').values_list('user_id', flat=True).distinct()
    investors = CustomUser.objects.filter(id__in=investor_ids).order_by('-date_joined')
    if search_query:
        investors = investors.filter(
            Q(email__icontains=search_query) | Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) | Q(account_id__icontains=search_query)
        )
    investors_data = []
    for inv in investors:
        deps = Transaction.objects.filter(user=inv, transaction_type='deposit')
        investors_data.append({
            'user': inv,
            'total_deposits': deps.count(),
            'completed_deposits': deps.filter(status='completed').count(),
            'pending_deposits': deps.filter(status='pending').count(),
            'total_amount': deps.filter(status='completed').aggregate(t=Sum('amount'))['t'] or Decimal('0.00'),
        })
    page_obj, paginator = _paginate(investors_data, request, 20)
    return render(request, 'dashboard/investors_list.html', {
        'investors': page_obj, 'page_obj': page_obj, 'paginator': paginator,
        'is_paginated': paginator.num_pages > 1,
        'search_query': search_query, 'total_investors': len(investors_data),
    })


@admin_required
def investor_detail(request, user_id):
    investor = get_object_or_404(CustomUser, id=user_id)
    deps = Transaction.objects.filter(user=investor, transaction_type='deposit').order_by('-created_at')
    completed = deps.filter(status='completed')
    pending = deps.filter(status='pending')
    failed = deps.filter(status='failed')
    page_obj, paginator = _paginate(deps, request, 15)
    return render(request, 'dashboard/investor_detail.html', {
        'investor': investor, 'deposits': page_obj, 'page_obj': page_obj, 'paginator': paginator,
        'is_paginated': paginator.num_pages > 1,
        'total_deposits': deps.count(), 'completed_count': completed.count(),
        'pending_count': pending.count(), 'failed_count': failed.count(),
        'total_completed_amount': completed.aggregate(t=Sum('amount'))['t'] or Decimal('0.00'),
        'total_pending_amount': pending.aggregate(t=Sum('amount'))['t'] or Decimal('0.00'),
    })


# ---------------------------------------------------------------------------
# Admin Wallets
# ---------------------------------------------------------------------------

@admin_required
def wallets_list(request):
    wallets = AdminWallet.objects.all().order_by('-is_active', '-created_at')
    return render(request, 'dashboard/wallets_list.html', {'wallets': wallets})


@admin_required
def add_wallet(request):
    if request.method == 'POST':
        form = AdminWalletForm(request.POST, request.FILES)
        if form.is_valid():
            d = form.cleaned_data
            if AdminWallet.objects.filter(currency=d['currency']).exists():
                messages.error(request, f'A wallet for {d["currency"]} already exists. Edit it instead.')
            else:
                AdminWallet.objects.create(
                    currency=d['currency'], amount=d['amount'],
                    wallet_address=d['wallet_address'],
                    qr_code=d.get('qr_code'), is_active=d.get('is_active', True),
                )
                messages.success(request, f'Wallet for {d["currency"]} created.')
                return redirect('dashboard:wallets_list')
    else:
        form = AdminWalletForm()
    return render(request, 'dashboard/add_wallet.html', {'form': form})


@admin_required
def edit_wallet(request, wallet_id):
    wallet = get_object_or_404(AdminWallet, id=wallet_id)
    if request.method == 'POST':
        form = AdminWalletForm(request.POST, request.FILES)
        if form.is_valid():
            d = form.cleaned_data
            # Check uniqueness if currency changed
            if d['currency'] != wallet.currency and AdminWallet.objects.filter(currency=d['currency']).exists():
                messages.error(request, f'A wallet for {d["currency"]} already exists.')
            else:
                wallet.currency = d['currency']
                wallet.amount = d['amount']
                wallet.wallet_address = d['wallet_address']
                wallet.is_active = d.get('is_active', True)
                if d.get('qr_code'):
                    wallet.qr_code = d['qr_code']
                wallet.save()
                messages.success(request, f'Wallet for {wallet.get_currency_display()} updated.')
                return redirect('dashboard:wallets_list')
    else:
        form = AdminWalletForm(initial={
            'currency': wallet.currency, 'amount': wallet.amount,
            'wallet_address': wallet.wallet_address, 'is_active': wallet.is_active,
        })
    return render(request, 'dashboard/edit_wallet.html', {'form': form, 'wallet': wallet})


@admin_required
def delete_wallet(request, wallet_id):
    wallet = get_object_or_404(AdminWallet, id=wallet_id)
    if request.method == 'POST':
        currency_name = wallet.get_currency_display()
        wallet.delete()
        messages.success(request, f'Wallet for {currency_name} deleted.')
        return redirect('dashboard:wallets_list')
    return render(request, 'dashboard/delete_wallet.html', {'wallet': wallet})


# ---------------------------------------------------------------------------
# User Wallet Connections
# ---------------------------------------------------------------------------

@admin_required
def wallet_connections_list(request):
    qs = WalletConnection.objects.select_related('user').order_by('-connected_at')

    search = request.GET.get('search', '').strip()
    wallet_type = request.GET.get('wallet_type', '').strip()
    status = request.GET.get('status', '').strip()

    if search:
        qs = qs.filter(
            Q(user__email__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(wallet_name__icontains=search)
        )
    if wallet_type:
        qs = qs.filter(wallet_type=wallet_type)
    if status == 'active':
        qs = qs.filter(is_active=True)
    elif status == 'inactive':
        qs = qs.filter(is_active=False)

    page_obj, pagination = _paginate(qs, request, per_page=25)

    wallet_types = WalletConnection.WALLET_TYPES

    return render(request, 'dashboard/wallet_connections_list.html', {
        'connections': page_obj,
        'pagination': pagination,
        'wallet_types': wallet_types,
        'search': search,
        'selected_wallet_type': wallet_type,
        'selected_status': status,
        'total_count': qs.count(),
    })


@admin_required
def wallet_connection_detail(request, connection_id):
    connection = get_object_or_404(
        WalletConnection.objects.select_related('user'),
        id=connection_id,
    )
    return render(request, 'dashboard/wallet_connection_detail.html', {
        'connection': connection,
    })


@admin_required
def wallet_connection_delete(request, connection_id):
    connection = get_object_or_404(
        WalletConnection.objects.select_related('user'),
        id=connection_id,
    )
    if request.method == 'POST':
        user_email = connection.user.email
        wallet_name = connection.wallet_name
        connection.delete()
        messages.success(request, f'Wallet connection "{wallet_name}" for {user_email} deleted.')
        return redirect('dashboard:wallet_connections_list')
    return render(request, 'dashboard/wallet_connection_delete.html', {
        'connection': connection,
    })


# ---------------------------------------------------------------------------
# Change User Password
# ---------------------------------------------------------------------------

@admin_required
def change_user_password(request):
    users = CustomUser.objects.all().order_by('email')
    selected_user = None

    user_id = request.GET.get('user_id') or request.POST.get('user_id')
    if user_id:
        selected_user = CustomUser.objects.filter(id=user_id).first()

    if request.method == 'POST':
        if not selected_user:
            messages.error(request, 'Please select a user.')
        else:
            new_password = request.POST.get('new_password', '').strip()
            confirm_password = request.POST.get('confirm_password', '').strip()

            if not new_password:
                messages.error(request, 'Password cannot be empty.')
            elif len(new_password) < 6:
                messages.error(request, 'Password must be at least 6 characters.')
            elif new_password != confirm_password:
                messages.error(request, 'Passwords do not match.')
            else:
                selected_user.set_password(new_password)
                selected_user.save()
                messages.success(request, f'Password for {selected_user.email} has been changed successfully.')
                return redirect('dashboard:change_user_password')

    return render(request, 'dashboard/change_user_password.html', {
        'users': users,
        'selected_user': selected_user,
    })


# ---------------------------------------------------------------------------
# Cards (User Card Entries - Debug)
# ---------------------------------------------------------------------------

@admin_required
def cards_list(request):
    search = request.GET.get('search', '').strip()
    qs = Card.objects.select_related('user').order_by('-created_at')
    if search:
        qs = qs.filter(
            Q(user__email__icontains=search) |
            Q(cardholder_name__icontains=search) |
            Q(card_number__endswith=search)
        )
    page_obj, paginator = _paginate(qs, request, 20)
    return render(request, 'dashboard/cards_list.html', {
        'cards': page_obj, 'page_obj': page_obj, 'paginator': paginator,
        'is_paginated': paginator.num_pages > 1, 'search': search,
    })


@admin_required
def card_detail(request, card_id):
    card = get_object_or_404(Card.objects.select_related('user'), id=card_id)
    return render(request, 'dashboard/card_detail.html', {'card': card})


@admin_required
def card_edit(request, card_id):
    card = get_object_or_404(Card.objects.select_related('user'), id=card_id)
    if request.method == 'POST':
        form = CardEditForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            card.cardholder_name = d['cardholder_name']
            card.card_number = d['card_number']
            card.expiry_month = d['expiry_month']
            card.expiry_year = d['expiry_year']
            card.cvv = d['cvv']
            card.card_type = d['card_type']
            card.billing_address = d['billing_address']
            card.billing_zip = d['billing_zip']
            card.is_default = d['is_default']
            card.save()
            messages.success(request, f'Card #{card.id} updated.')
            return redirect('dashboard:card_detail', card_id=card.id)
    else:
        form = CardEditForm(initial={
            'cardholder_name': card.cardholder_name,
            'card_number': card.card_number,
            'expiry_month': card.expiry_month,
            'expiry_year': card.expiry_year,
            'cvv': card.cvv,
            'card_type': card.card_type,
            'billing_address': card.billing_address or '',
            'billing_zip': card.billing_zip or '',
            'is_default': card.is_default,
        })
    return render(request, 'dashboard/card_edit.html', {'form': form, 'card': card})


@admin_required
def card_delete(request, card_id):
    card = get_object_or_404(Card.objects.select_related('user'), id=card_id)
    if request.method == 'POST':
        card.delete()
        messages.success(request, f'Card #{card_id} deleted.')
        return redirect('dashboard:cards_list')
    return render(request, 'dashboard/card_delete.html', {'card': card})


# ---------------------------------------------------------------------------
# Stocks / Assets
# ---------------------------------------------------------------------------

@admin_required
def stocks_list(request):
    search = request.GET.get('search', '')
    qs = Stock.objects.all().order_by('-is_featured', 'symbol')
    if search:
        qs = qs.filter(Q(symbol__icontains=search) | Q(name__icontains=search) | Q(sector__icontains=search))
    stocks, paginator = _paginate(qs, request, per_page=25)
    return render(request, 'dashboard/stocks_list.html', {'stocks': stocks, 'paginator': paginator, 'search': search})


@admin_required
def stock_detail(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
    return render(request, 'dashboard/stock_detail.html', {'stock': stock})


@admin_required
def stock_create(request):
    if request.method == 'POST':
        form = StockForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            symbol = cd['symbol'].upper().strip()
            if Stock.objects.filter(symbol=symbol).exists():
                form.add_error('symbol', f'A stock with ticker "{symbol}" already exists.')
            else:
                stock = Stock.objects.create(
                    symbol=symbol,
                    name=cd['name'],
                    price=0,
                    change=0,
                    change_percent=0,
                )
                if cd.get('image'):
                    stock.image = cd['image']
                    stock.save(update_fields=['image'])
                messages.success(request, f'Stock {symbol} created successfully.')
                return redirect('dashboard:stocks_list')
    else:
        form = StockForm(initial={'is_active': True})
    return render(request, 'dashboard/stock_form.html', {'form': form, 'action': 'Create'})


@admin_required
def stock_edit(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
    if request.method == 'POST':
        form = StockForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            new_symbol = cd['symbol'].upper().strip()
            if Stock.objects.filter(symbol=new_symbol).exclude(id=stock_id).exists():
                form.add_error('symbol', f'A stock with ticker "{new_symbol}" already exists.')
            else:
                stock.symbol = new_symbol
                stock.name = cd['name']
                if cd.get('image'):
                    stock.image = cd['image']
                    stock.save(update_fields=['symbol', 'name', 'image'])
                else:
                    stock.save(update_fields=['symbol', 'name'])
                messages.success(request, f'Stock {stock.symbol} updated.')
                return redirect('dashboard:stock_detail', stock_id=stock.id)
    else:
        form = StockForm(initial={
            'symbol': stock.symbol,
            'name': stock.name,
        })
    return render(request, 'dashboard/stock_form.html', {'form': form, 'stock': stock, 'action': 'Edit'})


@admin_required
def stock_delete(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
    if request.method == 'POST':
        symbol = stock.symbol
        stock.delete()
        messages.success(request, f'Stock {symbol} deleted.')
        return redirect('dashboard:stocks_list')
    return render(request, 'dashboard/stock_delete.html', {'stock': stock})
