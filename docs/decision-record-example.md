# Example decision record: "Delete" means reverse what the record caused

*Card Master keeps 21 decision records like this one. This is a shortened version.*

**Status:** in force since November 2026.

## Context

Mistakes happen during intake. For example, a grading order might be imported twice, or attached to the wrong cards. I needed a way to undo them. But simply deleting the record would leave its inventory and costs behind, and deleting everything connected to it could erase sales that really happened.

## Decision

When I delete a record, Card Master **reverses everything that record caused inside Card Master** (the inventory it created, the expenses and cost allocations it posted, the links it made) as one all-or-nothing operation that I review first.

A reversal never:

- **Erases a real sale.** Sales and money actually received stay recorded. They are detached, marked "needs link" with unknown cost, and can be relinked.
- **Reaches outside Card Master.** No refund and no change on eBay or the grading company.
- **Reuses an ID.** Reversed card IDs stay retired.
- **Happens silently.** I see what will change and confirm, and an audit record keeps what was removed and why.

## Why

Leaving inventory and costs behind after a mistake makes every profit figure wrong. Erasing a real sale makes revenue wrong. Reversing internal effects while keeping external facts keeps both true.

## Consequences

- Cases the system can't reverse cleanly are refused rather than half-done, and each needs its own rule and tests before it's allowed.
- Backups keep the reversal records, since they hold the kept sales and retired IDs.
