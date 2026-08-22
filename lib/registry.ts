import { SEED_SITES } from "../data/directory";
import { PRODUCTS, addRuntimeOffers, basePriceFor, getOffers } from "../data/catalog";
import { classifySite, type SiteClassification } from "./classify-site";
import type {
  CategoryId,
  IntegrationStatus,
  Offer,
  SiteKind,
  Store,
} from "./types";

const sites: Store[] = structuredClone(SEED_SITES);

export type DirectoryFilters = {
  query?: string;
  kind?: string;
  status?: string;
  city?: string;
};

function hash(value: string): number {
  let total = 0;
  for (let i = 0; i < value.length; i += 1) total += value.charCodeAt(i) * (i + 1);
  return total;
}

function colorFromId(id: string): string {
  return `hsl(${hash(id) % 360} 48% 36%)`;
}

export function allSites(): Store[] {
  return sites;
}

export function liveStores(): Store[] {
  return sites.filter((site) => site.status === "live");
}

export function findSite(idOrHost: string): Store | undefined {
  const needle = idOrHost.toLowerCase().replace(/^www\./, "");
  return sites.find(
    (site) =>
      site.id === needle ||
      site.domain === needle ||
      site.homepage.replace(/^https?:\/\//, "") === needle,
  );
}

export function getStore(id: string): Store {
  const site = findSite(id);
  if (!site) throw new Error(`Unknown store ${id}`);
  return site;
}

export function directoryStats() {
  return {
    total: sites.length,
    live: sites.filter((site) => site.status === "live").length,
    feedReady: sites.filter((site) => site.status === "feed-ready").length,
    pending: sites.filter((site) => site.status === "pending").length,
    watchlist: sites.filter((site) => site.status === "watchlist").length,
    kinds: [...new Set(sites.map((site) => site.kind))].length,
  };
}

export function searchSites(filters: DirectoryFilters = {}): Store[] {
  const query = filters.query?.trim().toLowerCase() ?? "";
  return sites
    .filter((site) => {
      if (filters.kind && site.kind !== filters.kind) return false;
      if (filters.status && site.status !== filters.status) return false;
      if (filters.city && site.city.toLowerCase() !== filters.city.toLowerCase()) return false;
      if (!query) return true;
      const haystack = [
        site.name,
        site.domain,
        site.blurb,
        site.kind,
        site.city,
        site.platform,
        ...site.categories,
        ...site.ecommerceSignals,
      ]
        .join(" ")
        .toLowerCase();
      return query.split(/\s+/).every((token) => haystack.includes(token));
    })
    .sort((a, b) => {
      const rank: Record<IntegrationStatus, number> = {
        live: 0,
        "feed-ready": 1,
        pending: 2,
        watchlist: 3,
      };
      if (rank[a.status] !== rank[b.status]) return rank[a.status] - rank[b.status];
      return a.name.localeCompare(b.name);
    });
}

function generateOffers(store: Store): Offer[] {
  const marketplace = store.kind === "marketplace" || store.kind === "classifieds";
  const products = PRODUCTS.filter(
    (product) => marketplace || store.categories.includes(product.category as CategoryId),
  );
  const bias = -0.02 + ((hash(store.id) % 9) - 4) / 100;

  return products.slice(0, 16).map((product) => {
    const base = basePriceFor(product.id) ?? 100000;
    const price = Math.round(base * (1 + bias));
    return {
      id: `${product.id}-${store.id}-new`,
      productId: product.id,
      storeId: store.id,
      title: `${product.brand} ${product.model} — ${store.name} store`,
      priceNgn: price,
      previousPriceNgn: Math.round(price * 1.04),
      url: `${store.homepage.replace(/\/$/, "")}/catalog/${product.slug}`,
      condition: "new" as const,
      inStock: true,
      rating: 3.8,
      reviewCount: 20 + (hash(store.id + product.id) % 80),
      deliveryLagDays: store.nationwide ? 2 : 3,
      sellerName: `${store.name} Official`,
      updatedAt: new Date().toISOString(),
    };
  });
}

export type IntegrateResult = {
  classification: SiteClassification;
  site?: Store;
  offersAdded: number;
  alreadyLive: boolean;
};

export function classifyUrl(input: string): SiteClassification {
  const classification = classifySite(input);
  const existing = classification.host ? findSite(classification.host) : undefined;
  if (existing) {
    return {
      ...classification,
      suggestedId: existing.id,
      suggestedName: existing.name,
      isNigerianWeb: true,
      isEcommerce: true,
      accepted: true,
      confidence: Math.max(classification.confidence, 0.92),
      kind: existing.kind,
      categories: existing.categories,
      signals: [...new Set([...classification.signals, "in-directory"])],
      reasons: [`Already in the Oja directory as ${existing.name}`, ...classification.reasons],
      rejectReason: undefined,
    };
  }
  return classification;
}

export function integrateSite(input: string, name?: string): IntegrateResult {
  const classification = classifyUrl(input);
  const existing = classification.host ? findSite(classification.host) : findSite(classification.suggestedId);

  if (existing) {
    const alreadyLive = existing.status === "live";
    if (alreadyLive) {
      return { classification, site: existing, offersAdded: 0, alreadyLive: true };
    }
    existing.status = "live";
    existing.integrationMethod =
      existing.integrationMethod === "unassigned" ? "manual" : existing.integrationMethod;
    const offers = generateOffers(existing);
    addRuntimeOffers(offers);
    return { classification, site: existing, offersAdded: offers.length, alreadyLive: false };
  }

  if (!classification.accepted) {
    return { classification, offersAdded: 0, alreadyLive: false };
  }

  const store: Store = {
    id: classification.suggestedId,
    name: name?.trim() || classification.suggestedName,
    domain: classification.host,
    homepage: classification.homepage,
    color: colorFromId(classification.suggestedId),
    affiliateRate: 0.03,
    featured: false,
    blurb: "Submitted from the Nigerian web and classified as ecommerce.",
    kind: classification.kind as SiteKind,
    categories: classification.categories,
    city: "Nigeria",
    nationwide: true,
    platform: classification.host.includes("myshopify")
      ? "shopify"
      : classification.kind === "classifieds"
        ? "jiji"
        : "custom",
    status: "live",
    integrationMethod: "manual",
    ecommerceSignals: classification.signals,
    checkout: ["paystack"],
    addedAt: new Date().toISOString(),
    source: "submitted",
  };

  sites.push(store);
  const offers = generateOffers(store);
  addRuntimeOffers(offers);
  return { classification, site: store, offersAdded: offers.length, alreadyLive: false };
}

export function offersForSite(storeId: string): Offer[] {
  return getOffers().filter((offer) => offer.storeId === storeId);
}
