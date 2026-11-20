# AI agents

Card Master has a small team of AI agents that help run the business day to day. I talk to them from my phone over Telegram, often by voice.

**The rule above all others: AI recommends; the owner decides.** No agent can change a price, answer a Best Offer or message a buyer by itself.

## The team

| Agent | Job | Can it change anything? |
|---|---|---|
| **Manager** | Takes my requests, hands work to the right analyst, checks their reports, and sends me short summaries with numbered actions I can approve with a tap. | Only creates previews for me to approve. |
| **Pricing analyst** | Reviews active eBay listings, finds ones that aren't selling, compares them with recent sales and listings in the same condition, and recommends a price with the expected profit. | No. Read-only. |
| **Offer analyst** | Scores each buyer Best Offer as Accept, Counter at a price, or Decline, using what I paid, my actual eBay fee rate and the market. | No. Read-only. |

## What runs on a schedule

- **Daily summary (6 AM):** what sold, profit on those sales, what needs shipping, offers waiting, listings that just went stale, and how much the agents cost in usage. This is a plain script, not AI, so it costs nothing to run.
- **Offer watch:** a new Best Offer triggers the offer analyst and a recommendation on my phone.
- **Buyer message watch:** a new buyer message asks me how I'd like to respond, then drafts a reply for me to approve.
- **Weekly reprice check:** listings with no sale after 7+ days that weren't repriced in the last week, ranked by money at stake.

## Controls

- **Tap to approve.** Every price change, shipping fix, offer response and buyer reply is a preview until I approve it.
- **Read-only analysts.** The pricing and offer analysts can only read data.
- **Profit math is done by Card Master, not the AI.** Agents ask the system for profit at a given price instead of calculating it, so the numbers match the books.
- **No guessed numbers.** Estimates are labelled, and unknown costs are reported as unknown, never $0.
- **Business rules in plain language.** A shared playbook records my pricing rules (for example "a listing is stale after 30 days with no sale" and "price at the market, don't chase the cheapest listing"). My edits always win.
- **Cost watching.** The daily summary flags unusually heavy AI usage, and the agents are kept deliberately small.
- **Done means confirmed.** A change counts as done only after a fresh read from eBay shows it.
