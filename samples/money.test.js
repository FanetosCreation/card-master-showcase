// Run with: node --test samples/money.test.js
// A small, standalone version of checks the private suite runs in the browser.
const test = require('node:test');
const assert = require('node:assert/strict');
const { allocateCents, orderNetProfit } = require('./money.js');

const sum = parts => parts.reduce((a, b) => a + b, 0);

test('a $100 lot split three ways adds back to exactly $100', () => {
  const parts = allocateCents(10000, [1, 1, 1]);
  assert.deepEqual(parts, [3334, 3333, 3333]);
  assert.equal(sum(parts), 10000);
});

test('cost follows market value: a $50 lot with a $90 card and two $5 cards', () => {
  const parts = allocateCents(5000, [9000, 500, 500]);
  assert.deepEqual(parts, [4500, 250, 250]);
});

test('awkward totals never gain or lose a penny', () => {
  for (const total of [1, 7, 999, 12345, 100001]) {
    const weights = [3, 7, 11, 13, 17];
    assert.equal(sum(allocateCents(total, weights)), total);
  }
});

test('all-zero weights fall back to an even split', () => {
  assert.deepEqual(allocateCents(10, [0, 0, 0]), [4, 3, 3]);
});

test('no cards, no parts', () => {
  assert.deepEqual(allocateCents(500, []), []);
});

test('order profit: a $60.00 card with $1.25 shipping charged', () => {
  const profit = orderNetProfit({
    itemSales: 6000, shippingCharged: 125,
    sellingFees: 816, shippingLabel: 85, cogs: 2160,
  });
  assert.equal(profit, 3064); // $30.64
});
