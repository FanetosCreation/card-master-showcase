"""Card Master: what a sale leaves the owner, worked out one way everywhere.

Taken from the private repository (companion/profit.py). This is the pure
arithmetic; the private module also looks up each listing's cost and
measures the fee rate from the last 90 days of real eBay orders.

Used by the pricing analyst, the offer analyst, the price-approval
message on my phone and the 6 AM summary, so every one of them shows the
same number.

  fee rate   my own: eBay fees / item subtotal over my recent orders
  net        price x (1 - fee rate), an ESTIMATE before the sale
  profit     net - what I paid for the card (purchase + grading)

UNKNOWN IS NEVER ZERO: no fee rate or no cost gives None, not $0.
A missing cost that silently became $0 would make every sale look
like pure profit.
"""


def _pct(part, whole):
    return round(part * 100.0 / whole, 1) if part is not None and whole else None


def at_price(price_cents, cost_cents, rate):
    """Profit if the card sells at `price_cents`. Estimate."""
    fee = int(round(price_cents * rate)) if rate is not None and price_cents is not None else None
    net = price_cents - fee if fee is not None else None
    profit = net - cost_cents if net is not None and cost_cents is not None else None
    return {'priceCents': price_cents, 'feeCents': fee, 'netCents': net, 'profitCents': profit,
            'marginPct': _pct(profit, price_cents),          # profit / price
            'returnOnCostPct': _pct(profit, cost_cents)}     # profit / what I paid


def describe(profit_cents):
    """'+$4.36' / '−$27.50' / None, for text sent to my phone."""
    if profit_cents is None:
        return None
    sign = '+' if profit_cents >= 0 else '−'
    return '%s$%d.%02d' % ((sign,) + divmod(abs(int(profit_cents)), 100))


def card_cost_cents(card):
    """One card's full cost: what was paid plus grading. None when the
    paid amount is unknown; grading adds only when recorded."""
    paid = (card or {}).get('unitCostCents')
    if not (isinstance(paid, int) and paid > 0):
        return None
    grading = (card or {}).get('gradingCostCents')
    return paid + (grading if isinstance(grading, int) and grading > 0 else 0)


def listing_cost_cents(cards):
    """A listing can hold one card or a set. A set's cost is its cards'
    total, and unknown when ANY card's cost is unknown: a partial sum
    would hide a below-cost price."""
    costs = [card_cost_cents(c) for c in cards]
    if costs and all(v is not None for v in costs):
        return sum(costs)
    return None
