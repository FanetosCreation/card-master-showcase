"""Run with: python -m pytest samples/
The first three follow the private suite (companion/tests/test_profit.py), with made-up numbers."""
import profit


def test_profit_is_price_less_the_owners_fee_rate_less_cost():
    r = profit.at_price(6000, 7500, 0.15)
    assert r['feeCents'] == 900 and r['netCents'] == 5100 and r['profitCents'] == -2400
    assert r['marginPct'] == -40.0 and r['returnOnCostPct'] == -32.0


def test_unknown_cost_or_rate_is_none_never_zero():
    assert profit.at_price(5000, None, 0.15)['profitCents'] is None
    r = profit.at_price(5000, 3000, None)
    assert r['feeCents'] is None and r['netCents'] is None and r['profitCents'] is None


def test_describe_signs_money_for_the_owner():
    assert profit.describe(436) == '+$4.36'
    assert profit.describe(-2750) == '−$27.50'
    assert profit.describe(0) == '+$0.00'
    assert profit.describe(None) is None


def test_grading_is_part_of_the_cost():
    assert profit.card_cost_cents({'unitCostCents': 4000, 'gradingCostCents': 2499}) == 6499
    assert profit.card_cost_cents({'unitCostCents': 4000}) == 4000


def test_a_set_with_one_unknown_cost_is_unknown_not_a_partial_sum():
    known = [{'unitCostCents': 1000}, {'unitCostCents': 500}]
    assert profit.listing_cost_cents(known) == 1500
    assert profit.listing_cost_cents(known + [{'unitCostCents': None}]) is None
