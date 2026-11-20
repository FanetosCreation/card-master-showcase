"""Run with: python -m pytest samples/
Test names follow the private suite (companion/tests/test_price_guard.py)."""
import pytest

from price_guard import GuardError, PriceGuard

COSTS = {'111': 4000, '222': None}   # listing 222: cost unknown


class Clock:
    def __init__(self):
        self.t = 1_000_000.0

    def __call__(self):
        return self.t


def guard(pin='2468'):
    clock = Clock()
    g = PriceGuard(COSTS.get, clock=clock)
    if pin:
        g.set_pin(pin)
    return g, clock


def code_of(fn):
    with pytest.raises(GuardError) as e:
        fn()
    return e.value.code


def test_no_pin_means_no_writes():
    g, _ = guard(pin=None)
    p = g.create_preview('111', 4500, 5000)
    assert code_of(lambda: g.authorize('111', 4500, 5000, '2468', p['approvalId'])) == 'pin_not_set'


def test_pin_is_hashed_not_stored():
    g, _ = guard()
    assert '2468' not in repr(vars(g))


def test_wrong_pin_locks_after_five_tries():
    g, clock = guard()
    p = g.create_preview('111', 4500, 5000)
    for _ in range(5):
        assert code_of(lambda: g.authorize('111', 4500, 5000, '0000', p['approvalId'])) == 'pin_wrong'
    assert code_of(lambda: g.authorize('111', 4500, 5000, '2468', p['approvalId'])) == 'locked'
    clock.t += 15 * 60 + 1
    assert g.authorize('111', 4500, 5000, '2468', p['approvalId'])['warnings'] == []


def test_preview_binds_exact_values_and_is_single_use():
    g, _ = guard()
    p = g.create_preview('111', 4500, 5000)
    assert code_of(lambda: g.authorize('111', 4400, 5000, '2468', p['approvalId'])) == 'preview_mismatch'
    assert code_of(lambda: g.authorize('999', 4500, 5000, '2468', p['approvalId'])) == 'preview_mismatch'
    g.authorize('111', 4500, 5000, '2468', p['approvalId'])
    assert code_of(lambda: g.authorize('111', 4500, 5000, '2468', p['approvalId'])) == 'preview_invalid'


def test_preview_expires():
    g, clock = guard()
    p = g.create_preview('111', 4500, 5000)
    clock.t += 30 * 60 + 1
    assert code_of(lambda: g.authorize('111', 4500, 5000, '2468', p['approvalId'])) == 'preview_expired'


def test_big_change_needs_acknowledge_and_failed_try_keeps_preview():
    g, _ = guard()
    p = g.create_preview('222', 3000, 5000)            # -40%
    assert [w['code'] for w in p['warnings']] == ['big_change']
    assert code_of(lambda: g.authorize('222', 3000, 5000, '2468', p['approvalId'])) == 'needs_acknowledge'
    assert g.authorize('222', 3000, 5000, '2468', p['approvalId'], acknowledge=True)['changePercent'] == -40.0


def test_below_cost_warns_but_unknown_cost_never_blocks():
    g, _ = guard()
    assert [w['code'] for w in g.create_preview('111', 3900, 4200)['warnings']] == ['below_cost']
    assert g.create_preview('222', 3900, 4200)['warnings'] == []


def test_acknowledge_must_be_literally_true():
    g, _ = guard()
    p = g.create_preview('111', 3900, 4200)
    assert code_of(lambda: g.authorize('111', 3900, 4200, '2468', p['approvalId'], acknowledge='yes')) == 'needs_acknowledge'


def test_invalid_prices_refused():
    g, _ = guard()
    for bad in (0, -5, 12.5, '4500', True):
        assert code_of(lambda: g.create_preview('111', bad, 5000)) == 'invalid_price'
