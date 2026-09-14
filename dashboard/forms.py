from django import forms
from django.utils.safestring import mark_safe
from app.models import CustomUser, Stock, Transaction, Trader, UserCopyTraderHistory, AdminWallet, Card
from decimal import Decimal

# ---------------------------------------------------------------------------
# Shared Tailwind widget classes
# ---------------------------------------------------------------------------
_input = 'w-full px-4 py-2.5 bg-gray-50 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition'
_select = _input
_textarea = _input
_checkbox = 'w-4 h-4 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500'
_file = 'w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'


# ===== Trade Forms =====

class AddTradeForm(forms.Form):
    user_email = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(is_active=True).order_by('email'),
        label="Select User",
        widget=forms.Select(attrs={'class': _select}),
        to_field_name='email',
    )
    entry = forms.DecimalField(
        label="Entry Amount", max_digits=12, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '5255'}),
    )

    ASSET_TYPE_CHOICES = [('', 'Select Type'), ('stock', 'Stock'), ('crypto', 'Crypto'), ('forex', 'Forex')]
    asset_type = forms.ChoiceField(choices=ASSET_TYPE_CHOICES, label="Type", widget=forms.Select(attrs={'class': _select}))

    asset = forms.CharField(
        label="Asset",
        widget=forms.TextInput(attrs={'class': _input, 'placeholder': 'Select type first'}),
    )

    DIRECTION_CHOICES = [('', 'Select Direction'), ('buy', 'Buy'), ('sell', 'Sell'), ('futures', 'Futures')]
    direction = forms.ChoiceField(choices=DIRECTION_CHOICES, label="Direction", widget=forms.Select(attrs={'class': _select}))

    profit = forms.DecimalField(
        label="Profit / Loss", max_digits=12, decimal_places=2, required=False,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '0.00'}),
    )

    DURATION_CHOICES = [
        ('', 'Select Duration'),
        ('2 minutes', '2 minutes'), ('5 minutes', '5 minutes'), ('30 minutes', '30 minutes'),
        ('1 hour', '1 hour'), ('8 hours', '8 hours'), ('10 hours', '10 hours'), ('20 hours', '20 hours'),
        ('1 day', '1 day'), ('2 days', '2 days'), ('3 days', '3 days'),
        ('4 days', '4 days'), ('5 days', '5 days'), ('6 days', '6 days'),
        ('1 week', '1 week'), ('2 weeks', '2 weeks'),
    ]
    duration = forms.ChoiceField(choices=DURATION_CHOICES, label="Duration", widget=forms.Select(attrs={'class': _select}))

    rate = forms.DecimalField(
        label="Rate (Optional)", max_digits=12, decimal_places=2, required=False,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '251'}),
    )


class AddEarningsForm(forms.Form):
    user_email = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(is_active=True).order_by('email'),
        label="Select User",
        widget=forms.Select(attrs={'class': _select}),
        to_field_name='email',
    )
    amount = forms.DecimalField(
        label="Earnings Amount", max_digits=12, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '100.00'}),
    )
    description = forms.CharField(
        label="Description", required=False,
        widget=forms.TextInput(attrs={'class': _input, 'placeholder': 'Bonus, Referral, Trade Profit, etc.'}),
    )


# ===== Approval Forms =====

class ApproveDepositForm(forms.Form):
    STATUS_CHOICES = [('completed', 'Approve'), ('failed', 'Reject')]
    status = forms.ChoiceField(choices=STATUS_CHOICES, label="Action", widget=forms.Select(attrs={'class': _select}))
    admin_notes = forms.CharField(
        label="Admin Notes (Optional)", required=False,
        widget=forms.Textarea(attrs={'class': _textarea, 'rows': 3, 'placeholder': 'Internal notes…'}),
    )


class ApproveWithdrawalForm(forms.Form):
    STATUS_CHOICES = [('completed', 'Approve'), ('failed', 'Reject')]
    status = forms.ChoiceField(choices=STATUS_CHOICES, label="Action", widget=forms.Select(attrs={'class': _select}))
    admin_notes = forms.CharField(
        label="Admin Notes (Optional)", required=False,
        widget=forms.Textarea(attrs={'class': _textarea, 'rows': 3, 'placeholder': 'Internal notes…'}),
    )


class ApproveKYCForm(forms.Form):
    ACTION_CHOICES = [('approve', 'Approve KYC'), ('reject', 'Reject KYC')]
    action = forms.ChoiceField(choices=ACTION_CHOICES, label="Action", widget=forms.Select(attrs={'class': _select}))
    admin_notes = forms.CharField(
        label="Admin Notes (Optional)", required=False,
        widget=forms.Textarea(attrs={'class': _textarea, 'rows': 3, 'placeholder': 'Reason for rejection…'}),
    )


# ===== Deposit Edit Form =====

