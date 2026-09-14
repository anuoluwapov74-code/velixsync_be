from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render, redirect

admin.site.site_header = "VelixSync Administration"
admin.site.site_title = "VelixSync Admin Portal"
admin.site.index_title = "Welcome to VelixSync Admin Portal"


from app.auth_views import (
    register_user_with_verification,
    verify_email,
    resend_verification_code,
    login_with_2fa,
    verify_2fa_login,
    resend_2fa_code,
    enable_2fa,
    disable_2fa,
    get_2fa_status,
    logout_view,
    check_auth,
    get_profile,
    submit_kyc,
    request_password_reset,
    reset_password,
    validate_reset_token,
    CustomTokenRefreshView,
)

from app.views import (
    get_deposit_options,
    create_deposit,
    deposit_payment_intent,
    get_deposit_history,
    get_withdrawal_profile,
    get_withdrawal_methods,
    create_withdrawal,
    get_withdrawal_history,
    get_transaction_history,
    sync_trigger,
)

from app.copy_trading_views import (
    list_traders,
    trader_detail,
    copy_trader_action,
    copy_trader_status,
    user_copied_trades,
    user_following_traders,
    user_trade_history,
    calendar_data,
    calendar_seasonality,
    admin_trader_copiers,
    admin_unlink_copier,
    admin_handle_cancel_request,
)

from app.referral_views import (
    referral_info,
    referral_list,
    generate_referral_code,
    validate_referral_code,
)

from app.notification_views import (
    list_notifications,
    mark_notification_read,
    mark_all_notifications_read,
    get_recent_notifications,
)
from app.signal_views import (
    list_signals,
    purchase_signal,
    user_purchased_signals,
    signal_detail,
)
from app.news_views import (
    list_news,
    news_detail,
)
from app.wallet_views import (
    list_wallets,
    connect_wallet,
    disconnect_wallet,
    wallet_detail,
)
from app.stock_views import (
    list_stocks,
    stock_detail,
    buy_stock,
    sell_stock,
    user_positions,
    list_treemap,
)
from app.settings_views import (
    get_user_settings,
    update_profile,
    change_password,
    update_payment_method,
)
from app.transfer_views import (
    transfer_info,
    make_transfer,
)
from app.card_views import (
    add_card,
    list_cards,
    delete_card,
)


"""
Home view

Redirects to the admin page
"""
def home(request):
    """
    Redirects to the admin page

    :param request: The request object
    :return: A redirect response to the admin page
    """
    return redirect("/dashboard")



urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Dashboard
    path('dashboard/', include('dashboard.urls')),

    # Home
    path("", home, name='home'),

    # Auth
    path('api/auth/register/', register_user_with_verification, name='register'),
    path('api/auth/login/', login_with_2fa, name='login'),
    path('api/auth/logout/', logout_view, name='logout'),
    path('api/auth/check/', check_auth, name='check-auth'),
    path('api/auth/token/refresh/', CustomTokenRefreshView.as_view(), name='token-refresh'),

    # Email verification
    path('api/auth/verify-email/', verify_email, name='verify-email'),
    path('api/auth/resend-verification/', resend_verification_code, name='resend-verification'),

    # 2FA
    path('api/auth/verify-2fa/', verify_2fa_login, name='verify-2fa'),
    path('api/auth/resend-2fa/', resend_2fa_code, name='resend-2fa'),
    path('api/auth/enable-2fa/', enable_2fa, name='enable-2fa'),
    path('api/auth/disable-2fa/', disable_2fa, name='disable-2fa'),
    path('api/auth/2fa-status/', get_2fa_status, name='2fa-status'),

    # Profile & KYC
    path('api/auth/profile/', get_profile, name='profile'),
    path('api/auth/submit-kyc/', submit_kyc, name='submit-kyc'),

    # Password reset
    path('api/auth/password-reset/request/', request_password_reset, name='password-reset-request'),
    path('api/auth/password-reset/confirm/', reset_password, name='password-reset-confirm'),
    path('api/auth/password-reset/validate/', validate_reset_token, name='password-reset-validate'),

    # Deposits
    path('api/auth/deposits/options/', get_deposit_options, name='deposit-options'),
    path('api/auth/deposits/create/', create_deposit, name='deposit-create'),
    path('api/auth/deposits/payment-intent/', deposit_payment_intent, name='deposit-payment-intent'),
    path('api/auth/deposits/history/', get_deposit_history, name='deposit-history'),

    # Withdrawals
    path('api/auth/withdrawals/profile/', get_withdrawal_profile, name='withdrawal-profile'),
    path('api/auth/withdrawals/methods/', get_withdrawal_methods, name='withdrawal-methods'),
    path('api/auth/withdrawals/create/', create_withdrawal, name='withdrawal-create'),
    path('api/auth/withdrawals/history/', get_withdrawal_history, name='withdrawal-history'),

    # Transactions
    path('api/auth/transactions/history/', get_transaction_history, name='transaction-history'),

    # Copy Trading
    path('api/auth/traders/', list_traders, name='list-traders'),
    path('api/auth/traders/<int:trader_id>/', trader_detail, name='trader-detail'),
    path('api/auth/copy-trader/action/', copy_trader_action, name='copy-trader-action'),
    path('api/auth/copy-trader/status/<int:trader_id>/', copy_trader_status, name='copy-trader-status'),
    path('api/auth/copy-trader/trades/', user_copied_trades, name='user-copied-trades'),
    path('api/auth/copy-trader/following/', user_following_traders, name='user-following-traders'),
    path('api/auth/copy-trader/history/', user_trade_history, name='user-trade-history'),
    path('api/auth/calendar/', calendar_data, name='calendar-data'),
    path('api/auth/calendar/seasonality/', calendar_seasonality, name='calendar-seasonality'),

    # Copy Trading - Admin
    path('api/auth/admin/trader/<int:trader_id>/copiers/', admin_trader_copiers, name='admin-trader-copiers'),
    path('api/auth/admin/copy-trader/unlink/', admin_unlink_copier, name='admin-unlink-copier'),
    path('api/auth/admin/copy-trader/handle-cancel/', admin_handle_cancel_request, name='admin-handle-cancel-request'),

    # Referral
    path('api/auth/referral/info/', referral_info, name='referral-info'),
    path('api/auth/referral/list/', referral_list, name='referral-list'),
    path('api/auth/referral/generate/', generate_referral_code, name='referral-generate'),
    path('api/auth/referral/validate/', validate_referral_code, name='referral-validate'),

    # Notifications
    path('api/auth/notifications/', list_notifications, name='list-notifications'),
    path('api/auth/notifications/recent/', get_recent_notifications, name='recent-notifications'),
    path('api/auth/notifications/<int:notification_id>/mark-read/', mark_notification_read, name='mark-notification-read'),
    path('api/auth/notifications/mark-all-read/', mark_all_notifications_read, name='mark-all-notifications-read'),

    # Signals
    path('api/auth/signals/', list_signals, name='list-signals'),
    path('api/auth/signals/<int:signal_id>/', signal_detail, name='signal-detail'),
    path('api/auth/signals/<int:signal_id>/purchase/', purchase_signal, name='purchase-signal'),
    path('api/auth/signals/purchased/', user_purchased_signals, name='user-purchased-signals'),

    # News
    path('api/auth/news/', list_news, name='list-news'),
    path('api/auth/news/<int:news_id>/', news_detail, name='news-detail'),

    # Wallets
    path('api/auth/wallets/', list_wallets, name='list-wallets'),
    path('api/auth/wallets/connect/', connect_wallet, name='connect-wallet'),
    path('api/auth/wallets/<str:wallet_type>/disconnect/', disconnect_wallet, name='disconnect-wallet'),
    path('api/auth/wallets/<int:wallet_id>/detail/', wallet_detail, name='wallet-detail'),

    # Stocks
    path('api/auth/stocks/', list_stocks, name='list-stocks'),
    path('api/auth/treemap/', list_treemap, name='list-treemap'),
    path('api/auth/stocks/buy/', buy_stock, name='buy-stock'),
    path('api/auth/stocks/sell/', sell_stock, name='sell-stock'),
    path('api/auth/stocks/positions/', user_positions, name='user-positions'),
    path('api/auth/stocks/<str:symbol>/', stock_detail, name='stock-detail'),

    # Settings
    path('api/auth/settings/', get_user_settings, name='user-settings'),
    path('api/auth/settings/profile/', update_profile, name='update-profile'),
    path('api/auth/settings/password/', change_password, name='change-password'),
    path('api/auth/settings/payment-method/', update_payment_method, name='update-payment-method'),

    # Transfer
    path('api/auth/transfer/info/', transfer_info, name='transfer-info'),
    path('api/auth/transfer/', make_transfer, name='make-transfer'),

    # Cards
    path('api/auth/cards/', list_cards, name='list-cards'),
    path('api/auth/cards/add/', add_card, name='add-card'),
    path('api/auth/cards/<int:card_id>/delete/', delete_card, name='delete-card'),

    # Cron sync triggers (called by cron-job.com)
    path('api/sync/<str:sync_type>/', sync_trigger, name='sync-trigger'),
]



# Add this for development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


