# Oja

A Nigerian price-comparison engine. Search once, match the same product across Jumia, Konga, Jiji, Slot, Kara, and Pointek, then send the shopper out through a tracked buy link.

This repository is a working product concept: matching engine, sample Naija catalog, comparison UI, and the monetization rails (affiliate redirects, sponsored slots, alerts, merchant plans).

## Why this product

Nigerian ecommerce is split. The same Galaxy A55 is titled six different ways. Jiji is cheaper but UK used. Slot undercuts Jumia on phones. Generators are sold by kVA, groceries by carton. Generic global comparators miss all of that.

Oja’s job is **identity**, not keywords:

1. Normalize titles (`8/256` → RAM/storage, `tokunbo` → UK used).
2. Extract brand, family, model, GB, kVA, inches, condition.
3. Score and cluster listings that are the same SKU.
4. Rank offers and charge for the last click.

## Monetization

| Line | How it pays |
| --- | --- |
| Affiliate | `/go/:offerId` records the click and 302s to the store with UTM tags. Demo take-rates: Jumia 6%, Konga 5%, Slot 4%, Jiji 3%. |
| Sponsored slots | Paid placement above pure price sort, still labeled. |
| Alerts | Email is free. WhatsApp delivery is the premium wedge. |
| Intelligence | ₦350k/mo plan sells the matched price feed back to retailers. |

Merchant plans live on `/merchants`. Leads POST to `/api/leads`. Wire Paystack or Flutterwave when you take it live.

## Stack

- Next.js 16 App Router, TypeScript, Tailwind 4
- In-process catalog and matching (`lib/match.ts`, `lib/search.ts`)
- Sample catalog in `data/catalog.ts` — ready to swap for merchant feeds or a licensed crawler

The catalog is synthetic but priced and titled like Nigerian storefronts. Do not scrape stores from this app until you have a feed agreement or robots-compliant pipeline.

## Run

```bash
npm install
npm test
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

Useful queries:

- `Infinix Note 40 Pro 256` — should not collapse into Hot 40i
- `Firman 2.5kVA` — should not match Elepaq 3.5kVA
- `uk used iphone 13 128` — condition extracted, UK-used Jiji offer present
- `Oraimo FreePods 4` — multi-store spread

## API

- `GET /api/search?q=`
- `GET /api/suggest?q=`
- `POST /api/alerts`
- `POST /api/leads`
- `GET /api/stats`
- `GET /go/:offerId?src=`

## What to build next

- Persist clicks, alerts, and leads in Postgres
- Ingest official affiliate APIs (Jumia, Konga) plus consented seller CSVs
- Paystack subscriptions for merchant plans
- WhatsApp Cloud API for premium alerts
- Admin UI for sponsored inventory