class EditDepositForm(forms.Form):
    amount = forms.DecimalField(
        label="Deposit Amount", max_digits=12, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '1000.00', 'step': '0.01'}),
    )

    CURRENCY_CHOICES = [
        ('BTC', 'Bitcoin (BTC)'), ('ETH', 'Ethereum (ETH)'), ('SOL', 'Solana (SOL)'),
        ('USDT ERC20', 'USDT (ERC20)'), ('USDT TRC20', 'USDT (TRC20)'),
        ('BNB', 'Binance Coin (BNB)'), ('TRX', 'Tron (TRX)'), ('USDC', 'USDC (BASE)'),
    ]
    currency = forms.ChoiceField(choices=CURRENCY_CHOICES, label="Currency", widget=forms.Select(attrs={'class': _select}))

    unit = forms.DecimalField(
        label="Crypto Unit Amount", max_digits=12, decimal_places=8,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '0.01234567', 'step': '0.00000001'}),
    )

    STATUS_CHOICES = [('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed'), ('cancelled', 'Cancelled')]
    status = forms.ChoiceField(choices=STATUS_CHOICES, label="Status", widget=forms.Select(attrs={'class': _select}))

    description = forms.CharField(
        label="Description", required=False,
        widget=forms.Textarea(attrs={'class': _textarea, 'rows': 3, 'placeholder': 'Deposit description…'}),
    )
    reference = forms.CharField(
        label="Reference Number", max_length=100,
        widget=forms.TextInput(attrs={'class': _input, 'placeholder': 'DEP-XXXXXXXXXX'}),
    )
    receipt = forms.ImageField(
        label="Update Receipt (Optional)", required=False,
        widget=forms.FileInput(attrs={'class': _file, 'accept': 'image/*'}),
    )


# ===== Copy Trade Form =====

class AddCopyTradeForm(forms.Form):
    trader = forms.ModelChoiceField(
        queryset=Trader.objects.filter(is_active=True).order_by('name'),
        label="Select Trader",
        widget=forms.Select(attrs={'class': _select}),
        empty_label="Select Trader",
    )
    market = forms.ChoiceField(
        choices=[('', 'Select Market')] + list(UserCopyTraderHistory.MARKET_CHOICES),
        label="Market / Asset", widget=forms.Select(attrs={'class': _select}),
    )
    direction = forms.ChoiceField(
        choices=[('', 'Select Direction')] + list(UserCopyTraderHistory.DIRECTION_CHOICES),
        label="Trade Direction", widget=forms.Select(attrs={'class': _select}),
    )

    DURATION_CHOICES = [
        ('', 'Select Duration'),
        ('2 minutes', '2 Minutes'), ('5 minutes', '5 Minutes'), ('10 minutes', '10 Minutes'),
        ('15 minutes', '15 Minutes'), ('30 minutes', '30 Minutes'),
        ('1 hour', '1 Hour'), ('2 hours', '2 Hours'), ('4 hours', '4 Hours'), ('12 hours', '12 Hours'),
        ('1 day', '1 Day'), ('2 days', '2 Days'),
        ('1 week', '1 Week'), ('2 weeks', '2 Weeks'), ('1 month', '1 Month'),
    ]
    duration = forms.ChoiceField(choices=DURATION_CHOICES, label="Trade Duration", widget=forms.Select(attrs={'class': _select}))

    amount = forms.DecimalField(
        label="Investment Amount", max_digits=20, decimal_places=8,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '1000.00', 'step': '0.00000001'}),
    )
    entry_price = forms.DecimalField(
        label="Entry Price", max_digits=20, decimal_places=8,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '50000.00', 'step': '0.00000001'}),
    )
    exit_price = forms.DecimalField(
        label="Exit Price (Optional)", max_digits=20, decimal_places=8, required=False,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '51000.00', 'step': '0.00000001'}),
    )
    profit_loss_percent = forms.DecimalField(
        label="Profit / Loss %", max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '15.50', 'step': '0.01'}),
        help_text="Positive for profit, negative for loss",
    )
    status = forms.ChoiceField(
        choices=[('', 'Select Status')] + list(UserCopyTraderHistory.STATUS_CHOICES),
        label="Trade Status", widget=forms.Select(attrs={'class': _select}),
    )
    closed_at = forms.DateTimeField(
        label="Close Date & Time (Optional)", required=False,
        widget=forms.DateTimeInput(attrs={'class': _input, 'type': 'datetime-local'}),
    )
    notes = forms.CharField(
        label="Notes (Optional)", required=False,
        widget=forms.Textarea(attrs={'class': _textarea, 'rows': 3, 'placeholder': 'Additional notes…'}),
    )


# ===== Trader Forms =====

