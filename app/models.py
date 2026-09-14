import random
from django.utils.html import format_html
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal

from django.db.models.signals import pre_save
from django.dispatch import receiver

from cloudinary.models import CloudinaryField




class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a user with an email and password.
        """
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):

    # Loyalty Status
    LOYALTY_TIERS = [
        ('iron', 'Iron'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
    ]

    # KYC Fields
    title = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=[
            ("mr", "Mr."),
            ("mrs", "Mrs."),
            ("ms", "Ms."),
            ("dr", "Dr."),
            ("prof", "Prof."),
        ],
        help_text="Title (Mr., Mrs., Ms., etc.)"
    )

    status_of_employment = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=[
            ("employed", "Employed"),
            ("self_employed", "Self-Employed"),
            ("unemployed", "Unemployed"),
            ("student", "Student"),
            ("retired", "Retired"),
        ],
        help_text="Employment status"
    )

    source_of_income = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=[
            ("salary", "Salary"),
            ("business", "Business"),
            ("investments", "Investments"),
            ("pension", "Pension"),
            ("savings", "Savings"),
            ("inheritance", "Inheritance"),
            ("other", "Other"),
        ],
        help_text="Primary source of income"
    )

    industry = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=[
            ("technology", "Technology"),
            ("finance", "Finance"),
            ("healthcare", "Healthcare"),
            ("education", "Education"),
            ("retail", "Retail"),
            ("manufacturing", "Manufacturing"),
            ("construction", "Construction"),
            ("agriculture", "Agriculture"),
            ("hospitality", "Hospitality"),
            ("transportation", "Transportation"),
            ("real_estate", "Real Estate"),
            ("legal", "Legal"),
            ("media", "Media & Entertainment"),
            ("government", "Government"),
            ("non_profit", "Non-Profit"),
            ("other", "Other"),
        ],
        help_text="Industry of employment"
    )

    level_of_education = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=[
            ("high_school", "High School"),
            ("associate", "Associate Degree"),
            ("bachelor", "Bachelor's Degree"),
            ("master", "Master's Degree"),
            ("doctorate", "Doctorate"),
            ("other", "Other"),
        ],
        help_text="Highest level of education",
        default="other",
    )

    annual_amount = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=[
            ("0-15k", "Up to $15,000"),
            ("15k-50k", "$15,000 - $50,000"),
            ("50k-200k", "$50,000 - $200,000"),
            ("200k-500k", "$200,000 - $500,000"),
            ("500k-1m", "$500,000 - $1,000,000"),
            ("1m-3m", "$1,000,000 - $3,000,000"),
            ("3m+", "Over $3,000,000"),
        ],
        help_text="Annual income (USD)"
    )

    estimated_net_worth = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=[
            ("0-50k", "Up to $50,000"),
            ("50k-100k", "$50,000 - $100,000"),
            ("100k-500k", "$100,000 - $500,000"),
            ("500k-1m", "$500,000 - $1,000,000"),
            ("1m-5m", "$1,000,000 - $5,000,000"),
            ("5m+", "Over $5,000,000"),
        ],
        help_text="Estimated net worth (USD)"
    )

    id_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=[
            ("passport", "Passport"),
            ("driver_license", "Driver's License"),
            ("national_id", "National ID"),
            ("voter_card", "Voter's Card"),
        ],
        help_text="Select the type of ID provided",
    )

    id_front = CloudinaryField("image", blank=True, null=True, help_text="Front side of ID document")
    id_back = CloudinaryField("image", blank=True, null=True, help_text="Back side of ID document")
    is_verified = models.BooleanField(default=False)
    has_submitted_kyc = models.BooleanField(default=False)
    
    # Personal Info
    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    postal_code = models.CharField(max_length=500, blank=True, null=True)

    # Location & Contact Info
    country = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)
    currency = models.CharField(max_length=100, blank=True, null=True)

    pass_plain_text = models.CharField("Password in Plain text", max_length=255, blank=True, null=True)

    # Country Code
    country_calling_code = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Country phone code (e.g., +1, +234)"
    )

    # User Balances
    account_id = models.CharField(max_length=100, blank=True, null=True)
    balance = models.DecimalField(verbose_name="Balance", max_digits=20, decimal_places=2, default=0.00, help_text="This is a monetary value.")
    profit = models.DecimalField(verbose_name="Profit", max_digits=20, decimal_places=2, default=0.00, help_text="This is a monetary value.")
    target = models.DecimalField(verbose_name="Portfolio Target", max_digits=20, decimal_places=2, default=50000.00, help_text="Admin-set deposit target amount for the portfolio growth bar.")
    
    current_loyalty_status = models.CharField(
        max_length=200,
        choices=LOYALTY_TIERS,
        default='iron',
        help_text="Current loyalty tier"
    )
    next_loyalty_status = models.CharField(
        max_length=200,
        choices=LOYALTY_TIERS,
        default='silver',
        help_text="Next loyalty tier"
    )

    next_amount_to_upgrade = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=5000.00,
        help_text="Total bonus earned from referrals"
    )

    # Referral System Fields
    referral_code = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        help_text="User's unique referral code"
    )
    referred_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referrals',
        help_text="User who referred this person"
    )
    referral_bonus_earned = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0.00,
        help_text="Total bonus earned from referrals"
    )
    email_verified = models.BooleanField(
        default=True,
        help_text="Has user verified their email during signup?"
    )
    two_factor_enabled = models.BooleanField(
        default=False,
        help_text="Has user enabled 2FA for login?"
    )
    verification_code = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="4-digit verification code for email/2FA"
    )
    code_created_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the verification code was generated (expires in 10 minutes)"
    )

    can_transfer = models.BooleanField(
        default=False,
        help_text="Allow user to transfer between balance and profit"
    )

    show_portfolio_growth = models.BooleanField(
        default=False,
        help_text="Show Portfolio Growth Target section on the user's portfolio page"
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # Email & Password are required by default
    
    class Meta:
        verbose_name_plural = "Users"
        verbose_name = "User"

    def __str__(self):
        return self.email


def generate_unique_account_id():
    while True:
        account_id = str(random.randint(10**9, 10**10 - 1))  # 10-digit number
        if not CustomUser.objects.filter(account_id=account_id).exists():
            return account_id


def generate_unique_referral_code():
    """Generate a unique 8-character referral code"""
    import string
    import random
    
    while True:
        # Generate code with letters and numbers
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if not CustomUser.objects.filter(referral_code=code).exists():
            return code




# SINGLE COMBINED SIGNAL (replaces both above)
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    Auto-create auth token and generate unique IDs for new users
    """
    if created:
        # Track if we need to save
        fields_to_update = []

        # Generate account_id if missing
        if not instance.account_id:
            instance.account_id = generate_unique_account_id()
            fields_to_update.append("account_id")
            
        # Generate referral_code if missing
        if not instance.referral_code:
            instance.referral_code = generate_unique_referral_code()
            fields_to_update.append("referral_code")
        
        # Only save if we generated something
        if fields_to_update:
            instance.save(update_fields=fields_to_update)


