import { PRODUCTS, getOffers, offersForProduct } from "../data/catalog";
import { extractProduct, productToExtracted } from "./extract";
import { scoreMatch } from "./match";
import { getStore, liveStores } from "./registry";
import type {
  Offer,
  ProductSearchHit,
  RankedOffer,
  SearchResult,
} from "./types";

export type SearchFilters = {
  storeId?: string;
  condition?: string;
  category?: string;
  maxPrice?: number;
  inStockOnly?: boolean;
  sort?: "match" | "price" | "savings";
};

function rankOffers(productId: string, offers: Offer[]): RankedOffer[] {
  const inScope = offers.filter((offer) => offer.productId === productId);
  if (inScope.length === 0) return [];
  const highest = Math.max(...inScope.map((offer) => offer.priceNgn));
  const lowest = Math.min(
    ...inScope.filter((offer) => offer.inStock).map((offer) => offer.priceNgn),
    Math.min(...inScope.map((offer) => offer.priceNgn)),
  );

  return inScope
    .map((offer) => {
      const store = getStore(offer.storeId);
      return {
        ...offer,
        matchScore: 1,
        savingsVsHigh: Math.max(0, highest - offer.priceNgn),
        estimatedCommission: Math.round(offer.priceNgn * store.affiliateRate),
        isBestPrice: offer.inStock && offer.priceNgn === lowest,
      };
    })
    .sort((a, b) => {
      if (a.sponsored !== b.sponsored) return a.sponsored ? -1 : 1;
      if (a.inStock !== b.inStock) return a.inStock ? -1 : 1;
      return a.priceNgn - b.priceNgn;
    });
}

function applyOfferFilters(offers: Offer[], filters: SearchFilters): Offer[] {
  return offers.filter((offer) => {
    if (filters.storeId && offer.storeId !== filters.storeId) return false;
    if (filters.condition && offer.condition !== filters.condition) return false;
    if (filters.maxPrice && offer.priceNgn > filters.maxPrice) return false;
    if (filters.inStockOnly && !offer.inStock) return false;
    return true;
  });
}

export function searchProducts(query: string, filters: SearchFilters = {}): SearchResult {
  const extracted = extractProduct(query.trim() || "popular deals");
  const filteredOffers = applyOfferFilters(getOffers(), filters);

  const hits: ProductSearchHit[] = PRODUCTS.filter((product) => {
    if (filters.category && product.category !== filters.category) return false;
    return true;
  })
    .map((product) => {
      const productExtracted = productToExtracted(product);
      const match = query.trim()
        ? scoreMatch(extracted, productExtracted)
        : { score: product.popular || product.sponsored ? 0.7 : 0.45, reasons: [] };
      const offers = rankOffers(product.id, filteredOffers);
      const prices = offers.map((offer) => offer.priceNgn);
      return {
        product,
        score: match.score + (product.sponsored ? 0.04 : 0),
        reasons: match.reasons,
        offers,
        lowestPrice: prices.length ? Math.min(...prices) : 0,
        highestPrice: prices.length ? Math.max(...prices) : 0,
        storeCount: new Set(offers.map((offer) => offer.storeId)).size,
      };
    })
    .filter((hit) => hit.offers.length > 0 && (query.trim() ? hit.score >= 0.32 : true));

  hits.sort((a, b) => {
    if (filters.sort === "price") return a.lowestPrice - b.lowestPrice;
    if (filters.sort === "savings") {
      return b.highestPrice - b.lowestPrice - (a.highestPrice - a.lowestPrice);
    }
    if (a.product.sponsored !== b.product.sponsored) return a.product.sponsored ? -1 : 1;
    return b.score - a.score;
  });

  return {
    query: { raw: query, extracted },
    hits,
    totalOffers: hits.reduce((sum, hit) => sum + hit.offers.length, 0),
  };
}

export function getProductPage(slug: string) {
  const product = PRODUCTS.find((item) => item.slug === slug);
  if (!product) return null;
  const offers = rankOffers(product.id, offersForProduct(product.id));
  const extracted = productToExtracted(product);
  const reasons = scoreMatch(extracted, extractProduct(offers[0]?.title ?? product.title));
  return {
    product,
    offers,
    reasons: reasons.reasons,
    lowestPrice: Math.min(...offers.map((offer) => offer.priceNgn)),
    highestPrice: Math.max(...offers.map((offer) => offer.priceNgn)),
  };
}

export function suggest(query: string, limit = 6) {
  return searchProducts(query).hits.slice(0, limit).map((hit) => ({
    slug: hit.product.slug,
    title: hit.product.title,
    brand: hit.product.brand,
    lowestPrice: hit.lowestPrice,
    score: hit.score,
  }));
}

export function suggestSites(query: string, limit = 5) {
  return liveStores()
    .filter((store) => {
      if (!query.trim()) return true;
      const hay = `${store.name} ${store.domain} ${store.kind}`.toLowerCase();
      return query
        .toLowerCase()
        .split(/\s+/)
        .every((token) => hay.includes(token));
    })
    .slice(0, limit)
    .map((store) => ({
      id: store.id,
      name: store.name,
      domain: store.domain,
      status: store.status,
    }));
}