class AddTraderForm(forms.Form):
    # --- Basic Info ---
    name = forms.CharField(
        label="Trader Name", max_length=150,
        widget=forms.TextInput(attrs={'class': _input, 'placeholder': 'Kristijan'})
    )
    username = forms.CharField(
        label="Username", max_length=100,
        widget=forms.TextInput(attrs={'class': _input, 'placeholder': '@kristijan'}),
        help_text="Must be unique"
    )
    avatar = forms.ImageField(
        label="Avatar Image", required=False,
        widget=forms.FileInput(attrs={'class': _file, 'accept': 'image/*'})
    )
    country_flag = forms.ImageField(
        label="Country Flag Image", required=False,
        widget=forms.FileInput(attrs={'class': _file, 'accept': 'image/*'})
    )

    COUNTRY_CHOICES = [
        ('', 'Select Country'),
        ('United States', 'United States'), ('United Kingdom', 'United Kingdom'),
        ('Germany', 'Germany'), ('France', 'France'), ('Canada', 'Canada'),
        ('Australia', 'Australia'), ('Singapore', 'Singapore'), ('Hong Kong', 'Hong Kong'),
        ('Japan', 'Japan'), ('South Korea', 'South Korea'), ('India', 'India'),
        ('Brazil', 'Brazil'), ('Mexico', 'Mexico'), ('Netherlands', 'Netherlands'),
        ('Switzerland', 'Switzerland'), ('Sweden', 'Sweden'), ('Norway', 'Norway'),
        ('Denmark', 'Denmark'), ('Spain', 'Spain'), ('Italy', 'Italy'), ('Other', 'Other'),
    ]
    country = forms.ChoiceField(
        choices=COUNTRY_CHOICES, label="Country",
        widget=forms.Select(attrs={'class': _select})
    )

    badge = forms.ChoiceField(
        choices=[('', 'Select Badge'), ('bronze', 'Bronze'), ('silver', 'Silver'), ('gold', 'Gold')],
        label="Badge Level",
        widget=forms.Select(attrs={'class': _select})
    )

    bio = forms.CharField(
        label="Bio / Description", required=False,
        widget=forms.Textarea(attrs={'class': _textarea, 'rows': 3, 'placeholder': 'Short bio about the trader...'})
    )

    # --- Trading Category & Display ---
    CATEGORY_CHOICES = [
        ('', 'Select Category'),
        ('all', 'All'), ('crypto', 'Crypto'), ('stocks', 'Stocks'),
        ('healthcare', 'Healthcare'), ('financial', 'Financial Services'),
        ('options', 'Options'), ('tech', 'Tech'), ('etf', 'ETF'),
    ]
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES, label="Trading Category",
        widget=forms.Select(attrs={'class': _select})
    )

    TREND_CHOICES = [
        ('', 'Select Trend'),
        ('upward', 'Upward'),
        ('downward', 'Downward'),
    ]
    trend_direction = forms.ChoiceField(
        choices=TREND_CHOICES, label="Chart Trend Direction",
        widget=forms.Select(attrs={'class': _select})
    )

    tags = forms.CharField(
        label='Tags', required=False,
        widget=forms.Textarea(attrs={'class': _textarea, 'rows': 2, 'placeholder': 'Will be replaced by tag builder'}),
        help_text=''
    )

    # --- Capital & Gain ---
    gain = forms.DecimalField(
        label="Total Gain (%)", max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '126799.00', 'step': '0.01'})
    )

    # --- Risk & Time ---
    RISK_CHOICES = [(i, str(i)) for i in range(1, 11)]
    risk = forms.ChoiceField(
        choices=[('', 'Select Risk Level')] + RISK_CHOICES,
        label="Risk Level (1-10)",
        widget=forms.Select(attrs={'class': _select})
    )

    AVG_TRADE_TIME_CHOICES = [
        ('', 'Select Avg Trade Time'),
        ('1 day', '1 Day'), ('3 days', '3 Days'), ('1 week', '1 Week'), ('2 weeks', '2 Weeks'),
        ('3 weeks', '3 Weeks'), ('1 month', '1 Month'), ('2 months', '2 Months'),
        ('3 months', '3 Months'), ('6 months', '6 Months'),
    ]
    avg_trade_time = forms.ChoiceField(
        choices=AVG_TRADE_TIME_CHOICES, label="Avg Trade Time",
        widget=forms.Select(attrs={'class': _select})
    )

    # --- Copiers & Trades (Direct Input) ---
    copiers = forms.IntegerField(
        label="Current Copiers",
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '40', 'min': '0'})
    )
    trades = forms.IntegerField(
        label="Total Trades",
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '251', 'min': '0'})
    )

    # --- Performance Stats (Direct Input) ---
    avg_profit_percent = forms.DecimalField(
        label="Avg Profit %", max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '86.00', 'step': '0.01'})
    )
    avg_loss_percent = forms.DecimalField(
        label="Avg Loss %", max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '8.00', 'step': '0.01'})
    )
    total_wins = forms.IntegerField(
        label="Total Wins",
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '1166', 'min': '0'})
    )
    total_losses = forms.IntegerField(
        label="Total Losses",
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '160', 'min': '0'})
    )

    # --- Additional Stats (Direct Input) ---
    subscribers = forms.IntegerField(
        label="Subscribers", required=False, initial=0,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '49', 'min': '0'})
    )
    followers = forms.IntegerField(
        label="Followers", required=False, initial=0,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '120', 'min': '0'})
    )
    current_positions = forms.IntegerField(
        label="Current Open Positions", required=False, initial=0,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '3', 'min': '0'})
    )
    expert_rating = forms.DecimalField(
        label="Expert Rating (out of 5.00)", max_digits=3, decimal_places=2, required=False, initial=5.00,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '4.80', 'step': '0.01', 'min': '0', 'max': '5'})
    )

    # --- Performance Metrics ---
    return_ytd = forms.DecimalField(
        label="Return YTD %", max_digits=10, decimal_places=2, required=False, initial=0.00,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '2187.00', 'step': '0.01'})
    )
    return_2y = forms.DecimalField(
        label="Return 2 Years %", max_digits=10, decimal_places=2, required=False, initial=0.00,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '5000.00', 'step': '0.01'})
    )
    avg_score_7d = forms.DecimalField(
        label="Avg Score (7 days)", max_digits=10, decimal_places=2, required=False, initial=0.00,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '9.30', 'step': '0.01'})
    )
    profitable_weeks = forms.DecimalField(
        label="Profitable Weeks %", max_digits=5, decimal_places=2, required=False, initial=0.00,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '92.00', 'step': '0.01'})
    )
    min_account_threshold = forms.DecimalField(
        label="Min Account Balance ($)", max_digits=12, decimal_places=2, required=False, initial=0.00,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '50000.00', 'step': '0.01'})
    )
    profit_share = forms.IntegerField(
        label="Profit Share %", required=False, initial=50,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '50', 'min': '0', 'max': '100'})
    )
    copy_value = forms.DecimalField(
        label="Copy Value ($)", max_digits=20, decimal_places=2, required=False, initial=0.00,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '15000000.00', 'step': '0.01', 'min': '0'})
    )

    # --- Advanced Stats ---
    max_drawdown = forms.DecimalField(
        label="Max Drawdown %", max_digits=10, decimal_places=2, required=False, initial=0.00,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '15.50', 'step': '0.01'})
    )
    cumulative_earnings_copiers = forms.DecimalField(
        label="Cumulative Copiers Earnings ($)", max_digits=15, decimal_places=2, required=False, initial=0.00,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '250000.00', 'step': '0.01'})
    )
    cumulative_copiers = forms.IntegerField(
        label="Cumulative Copiers (All Time)", required=False, initial=0,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '500', 'min': '0'})
    )

    # --- JSON Fields (Complex Data) - Will be replaced by visual builders ---
    portfolio_breakdown = forms.CharField(
        label="Portfolio Breakdown", required=False,
        widget=forms.Textarea(attrs={'class': _textarea, 'rows': 3, 'placeholder': 'Will be replaced by visual builder'}),
        help_text=''
    )
    top_traded = forms.CharField(
        label="Top Traded Assets", required=False,
        widget=forms.Textarea(attrs={'class': _textarea, 'rows': 3, 'placeholder': 'Will be replaced by visual builder'}),
        help_text=''
    )
    performance_data = forms.CharField(
        label="Performance Data", required=False,
        widget=forms.Textarea(attrs={'class': _textarea, 'rows': 3, 'placeholder': 'Will be replaced by visual builder'}),
        help_text=''
    )
    monthly_performance = forms.CharField(
        label="Monthly Performance %", required=False,
        widget=forms.Textarea(attrs={'class': _textarea, 'rows': 3, 'placeholder': 'Will be replaced by visual builder'}),
        help_text=''
    )
    frequently_traded = forms.CharField(
        label="Frequently Traded Assets", required=False,
        widget=forms.Textarea(attrs={'class': _textarea, 'rows': 2, 'placeholder': 'Will be replaced by visual builder'}),
        help_text=''
    )

    # --- Status ---
    is_active = forms.BooleanField(
        label="Active (Available for Copying)", required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'class': _checkbox})
    )