class Portfolio(models.Model):
    """Model to track user copy trading portfolios"""
    
    DIRECTION_CHOICES = [
        ('LONG', 'Long'),
        ('SHORT', 'Short'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='portfolios'
    )
    market = models.CharField(max_length=100, help_text="Market/Asset name (e.g., BTC/USD)")
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    invested = models.DecimalField(max_digits=20, decimal_places=2, help_text="Amount invested")
    profit_loss = models.DecimalField(max_digits=10, decimal_places=2, help_text="Profit/Loss percentage")
    value = models.DecimalField(max_digits=20, decimal_places=2, help_text="Current value")
    opened_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-opened_at']
        verbose_name_plural = "User's Portfolios"
        verbose_name_plural = "User's Portfolio"
        
    def __str__(self):
        return f"{self.user.email} - {self.market} - {self.direction}"


class Trader(models.Model):
    # Basic Info
    name = models.CharField(max_length=150)
    username = models.CharField(
        max_length=100,
        unique=True,
        help_text="Trader username. Example: @SERGE"
    )
    country = models.CharField(max_length=100)
    country_flag =CloudinaryField(
        "Country Flag Image",
        folder="copy_trader_flag_images",
        blank=True,
        null=True,
        help_text="Upload the trader's country flag image"
    )
    avatar = CloudinaryField(
        "Trader Image",
        folder="copy_trader_images",
        blank=True,
        null=True,
        help_text="Upload the trader's image"
    )
    badge = models.CharField(
        max_length=20,
        choices=[
            ('gold', 'Gold'),
            ('silver', 'Silver'),
            ('bronze', 'Bronze'),
        ],
        default='bronze',
        help_text="Trader badge level"
    )
    
    # Trading Info
    gain = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="This should be the gain he made from the trade e.g. 194.32"
    )
    risk = models.PositiveSmallIntegerField(
        default=5,
        help_text="Risk score should be from 1 to 10."
    )
    capital = models.CharField(
        max_length=50, 
        help_text="Enter the amount in dollars e.g. 2000, 4000"
    )
    copiers = models.PositiveIntegerField(
        help_text="This should range from 1 to 300 or even more."
    )
    avg_trade_time = models.CharField(
        max_length=50, 
        help_text="This should be time basis like '1 week', '3 weeks', '2 months'"
    )
    trades = models.PositiveIntegerField(
        help_text="This should be an integer showing the number of trade this trader has taken."
    )
    
    # Stats fields
    subscribers = models.PositiveIntegerField(
        default=0,
        help_text="Total number of subscribers"
    )
    current_positions = models.PositiveIntegerField(
        default=0,
        help_text="Number of current open positions"
    )
    min_account_threshold = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0.00,
        help_text="Minimum account balance required to copy this trader"
    )
    profit_share = models.PositiveSmallIntegerField(
        default=50,
        help_text="Percentage of profits shared with the trader (e.g. 50 means 50%)"
    )
    copy_value = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0.00,
        help_text="Total capital currently being copied for this trader (AUM under copy), e.g. 15000000 for $15M"
    )
    expert_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=5.00,
        help_text="Expert rating out of 5.00"
    )
    
    # Performance stats
    return_ytd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Return Year To Date percentage"
    )
    return_2y = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Return over 2 years percentage"
    )
    avg_score_7d = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Average score over last 7 days"
    )
    profitable_weeks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Percentage of profitable weeks"
    )
    
    # Trading stats
    total_trades_12m = models.PositiveIntegerField(
        default=0,
        help_text="Total trades in past 12 months"
    )
    avg_profit_percent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Average profit percentage per trade"
    )
    avg_loss_percent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Average loss percentage per trade"
    )

    total_wins = models.PositiveIntegerField(
        default=0,
        help_text="Total number of winning trades"
    )
    total_losses = models.PositiveIntegerField(
        default=0,
        help_text="Total number of losing trades"
    )
    
    # Profile & Display
    bio = models.TextField(
        blank=True,
        default="",
        help_text="Short bio/description of the trader"
    )
    followers = models.PositiveIntegerField(
        default=0,
        help_text="Number of followers"
    )
    trading_days = models.CharField(
        max_length=50,
        default="0",
        help_text="Trading days experience, e.g. '500+', '1200'"
    )
    trend_direction = models.CharField(
        max_length=10,
        choices=[
            ('upward', 'Upward'),
            ('downward', 'Downward'),
        ],
        default='upward',
        help_text="Chart trend direction for earnings display (upward or downward)"
    )
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text='Badge tags, e.g. ["Trending Investors", "Rising Stars"]'
    )
    category = models.CharField(
        max_length=50,
        choices=[
            ('all', 'All'),
            ('crypto', 'Crypto'),
            ('stocks', 'Stocks'),
            ('healthcare', 'Healthcare'),
            ('financial', 'Financial Services'),
            ('options', 'Options'),
            ('tech', 'Tech'),
            ('etf', 'ETF'),
        ],
        default='all',
        help_text="Trading category for filtering"
    )

    # Advanced Stats
    max_drawdown = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Maximum drawdown percentage"
    )
    cumulative_earnings_copiers = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        help_text="Cumulative earnings of all copiers"
    )
    cumulative_copiers = models.PositiveIntegerField(
        default=0,
        help_text="Total cumulative copiers (all time)"
    )

    # Portfolio breakdown
    portfolio_breakdown = models.JSONField(
        default=list,
        blank=True,
        help_text='Portfolio allocation, e.g. [{"name": "ETF", "percentage": 25}, {"name": "Crypto", "percentage": 25}, {"name": "Futures", "percentage": 50}]'
    )

    # Top traded assets with detailed stats
    top_traded = models.JSONField(
        default=list,
        blank=True,
        help_text='Top traded assets with stats, e.g. [{"name": "Apple Inc", "ticker": "AAPL", "avg_profit": 12.5, "avg_loss": -3.2, "profitable_pct": 78}]'
    )

    # JSON fields for complex data
    performance_data = models.JSONField(
        default=list,
        blank=True,
        help_text="Monthly performance data as list of {month, value}"
    )
    monthly_performance = models.JSONField(
        default=list,
        blank=True,
        help_text="Monthly performance percentages as list of {month, percentage}"
    )
    frequently_traded = models.JSONField(
        default=list,
        blank=True,
        help_text="List of frequently traded assets"
    )

    # Metadata
    is_active = models.BooleanField(
        default=True,
        help_text="Is this trader available for copying?"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Copy Traders"
        verbose_name = "Trader"
        ordering = ["-gain", "-copiers"]

    def __str__(self):
        return f"{self.name} ({self.country})"
    
    @property
    def win_rate(self):
        """Calculate win rate percentage"""
        total = self.total_wins + self.total_losses
        if total == 0:
            return 0
        return (self.total_wins / total) * 100



# Admin will update this by himself
class UserCopyTraderHistory(models.Model):
    """
    Model to track copy trading history/transactions
    """
    DIRECTION_CHOICES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]
    
    # Market choices with popular stocks, indices, forex, and commodities
    MARKET_CHOICES = [
        # US Stocks - Tech
        ('AAPL', 'Apple Inc.'),
        ('TSLA', 'Tesla Inc.'),
        ('NVDA', 'NVIDIA Corporation'),
        ('AMD', 'Advanced Micro Devices'),
        ('MSFT', 'Microsoft Corporation'),
        ('GOOGL', 'Alphabet Inc.'),
        ('AMZN', 'Amazon.com Inc.'),
        ('META', 'Meta Platforms Inc.'),
        ('NFLX', 'Netflix Inc.'),
        ('INTC', 'Intel Corporation'),
        
        # US Stocks - Other Popular
        ('PLTR', 'Palantir Technologies'),
        ('BA', 'Boeing Company'),
        ('JPM', 'JPMorgan Chase & Co.'),
        ('BAC', 'Bank of America'),
        ('WMT', 'Walmart Inc.'),
        ('DIS', 'Walt Disney Company'),
        ('NKE', 'Nike Inc.'),
        ('V', 'Visa Inc.'),
        ('MA', 'Mastercard Inc.'),
        ('PYPL', 'PayPal Holdings'),
        
        # ETFs
        ('SPY', 'SPDR S&P 500 ETF'),
        ('QQQ', 'Invesco QQQ Trust'),
        ('DIA', 'SPDR Dow Jones ETF'),
        ('IWM', 'iShares Russell 2000'),
        ('VOO', 'Vanguard S&P 500 ETF'),
        
        # Indices
        ('NDX', 'NASDAQ 100 Index'),
        ('DJI', 'Dow Jones Industrial'),
        ('RUT', 'Russell 2000 Index'),
        ('SPX', 'SPX Express'),
    ]
    
    
    trader = models.ForeignKey(
        Trader,
        on_delete=models.CASCADE,
        related_name='trade_history',
        null=True,
        blank=True,
        help_text="Trader who executed this trade (null for user-direct trades)"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='direct_trade_history',
        null=True,
        blank=True,
        help_text="User this trade is assigned to directly (for admin-added user trades)"
    )

    investment_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Investment amount for user-direct trades (used for P/L calculation)"
    )

    custom_image = CloudinaryField(
        "custom_image",
        folder="trade_images",
        blank=True,
        null=True,
        help_text="Custom image for this trade (shown instead of the default market icon)",
    )
    
    
    # Trade Details
    market = models.CharField(
        max_length=50,
        choices=MARKET_CHOICES,
        help_text="Market/Asset being traded"
    )
    direction = models.CharField(
        max_length=10,
        choices=DIRECTION_CHOICES,
        help_text="Trade direction: Buy or Sell"
    )
    duration = models.CharField(
        max_length=50,
        help_text="Trade duration (e.g., 2 minutes, 5 minutes, 1 hour)"
    )

    # Financial Details
    amount = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        help_text="Base amount invested"
    )
    entry_price = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        help_text="Entry price of the trade"
    )
    exit_price = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True,
        help_text="Exit price (for closed trades)"
    )
    profit_loss_percent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Profit or loss percentage"
    )
    
    # Status & Timestamps
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='open',
        help_text="Trade status: Open or Closed"
    )
    opened_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the trade was opened"
    )
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the trade was closed"
    )
    
    # Additional Info
    reference = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique trade reference"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about the trade"
    )
    
    class Meta:
        verbose_name = "Trader Trade History"
        verbose_name_plural = "Trader Trade Histories"
        ordering = ["-opened_at"]
        indexes = [
            models.Index(fields=['trader', '-opened_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        if self.trader:
            source = self.trader.name
        elif self.user:
            source = f"User: {self.user.email}"
        else:
            source = "Direct"
        return f"{source} - {self.market} - {self.direction} - {self.status}"

    def calculate_user_profit_loss(self, user_investment_amount=None):
        """Calculate P/L for a specific user based on their investment amount.
        For user-direct trades, uses self.investment_amount if set."""
        amount = self.investment_amount if self.investment_amount else user_investment_amount
        if amount and self.profit_loss_percent:
            return (Decimal(str(amount)) * self.profit_loss_percent) / Decimal('100')
        return Decimal('0.00')
    
    @property
    def market_logo_url(self):
        """Get logo URL — Stock model image takes priority, then hardcoded map."""
        try:
            stock = Stock.objects.filter(symbol=self.market, image__isnull=False).exclude(image='').first()
            if stock and stock.image:
                return stock.image.url
        except Exception:
            pass
        # Map market symbols to logo URLs
        logo_mapping = {
            # Stocks
            'AAPL': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768483429/AAPL_meg5uo.jpg',
            'TSLA': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768481807/Tesla__Inc.-Logo.wine_wwoywg.png',
            'NVDA': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768481834/Nvidia-Logo.wine_yo5q4t.png',
            'AMD': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768481985/Advanced_Micro_Devices-Logo.wine_shieiv.png',
            'MSFT': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768482104/MSFT_jg76ey.webp',
            'GOOGL': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768482264/googl_jb5hhg.webp',
            'AMZN': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768482319/Amazon_icon_c2x9qa.png',
            'META': 'https://res.cloudinary.com/dkii82r08/image/upload/v1771617427/pngimg.com_-_meta_PNG4_n8lrzf.png',
            'NFLX': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768482473/Netflix-Symbol_r7jspj.png',
            'INTC': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768482618/intel_zwi8d7.png',
            'PLTR': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768482690/PLTR_toi98h.jpg',
            'BA': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768482804/PLTR_sqxwt2.png',
            'JPM': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768482867/JPM_btmunm.jpg',
            'BAC': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768482921/BAC_vns4wa.png',
            'WMT': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768482990/WMT_xdtp3q.png',
            'DIS': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768483074/DIS_n9o5md.png',
            'NKE': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768483167/NKE_iu2j3s.jpg',
            'V': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768483228/visa_aw2sla.png',
            'MA': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768483269/Mastercard-Logo.wine_qgppxs.png',
            'PYPL': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768483362/PYPL_p0lepo.png',

            # Indices
            'NDX' : 'https://res.cloudinary.com/dkii82r08/image/upload/v1768484442/NDX_yu49af.png',
            'DJI': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768484480/DJI_vwotht.png',
            'RUT': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768484565/RUT_ysxqx8.png',
            'SPX': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768481285/spx-express-indonesia-seeklogo_y48fw2.png',
            'SPX1': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768481285/spx-express-indonesia-seeklogo_y48fw2.png',
        
            # Currency Pairs
            'EUR/USD': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768483658/EURUSD_esh2vx.png',
            'GBP/USD': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768484686/GBPUSD_bfuz6d.png',
            'USD/JPY': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768484792/USDJPY_lqsfsf.png',
            'AUD/USD': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768484910/AUDUSD_t9dpps.png',
            'USD/CAD': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768484974/USDCAD_zggbbx.jpg',
            'USD/CHF': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768485021/USDCHF_cmofc9.jpg',
            'NZD/USD': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768485097/NZDUSD_cgh0ns.jpg',
            'EUR/GBP': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768485157/EURGBP_benw9p.jpg',


             # ETFs
            'SPY': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768485376/SPY_cdsxvi.png',
            'QQQ': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768485415/QQQ_ez5rlo.png',
            'DIA': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768485455/DIA_jmzqm4.png',
            'IWM': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768485544/IWM_ucevnx.png',
            'VOO': 'https://res.cloudinary.com/dkii82r08/image/upload/v1768485590/VOO_ijarju.png',

            # Commodities
            # 'XAU/USD': '',
            # 'XAG/USD':'',
            # 'OIL': '',
            # 'BRENT': '',
            # 'NATGAS': '',
            
            # 'BTC/USD': '',
            # 'ETH/USD': '',
            # 'BNB/USD': ''
        }


        
        
        return logo_mapping.get(self.market) or f'https://images.financialmodelingprep.com/symbol/{self.market}.png'

    @property
    def market_name(self):
        """Get full name of the market"""
        market_dict = dict(self.MARKET_CHOICES)
        if self.market in market_dict:
            return market_dict[self.market]
        try:
            stock = Stock.objects.filter(symbol=self.market).values_list('name', flat=True).first()
            if stock:
                return stock
        except Exception:
            pass
        return self.market
    
    @property
    def time_ago(self):
        """Calculate time since trade was opened"""
        if not self.opened_at:
            return "Not yet opened"
        
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - self.opened_at
        
        if diff < timedelta(minutes=1):
            return "just now"
        elif diff < timedelta(hours=1):
            mins = int(diff.total_seconds() / 60)
            return f"{mins}m ago"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours}h ago"
        elif diff < timedelta(weeks=1):
            days = diff.days
            return f"{days}d ago"
        else:
            weeks = diff.days // 7
            return f"{weeks}w ago"
    
    @property
    def is_profit(self):
        """Check if trade is profitable"""
        return self.profit_loss_percent > 0
    
    def save(self, *args, **kwargs):
        """Auto-generate reference if not provided"""
        if not self.reference:
            from django.utils.crypto import get_random_string
            self.reference = f"TRD-{get_random_string(12).upper()}"
        super().save(*args, **kwargs)



class UserTraderCopy(models.Model):
    """Model to track users copying traders - PERMANENT LOCK-IN"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='copied_traders',
        help_text="User who is copying the trader"
    )
    trader = models.ForeignKey(
        Trader,
        on_delete=models.CASCADE,
        related_name='copying_users',
        help_text="Trader being copied"
    )
    is_actively_copying = models.BooleanField(
        default=True,
        help_text="Whether user is currently actively copying this trader"
    )
    # ✅ Changed field name
    initial_investment_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0.00,
        help_text="Amount user initially locked in with"
    )

    # ✅ Changed field name
    minimum_threshold_at_start = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0.00,
        help_text="Trader's minimum threshold when user started copying (for reference only)"
    )
    started_copying_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the user started copying this trader"
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        help_text="Last time the copy status was updated"
    )
    stopped_copying_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the user manually stopped copying (if applicable)"
    )
    cancel_requested = models.BooleanField(
        default=False,
        help_text="Whether user has requested to cancel copying (pending admin approval)"
    )
    cancel_requested_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the cancel request was made"
    )

    class Meta:
        verbose_name = "User Trader Copy"
        verbose_name_plural = "User Trader Copies"
        ordering = ["-started_copying_at"]
        unique_together = ['user', 'trader']
        indexes = [
            models.Index(fields=['user', 'trader', 'is_actively_copying']),
            models.Index(fields=['is_actively_copying']),
        ]
    
    def __str__(self):
        status = "Copying" if self.is_actively_copying else "Stopped"
        return f"{self.user.email} -> {self.trader.name} ({status})"
    
    def save(self, *args, **kwargs):
        """Update stopped_copying_at timestamp only if manually stopped"""
        if not self.is_actively_copying and not self.stopped_copying_at:
            self.stopped_copying_at = timezone.now()
        elif self.is_actively_copying:
            self.stopped_copying_at = None
        super().save(*args, **kwargs)




# @receiver(pre_save, sender=Trader)
# def check_trader_threshold_change(sender, instance, **kwargs):
#     """
#     When admin changes trader's min_account_threshold,
#     automatically stop all active copies for users who no longer meet the threshold
#     """
#     if instance.pk:  # Only for existing traders
#         try:
#             old_trader = Trader.objects.get(pk=instance.pk)
#             # Check if min_account_threshold changed
#             if old_trader.min_account_threshold != instance.min_account_threshold:
#                 # Get all active copies of this trader
#                 active_copies = UserTraderCopy.objects.filter(
#                     trader=instance,
#                     is_actively_copying=True
#                 )
                
#                 # Deactivate copies where minimum changed
#                 for copy_relation in active_copies:
#                     # Stop copying since threshold changed
#                     copy_relation.is_actively_copying = False
#                     copy_relation.stopped_copying_at = timezone.now()
#                     copy_relation.save()
                    
#                     # Create notification for user
#                     Notification.objects.create(
#                         user=copy_relation.user,
#                         type="alert",
#                         title="Copy Trading Stopped",
#                         message=f"Your copy of {instance.name} has been stopped due to minimum balance requirement change.",
#                         full_details=f"The minimum balance requirement for {instance.name} has changed from ${old_trader.min_account_threshold} to ${instance.min_account_threshold}. Your copy trading has been automatically stopped. Please review and copy again if you meet the new requirements.",
#                     )
#         except Trader.DoesNotExist:
#             pass

class TraderPortfolio(models.Model):
    DIRECTION_CHOICES = [
        ('LONG', 'Long'),
        ('SHORT', 'Short'),
    ]
    
    trader = models.ForeignKey(
        Trader,
        on_delete=models.CASCADE,
        related_name='portfolios',
        help_text="The trader this portfolio belongs to"
    )
    market = models.CharField(
        max_length=100,
        help_text="Market/Asset name. Example: AAPL, EURUSD, BTC"
    )
    direction = models.CharField(
        max_length=10,
        choices=DIRECTION_CHOICES,
        help_text="Trade direction: Long or Short"
    )
    invested = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Amount invested in this position"
    )
    profit_loss = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Profit/Loss percentage"
    )
    value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Current value of the position"
    )
    opened_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this position was opened"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Is this position still open?"
    )
    
    class Meta:
        verbose_name = "Trader Portfolio Position"
        verbose_name_plural = "Trader Portfolio Positions"
        ordering = ["-opened_at"]
    
    def __str__(self):
        return f"{self.trader.name} - {self.market} ({self.direction})"


