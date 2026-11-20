"""Card Master: the server-side gate for live eBay price changes.

TRIMMED from the private repository (companion/price_guard.py, ~570
lines). The rules below are the real ones. To keep the sample short and
runnable on its own, this version keeps state in memory instead of
files, leaves out the one-time code sent to my phone over Telegram, and
leaves out the append-only audit log.

Why it exists: an AI agent can suggest a price, and "the owner approved
it" used to be only a rule in the agent's instructions. This module makes
my approval something the server checks.

  * A PIN only I know. Stored as a salted scrypt hash, never in plain
    text. Five wrong tries lock price writes for 15 minutes. Until a PIN
    is set, writes are refused.
  * Previews need no PIN, so agents can make them, but a preview changes
    nothing. It binds ONE listing, ONE new price and the live price it was
    read at. It expires, and one write uses it up.
  * Warnings: a change of more than 30%, or a price under what I paid,
    needs an explicit acknowledge=True. Unknown cost never blocks.
"""
import hashlib
import hmac
import secrets
import time

MAX_FAILURES = 5
LOCK_SECONDS = 15 * 60
PREVIEW_TTL = 30 * 60
BIG_CHANGE_PERCENT = 30


class GuardError(Exception):
    def __init__(self, message, code, status=400):
        super().__init__(message)
        self.code, self.status = code, status


class PriceGuard:
    def __init__(self, cost_lookup, clock=time.time):
        self._cost = cost_lookup          # listing_id -> cents, or None when unknown
        self._now = clock
        self._pin = None                  # {'salt', 'hash'}; the PIN itself is never kept
        self._failures, self._locked_until = 0, 0
        self._previews = {}

    # ---------------- PIN ----------------

    @staticmethod
    def _hash(pin, salt):
        return hashlib.scrypt(pin.encode(), salt=bytes.fromhex(salt), n=2 ** 14, r=8, p=1).hex()

    def set_pin(self, new_pin, current_pin=None):
        if self._pin:
            self._check_pin(current_pin)
        if not (isinstance(new_pin, str) and new_pin.isdigit() and 4 <= len(new_pin) <= 64):
            raise GuardError('The PIN must be 4 to 64 digits.', 'invalid_pin')
        salt = secrets.token_hex(16)
        self._pin = {'salt': salt, 'hash': self._hash(new_pin, salt)}

    def _check_pin(self, pin):
        if not self._pin:
            raise GuardError('Set a PIN before any price can change.', 'pin_not_set', 403)
        if self._now() < self._locked_until:
            raise GuardError('Too many wrong PINs. Try again later.', 'locked', 423)
        if not hmac.compare_digest(self._hash(str(pin or ''), self._pin['salt']), self._pin['hash']):
            self._failures += 1
            if self._failures >= MAX_FAILURES:
                self._failures, self._locked_until = 0, self._now() + LOCK_SECONDS
            raise GuardError('That PIN is not right.', 'pin_wrong', 403)
        self._failures = 0

    # ---------------- warnings ----------------

    def assess(self, listing_id, current_cents, new_cents):
        warnings = []
        change = round((new_cents - current_cents) * 100.0 / current_cents, 1) if current_cents else None
        if change is not None and abs(change) > BIG_CHANGE_PERCENT:
            warnings.append({'code': 'big_change', 'message': 'This changes the price by %s%%.' % change})
        cost = self._cost(listing_id)
        if cost is not None and new_cents < cost:
            warnings.append({'code': 'below_cost',
                             'message': 'This is below what you paid ($%d.%02d).' % divmod(cost, 100)})
        return {'changePercent': change, 'costCents': cost, 'warnings': warnings}

    # ---------------- previews ----------------

    @staticmethod
    def _cents(value, name):
        if type(value) is not int or value <= 0 or value > 100000000:
            raise GuardError('%s must be a whole number of cents above zero.' % name, 'invalid_price')
        return value

    def create_preview(self, listing_id, price_cents, live_price_cents):
        """No PIN needed: a preview changes nothing. The caller has already
        read the live price from eBay and passes it in."""
        price_cents = self._cents(price_cents, 'priceCents')
        live_price_cents = self._cents(live_price_cents, 'livePriceCents')
        info = self.assess(listing_id, live_price_cents, price_cents)
        record = {'approvalId': 'PV-' + secrets.token_hex(6), 'state': 'pending',
                  'listingId': str(listing_id), 'priceCents': price_cents,
                  'livePriceCents': live_price_cents, 'expiresAt': self._now() + PREVIEW_TTL, **info}
        self._previews[record['approvalId']] = record
        return dict(record)

    def authorize(self, listing_id, price_cents, live_price_cents, pin, approval_id, acknowledge=False):
        """Everything a live price write must pass. Raises GuardError,
        otherwise uses up the preview and returns the assessment."""
        price_cents = self._cents(price_cents, 'priceCents')
        live_price_cents = self._cents(live_price_cents, 'livePriceCents')
        self._check_pin(pin)
        preview = self._previews.get(approval_id)
        if not preview or preview['state'] != 'pending':
            raise GuardError('That preview is unknown or already used.', 'preview_invalid', 409)
        if preview['expiresAt'] < self._now():
            raise GuardError('That preview expired. Ask for a new one.', 'preview_expired', 409)
        if (preview['listingId'], preview['priceCents'], preview['livePriceCents']) != \
                (str(listing_id), price_cents, live_price_cents):
            raise GuardError('This does not match what was previewed.', 'preview_mismatch', 409)
        # Re-assess now: the cost on record may have changed since the preview.
        info = self.assess(listing_id, live_price_cents, price_cents)
        if info['warnings'] and acknowledge is not True:   # literally True, not just "truthy"
            raise GuardError('Please confirm: ' + ' '.join(w['message'] for w in info['warnings']),
                             'needs_acknowledge', 409)
        preview['state'] = 'used'
        return info