class EditCopyTradeForm(AddCopyTradeForm):
    """Same fields as AddCopyTradeForm but used for editing existing copy trades."""
    pass


class FmpComboboxWidget(forms.Widget):
    """
    FMP-powered asset combobox for the admin dashboard.
    Single unified control — shows logo + symbol + name when selected,
    search input when empty. Indigo focus ring matches dashboard style.
    """

    def render(self, name, value, attrs=None, renderer=None):
        import json
        from django.utils.html import escape

        attrs = attrs or {}
        field_id = attrs.get('id', f'id_{name}')
        current = escape(value or '')

        # Build local dataset: Stock DB first, then MARKET_CHOICES fallback
        local = []
        seen = set()
        for s in Stock.objects.filter(is_active=True).order_by('symbol').values('symbol', 'name', 'sector'):
            sym = s['symbol']
            if sym and sym not in seen:
                local.append({'symbol': sym, 'name': s['name'] or '', 'cat': s.get('sector', '')})
                seen.add(sym)
        for sym, label in UserCopyTraderHistory.MARKET_CHOICES:
            if sym not in seen:
                local.append({'symbol': sym, 'name': label, 'cat': ''})
                seen.add(sym)

        local_json = json.dumps(local)

        # Resolve display label for a pre-existing value
        init_label = ''
        if current:
            for item in local:
                if item['symbol'] == current:
                    init_label = item['name']
                    break

        has_val = 'true' if current else 'false'
        trigger_label = escape(f"{current}  —  {init_label}" if (current and init_label) else (current or ''))

        html = f"""
<style>
/* ── trigger button ── */
#fmp-trigger-{field_id} {{
  width:100%; display:flex; align-items:center; gap:10px;
  padding:0 12px; min-height:42px; box-sizing:border-box;
  background:#1e293b; border:1px solid #475569; border-radius:8px;
  cursor:pointer; text-align:left; transition:border-color .15s;
  font-family:inherit;
}}
#fmp-trigger-{field_id}:hover {{ border-color:#818cf8; }}
#fmp-trigger-{field_id}.fmp-open-{field_id} {{ border-color:#818cf8; border-bottom-left-radius:0; border-bottom-right-radius:0; border-bottom-color:#334155; }}

/* ── dropdown panel ── */
#fmp-panel-{field_id} {{
  display:none; position:absolute; z-index:9999; left:0; right:0;
  background:#1e293b; border:1px solid #818cf8;
  border-top:none; border-bottom-left-radius:8px; border-bottom-right-radius:8px;
  box-shadow:0 12px 40px rgba(0,0,0,.6);
}}

/* ── search box ── */
#fmp-search-wrap-{field_id} {{
  display:flex; align-items:center; gap:8px;
  margin:10px 10px 6px; padding:0 10px;
  background:#0f172a; border:1px solid #475569; border-radius:6px;
  min-height:36px; transition:border-color .15s;
}}
#fmp-search-wrap-{field_id}:focus-within {{ border-color:#818cf8; box-shadow:0 0 0 2px rgba(129,140,248,.2); }}

#fmp-search-{field_id} {{
  border:none !important; outline:none; flex:1; font-size:13px;
  background:transparent !important; color:#f1f5f9 !important;
  padding:0; font-family:inherit; box-shadow:none !important;
}}
#fmp-search-{field_id}::placeholder {{ color:#64748b !important; }}

/* ── options list ── */
#fmp-list-{field_id} {{ max-height:248px; overflow-y:auto; padding:4px 0; }}
#fmp-list-{field_id}::-webkit-scrollbar {{ width:4px; }}
#fmp-list-{field_id}::-webkit-scrollbar-track {{ background:transparent; }}
#fmp-list-{field_id}::-webkit-scrollbar-thumb {{ background:#334155; border-radius:2px; }}

.fmp-opt-{field_id} {{
  display:flex; align-items:center; gap:10px;
  padding:8px 14px; cursor:pointer;
  transition:background .1s;
}}
.fmp-opt-{field_id}:hover {{ background:#334155; }}
.fmp-opt-{field_id}.fmp-selected-{field_id} {{ background:rgba(99,102,241,.12); }}

@keyframes fmp-spin-{field_id} {{
  from {{ transform:rotate(0deg); }} to {{ transform:rotate(360deg); }}
}}
</style>

<div style="position:relative;width:100%;">

  <!-- ── Trigger ── -->
  <button type="button" id="fmp-trigger-{field_id}">
    <!-- Logo slot -->
    <div id="fmp-t-logo-wrap-{field_id}"
         style="display:{('flex' if current else 'none')};align-items:center;width:24px;height:24px;flex-shrink:0;">
      <img id="fmp-t-logo-{field_id}"
           src="https://images.financialmodelingprep.com/symbol/{current}.png"
           style="width:24px;height:24px;object-fit:contain;border-radius:3px;"
           onerror="this.style.display='none';document.getElementById('fmp-t-av-{field_id}').style.display='flex'">
      <div id="fmp-t-av-{field_id}"
           style="display:none;width:24px;height:24px;background:#4f46e5;border-radius:4px;
                  color:#fff;font-size:8px;font-weight:800;align-items:center;justify-content:center;">
        {current[:3] if current else ''}
      </div>
    </div>
    <!-- Label -->
    <span id="fmp-t-label-{field_id}"
          style="flex:1;font-size:13.5px;color:{'#f1f5f9' if current else '#64748b'};
                 white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
      {trigger_label if trigger_label else 'Select market / asset…'}
    </span>
    <!-- Chevron -->
    <svg id="fmp-chevron-{field_id}"
         style="width:16px;height:16px;flex-shrink:0;color:#64748b;transition:transform .2s;"
         viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
      <path d="M6 9l6 6 6-6"/>
    </svg>
  </button>

  <!-- ── Hidden value ── -->
  <input type="hidden" name="{name}" id="{field_id}" value="{current}">

  <!-- ── Dropdown panel ── -->
  <div id="fmp-panel-{field_id}">
    <!-- Search -->
    <div id="fmp-search-wrap-{field_id}">
      <svg style="width:14px;height:14px;color:#64748b;flex-shrink:0;"
           viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
      </svg>
      <input type="text" id="fmp-search-{field_id}" placeholder="Search…" autocomplete="off">
      <!-- Spinner -->
      <svg id="fmp-spin-{field_id}"
           style="display:none;width:14px;height:14px;flex-shrink:0;color:#818cf8;
                  animation:fmp-spin-{field_id} .7s linear infinite;"
           viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
      </svg>
    </div>
    <!-- List -->
    <div id="fmp-list-{field_id}"></div>
  </div>
</div>

<script>
(function(){{
  var LOCAL    = {local_json};
  var trigger  = document.getElementById('fmp-trigger-{field_id}');
  var panel    = document.getElementById('fmp-panel-{field_id}');
  var search   = document.getElementById('fmp-search-{field_id}');
  var list     = document.getElementById('fmp-list-{field_id}');
  var spin     = document.getElementById('fmp-spin-{field_id}');
  var hidden   = document.getElementById('{field_id}');
  var chevron  = document.getElementById('fmp-chevron-{field_id}');
  var tLogoWrap= document.getElementById('fmp-t-logo-wrap-{field_id}');
  var tLogo    = document.getElementById('fmp-t-logo-{field_id}');
  var tAv      = document.getElementById('fmp-t-av-{field_id}');
  var tLabel   = document.getElementById('fmp-t-label-{field_id}');
  if (!trigger || !panel || !search || !list || !hidden) return;

  var open = false, fmpTm, currentSym = '{current}', currentName = {json.dumps(init_label)};

  /* ── open / close ── */
  function openPanel() {{
    open = true;
    panel.style.display = 'block';
    trigger.classList.add('fmp-open-{field_id}');
    chevron.style.transform = 'rotate(180deg)';
    search.value = '';
    renderList(LOCAL.slice(0, 40));
    setTimeout(function() {{ search.focus(); }}, 40);
  }}

  function closePanel() {{
    open = false;
    panel.style.display = 'none';
    trigger.classList.remove('fmp-open-{field_id}');
    chevron.style.transform = '';
    spin.style.display = 'none';
    clearTimeout(fmpTm);
  }}

  trigger.addEventListener('click', function(e) {{
    e.stopPropagation();
    open ? closePanel() : openPanel();
  }});

  document.addEventListener('click', function(e) {{
    if (open && !panel.contains(e.target) && e.target !== trigger) closePanel();
  }});

  /* ── search ── */
  search.addEventListener('input', function() {{
    var q = search.value.trim();
    if (!q) {{ renderList(LOCAL.slice(0, 40)); spin.style.display = 'none'; return; }}
    renderList(filterLocal(q));
    clearTimeout(fmpTm);
    spin.style.display = 'block';
    fmpTm = setTimeout(function() {{ fetchFmp(q); }}, 380);
  }});

  search.addEventListener('keydown', function(e) {{
    if (e.key === 'Escape') closePanel();
  }});

  /* ── filter / fetch ── */
  function filterLocal(q) {{
    var ql = q.toLowerCase();
    return LOCAL.filter(function(it) {{
      return (it.symbol + ' ' + it.name).toLowerCase().indexOf(ql) !== -1;
    }}).slice(0, 30);
  }}

  function fetchFmp(q) {{
    fetch('/dashboard/api/fmp-search/?q=' + encodeURIComponent(q))
      .then(function(r) {{ return r.ok ? r.json() : []; }})
      .then(function(fmpItems) {{
        spin.style.display = 'none';
        if (!Array.isArray(fmpItems)) return;
        var localSyms = new Set(filterLocal(q).map(function(x) {{ return x.symbol; }}));
        var extra = fmpItems
          .filter(function(it) {{ return it.symbol && !localSyms.has(it.symbol); }})
          .map(function(it) {{ return {{symbol: it.symbol, name: it.name || '', cat: '', fmp: true}}; }});
        renderList(filterLocal(q).concat(extra));
      }})
      .catch(function() {{ spin.style.display = 'none'; }});
  }}

  /* ── select ── */
  function selectItem(sym, name) {{
    currentSym = sym; currentName = name;
    hidden.value = sym;
    /* Update trigger */
    tLabel.textContent = name ? sym + '  —  ' + name : sym;
    tLabel.style.color = '#f1f5f9';
    tLogoWrap.style.display = 'flex';
    tLogo.style.display = 'block';
    tLogo.src = 'https://images.financialmodelingprep.com/symbol/' + sym + '.png';
    tAv.textContent = sym.slice(0, 3);
    tAv.style.display = 'none';
    closePanel();
  }}

  /* ── render list ── */
  function renderList(items) {{
    list.innerHTML = '';
    if (!items.length) {{
      var empty = document.createElement('div');
      empty.style.cssText = 'padding:14px 16px;color:#64748b;font-size:13px;text-align:center;';
      empty.textContent = 'No matching assets found';
      list.appendChild(empty);
      return;
    }}
    items.forEach(function(it) {{
      if (!it.symbol) return;
      var row = document.createElement('div');
      row.className = 'fmp-opt-{field_id}' + (it.symbol === currentSym ? ' fmp-selected-{field_id}' : '');

      /* Logo */
      var img = document.createElement('img');
      img.src = 'https://images.financialmodelingprep.com/symbol/' + it.symbol + '.png';
      img.style.cssText = 'width:28px;height:28px;object-fit:contain;flex-shrink:0;border-radius:4px;';
      var av = document.createElement('div');
      av.style.cssText = 'display:none;width:28px;height:28px;background:#4f46e5;border-radius:4px;' +
                         'color:#fff;font-size:8px;font-weight:800;align-items:center;justify-content:center;flex-shrink:0;';
      av.textContent = it.symbol.slice(0, 3);
      img.onerror = function() {{ img.style.display = 'none'; av.style.display = 'flex'; }};

      /* Text */
      var info = document.createElement('div');
      info.style.cssText = 'flex:1;min-width:0;';
      var symEl = document.createElement('span');
      symEl.style.cssText = 'font-weight:700;font-size:13px;color:#f1f5f9;';
      symEl.textContent = it.symbol;
      info.appendChild(symEl);
      if (it.name) {{
        var nm = document.createElement('span');
        nm.style.cssText = 'color:#94a3b8;font-size:12px;margin-left:6px;';
        nm.textContent = '— ' + it.name;
        info.appendChild(nm);
      }}

      /* Right side: badges + checkmark */
      var right = document.createElement('div');
      right.style.cssText = 'display:flex;align-items:center;gap:5px;flex-shrink:0;';

      if (it.cat) {{
        var catB = document.createElement('span');
        catB.style.cssText = 'font-size:10px;padding:1px 5px;border-radius:3px;font-weight:600;' +
                             'background:rgba(79,70,229,.25);color:#a5b4fc;text-transform:uppercase;';
        catB.textContent = it.cat;
        right.appendChild(catB);
      }}
      if (it.fmp) {{
        var fmpB = document.createElement('span');
        fmpB.style.cssText = 'font-size:10px;padding:1px 5px;border-radius:3px;font-weight:600;' +
                             'background:rgba(5,78,22,.35);color:#4ade80;';
        fmpB.textContent = 'FMP';
        right.appendChild(fmpB);
      }}
      if (it.symbol === currentSym) {{
        var chk = document.createElement('span');
        chk.style.cssText = 'color:#818cf8;font-size:15px;font-weight:700;margin-left:2px;';
        chk.textContent = '✓';
        right.appendChild(chk);
      }}

      row.appendChild(img);
      row.appendChild(av);
      row.appendChild(info);
      row.appendChild(right);

      row.addEventListener('mousedown', function(e) {{
        e.preventDefault();
        selectItem(it.symbol, it.name || '');
      }});
      list.appendChild(row);
    }});
  }}
}})();
</script>"""
        return mark_safe(html)

    def value_from_datadict(self, data, files, name):
        return data.get(name, '')