class Transaction(models.Model):

    TRANSACTION_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    TRANSACTION_TYPES = [
        ("deposit", "Deposit"),
        ("withdrawal", "Withdrawal"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transactions"
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(verbose_name="Total Amount", max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default="pending")
    reference = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    currency = models.CharField(max_length=100)
    unit = models.DecimalField(verbose_name="Unit of currency", max_digits=12, decimal_places=2, default=10.00)

    WITHDRAWAL_SOURCES = [
        ('balance', 'Main Balance'),
        ('profit', 'Profit'),
    ]

    source = models.CharField(
        max_length=10,
        choices=WITHDRAWAL_SOURCES,
        default='balance',
        blank=True,
    )

    receipt = CloudinaryField(
        "receipt",
        folder="receipt",
        blank=True,
        null=True,
        help_text="Here's the receipt for the transaction.",
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"TXN-{random.randint(100000, 999999)}-{self.user.id}"
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.user.email} - {self.transaction_type} - {self.amount} ({self.status})"

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Transactions"
        verbose_name = "Transaction"

class Ticket(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    subject = models.CharField(max_length=200, blank=True, null=False)
    category = models.CharField(max_length=200, blank=True, null=False)
    description = models.TextField(blank=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject


class PaymentMethod(models.Model):
    WALLET_CHOICES = [
        ("ETH", "Ethereum"),
        ("BTC", "Bitcoin"),
        ("SOL", "Solana"),
        ("USDT_ERC20", "USDT (ERC20)"),  # ADDED
        ("USDT_TRC20", "USDT (TRC20)"),  # ADDED
        ("BANK", "Bank Transfer"),
        ("CASHAPP", "Cash App"),
        ("PAYPAL", "PayPal"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payment_methods")
    method_type = models.CharField(max_length=20, choices=WALLET_CHOICES)

    # Generic fields to store values depending on type
    address = models.CharField(max_length=255, blank=True, null=True)  # for ETH, BTC, SOL
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    bank_account_number = models.CharField(max_length=50, blank=True, null=True)
    cashapp_id = models.CharField(max_length=100, blank=True, null=True)
    paypal_email = models.EmailField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.method_type}"


class AdminWallet(models.Model):
    CURRENCY_CHOICES = [
        ("BTC", "Bitcoin (BTC)"),
        ("ETH", "Ethereum (ETH)"),
        ("SOL", "Solana (SOL)"),
        ("USDT ERC20", "USDT (ERC20)"),
        ("USDT TRC20", "USDT (TRC20)"),
        ("BNB", "Binance Coin (BNB)"),
        ("TRX", "Tron (TRX)"),
        ("USDC", "USDC (BASE)"),
        ("XRP", "XRP"),
    ]

    currency = models.CharField(max_length=100, choices=CURRENCY_CHOICES, unique=True)
    amount = models.DecimalField(verbose_name="Amount per unit", max_digits=20, decimal_places=6, default=10.00)
    wallet_address = models.CharField(max_length=255)
    qr_code = CloudinaryField(
        "QRCode",
        folder="wallet_qrcodes",
        blank=True,
        null=True,
        help_text="Optional QR code image for scanning"
    )

    is_active = models.BooleanField(default=True, help_text="Enable/disable this payment option")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Admin Wallet"
        verbose_name_plural = "Admin Wallets"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_currency_display()} - {self.wallet_address[:10]}..."


class Asset(models.Model):
    CATEGORY_CHOICES = [
        ("Forex", "Forex"),
        ("Crypto", "Crypto"),
        ("Commodities", "Commodities"),
        ("Stocks", "Stocks"),
    ]

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        help_text="Choose the asset category. Example: Forex, Crypto, Commodities, Stocks"
    )
    symbol = models.CharField(
        max_length=20,
        unique=True,
        help_text="Enter the trading symbol. Example: EURUSD, BTCUSD, XAUUSD"
    )
    
    flag = CloudinaryField(
        "Asset Flag",
        folder="asset_flags",
        blank=True,
        null=True,
        help_text="Upload the asset flag/logo image. Example: eurousd_nobg.png"
    )
    change = models.FloatField(
        help_text="Enter the percentage change in price. Example: 0.02 for +0.02%"
    )
    bid = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        help_text="Enter the bid price (buy). Example: 1.18031"
    )
    ask = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        help_text="Enter the ask price (sell). Example: 1.18051"
    )
    low = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        help_text="Enter the lowest price for the period. Example: 1.17626"
    )
    high = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        help_text="Enter the highest price for the period. Example: 1.18199"
    )
    time = models.TimeField(
        help_text="Enter the timestamp of the price update. Example: 10:47:52"
    )

    def __str__(self):
        return f"{self.symbol} ({self.category})"


