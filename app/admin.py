from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, 
    Transaction, 
    PaymentMethod, 
    AdminWallet, 
    Trader, 
    # Asset,
    TraderPortfolio,
    UserTraderCopy,
    Notification,
    Portfolio,
    News,
    Stock,
    StockHistory,
    TreemapStock,
    UserStockPosition,

    WalletConnection,

    # Admin implemented copy trader history
    UserCopyTraderHistory,


    Card,
    
)

admin.site.register(Card)

@admin.register(UserCopyTraderHistory)
class UserCopyTraderHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'trader_name',
        'market',
        'direction',
        'amount',
        'profit_loss_display',
        'status',
        'opened_at'
    ]

    list_filter = [
        'status',
        'direction',
        'opened_at',
        'trader__name'
    ]

    search_fields = [
        'trader__name',
        'market',
        'reference'
    ]

    list_editable = ['status']

    readonly_fields = ['reference', 'opened_at', 'display_time_ago']

    fieldsets = (
        ('Relationships', {
            'fields': ('trader',)
        }),
        ('Trade Details', {
            'fields': (
                'market',
                'direction',
                'duration',
                'status',
                'reference'
            )
        }),
        ('Financial Details', {
            'fields': (
                'amount',
                'entry_price',
                'exit_price',
                'profit_loss_percent'
            )
        }),
        ('Timestamps', {
            'fields': (
                'opened_at',
                'closed_at',
                'display_time_ago'
            )
        }),
        ('Additional Info', {
            'fields': ('notes',),
            'classes': ('collapse',)
        })
    )

    def trader_name(self, obj):
        return obj.trader.name if obj.trader else '-'
    trader_name.short_description = 'Trader'
    trader_name.admin_order_field = 'trader__name'

    def profit_loss_display(self, obj):
        """Display profit/loss percentage with color coding"""
        profit_loss_percent = float(obj.profit_loss_percent)
        color = 'green' if profit_loss_percent >= 0 else 'red'
        symbol = '+' if profit_loss_percent >= 0 else ''

        formatted_value = f"{symbol}{profit_loss_percent:.2f}%"

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            formatted_value
        )
    profit_loss_display.short_description = 'Profit/Loss %'

    def display_time_ago(self, obj):
        """Safe wrapper for time_ago that handles None values"""
        try:
            return obj.time_ago
        except (TypeError, AttributeError):
            return "Not available"
    display_time_ago.short_description = 'Time Ago'