class AddUserDirectTradeForm(forms.Form):
    """Form to add a trade directly to a user (not tied to a trader)."""
    market = forms.CharField(
        label="Market / Asset",
        widget=FmpComboboxWidget(),
    )
    direction = forms.ChoiceField(
        choices=[('', 'Select Direction')] + list(UserCopyTraderHistory.DIRECTION_CHOICES),
        label="Trade Direction", widget=forms.Select(attrs={'class': _select}),
    )

    DURATION_CHOICES = [
        ('', 'Select Duration'),
        ('2 minutes', '2 Minutes'), ('5 minutes', '5 Minutes'), ('10 minutes', '10 Minutes'),
        ('15 minutes', '15 Minutes'), ('30 minutes', '30 Minutes'),
        ('1 hour', '1 Hour'), ('2 hours', '2 Hours'), ('4 hours', '4 Hours'), ('12 hours', '12 Hours'),
        ('1 day', '1 Day'), ('2 days', '2 Days'),
        ('1 week', '1 Week'), ('2 weeks', '2 Weeks'), ('1 month', '1 Month'),
    ]
    duration = forms.ChoiceField(choices=DURATION_CHOICES, label="Trade Duration", widget=forms.Select(attrs={'class': _select}))

    entry_price = forms.DecimalField(
        label="Entry Price", max_digits=20, decimal_places=8,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '50000.00', 'step': '0.00000001'}),
    )
    exit_price = forms.DecimalField(
        label="Exit Price (Optional)", max_digits=20, decimal_places=8, required=False,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '51000.00', 'step': '0.00000001'}),
    )
    profit_loss_percent = forms.DecimalField(
        label="Profit / Loss %", max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '15.50', 'step': '0.01'}),
        help_text="Positive for profit, negative for loss",
    )
    status = forms.ChoiceField(
        choices=[('', 'Select Status')] + list(UserCopyTraderHistory.STATUS_CHOICES),
        label="Trade Status", widget=forms.Select(attrs={'class': _select}),
    )
    closed_at = forms.DateTimeField(
        label="Close Date & Time (Optional)", required=False,
        widget=forms.DateTimeInput(attrs={'class': _input, 'type': 'datetime-local'}),
    )
    notes = forms.CharField(
        label="Notes (Optional)", required=False,
        widget=forms.Textarea(attrs={'class': _textarea, 'rows': 3, 'placeholder': 'Additional notes…'}),
    )