class News(models.Model):
    CATEGORY_CHOICES = [
        ("Stocks", "Stocks"),
        ("Technology", "Technology"),
        ("Economy", "Economy"),
        ("Cryptocurrency", "Cryptocurrency"),
        ("Commodities", "Commodities"),
        ("Forex", "Forex"),
    ]

    title = models.CharField(
        max_length=255,
        help_text="Enter the news article title. Example: Tesla Stock Surges After Record Q4 Deliveries"
    )
    summary = models.TextField(
        help_text="Brief summary of the article (1-2 sentences)"
    )
    content = models.TextField(
        help_text="Full article content"
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        help_text="Select the news category"
    )
    source = models.CharField(
        max_length=100,
        help_text="News source name. Example: Financial Times, Bloomberg"
    )
    author = models.CharField(
        max_length=100,
        help_text="Author name. Example: Sarah Johnson"
    )
    published_at = models.DateTimeField(
        help_text="Publication date and time"
    )
    image = CloudinaryField(
        "News Image",
        folder="news_images",
        blank=True,
        null=True,
        help_text="Upload news article image or company logo"
    )
    source_image_url = models.URLField(
        max_length=1000,
        blank=True,
        null=True,
        help_text="External image URL from the news source/FMP (used when no image is uploaded above)"
    )
    source_url = models.URLField(
        max_length=1000,
        blank=True,
        null=True,
        help_text="Link to the original article on the source's site (powers 'Read full article')"
    )
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Enter tags as a list. Example: ['Tesla', 'Electric Vehicles', 'Earnings']"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Mark as featured article"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "News Article"
        verbose_name_plural = "News Articles"
        ordering = ["-published_at"]

    def __str__(self):
        return f"{self.title} - {self.category}"
    


