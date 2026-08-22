import { getOffers } from "../data/catalog";
import { getStore } from "./registry";
import type { ClickEvent, MerchantLead, PriceAlert } from "./types";

const clicks: ClickEvent[] = [];
const alerts: PriceAlert[] = [];
const leads: MerchantLead[] = [];

function id(prefix: string): string {
  return `${prefix}_${Math.random().toString(36).slice(2, 10)}`;
}

export function recordClick(offerId: string, source = "web"): ClickEvent | null {
  const offer = getOffers().find((item) => item.id === offerId);
  if (!offer) return null;
  const store = getStore(offer.storeId);
  const event: ClickEvent = {
    id: id("clk"),
    offerId: offer.id,
    productId: offer.productId,
    storeId: offer.storeId,
    priceNgn: offer.priceNgn,
    estimatedCommission: Math.round(offer.priceNgn * store.affiliateRate),
    source,
    createdAt: new Date().toISOString(),
  };
  clicks.unshift(event);
  return event;
}

export function recordAlert(input: Omit<PriceAlert, "id" | "createdAt">): PriceAlert {
  const alert: PriceAlert = {
    ...input,
    id: id("alrt"),
    createdAt: new Date().toISOString(),
  };
  alerts.unshift(alert);
  return alert;
}

export function recordLead(input: Omit<MerchantLead, "id" | "createdAt">): MerchantLead {
  const lead: MerchantLead = {
    ...input,
    id: id("lead"),
    createdAt: new Date().toISOString(),
  };
  leads.unshift(lead);
  return lead;
}

export function monetizationSnapshot() {
  const commission = clicks.reduce((sum, click) => sum + click.estimatedCommission, 0);
  const byStore = clicks.reduce<Record<string, { clicks: number; commission: number }>>(
    (acc, click) => {
      const current = acc[click.storeId] ?? { clicks: 0, commission: 0 };
      current.clicks += 1;
      current.commission += click.estimatedCommission;
      acc[click.storeId] = current;
      return acc;
    },
    {},
  );

  return {
    clicks: clicks.slice(0, 25),
    clickCount: clicks.length,
    estimatedCommission: commission,
    alerts: alerts.length,
    leads: leads.length,
    byStore,
    sponsoredFillRate: 0.64,
    plans: [
      {
        id: "starter" as const,
        name: "Starter",
        priceNgn: 45000,
        blurb: "One sponsored slot and a weekly click report.",
        features: ["1 category sponsored slot", "Affiliate link tracking", "Weekly email report"],
      },
      {
        id: "growth" as const,
        name: "Growth",
        priceNgn: 120000,
        blurb: "Own the comparison table when shoppers are ready to buy.",
        features: [
          "5 sponsored slots",
          "Featured store badge",
          "Category takeover 2 days/month",
          "WhatsApp lead forwarding",
        ],
      },
      {
        id: "intelligence" as const,
        name: "Intelligence",
        priceNgn: 350000,
        blurb: "Competitor prices as a feed — undercut alerts included.",
        features: [
          "Everything in Growth",
          "Price-match API",
          "Undercut alerts",
          "Share of search report",
        ],
      },
    ],
  };
}

export function outboundUrl(offerId: string, source = "web"): string | null {
  const offer = getOffers().find((item) => item.id === offerId);
  if (!offer) return null;
  const tagged = new URL(offer.url);
  tagged.searchParams.set("utm_source", "oja");
  tagged.searchParams.set("utm_medium", "affiliate");
  tagged.searchParams.set("utm_campaign", source);
  tagged.searchParams.set("click", offerId);
  return tagged.toString();
}
