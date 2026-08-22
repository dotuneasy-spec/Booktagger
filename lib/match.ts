import { jaccard } from "./normalize";
import type { ExtractedProduct, MatchReason, ScoredMatch } from "./types";

const WEIGHTS = {
  brand: 0.28,
  family: 0.12,
  model: 0.22,
  storage: 0.12,
  ram: 0.08,
  capacity: 0.14,
  screen: 0.06,
  lexical: 0.16,
  condition: 0.04,
};

function overlap(a: string[], b: string[]): number {
  if (a.length === 0 || b.length === 0) return 0;
  const setB = new Set(b);
  const hits = a.filter((token) => setB.has(token)).length;
  return hits / Math.max(a.length, 1);
}

function sameBrand(query?: string, listing?: string): boolean {
  if (!query || !listing) return false;
  if (query === listing) return true;
  const apple = new Set(["apple", "iphone", "macbook"]);
  const xiaomi = new Set(["xiaomi", "redmi"]);
  return (
    (apple.has(query) && apple.has(listing)) ||
    (xiaomi.has(query) && xiaomi.has(listing))
  );
}

export function scoreMatch(
  query: ExtractedProduct,
  listing: ExtractedProduct,
): ScoredMatch {
  const reasons: MatchReason[] = [];
  let score = 0;

  if (query.brand) {
    if (sameBrand(query.brand, listing.brand)) {
      score += WEIGHTS.brand;
      reasons.push({ label: `Brand match: ${listing.brand}`, weight: WEIGHTS.brand });
    } else if (listing.brand && query.brand !== listing.brand) {
      score -= 0.2;
      reasons.push({ label: `Different brand (${listing.brand})`, weight: -0.2 });
    }
  }

  if (query.family) {
    if (query.family === listing.family) {
      score += WEIGHTS.family;
      reasons.push({ label: `Family match: ${query.family}`, weight: WEIGHTS.family });
    } else if (listing.family && query.family !== listing.family) {
      score -= 0.12;
      reasons.push({ label: `Different family (${listing.family})`, weight: -0.12 });
    }
  }

  if (query.modelTokens.length > 0) {
    const modelScore = overlap(query.modelTokens, listing.modelTokens);
    const weighted = modelScore * WEIGHTS.model;
    score += weighted;
    if (modelScore > 0) {
      reasons.push({
        label: `Model overlap ${Math.round(modelScore * 100)}%`,
        weight: weighted,
      });
    }
  }

  const specChecks: Array<{
    key: keyof Pick<
      ExtractedProduct,
      "storageGb" | "ramGb" | "capacityKva" | "screenInches"
    >;
    weight: number;
    label: string;
  }> = [
    { key: "storageGb", weight: WEIGHTS.storage, label: "Storage" },
    { key: "ramGb", weight: WEIGHTS.ram, label: "RAM" },
    { key: "capacityKva", weight: WEIGHTS.capacity, label: "Capacity" },
    { key: "screenInches", weight: WEIGHTS.screen, label: "Screen size" },
  ];

  for (const spec of specChecks) {
    const wanted = query[spec.key];
    const got = listing[spec.key];
    if (!wanted) continue;
    if (got === wanted) {
      score += spec.weight;
      reasons.push({ label: `${spec.label} match: ${wanted}`, weight: spec.weight });
    } else if (got && got !== wanted) {
      score -= spec.weight * 0.8;
      reasons.push({
        label: `${spec.label} mismatch (${got} vs ${wanted})`,
        weight: -spec.weight * 0.8,
      });
    }
  }

  const lexical = jaccard(query.tokens, listing.tokens);
  score += lexical * WEIGHTS.lexical;
  reasons.push({
    label: `Title similarity ${Math.round(lexical * 100)}%`,
    weight: lexical * WEIGHTS.lexical,
  });

  if (query.condition !== "new") {
    if (query.condition === listing.condition) {
      score += WEIGHTS.condition;
      reasons.push({
        label: `Condition match: ${query.condition}`,
        weight: WEIGHTS.condition,
      });
    } else {
      score -= 0.06;
      reasons.push({
        label: `Condition differs (${listing.condition})`,
        weight: -0.06,
      });
    }
  }

  return {
    score: Math.max(0, Math.min(1, score)),
    reasons: reasons.sort((a, b) => Math.abs(b.weight) - Math.abs(a.weight)),
  };
}

export function sameProduct(query: ExtractedProduct, listing: ExtractedProduct): boolean {
  const { score } = scoreMatch(query, listing);
  if (query.brand && listing.brand && !sameBrand(query.brand, listing.brand)) {
    return false;
  }
  if (query.capacityKva && listing.capacityKva && query.capacityKva !== listing.capacityKva) {
    return false;
  }
  if (query.storageGb && listing.storageGb && query.storageGb !== listing.storageGb) {
    return score >= 0.72;
  }
  return score >= 0.48;
}

export function clusterListings<T extends { id: string; extracted: ExtractedProduct }>(
  listings: T[],
  threshold = 0.55,
): T[][] {
  const parent = listings.map((_, index) => index);

  function find(index: number): number {
    if (parent[index] !== index) parent[index] = find(parent[index]);
    return parent[index];
  }

  function union(a: number, b: number) {
    const rootA = find(a);
    const rootB = find(b);
    if (rootA !== rootB) parent[rootB] = rootA;
  }

  for (let i = 0; i < listings.length; i += 1) {
    for (let j = i + 1; j < listings.length; j += 1) {
      const { score } = scoreMatch(listings[i].extracted, listings[j].extracted);
      if (score >= threshold && sameProduct(listings[i].extracted, listings[j].extracted)) {
        union(i, j);
      }
    }
  }

  const groups = new Map<number, T[]>();
  listings.forEach((listing, index) => {
    const root = find(index);
    const group = groups.get(root) ?? [];
    group.push(listing);
    groups.set(root, group);
  });

  return [...groups.values()].sort((a, b) => b.length - a.length);
}