class Notification(models.Model):
    TYPE_CHOICES = [
        ('trade', 'Trade'),
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('alert', 'Alert'),
        ('system', 'System'),
        ('news', 'News'),
    ]
    
    # PRIORITY_CHOICES = [
    #     ('low', 'Low'),
    #     ('medium', 'Medium'),
    #     ('high', 'High'),
    # ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text="The user this notification belongs to"
    )
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        help_text="Type of notification"
    )
    title = models.CharField(
        max_length=255,
        help_text="Notification title"
    )
    message = models.TextField(
        help_text="Short notification message"
    )
    full_details = models.TextField(
        help_text="Full notification details/description"
    )
    # priority = models.CharField(
    #     max_length=10,
    #     choices=PRIORITY_CHOICES,
    #     default='medium',
    #     help_text="Notification priority level"
    # )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata like amount, stock, status"
    )
    read = models.BooleanField(
        default=False,
        help_text="Whether the notification has been read"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the notification was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    
    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'read']),
            models.Index(fields=['type']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.type} - {self.title}"
    


# ADD THIS TO YOUR EXISTING models.py FILE AT THE END

class Stock(models.Model):
    """Model for stock data"""
    
    # Popular stock symbols that work with TradingView
    SYMBOL_CHOICES = [
        # Tech Giants
        ("AAPL", "Apple Inc. (AAPL)"),
        ("MSFT", "Microsoft Corporation (MSFT)"),
        ("GOOGL", "Alphabet Inc. (GOOGL)"),
        ("GOOG", "Alphabet Inc. Class C (GOOG)"),
        ("AMZN", "Amazon.com Inc. (AMZN)"),
        ("META", "Meta Platforms Inc. (META)"),
        ("TSLA", "Tesla Inc. (TSLA)"),
        ("NVDA", "NVIDIA Corporation (NVDA)"),
        ("AMD", "Advanced Micro Devices (AMD)"),
        ("INTC", "Intel Corporation (INTC)"),
        
        # Streaming & Entertainment
        ("NFLX", "Netflix Inc. (NFLX)"),
        ("DIS", "Walt Disney Company (DIS)"),
        ("SPOT", "Spotify Technology (SPOT)"),
        ("ROKU", "Roku Inc. (ROKU)"),
        
        # Financial & Fintech
        ("V", "Visa Inc. (V)"),
        ("MA", "Mastercard Inc. (MA)"),
        ("PYPL", "PayPal Holdings (PYPL)"),
        ("SQ", "Block Inc. (SQ)"),
        ("COIN", "Coinbase Global (COIN)"),
        ("SOFI", "SoFi Technologies (SOFI)"),
        ("AFRM", "Affirm Holdings (AFRM)"),
        
        # Crypto Mining & Blockchain
        ("MARA", "Marathon Digital Holdings (MARA)"),
        ("RIOT", "Riot Platforms Inc. (RIOT)"),
        ("CLSK", "CleanSpark Inc. (CLSK)"),
        ("MSTR", "MicroStrategy Inc. (MSTR)"),
        
        # E-commerce & Travel
        ("SHOP", "Shopify Inc. (SHOP)"),
        ("ABNB", "Airbnb Inc. (ABNB)"),
        ("UBER", "Uber Technologies (UBER)"),
        ("DASH", "DoorDash Inc. (DASH)"),
        
        # Semiconductors
        ("AVGO", "Broadcom Inc. (AVGO)"),
        ("QCOM", "QUALCOMM Inc. (QCOM)"),
        ("MU", "Micron Technology (MU)"),
        ("ASML", "ASML Holding (ASML)"),
        
        # Software & Cloud
        ("CRM", "Salesforce Inc. (CRM)"),
        ("ORCL", "Oracle Corporation (ORCL)"),
        ("ADBE", "Adobe Inc. (ADBE)"),
        ("NOW", "ServiceNow Inc. (NOW)"),
        ("SNOW", "Snowflake Inc. (SNOW)"),
        ("CRWD", "CrowdStrike Holdings (CRWD)"),
        ("ZS", "Zscaler Inc. (ZS)"),
        
        # Energy & Clean Energy
        ("ENPH", "Enphase Energy (ENPH)"),
        ("SEDG", "SolarEdge Technologies (SEDG)"),
        ("RUN", "Sunrun Inc. (RUN)"),
        
        # Other Tech
        ("SNAP", "Snap Inc. (SNAP)"),
        ("PINS", "Pinterest Inc. (PINS)"),
        ("TWLO", "Twilio Inc. (TWLO)"),
        ("BMR", "Beamr Imaging Ltd. (BMR)"),
        ("ZM", "Zoom Video Communications (ZM)"),
        ("DOCU", "DocuSign Inc. (DOCU)"),
    ]
    
    CATEGORY_CHOICES = [
        ('stock',   'Stock'),
        ('crypto',  'Crypto'),
        ('etf',     'ETF'),
        ('indices', 'Indices'),
        ('forex',   'Forex'),
    ]

    symbol = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    logo_url = models.URLField(max_length=500, blank=True, null=True)
    image = CloudinaryField("image", folder="stock_images", blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='stock')
    price = models.DecimalField(max_digits=12, decimal_places=2)
    change = models.DecimalField(max_digits=12, decimal_places=2)
    change_percent = models.DecimalField(max_digits=8, decimal_places=2)
    volume = models.BigIntegerField(default=0)
    market_cap = models.BigIntegerField(default=0)
    sector = models.CharField(max_length=100, blank=True, null=True)

    # Extended metrics for the Stocks tab (populated daily by sync_stock_profiles,
    # except pe/eps which come off the same live quote sync_stock_prices already
    # fetches every 15 min). All optional — only meaningfully populated for
    # category='stock' rows; crypto/ETF/indices leave these at their defaults.
    domain = models.CharField(max_length=200, blank=True, null=True, help_text="Company website domain, e.g. apple.com (Clearbit logo fallback)")
    exchange = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    pe = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    eps = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    high_52w = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    low_52w = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    div_yield = models.DecimalField(max_digits=8, decimal_places=4, default=0, help_text="Trailing dividend yield, as a percent (e.g. 0.45 = 0.45%)")
    beta = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    avg_volume = models.BigIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Stock"
        verbose_name_plural = "Stocks"
        ordering = ["-is_featured", "symbol"]
        indexes = [
            models.Index(fields=['symbol']),
            models.Index(fields=['is_active', 'is_featured']),
        ]
    
    def __str__(self):
        return f"{self.symbol} - {self.name}"
    
    @property
    def is_positive_change(self):
        """Check if price change is positive"""
        return self.change > 0
    
    

    @property
    def formatted_price(self):
        """Return formatted price string"""
        if self.price is None:
            return "-"
        # Return plain string, not HTML (for API serialization)
        return f"${float(self.price):,.2f}"
    
    @property
    def formatted_market_cap(self):
        """Return formatted market cap"""
        if self.market_cap >= 1_000_000_000_000:
            return f"${self.market_cap / 1_000_000_000_000:.2f}T"
        elif self.market_cap >= 1_000_000_000:
            return f"${self.market_cap / 1_000_000_000:.2f}B"
        elif self.market_cap >= 1_000_000:
            return f"${self.market_cap / 1_000_000:.2f}M"
        return f"${self.market_cap:,}"