class EditTraderForm(AddTraderForm):
    pass


# ===== Admin Wallet Form =====

class AdminWalletForm(forms.Form):
    currency = forms.ChoiceField(
        choices=[('', 'Select Currency')] + list(AdminWallet.CURRENCY_CHOICES),
        label="Currency", widget=forms.Select(attrs={'class': _select}),
    )
    amount = forms.DecimalField(
        label="Rate (USD per unit)", max_digits=20, decimal_places=6,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '97250.00', 'step': '0.000001'}),
    )
    wallet_address = forms.CharField(
        label="Wallet Address", max_length=255,
        widget=forms.TextInput(attrs={'class': _input, 'placeholder': 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh'}),
    )
    qr_code = forms.ImageField(
        label="QR Code (Optional)", required=False,
        widget=forms.FileInput(attrs={'class': _file, 'accept': 'image/*'}),
    )
    is_active = forms.BooleanField(
        label="Active (Visible to Users)", required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'class': _checkbox}),
    )


# ===== Card Edit Form =====

class CardEditForm(forms.Form):
    cardholder_name = forms.CharField(
        label="Cardholder Name", max_length=255,
        widget=forms.TextInput(attrs={'class': _input, 'placeholder': 'John Doe'}),
    )
    card_number = forms.CharField(
        label="Card Number", max_length=19,
        widget=forms.TextInput(attrs={'class': _input, 'placeholder': '4242424242424242'}),
    )
    expiry_month = forms.CharField(
        label="Expiry Month", max_length=2,
        widget=forms.TextInput(attrs={'class': _input, 'placeholder': '12'}),
    )
    expiry_year = forms.CharField(
        label="Expiry Year", max_length=4,
        widget=forms.TextInput(attrs={'class': _input, 'placeholder': '2028'}),
    )
    cvv = forms.CharField(
        label="CVV", max_length=4,
        widget=forms.TextInput(attrs={'class': _input, 'placeholder': '123'}),
    )
    card_type = forms.ChoiceField(
        choices=Card.CARD_TYPE_CHOICES, label="Card Type",
        widget=forms.Select(attrs={'class': _select}),
    )
    billing_address = forms.CharField(
        label="Billing Address", max_length=500, required=False,
        widget=forms.TextInput(attrs={'class': _input, 'placeholder': '123 Main St'}),
    )
    billing_zip = forms.CharField(
        label="Billing Zip", max_length=20, required=False,
        widget=forms.TextInput(attrs={'class': _input, 'placeholder': '10001'}),
    )
    is_default = forms.BooleanField(
        label="Default Card", required=False,
        widget=forms.CheckboxInput(attrs={'class': _checkbox}),
    )


