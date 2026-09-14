from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from django.utils.crypto import get_random_string
from .models import Stock, UserStockPosition, TradeHistory, Notification, TreemapStock, StockHistory

INDEX_NAMES = {
    'SPX': 'S&P 500', 'NDX': 'NASDAQ 100', 'DJI': 'Dow Jones',
    'RUT': 'Russell 2000', 'VIX': 'CBOE VIX',
}


def _fmt_volume(v):
    v = v or 0
    if v >= 1_000_000_000:
        return f"{v / 1_000_000_000:.1f}B"
    if v >= 1_000_000:
        return f"{v / 1_000_000:.1f}M"
    if v >= 1_000:
        return f"{v / 1_000:.1f}K"
    return str(v)


def _fmt_market_cap(mc):
    mc = mc or 0
    if mc >= 1_000_000_000_000:
        return f"{mc / 1_000_000_000_000:.2f}T"
    if mc >= 1_000_000_000:
        return f"{mc / 1_000_000_000:.1f}B"
    if mc >= 1_000_000:
        return f"{mc / 1_000_000:.1f}M"
    return str(mc)


@api_view(["GET"])
@permission_classes([AllowAny])
def list_treemap(request):
    """Dow Jones 30 snapshot for the Markets > Treemap tab, grouped by market-cap tier."""
    qs = TreemapStock.objects.filter(index='dow30').order_by('-market_cap')

    stocks_list = [
        {
            "symbol": s.symbol,
            "name": s.name,
            "price": str(s.price),
            "change_percent": str(s.change_percent),
            "market_cap": s.market_cap,
            "tier": s.tier,
        }
        for s in qs
    ]

    return Response({
        "success": True,
        "index": "dow30",
        "updated_at": qs.first().updated_at.isoformat() if qs.exists() else None,
        "stocks": stocks_list,
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def list_stocks(request):
    category = request.GET.get('category', 'all').lower()
    featured = request.GET.get('featured', '').lower() == 'true'

    qs = Stock.objects.exclude(category='indices').filter(is_active=True)
    if featured:
        qs = qs.filter(is_featured=True)
    if category != 'all':
        qs = qs.filter(category=category)
    qs = qs.order_by('-is_featured', 'symbol')

    histories = {h.symbol: h.prices for h in StockHistory.objects.filter(
        symbol__in=qs.values_list('symbol', flat=True)
    )}

    stocks_list = [
        {
            "id": stock.id,
            "symbol": stock.symbol,
            "name": stock.name,
            "logo_url": stock.logo_url,
            "domain": stock.domain,
            "category": stock.category,
            "sector": stock.sector,
            "exchange": stock.exchange,
            "description": stock.description,
            "price": str(stock.price),
            "change": str(stock.change),
            "change_percent": str(stock.change_percent),
            "is_positive_change": stock.is_positive_change,
            "is_featured": stock.is_featured,
            "volume": _fmt_volume(stock.volume),
            "market_cap": _fmt_market_cap(stock.market_cap),
            "pe": float(stock.pe) if stock.pe is not None else None,
            "eps": float(stock.eps),
            "high_52w": float(stock.high_52w),
            "low_52w": float(stock.low_52w),
            "div_yield": f"{float(stock.div_yield):.2f}%" if stock.div_yield else "—",
            "beta": float(stock.beta),
            "avg_vol": _fmt_volume(stock.avg_volume) if stock.avg_volume else "N/A",
            "sparkline": histories.get(stock.symbol, []),
        }
        for stock in qs
    ]

    # Market-overview index bar — independent of the category filter above,
    # since it's always shown regardless of which asset tab is selected.
    indices_list = []
    for idx in Stock.objects.filter(category='indices', is_active=True):
        positive = idx.change >= 0
        sign = "+" if positive else ""
        indices_list.append({
            "name": INDEX_NAMES.get(idx.symbol, idx.name),
            "value": f"{float(idx.price):,.2f}",
            "change": f"{sign}{float(idx.change):,.2f}",
            "change_pct": f"{sign}{float(idx.change_percent):.2f}%",
            "positive": positive,
        })

    return Response({"success": True, "stocks": stocks_list, "indices": indices_list})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def stock_detail(request, symbol):
    from app.fmp_client import fmp_get, get_profile

    symbol = symbol.upper()
    user = request.user

    # Fetch live quote from FMP
    try:
        quotes = fmp_get("/quote", {"symbol": symbol})
        if not isinstance(quotes, list) or not quotes:
            return Response({"success": False, "error": "Symbol not found"}, status=status.HTTP_404_NOT_FOUND)
        q = quotes[0]
    except Exception:
        return Response({"success": False, "error": "Unable to fetch market data"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    # Fetch company profile (sector, description, CEO, website, etc.)
    profile = get_profile(symbol)

    # Prefer a curated/admin-set logo on the Stock row; fall back to FMP's own logo CDN.
    curated_logo = Stock.objects.filter(symbol=symbol).values_list("logo_url", flat=True).first()

    price     = float(q.get("price") or 0)
    change    = float(q.get("change") or 0)
    change_pct = float(q.get("changePercentage") or q.get("changesPercentage") or 0)

    stock_data = {
        "symbol":           symbol,
        "name":             q.get("name") or profile.get("companyName") or symbol,
        "logo_url":         curated_logo or f"https://images.financialmodelingprep.com/symbol/{symbol}.png",
        "price":            f"{price:.2f}",
        "change":           f"{change:.2f}",
        "change_percent":   f"{change_pct:.2f}",
        "is_positive_change": change_pct >= 0,
        "open":             float(q.get("open") or 0),
        "previous_close":   float(q.get("previousClose") or 0),
        "day_high":         float(q.get("dayHigh") or 0),
        "day_low":          float(q.get("dayLow") or 0),
        "year_high":        float(q.get("yearHigh") or 0),
        "year_low":         float(q.get("yearLow") or 0),
        "market_cap":       q.get("marketCap") or profile.get("mktCap"),
        "volume":           q.get("volume"),
        "avg_volume":       q.get("avgVolume"),
        "eps":              q.get("eps"),
        "pe":               q.get("pe"),
        "exchange":         q.get("exchange") or profile.get("exchangeShortName"),
        "sector":           profile.get("sector"),
        "industry":         profile.get("industry"),
        "description":      profile.get("description"),
        "website":          profile.get("website"),
        "ceo":              profile.get("ceo"),
    }

    # User position if they own this stock
    user_position = None
    try:
        db_stock = Stock.objects.get(symbol=symbol, is_active=True)
        position = UserStockPosition.objects.get(user=user, stock=db_stock, is_active=True)
        user_position = {
            "id": position.id,
            "shares": str(position.shares),
            "average_buy_price": str(position.average_buy_price),
            "total_invested": str(position.total_invested),
            "current_value": str(position.current_value),
            "profit_loss": str(position.profit_loss),
            "profit_loss_percent": str(position.profit_loss_percent),
        }
    except (Stock.DoesNotExist, UserStockPosition.DoesNotExist):
        pass

    return Response({"success": True, "stock": stock_data, "user_position": user_position})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def buy_stock(request):
    """
    Buy stock shares
    """
    user = request.user
    symbol = request.data.get('symbol', '').strip().upper()
    shares = request.data.get('shares', '0')

    # Validate inputs
    try:
        shares = Decimal(shares)
        if shares <= 0:
            return Response({
                "success": False,
                "error": "Shares must be greater than 0"
            }, status=status.HTTP_400_BAD_REQUEST)
    except (ValueError, TypeError):
        return Response({
            "success": False,
            "error": "Invalid shares amount"
        }, status=status.HTTP_400_BAD_REQUEST)

    # Get stock
    try:
        stock = Stock.objects.get(symbol=symbol, is_active=True)
    except Stock.DoesNotExist:
        return Response({
            "success": False,
            "error": "Stock not found"
        }, status=status.HTTP_404_NOT_FOUND)

    # Calculate total cost
    total_cost = shares * stock.price

    # Check user balance
    if user.balance < total_cost:
        return Response({
            "success": False,
            "error": f"Insufficient balance. You need ${total_cost} but only have ${user.balance}",
            "required": str(total_cost),
            "current_balance": str(user.balance),
        }, status=status.HTTP_400_BAD_REQUEST)

    # Deduct from balance
    user.balance -= total_cost
    user.save(update_fields=['balance'])

    # Get or create position
    position, created = UserStockPosition.objects.get_or_create(
        user=user,
        stock=stock,
        is_active=True,
        defaults={
            'shares': shares,
            'average_buy_price': stock.price,
            'total_invested': total_cost,
        }
    )

    if not created:
        # Update existing position
        total_shares = position.shares + shares
        total_invested = position.total_invested + total_cost
        position.average_buy_price = total_invested / total_shares
        position.shares = total_shares
        position.total_invested = total_invested
        position.save(update_fields=['shares', 'average_buy_price', 'total_invested'])

    # Create trade history
    reference = f"BUY-{get_random_string(12).upper()}"
    TradeHistory.objects.create(
        user=user,
        stock=stock,
        trade_type='buy',
        shares=shares,
        price_per_share=stock.price,
        total_amount=total_cost,
        reference=reference,
    )

    # Create notification
    Notification.objects.create(
        user=user,
        type="trade",
        title="Stock Purchase Successful",
        message=f"You bought {shares} shares of {stock.symbol} for ${total_cost}",
        full_details=f"Your purchase of {shares} shares of {stock.name} ({stock.symbol}) at ${stock.price} per share has been completed. Total cost: ${total_cost}. Reference: {reference}",
        metadata={
            "stock": stock.symbol,
            "amount": f"${total_cost}",
            "shares": str(shares),
            "reference": reference,
        }
    )

    return Response({
        "success": True,
        "message": f"Successfully bought {shares} shares of {stock.symbol}",
        "reference": reference,
        "new_balance": str(user.balance),
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def sell_stock(request):
    """
    Sell stock shares
    """
    user = request.user
    symbol = request.data.get('symbol', '').strip().upper()
    shares = request.data.get('shares', '0')

    # Validate inputs
    try:
        shares = Decimal(shares)
        if shares <= 0:
            return Response({
                "success": False,
                "error": "Shares must be greater than 0"
            }, status=status.HTTP_400_BAD_REQUEST)
    except (ValueError, TypeError):
        return Response({
            "success": False,
            "error": "Invalid shares amount"
        }, status=status.HTTP_400_BAD_REQUEST)

    # Get stock
    try:
        stock = Stock.objects.get(symbol=symbol, is_active=True)
    except Stock.DoesNotExist:
        return Response({
            "success": False,
            "error": "Stock not found"
        }, status=status.HTTP_404_NOT_FOUND)

    # Get user position
    try:
        position = UserStockPosition.objects.get(user=user, stock=stock, is_active=True)
    except UserStockPosition.DoesNotExist:
        return Response({
            "success": False,
            "error": "You don't own any shares of this stock"
        }, status=status.HTTP_400_BAD_REQUEST)

    # Check if user has enough shares
    if position.shares < shares:
        return Response({
            "success": False,
            "error": f"You only have {position.shares} shares available",
            "available_shares": str(position.shares),
        }, status=status.HTTP_400_BAD_REQUEST)

    # Calculate sale proceeds
    sale_proceeds = shares * stock.price

    # Calculate profit/loss for this sale
    cost_basis = (position.total_invested / position.shares) * shares
    profit_loss = sale_proceeds - cost_basis

    # Add proceeds to balance
    user.balance += sale_proceeds
    user.save(update_fields=['balance'])

    # Update position
    remaining_shares = position.shares - shares
    if remaining_shares == 0:
        # Close position
        position.is_active = False
        position.save(update_fields=['is_active'])
    else:
        # Update position
        remaining_investment = position.total_invested - cost_basis
        position.shares = remaining_shares
        position.total_invested = remaining_investment
        position.save(update_fields=['shares', 'total_invested'])

    # Create trade history
    reference = f"SELL-{get_random_string(12).upper()}"
    TradeHistory.objects.create(
        user=user,
        stock=stock,
        trade_type='sell',
        shares=shares,
        price_per_share=stock.price,
        total_amount=sale_proceeds,
        profit_loss=profit_loss,
        reference=reference,
    )

    # Create notification
    profit_loss_text = f"profit of ${profit_loss}" if profit_loss >= 0 else f"loss of ${abs(profit_loss)}"
    Notification.objects.create(
        user=user,
        type="trade",
        title="Stock Sale Successful",
        message=f"You sold {shares} shares of {stock.symbol} for ${sale_proceeds} ({profit_loss_text})",
        full_details=f"Your sale of {shares} shares of {stock.name} ({stock.symbol}) at ${stock.price} per share has been completed. Sale proceeds: ${sale_proceeds}. {profit_loss_text.capitalize()}. Reference: {reference}",
        metadata={
            "stock": stock.symbol,
            "amount": f"${sale_proceeds}",
            "shares": str(shares),
            "profit_loss": str(profit_loss),
            "reference": reference,
        }
    )

    return Response({
        "success": True,
        "message": f"Successfully sold {shares} shares of {stock.symbol}",
        "reference": reference,
        "sale_proceeds": str(sale_proceeds),
        "profit_loss": str(profit_loss),
        "new_balance": str(user.balance),
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_positions(request):
    """
    Get all user's active stock positions
    """
    user = request.user

    positions = UserStockPosition.objects.filter(user=user, is_active=True).select_related('stock')

    positions_list = []
    for position in positions:
        stock = position.stock
        positions_list.append({
            "id": position.id,
            "stock": {
                "symbol": stock.symbol,
                "name": stock.name,
                "logo_url": stock.logo_url,
                "current_price": str(stock.price),
            },
            "shares": str(position.shares),
            "average_buy_price": str(position.average_buy_price),
            "total_invested": str(position.total_invested),
            "current_value": str(position.current_value),
            "profit_loss": str(position.profit_loss),
            "profit_loss_percent": str(position.profit_loss_percent),
            "is_positive": position.profit_loss >= 0,
        })

    return Response({
        "success": True,
        "positions": positions_list,
    })