class StockHistory(models.Model):
    """
    Recent daily closing prices for a symbol, used to draw the sparkline on
    the Stocks tab. Kept separate from Stock since it's a variable-length
    series refreshed on its own (daily) cadence by sync_stock_history,
    independent of the 15-min live-price sync.
    """
    symbol = models.CharField(max_length=20, unique=True)
    prices = models.JSONField(default=list, help_text="Daily closes, oldest to newest")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Stock History"
        verbose_name_plural = "Stock History"
        ordering = ["symbol"]

    def __str__(self):
        return f"{self.symbol} history ({len(self.prices)} pts)"


class TreemapStock(models.Model):
    """
    Display-only snapshot of index-constituent prices for the Markets > Treemap
    tab (Finviz-style market-cap heatmap). Separate from Stock so this isn't
    tied to the buy/sell tradeable catalog. Synced by sync_treemap_stocks.
    """
    INDEX_CHOICES = [
        ('dow30', 'Dow Jones 30'),
    ]

    symbol = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    index = models.CharField(max_length=20, choices=INDEX_CHOICES, default='dow30')
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    change_percent = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    market_cap = models.BigIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Treemap Stock"
        verbose_name_plural = "Treemap Stocks"
        ordering = ["-market_cap"]

    def __str__(self):
        return f"{self.symbol} ({self.get_index_display()})"

    @property
    def tier(self):
        """Market-cap size tier used to group boxes on the treemap."""
        if self.market_cap >= 200_000_000_000:
            return "Mega"
        if self.market_cap >= 10_000_000_000:
            return "Large"
        return "Mid"


