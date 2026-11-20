// Card Master: money in whole cents.
// Taken from the private repository (src/finance.js), unchanged apart from
// comments and the export line at the bottom.
//
// Every dollar amount in Card Master is an integer number of cents.
// Floating-point dollars drift (0.1 + 0.2 !== 0.3), and a business that
// reconciles thousands of sales cannot let pennies appear or vanish.

/** Add integer-cent amounts. */
function addCents(...vals) {
  return vals.reduce((sum, v) => sum + (Math.round(Number(v)) || 0), 0);
}

function sumCents(arr) {
  return addCents(...(arr || []));
}

/**
 * Split totalCents across the given non-negative weights using the
 * largest-remainder method: divide proportionally, round each share down,
 * then hand out the leftover pennies one at a time to the shares with the
 * largest fractional remainder. The parts always add up exactly to
 * totalCents. Used to spread a bulk lot's cost across its cards, or one
 * shipping label across the items in a package.
 *
 * If every weight is 0, it falls back to an even split so the total
 * still lands exactly.
 */
function allocateCents(totalCents, weights) {
  const total = Math.round(Number(totalCents) || 0);
  const n = (weights || []).length;
  if (n === 0) return [];

  const wSum = weights.reduce((s, w) => s + (Number(w) || 0), 0);
  const effectiveWeights = wSum > 0 ? weights : weights.map(() => 1);
  const effectiveSum = wSum > 0 ? wSum : n;

  const raw = effectiveWeights.map(w => (total * (Number(w) || 0)) / effectiveSum);
  const base = raw.map(r => Math.floor(r));
  const remainder = total - sumCents(base);

  const order = raw
    .map((r, i) => ({ i, frac: r - base[i] }))
    .sort((a, b) => b.frac - a.frac);

  // remainder is normally < n; the modulo guards against a stray
  // floating-point edge case so the loop never runs past the array.
  for (let k = 0; k < Math.abs(remainder); k++) {
    const idx = order[k % n].i;
    base[idx] += remainder > 0 ? 1 : -1;
  }
  return base;
}

/**
 * Profit on one order. All inputs are integer cents and positive amounts
 * (sellingFees: 110 means "$1.10 of fees"); the function does the
 * subtracting. Omitted fields count as 0.
 *
 *   profit = item sales + shipping charged
 *          − refunds − eBay fees − promoted-listing fees
 *          − shipping label − other direct costs − cost of the cards
 */
function orderNetProfit({
  itemSales = 0,
  shippingCharged = 0,
  refunds = 0,
  sellingFees = 0,
  promotedFees = 0,
  shippingLabel = 0,
  otherCosts = 0,
  cogs = 0,
} = {}) {
  return addCents(itemSales, shippingCharged) -
    addCents(refunds, sellingFees, promotedFees, shippingLabel, otherCosts, cogs);
}

module.exports = { addCents, sumCents, allocateCents, orderNetProfit };
