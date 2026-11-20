# Controls and data rules

Card Master is built around a written list of rules that every change must keep. They work like internal controls: they protect the accuracy of inventory, revenue, cost and profit.

## Accuracy of the numbers

- **Money is stored in whole cents.** No rounding drift.
- **Unknown is never zero.** An unknown cost or fee is shown as unknown or pending, never a silent $0.
- **Actual fees only.** Profit uses the fees eBay actually charged. Until eBay confirms them, the fee is marked pending.
- **A verified paid order is the sale boundary.** Listing a card, linking it or receiving an offer is never counted as a sale.
- **Realized vs. unrealized** profit are kept separate.

## Inventory integrity

- **Purchase first.** Every card that is listed or sold must already exist in inventory. Syncing from a marketplace never creates inventory.
- **One ID per card, never reused.** IDs are created in one place only, and a deleted card's ID stays retired.
- **Exact matching.** An outside SKU matches a card exactly or not at all.

## Changes and corrections

- **Delete means reverse.** Deleting a record undoes everything it caused inside Card Master but keeps real sales, which are flagged to be relinked. See the [example decision record](decision-record-example.md).
- **No silent corrections.** Stored data is never rewritten or deleted without my review.
- **Disagreements are reported, not fixed quietly.** When a record and a live listing disagree, the agents list it under "Fix in Card Master" for me.

## Security and access

- **No secret reaches the browser.** API credentials live only in the local service, never in browser storage or backups.
- **Limited outside writes.** Card Master can write to eBay only to publish or edit a listing, change a price, answer a Best Offer or reply to a buyer message, and only with my consent. Test and live eBay accounts never cross.
- **Workspace isolation.** In the hosted version, database row-level security keeps each workspace's data separate, and tests prove it.
- **Approved hosts only.** The system talks only to the outside services it needs. No telemetry.

## Evidence

- Rules are written down, and significant decisions are recorded as decision records with context, decision and consequences.
- Automated tests pin each rule so a future change can't quietly break it.