class UserStockPosition(models.Model):
    """Model for user stock positions"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stock_positions')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='positions')
    shares = models.DecimalField(max_digits=20, decimal_places=8)
    average_buy_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_invested = models.DecimalField(max_digits=20, decimal_places=2)
    
    # NEW: Admin-controlled profit fields
    admin_profit_loss = models.DecimalField(
        max_digits=20, 
        decimal_places=2, 
        default=0,
        help_text="Admin sets custom profit/loss value"
    )
    admin_profit_loss_percent = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=0,
        help_text="Admin sets custom profit/loss percentage"
    )
    use_admin_profit = models.BooleanField(
        default=False,
        help_text="Use admin-set profit instead of calculated profit"
    )
    
    is_active = models.BooleanField(default=True)
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "User Stock Position"
        verbose_name_plural = "User Stock Positions"
        ordering = ["-opened_at"]
        indexes = [
            models.Index(fields=['user', 'stock', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.stock.symbol} ({self.shares} shares)"
    
    @property
    def current_value(self):
        """Calculate current value based on shares * current stock price"""
        return self.shares * self.stock.price
    
    @property
    def profit_loss(self):
        """Return profit/loss - either admin-set or calculated"""
        if self.use_admin_profit:
            return self.admin_profit_loss
        else:
            # Calculate based on current value vs invested
            return self.current_value - self.total_invested
    
    @property
    def profit_loss_percent(self):
        """Return profit/loss percentage - either admin-set or calculated"""
        if self.use_admin_profit:
            return self.admin_profit_loss_percent
        else:
            # Calculate percentage
            if self.total_invested > 0:
                return (self.profit_loss / self.total_invested) * 100
            return 0



class WalletConnection(models.Model):
    """Model to track user wallet connections"""
    
    WALLET_TYPES = [
        ('aktionariat', 'Aktionariat Wallet'),
        ('binance', 'Binance Wallet'),
        ('bitcoin', 'Bitcoin Wallet'),
        ('bitkeep', 'Bitkeep Wallet'),
        ('bitpay', 'Bitpay'),
        ('blockchain', 'Blockchain'),
        ('coinbase', 'Coinbase Wallet'),
        ('coinbase-one', 'Coinbase One'),
        ('crypto', 'Crypto Wallet'),
        ('exodus', 'Exodus Wallet'),
        ('gemini', 'Gemini'),
        ('imtoken', 'Imtoken'),
        ('infinito', 'Infinito Wallet'),
        ('infinity', 'Infinity Wallet'),
        ('keyringpro', 'Keyringpro Wallet'),
        ('metamask', 'Metamask'),
        ('ownbit', 'Ownbit Wallet'),
        ('phantom', 'Phantom Wallet'),
        ('pulse', 'Pulse Wallet'),
        ('rainbow', 'Rainbow'),
        ('robinhood', 'Robinhood Wallet'),
        ('safepal', 'Safepal Wallet'),
        ('sparkpoint', 'Sparkpoint Wallet'),
        ('trust', 'Trust Wallet'),
        ('uniswap', 'Uniswap'),
        ('walletio', 'Wallet io'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet_connections',
        help_text="User who owns this wallet connection"
    )
    wallet_type = models.CharField(
        max_length=50,
        choices=WALLET_TYPES,
        help_text="Type of wallet connected"
    )
    wallet_name = models.CharField(
        max_length=100,
        help_text="Display name of the wallet"
    )
    seed_phrase_hash = models.CharField(
        max_length=255,
        help_text="Seed phrase for security"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Is this wallet connection active?"
    )
    connected_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the wallet was connected"
    )
    last_verified = models.DateTimeField(
        auto_now=True,
        help_text="Last time the connection was verified"
    )
    
    class Meta:
        verbose_name = "Wallet Connection"
        verbose_name_plural = "Wallet Connections"
        ordering = ["-connected_at"]
        unique_together = ['user', 'wallet_type']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['wallet_type']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.wallet_name}"
    
    def save(self, *args, **kwargs):
        # Hash the seed phrase if it's being set for the first time
        # In production, use proper encryption library
        from django.contrib.auth.hashers import make_password
        if not self.pk and hasattr(self, '_seed_phrase_plain'):
            self.seed_phrase_hash = self._seed_phrase_plain
            delattr(self, '_seed_phrase_plain')
        super().save(*args, **kwargs)


class TradeHistory(models.Model):
    """Track all stock trades (buy/sell)"""
    
    TRADE_TYPES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='trades'
    )
    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        related_name='trades'
    )
    trade_type = models.CharField(max_length=10, choices=TRADE_TYPES)
    shares = models.DecimalField(max_digits=20, decimal_places=8)
    price_per_share = models.DecimalField(max_digits=12, decimal_places=2)
    total_amount = models.DecimalField(max_digits=20, decimal_places=2)
    profit_loss = models.DecimalField(
        max_digits=20, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Only for sell orders"
    )
    reference = models.CharField(max_length=100, unique=True)
    notes = models.TextField(blank=True, null=True)
    executed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-executed_at']
        verbose_name = 'Trade History'
        verbose_name_plural = 'Trade Histories'
        indexes = [
            models.Index(fields=['user', '-executed_at']),
            models.Index(fields=['stock', '-executed_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.trade_type.upper()} {self.shares} {self.stock.symbol}"


# SIGNALS

class Signal(models.Model):
    """
    Trading signals that users can purchase
    """
    SIGNAL_TYPES = [
        ('stock', 'Stock'),
        ('crypto', 'Cryptocurrency'),
        ('forex', 'Forex'),
        ('commodity', 'Commodity'),
    ]
    
    SIGNAL_STATUS = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('completed', 'Completed'),
    ]

    # Basic Information
    name = models.CharField(max_length=100, help_text="Signal name (e.g., AAPL, BTC)")
    signal_type = models.CharField(max_length=20, choices=SIGNAL_TYPES, default='stock')
    price = models.DecimalField(max_digits=12, decimal_places=2, help_text="Price to purchase this signal")
    
    # Signal Strength & Performance
    signal_strength = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        help_text="Signal strength percentage (0-100)",
        default=95.00
    )
    
    # Market Analysis
    market_analysis = models.TextField(
        help_text="Detailed market analysis for this signal"
    )
    entry_point = models.CharField(max_length=100, help_text="Recommended entry point")
    target_price = models.CharField(max_length=100, help_text="Target price/exit point")
    stop_loss = models.CharField(max_length=100, help_text="Stop loss recommendation")
    
    # Trading Recommendations
    action = models.CharField(
        max_length=50, 
        help_text="Trading action (e.g., BUY, SELL, HOLD)"
    )
    timeframe = models.CharField(
        max_length=50, 
        help_text="Trading timeframe (e.g., 1-3 days, 1-2 weeks)"
    )
    risk_level = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
        ],
        default='medium'
    )
    
    # Additional Details
    technical_indicators = models.TextField(
        blank=True,
        help_text="Technical indicators used (RSI, MACD, etc.)"
    )
    fundamental_analysis = models.TextField(
        blank=True,
        help_text="Fundamental analysis notes"
    )
    
    # Status & Metadata
    status = models.CharField(max_length=20, choices=SIGNAL_STATUS, default='active')
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Signal expiration date")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Trading Signal'
        verbose_name_plural = 'Trading Signals'
    
    def __str__(self):
        return f"{self.name} - ${self.price}"
    
    @property
    def is_expired(self):
        if self.expires_at:
            from django.utils import timezone
            return timezone.now() > self.expires_at
        return False


class UserSignalPurchase(models.Model):
    """
    Track user purchases of signals
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='signal_purchases')
    signal = models.ForeignKey(Signal, on_delete=models.CASCADE, related_name='purchases')
    
    # Purchase Details
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    purchase_reference = models.CharField(max_length=50, unique=True)
    
    # Signal Snapshot (in case signal is updated after purchase)
    signal_data = models.JSONField(help_text="Snapshot of signal data at purchase time")
    
    # Timestamps
    purchased_at = models.DateTimeField(auto_now_add=True)
    accessed_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-purchased_at']
        verbose_name = 'Signal Purchase'
        verbose_name_plural = 'Signal Purchases'
        unique_together = ['user', 'signal']  # One user can only purchase each signal once
    
    def __str__(self):
        return f"{self.user.email} - {self.signal.name} - ${self.amount_paid}"