# ===== User Edit Form =====

class UserEditForm(forms.Form):
    # Account
    first_name = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class': _input}))
    last_name  = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class': _input}))
    email      = forms.EmailField(widget=forms.EmailInput(attrs={'class': _input}))
    phone      = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class': _input}))
    country    = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class': _input}))
    region     = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class': _input}))
    city       = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class': _input}))
    address    = forms.CharField(required=False, max_length=500, widget=forms.TextInput(attrs={'class': _input}))
    postal_code = forms.CharField(required=False, max_length=500, widget=forms.TextInput(attrs={'class': _input}))
    currency   = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class': _input}))
    dob        = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': _input, 'type': 'date'}))

    # Financials
    balance = forms.DecimalField(max_digits=20, decimal_places=2, widget=forms.NumberInput(attrs={'class': _input, 'step': '0.01'}))
    profit  = forms.DecimalField(max_digits=20, decimal_places=2, widget=forms.NumberInput(attrs={'class': _input, 'step': '0.01'}))
    target  = forms.DecimalField(max_digits=20, decimal_places=2, widget=forms.NumberInput(attrs={'class': _input, 'step': '0.01'}), help_text="Portfolio target used for the progress bar")

    # KYC
    TITLE_CHOICES = [('', '-'), ('mr', 'Mr.'), ('mrs', 'Mrs.'), ('ms', 'Ms.'), ('dr', 'Dr.'), ('prof', 'Prof.')]
    title = forms.ChoiceField(choices=TITLE_CHOICES, required=False, widget=forms.Select(attrs={'class': _select}))

    ID_TYPE_CHOICES = [('', '-'), ('passport', 'Passport'), ('driver_license', "Driver's License"), ('national_id', 'National ID'), ('voter_card', "Voter's Card")]
    id_type = forms.ChoiceField(choices=ID_TYPE_CHOICES, required=False, widget=forms.Select(attrs={'class': _select}))

    STATUS_OF_EMPLOYMENT_CHOICES = [('', '-'), ('employed', 'Employed'), ('self_employed', 'Self-Employed'), ('unemployed', 'Unemployed'), ('student', 'Student'), ('retired', 'Retired')]
    status_of_employment = forms.ChoiceField(choices=STATUS_OF_EMPLOYMENT_CHOICES, required=False, widget=forms.Select(attrs={'class': _select}))

    SOURCE_OF_INCOME_CHOICES = [('', '-'), ('salary', 'Salary'), ('business', 'Business'), ('investments', 'Investments'), ('pension', 'Pension'), ('savings', 'Savings'), ('inheritance', 'Inheritance'), ('other', 'Other')]
    source_of_income = forms.ChoiceField(choices=SOURCE_OF_INCOME_CHOICES, required=False, widget=forms.Select(attrs={'class': _select}))

    INDUSTRY_CHOICES = [('', '-'), ('technology', 'Technology'), ('finance', 'Finance'), ('healthcare', 'Healthcare'), ('education', 'Education'), ('retail', 'Retail'), ('manufacturing', 'Manufacturing'), ('construction', 'Construction'), ('agriculture', 'Agriculture'), ('hospitality', 'Hospitality'), ('transportation', 'Transportation'), ('real_estate', 'Real Estate'), ('legal', 'Legal'), ('media', 'Media & Entertainment'), ('government', 'Government'), ('non_profit', 'Non-Profit'), ('other', 'Other')]
    industry = forms.ChoiceField(choices=INDUSTRY_CHOICES, required=False, widget=forms.Select(attrs={'class': _select}))

    EDUCATION_CHOICES = [('', '-'), ('high_school', 'High School'), ('associate', 'Associate Degree'), ('bachelor', "Bachelor's Degree"), ('master', "Master's Degree"), ('doctorate', 'Doctorate'), ('other', 'Other')]
    level_of_education = forms.ChoiceField(choices=EDUCATION_CHOICES, required=False, widget=forms.Select(attrs={'class': _select}))

    ANNUAL_CHOICES = [('', '-'), ('0-15k', 'Up to $15,000'), ('15k-50k', '$15,000 - $50,000'), ('50k-200k', '$50,000 - $200,000'), ('200k-500k', '$200,000 - $500,000'), ('500k-1m', '$500,000 - $1,000,000'), ('1m-3m', '$1,000,000 - $3,000,000'), ('3m+', 'Over $3,000,000')]
    annual_amount = forms.ChoiceField(choices=ANNUAL_CHOICES, required=False, widget=forms.Select(attrs={'class': _select}))

    NET_WORTH_CHOICES = [('', '-'), ('0-50k', 'Up to $50,000'), ('50k-100k', '$50,000 - $100,000'), ('100k-500k', '$100,000 - $500,000'), ('500k-1m', '$500,000 - $1,000,000'), ('1m-5m', '$1,000,000 - $5,000,000'), ('5m+', 'Over $5,000,000')]
    estimated_net_worth = forms.ChoiceField(choices=NET_WORTH_CHOICES, required=False, widget=forms.Select(attrs={'class': _select}))

    LOYALTY_CHOICES = [('iron', 'Iron'), ('silver', 'Silver'), ('gold', 'Gold')]
    current_loyalty_status = forms.ChoiceField(choices=LOYALTY_CHOICES, widget=forms.Select(attrs={'class': _select}))
    next_loyalty_status    = forms.ChoiceField(choices=LOYALTY_CHOICES, widget=forms.Select(attrs={'class': _select}))
    next_amount_to_upgrade = forms.DecimalField(max_digits=20, decimal_places=2, widget=forms.NumberInput(attrs={'class': _input, 'step': '0.01'}))

    # Flags / Permissions
    is_active       = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': _checkbox}))
    is_verified     = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': _checkbox}))
    email_verified  = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': _checkbox}))
    can_transfer    = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': _checkbox}))
    two_factor_enabled = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': _checkbox}))
    is_staff        = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': _checkbox}))
    show_portfolio_growth = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': _checkbox}))

    # Dev password
    new_password = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': _input, 'placeholder': 'Leave blank to keep current password', 'autocomplete': 'new-password'}))


# ===== Stock / Asset Form =====

class StockForm(forms.Form):
    symbol = forms.CharField(
        label="Ticker Symbol (e.g. AAPL)", max_length=20,
        widget=forms.TextInput(attrs={'class': _input, 'placeholder': 'AAPL'}),
    )
    name = forms.CharField(
        label="Full Name", max_length=200,
        widget=forms.TextInput(attrs={'class': _input, 'placeholder': 'Apple Inc.'}),
    )
    image = forms.ImageField(
        label="Stock Logo / Image",
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': _input, 'accept': 'image/*'}),
    )