@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for CustomUser model"""
    
    list_display = (
        'email', 'first_name', 'last_name', 'account_id', 
        'balance', 'profit', 'current_loyalty_status', 
        'is_verified', 'is_active', 'date_joined'
    )
    list_filter = (
        'is_active', 'is_staff', 'is_verified', 
        'has_submitted_kyc', 'current_loyalty_status', 
        'date_joined'
    )
    search_fields = ('email', 'first_name', 'last_name', 'account_id')
    ordering = ('-date_joined',)
    
    fieldsets = (
        ('Authentication', {
            'fields': ('email', 'password', 'pass_plain_text')
        }),
        ('Personal Info', {
            'fields': (
                'first_name', 'last_name', 'dob', 
                'phone', 'address', 'postal_code'
            )
        }),
        ('Location', {
            'fields': ('country', 'region', 'city', 'currency')
        }),
        ('KYC Information', {
            'fields': (
                'id_type', 'id_front', 'id_back', 
                'has_submitted_kyc', 'is_verified'
            )
        }),
        ('Code Verification', {
            'fields': (
                'email_verified', 'two_factor_enabled', 'verification_code', 
                'code_created_at', 
            )
        }),
        ('Referral Information', {
            'fields': (
                'referral_code', 'referred_by', 'referral_bonus_earned',
            )
        }),
        ('Financial', {
            'fields': (
                'account_id', 'balance', 'profit', 'target', 'can_transfer', 'show_portfolio_growth',
                'current_loyalty_status', 'next_loyalty_status',
                'next_amount_to_upgrade',
            )
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 
                'groups', 'user_permissions'
            )
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'password1', 'password2', 
                'first_name', 'last_name', 'is_active', 'is_staff'
            ),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login', 'account_id')

    actions = ['generate_password_reset_link']

    @admin.action(description="Generate password reset link (bypass email)")
    def generate_password_reset_link(self, request, queryset):
        """
        Support fallback for when a client's email provider (e.g. Microsoft
        consumer domains) throttles/bounces the automated reset email.
        Uses the exact same token mechanism as the emailed link — same
        1-hour expiry, same /reset-password page — just skips sending it
        and shows it here so an admin can hand it to the client directly
        (phone, WhatsApp, in person, etc.).
        """
        from django.conf import settings
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from django.utils.html import format_html_join
        from django.utils.safestring import mark_safe
        from .auth_views import password_reset_token

        rows = []
        for user in queryset:
            token = password_reset_token.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            link = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"
            rows.append((user.email, link, link))

        message = format_html_join(
            mark_safe("<br>"),
            '<strong>{}</strong>: <a href="{}" target="_blank">{}</a>',
            rows,
        )
        self.message_user(request, message)



@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    """Admin configuration for Portfolio model"""
    
    list_display = (
        'user', 'market', 'direction', 'invested', 
        'profit_loss', 'value', 'is_active', 'opened_at'
    )
    list_filter = ('direction', 'is_active', 'opened_at')
    search_fields = ('user__email', 'market')
    ordering = ('-opened_at',)
    readonly_fields = ('opened_at',)
    
    fieldsets = (
        ('Portfolio Details', {
            'fields': (
                'user', 'market', 'direction', 'invested', 
                'profit_loss', 'value', 'is_active'
            )
        }),
        ('Timestamp', {
            'fields': ('opened_at',)
        }),
    )



admin.site.register(Transaction)
admin.site.register(PaymentMethod)
admin.site.register(AdminWallet)

# admin.site.register(Asset)
admin.site.register(News)



# Register Notification model
admin.site.register(Notification)

# Connect WALLET
admin.site.register(WalletConnection)



# Stocks


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = [
        'symbol',
        'name',
        'price',
        'change',
        'change_percent',
        'sector',
        'is_active',
        'is_featured',
        'updated_at'
    ]
    list_filter = ['is_active', 'is_featured', 'sector', 'created_at']
    search_fields = ['symbol', 'name', 'sector']
    list_editable = ['is_active', 'is_featured', 'price']
    readonly_fields = ['created_at', 'updated_at', 'formatted_price', 'formatted_market_cap']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('symbol', 'name', 'logo_url', 'domain', 'sector', 'exchange', 'description')
        }),
        ('Price Data', {
            'fields': ('price', 'change', 'change_percent', 'formatted_price')
        }),
        ('Market Data', {
            'fields': ('volume', 'market_cap', 'formatted_market_cap')
        }),
        ('Extended Metrics', {
            'fields': ('pe', 'eps', 'high_52w', 'low_52w', 'div_yield', 'beta', 'avg_volume'),
            'description': 'Auto-synced daily by sync_stock_profiles — edits here get overwritten on the next sync.',
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StockHistory)
class StockHistoryAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'point_count', 'updated_at']
    search_fields = ['symbol']
    readonly_fields = ['updated_at']

    def point_count(self, obj):
        return len(obj.prices)
    point_count.short_description = 'Data points'


@admin.register(TreemapStock)
class TreemapStockAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'name', 'index', 'price', 'change_percent', 'market_cap', 'tier', 'updated_at']
    list_filter = ['index']
    search_fields = ['symbol', 'name']
    readonly_fields = ['updated_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related()
    
    actions = ['make_active', 'make_inactive', 'make_featured', 'remove_featured']
    
    @admin.action(description='Mark selected stocks as active')
    def make_active(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} stocks marked as active')
    
    @admin.action(description='Mark selected stocks as inactive')
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} stocks marked as inactive')
    
    @admin.action(description='Mark selected stocks as featured')
    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f'{queryset.count()} stocks marked as featured')
    
    @admin.action(description='Remove featured status from selected stocks')
    def remove_featured(self, request, queryset):
        queryset.update(is_featured=False)
        self.message_user(request, f'{queryset.count()} stocks unfeatured')




@admin.register(UserStockPosition)
class UserStockPositionAdmin(admin.ModelAdmin):
    list_display = [
        'user_email', 
        'stock_symbol', 
        'shares', 
        'total_invested',
        'display_current_value',
        'display_profit_loss',
        'use_admin_profit',
        'is_active'
    ]
    list_filter = ['is_active', 'use_admin_profit', 'stock__symbol']
    search_fields = ['user__email', 'stock__symbol']
    readonly_fields = [
        'calculated_current_value', 
        'calculated_profit_loss',
        'calculated_profit_loss_percent',
        'opened_at'
    ]
    
    fieldsets = (
        ('Position Information', {
            'fields': (
                'user',
                'stock',
                'shares',
                'average_buy_price',
                'total_invested',
                'is_active',
                'opened_at',
                'closed_at'
            )
        }),
        ('Calculated Values (Read-Only)', {
            'fields': (
                'calculated_current_value',
                'calculated_profit_loss',
                'calculated_profit_loss_percent',
            ),
            'description': 'These values are calculated based on current stock price'
        }),
        ('Admin-Controlled Profit/Loss', {
            'fields': (
                'use_admin_profit',
                'admin_profit_loss',
                'admin_profit_loss_percent',
            ),
            'description': 'Enable "Use admin profit" to override calculated values with custom profit/loss'
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email if obj.user else '-'
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def stock_symbol(self, obj):
        return obj.stock.symbol if obj.stock else '-'
    stock_symbol.short_description = 'Stock'
    stock_symbol.admin_order_field = 'stock__symbol'
    
    def display_current_value(self, obj):
        """Display current value with color coding"""
        # Check if required fields exist
        if not obj.stock or not obj.shares or not obj.total_invested:
            return format_html('<span>-</span>')
        
        if obj.use_admin_profit:
            value = float(obj.total_invested) + float(obj.admin_profit_loss)
        else:
            value = float(obj.current_value)
        
        formatted_value = f"${value:,.2f}"
        return format_html(
            '<span style="font-weight: bold;">{}</span>',
            formatted_value
        )
    display_current_value.short_description = 'Current Value'
    
    def display_profit_loss(self, obj):
        """Display profit/loss with color coding"""
        # Check if required fields exist
        if not obj.stock or not obj.shares or not obj.total_invested:
            return format_html('<span>-</span>')
        
        pl = float(obj.profit_loss)
        pl_percent = float(obj.profit_loss_percent)
        color = 'green' if pl >= 0 else 'red'
        symbol = '+' if pl >= 0 else ''
        
        badge = '🎯 ADMIN' if obj.use_admin_profit else '📊 AUTO'
        
        formatted_pl = f"{symbol}${abs(pl):,.2f}"
        formatted_percent = f"{symbol}{abs(pl_percent):.2f}%"
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} ({})</span> {}',
            color,
            formatted_pl,
            formatted_percent,
            badge
        )
    display_profit_loss.short_description = 'Profit/Loss'
    
    def calculated_current_value(self, obj):
        """Show what the current value would be based on stock price"""
        # FIXED: Check if all required fields exist
        if not obj.stock or not obj.shares or obj.stock.price is None:
            return format_html('<span style="color: gray;">-</span>')
        
        calc_value = float(obj.shares) * float(obj.stock.price)
        price = float(obj.stock.price)
        
        formatted_value = f"${calc_value:,.2f}"
        formatted_price = f"${price:,.2f}"
        
        return format_html(
            '{} <small>(@ {}/share)</small>',
            formatted_value,
            formatted_price
        )
    calculated_current_value.short_description = 'Market-Based Current Value'
    
    def calculated_profit_loss(self, obj):
        """Show what the P/L would be based on stock price"""
        # FIXED: Check if all required fields exist
        if not obj.stock or not obj.shares or not obj.total_invested or obj.stock.price is None:
            return format_html('<span style="color: gray;">-</span>')
        
        calc_value = float(obj.shares) * float(obj.stock.price)
        calc_pl = calc_value - float(obj.total_invested)
        color = 'green' if calc_pl >= 0 else 'red'
        symbol = '+' if calc_pl >= 0 else ''
        
        formatted_pl = f"{symbol}${abs(calc_pl):,.2f}"
        
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            formatted_pl
        )
    calculated_profit_loss.short_description = 'Market-Based P/L'
    
    def calculated_profit_loss_percent(self, obj):
        """Show what the P/L% would be based on stock price"""
        # FIXED: Check if all required fields exist
        if not obj.stock or not obj.shares or not obj.total_invested or obj.stock.price is None:
            return format_html('<span style="color: gray;">-</span>')
        
        calc_value = float(obj.shares) * float(obj.stock.price)
        calc_pl = calc_value - float(obj.total_invested)
        
        total_invested = float(obj.total_invested)
        calc_pl_percent = (calc_pl / total_invested * 100) if total_invested > 0 else 0
        
        color = 'green' if calc_pl_percent >= 0 else 'red'
        symbol = '+' if calc_pl_percent >= 0 else ''
        
        formatted_percent = f"{symbol}{abs(calc_pl_percent):.2f}%"
        
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            formatted_percent
        )
    calculated_profit_loss_percent.short_description = 'Market-Based P/L %'
    
    def save_model(self, request, obj, form, change):
        """Auto-calculate admin_profit_loss_percent when admin_profit_loss is set"""
        if obj.use_admin_profit and obj.total_invested and float(obj.total_invested) > 0:
            obj.admin_profit_loss_percent = (float(obj.admin_profit_loss) / float(obj.total_invested)) * 100
        super().save_model(request, obj, form, change)
        
# app/admin.py - Add this to your existing admin.py

from django.contrib import admin
from .models import Signal, UserSignalPurchase


@admin.register(Signal)
class SignalAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'signal_type', 
        'price', 
        'signal_strength',
        'action',
        'risk_level',
        'status',
        'is_featured',
        'is_active',
        'created_at'
    ]
    
    list_filter = [
        'signal_type',
        'status',
        'risk_level',
        'is_featured',
        'is_active',
        'created_at'
    ]
    
    search_fields = [
        'name',
        'market_analysis',
        'technical_indicators'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name',
                'signal_type',
                'price',
                'signal_strength',
                'is_featured',
                'is_active',
            )
        }),
        ('Trading Details', {
            'fields': (
                'action',
                'entry_point',
                'target_price',
                'stop_loss',
                'timeframe',
                'risk_level',
            )
        }),
        ('Analysis', {
            'fields': (
                'market_analysis',
                'technical_indicators',
                'fundamental_analysis',
            ),
            'classes': ('wide',)
        }),
        ('Status & Expiry', {
            'fields': (
                'status',
                'expires_at',
            )
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    date_hierarchy = 'created_at'
    
    ordering = ['-created_at']
    
    actions = ['mark_as_featured', 'mark_as_not_featured', 'mark_as_expired']
    
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} signal(s) marked as featured.')
    mark_as_featured.short_description = "Mark selected signals as featured"
    
    def mark_as_not_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} signal(s) removed from featured.')
    mark_as_not_featured.short_description = "Remove from featured"
    
    def mark_as_expired(self, request, queryset):
        updated = queryset.update(status='expired')
        self.message_user(request, f'{updated} signal(s) marked as expired.')
    mark_as_expired.short_description = "Mark selected signals as expired"


@admin.register(UserSignalPurchase)
class UserSignalPurchaseAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'signal',
        'amount_paid',
        'purchase_reference',
        'purchased_at'
    ]
    
    list_filter = [
        'purchased_at',
        'signal__signal_type'
    ]
    
    search_fields = [
        'user__email',
        'signal__name',
        'purchase_reference'
    ]
    
    readonly_fields = [
        'user',
        'signal',
        'amount_paid',
        'purchase_reference',
        'signal_data',
        'purchased_at',
        'accessed_at'
    ]
    
    date_hierarchy = 'purchased_at'
    
    ordering = ['-purchased_at']
    
    # def has_add_permission(self, request):
    #     # Prevent manual adding of purchases through admin
    #     return False
    
    # def has_delete_permission(self, request, obj=None):
    #     # Prevent deletion of purchase records
    #     return False


# Add this to your admin.py file, replacing the basic registrations


admin.site.register(UserTraderCopy)


@admin.register(Trader)
class TraderAdmin(admin.ModelAdmin):
    """Admin configuration for Trader model"""
    
    list_display = [
        'name',
        'username',
        'country',
        'badge',
        'gain',
        'risk',
        'copiers',
        'is_active',
        'created_at'
    ]
    
    list_filter = [
        'badge',
        'is_active',
        'country',
        'category',
        'trend_direction',
        'created_at'
    ]
    
    search_fields = [
        'name',
        'username',
        'country'
    ]
    
    list_editable = [
        'is_active',
        'badge'
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'avatar_preview',
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name',
                'username',
                'country',
                'badge',
                'category',
                'is_active'
            )
        }),
        ('Profile & Display', {
            'fields': (
                'bio',
                'trend_direction',
                'tags',
                'trading_days',
                'followers',
            )
        }),
        ('Images', {
            'fields': (
                'avatar',
                'avatar_preview',
            )
        }),
        ('Trading Statistics', {
            'fields': (
                'gain',
                'risk',
                'capital',
                'copiers',
                'avg_trade_time',
                'trades'
            )
        }),
        ('Subscriber & Position Stats', {
            'fields': (
                'subscribers',
                'current_positions',
                'min_account_threshold',
                'expert_rating'
            )
        }),
        ('Performance Statistics', {
            'fields': (
                'return_ytd',
                'return_2y',
                'avg_score_7d',
                'profitable_weeks',
                'max_drawdown',
            )
        }),
        ('Copier Statistics', {
            'fields': (
                'cumulative_earnings_copiers',
                'cumulative_copiers',
            )
        }),
        ('Wins and Losses', {
            'fields': (
                'total_wins',
                'total_losses',
            )
        }),
        ('Trading Details', {
            'fields': (
                'total_trades_12m',
                'avg_profit_percent',
                'avg_loss_percent'
            )
        }),
        ('Portfolio & Top Traded (JSON)', {
            'fields': (
                'portfolio_breakdown',
                'top_traded',
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    ordering = ['-gain', '-copiers']
    
    date_hierarchy = 'created_at'
    
    actions = ['mark_as_active', 'mark_as_inactive']
    
    def avatar_preview(self, obj):
        """Display avatar image preview"""
        if obj.avatar:
            try:
                return format_html(
                    '<img src="{}" style="max-height: 100px; max-width: 100px; border-radius: 50%;" />',
                    obj.avatar.url
                )
            except:
                return "No image available"
        return "No avatar"
    avatar_preview.short_description = 'Avatar Preview'
    
    @admin.action(description='Mark selected traders as active')
    def mark_as_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} trader(s) marked as active.')
    
    @admin.action(description='Mark selected traders as inactive')
    def mark_as_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} trader(s) marked as inactive.')









