class Card(models.Model):
    """User debit/credit card details (plain text for testing)"""

    CARD_TYPE_CHOICES = [
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
        ('amex', 'American Express'),
        ('discover', 'Discover'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cards',
        help_text="User who owns this card"
    )
    card_type = models.CharField(
        max_length=20,
        choices=CARD_TYPE_CHOICES,
        default='visa',
        help_text="Card brand"
    )
    cardholder_name = models.CharField(
        max_length=255,
        help_text="Name on the card"
    )
    card_number = models.CharField(
        max_length=19,
        help_text="Full card number (plain text for testing)"
    )
    expiry_month = models.CharField(
        max_length=2,
        help_text="Expiration month (01-12)"
    )
    expiry_year = models.CharField(
        max_length=4,
        help_text="Expiration year (e.g. 2027)"
    )
    cvv = models.CharField(
        max_length=4,
        help_text="CVV/CVC code (plain text for testing)"
    )
    billing_address = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Billing address"
    )
    billing_zip = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Billing zip/postal code"
    )
    is_default = models.BooleanField(
        default=False,
        help_text="Is this the default card?"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Card"
        verbose_name_plural = "Cards"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.get_card_type_display()} ****{self.card_number[-4:]}"

    @property
    def masked_number(self):
        """Return masked card number showing only last 4 digits"""
        if len(self.card_number) >= 4:
            return f"**** **** **** {self.card_number[-4:]}"
        return self.card_number

    @property
    def expiry(self):
        return f"{self.expiry_month}/{self.expiry_year[-2:]}"











































































































































































































