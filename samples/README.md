# Code samples

Three pieces of Card Master's code, chosen because they enforce the rules that keep the business's numbers trustworthy. Each one comes with tests you can run.

```bash
node --test samples/money.test.js            # JavaScript, Node 18+
python -m pytest samples/                    # Python 3.8+, needs pytest
```

| File | What it handles | Origin |
|---|---|---|
| [money.js](money.js) | Splitting a lot's cost across cards to the exact cent, and profit per order | Unchanged from the private code |
| [profit.py](profit.py) | What a sale leaves me after eBay fees and card cost | The pure math, unchanged |
| [price_guard.py](price_guard.py) | The server-side check that a live eBay price change was approved by me | Trimmed to run on its own (see the note at the top of the file) |

I wrote the rules each piece enforces and the decisions behind them. AI coding agents wrote the code, and I checked every change against the automated tests.

---

## 1. Exact cost splitting: `money.js`

**What it handles.** I often buy cards in bulk lots: one price for many cards. To know the profit on any single card, each card needs its own cost. `allocateCents` splits the lot price across the cards in proportion to their value, and the shares **always add up exactly to what I paid**. The same function spreads one shipping label across the items in a package. `orderNetProfit` is the one formula for an order's profit: sales and shipping charged, minus refunds, fees, ads, label and card cost.

**How I came up with it.**
- **Store money as whole cents.** Dollar amounts stored as decimals drift, because a computer can't hold 0.1 exactly. Whole cents can't.
- **Splits must add back to the exact total.** If each card's share is rounded separately, the total can end up a few cents off what I really paid. Over hundreds of cards, my costs would stop matching my bank account. So I set this rule: a split always adds back to the exact total.
- **Hand out the leftover pennies fairly.** The largest-remainder method gives each leftover cent to the card that was closest to rounding up, so no card is systematically over- or under-costed.

## 2. One profit calculation: `profit.py`

**What it handles.** It estimates profit at any price: price minus my real eBay fee rate (measured from my last 90 days of orders), minus what I paid for the card, including grading. My pricing agent, my offer agent, the approval message on my phone and my 6 AM summary all call this same code, so they always show the same number.

**How I came up with it.**
- **I couldn't see what a price cut did to profit.** I approved three price cuts from a table that only showed a "below cost" flag. I asked for *"a profitability analyzer that checks what's truly going on and how these affect my profit at the end of the day. eBay is somewhere where we can keep volume, not fire sale."*
- **Code does the math; AI only judges.** Any calculation with one right answer lives in code. The AI agents ask the system for the number instead of working it out themselves, so the books and the agents never disagree.
- **Unknown is never zero.** If a card's cost isn't recorded, profit is reported as unknown. A missing cost that silently became $0 would make the sale look like pure profit. For a set listing, one card with an unknown cost makes the whole set's cost unknown, because a partial total would hide a below-cost price.

## 3. Approval enforced by the server: `price_guard.py`

**What it handles.** Before any price changes on a live eBay listing, the server checks:
- **The change was approved with my PIN.** The PIN is stored only as a salted hash, and five wrong tries lock price changes for 15 minutes.
- **It exactly matches a preview.** The preview names one listing, one new price and the live price it was read at. Previews expire after 30 minutes, and each one can be used only once.
- **Risky changes are confirmed.** A change of more than 30%, or a price below what I paid, needs an extra confirmation.

AI agents can create previews but can't approve them.

**How I came up with it.**
- **Approval was only an instruction.** My AI agents were told to wait for my OK, but nothing actually *stopped* a price change I hadn't approved. A business control can't depend on software following instructions, so I moved the check into the server, where the agents can't skip it.
- **Approve exactly what I saw.** A preview locks in the listing, the new price and the price it was read at. If the price on eBay moved in between, the approval no longer matches and is refused, so I never approve one thing and get another.
- **Unknown cost never blocks.** It also never hides a warning: a card with no recorded cost can still be repriced, but a known cost always triggers the below-cost check.
- **Done means confirmed.** Some price cuts I'd marked "done" turned out never to have reached eBay. Now a change only counts once a fresh read from eBay shows it. That part lives in the full private module.

The private version also sends me a one-time code by Telegram, so I can approve from my phone, and keeps an append-only log of every preview, approval, refusal and change.
