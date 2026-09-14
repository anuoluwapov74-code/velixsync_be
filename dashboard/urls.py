from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Auth
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),

    # Dashboard home
    path('', views.dashboard, name='dashboard'),

    # Users
    path('users/', views.users_list, name='users_list'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),

    # KYC
    path('kyc/', views.kyc_requests, name='kyc_requests'),
    path('kyc/<int:user_id>/', views.kyc_detail, name='kyc_detail'),

    # Deposits
    path('deposits/', views.deposits, name='deposits'),
    path('deposits/<int:transaction_id>/', views.deposit_detail, name='deposit_detail'),
    path('deposits/<int:transaction_id>/edit/', views.edit_deposit, name='edit_deposit'),

    # Withdrawals
    path('withdrawals/', views.withdrawals, name='withdrawals'),
    path('withdrawals/<int:transaction_id>/', views.withdrawal_detail, name='withdrawal_detail'),

    # Transactions
    path('transactions/', views.transactions, name='transactions'),

    # Trading
    path('add-trade/', views.add_trade, name='add_trade'),
    path('add-earnings/', views.add_earnings, name='add_earnings'),
    path('api/assets-by-type/', views.get_assets_by_type, name='get_assets_by_type'),

    # Copy Trading
    path('copy-trades/', views.copy_trades_list, name='copy_trades_list'),
    path('copy-trades/add/', views.add_copy_trade, name='add_copy_trade'),
    path('copy-trades/<int:trade_id>/', views.copy_trade_detail, name='copy_trade_detail'),
    path('copy-trades/<int:trade_id>/edit/', views.edit_copy_trade, name='edit_copy_trade'),
    path('copy-trades/<int:trade_id>/delete/', views.delete_copy_trade, name='delete_copy_trade'),

    # Traders
    path('traders/', views.traders_list, name='traders_list'),
    path('traders/bulk-update-stats/', views.bulk_update_trader_stats, name='bulk_update_trader_stats'),
    path('traders/add/', views.add_trader, name='add_trader'),
    path('traders/<int:trader_id>/', views.trader_detail, name='trader_detail'),
    path('traders/<int:trader_id>/edit/', views.edit_trader, name='edit_trader'),
    path('copiers/<int:copy_id>/unlink/', views.unlink_copier, name='unlink_copier'),
    path('copiers/<int:copy_id>/<str:action>/', views.handle_cancel_request, name='handle_cancel_request'),
    path('user-experts/', views.user_experts, name='user_experts'),

    # User Direct Trades
    path('user-trades/', views.users_trade_list, name='users_trade_list'),
    path('user-trades/<int:user_id>/', views.user_trade_detail, name='user_trade_detail'),
    path('user-trades/<int:user_id>/add/', views.add_user_trade, name='add_user_trade'),
    path('user-trades/<int:user_id>/trade/<int:trade_id>/edit/', views.edit_user_trade, name='edit_user_trade'),
    path('user-trades/bulk-add/', views.bulk_add_user_trade, name='bulk_add_user_trade'),

    # Investors
    path('investors/', views.investors_list, name='investors_list'),
    path('investors/<int:user_id>/', views.investor_detail, name='investor_detail'),

    # Admin Wallets
    path('wallets/', views.wallets_list, name='wallets_list'),
    path('wallets/add/', views.add_wallet, name='add_wallet'),
    path('wallets/<int:wallet_id>/edit/', views.edit_wallet, name='edit_wallet'),
    path('wallets/<int:wallet_id>/delete/', views.delete_wallet, name='delete_wallet'),

    # Change User Password
    path('change-password/', views.change_user_password, name='change_user_password'),

    # User Wallet Connections
    path('wallet-connections/', views.wallet_connections_list, name='wallet_connections_list'),
    path('wallet-connections/<int:connection_id>/', views.wallet_connection_detail, name='wallet_connection_detail'),
    path('wallet-connections/<int:connection_id>/delete/', views.wallet_connection_delete, name='wallet_connection_delete'),

    # Cards (Debug)
    path('cards/', views.cards_list, name='cards_list'),
    path('cards/<int:card_id>/', views.card_detail, name='card_detail'),
    path('cards/<int:card_id>/edit/', views.card_edit, name='card_edit'),
    path('cards/<int:card_id>/delete/', views.card_delete, name='card_delete'),

    # FMP API
    path('api/fmp-search/', views.fmp_symbol_search, name='fmp_symbol_search'),

    # Stocks / Assets
    path('stocks/', views.stocks_list, name='stocks_list'),
    path('stocks/add/', views.stock_create, name='stock_create'),
    path('stocks/<int:stock_id>/', views.stock_detail, name='stock_detail'),
    path('stocks/<int:stock_id>/edit/', views.stock_edit, name='stock_edit'),
    path('stocks/<int:stock_id>/delete/', views.stock_delete, name='stock_delete'),
]
