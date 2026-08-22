import type { Condition, ExtractedProduct } from "./types";
import { normalizeText, tokenize } from "./normalize";

export const BRANDS = [
  "samsung",
  "apple",
  "iphone",
  "tecno",
  "infinix",
  "itel",
  "xiaomi",
  "redmi",
  "oraimo",
  "sony",
  "hp",
  "dell",
  "lenovo",
  "macbook",
  "firman",
  "elepaq",
  "qasa",
  "luminous",
  "felicity",
  "hisense",
  "thermocool",
  "binatone",
  "nexus",
  "nivea",
  "nike",
  "adidas",
  "peak",
  "indomie",
  "dangote",
  "hollandia",
  "polystar",
] as const;

const FAMILIES: Record<string, string> = {
  galaxy: "galaxy",
  camon: "camon",
  spark: "spark",
  note: "note",
  hot: "hot",
  phantom: "phantom",
  iphone: "iphone",
  freepods: "freepods",
  inspiron: "inspiron",
  ideapad: "ideapad",
  revolution: "revolution",
  samba: "samba",
};

const MODEL_HINTS: Array<{ pattern: RegExp; brand: string; family?: string }> = [
  { pattern: /\ba(?:1[0-9]|[2-7]\d)\b/, brand: "samsung", family: "galaxy" },
  { pattern: /\biphone\b/, brand: "apple", family: "iphone" },
  { pattern: /\bcamon\b/, brand: "tecno", family: "camon" },
  { pattern: /\bspark\b/, brand: "tecno", family: "spark" },
  { pattern: /\bhot\b/, brand: "infinix", family: "hot" },
  { pattern: /\bfreepods\b/, brand: "oraimo", family: "freepods" },
];

const COLORS = [
  "black",
  "white",
  "blue",
  "navy",
  "green",
  "gold",
  "silver",
  "purple",
  "pink",
  "red",
  "grey",
  "gray",
  "titanium",
  "midnight",
];

function detectCondition(text: string): Condition {
  if (/\b(uk[\s-]?used|tokunbo)\b/.test(text)) return "uk-used";
  if (/\bfairly[\s-]?used\b/.test(text)) return "fairly-used";
  return "new";
}

function detectBrand(text: string): string | undefined {
  const sorted = [...BRANDS].sort((a, b) => b.length - a.length);
  for (const brand of sorted) {
    if (new RegExp(`\\b${brand}\\b`).test(text)) {
      if (brand === "apple" || brand === "iphone" || brand === "macbook") return "apple";
      if (brand === "redmi") return "xiaomi";
      return brand;
    }
  }
  const hinted = MODEL_HINTS.find((hint) => hint.pattern.test(text));
  return hinted?.brand;
}

function detectFamily(text: string): string | undefined {
  for (const [token, family] of Object.entries(FAMILIES)) {
    if (new RegExp(`\\b${token}\\b`).test(text)) return family;
  }
  const hinted = MODEL_HINTS.find((hint) => hint.pattern.test(text));
  return hinted?.family;
}

function numberBefore(text: string, unit: string): number | undefined {
  const match = text.match(new RegExp(`(\\d+(?:\\.\\d+)?)\\s*${unit}\\b`));
  return match ? Number(match[1]) : undefined;
}

function parseMemory(text: string): { ramGb?: number; storageGb?: number } {
  const ramKeyword = text.match(/(\d+)\s*gb\s*ram/);
  const romKeyword = text.match(/(\d+)\s*gb\s*rom/);
  const values = [...text.matchAll(/(\d+)\s*gb\b/g)].map((match) => Number(match[1]));
  const ramFromPair = values.find((value) => value <= 32);
  const storageFromPair = values.find((value) => value >= 64);

  return {
    ramGb: ramKeyword ? Number(ramKeyword[1]) : values.length >= 2 ? ramFromPair : undefined,
    storageGb: romKeyword
      ? Number(romKeyword[1])
      : storageFromPair ?? (values.length === 1 && values[0] >= 64 ? values[0] : undefined),
  };
}

export function extractProduct(input: string): ExtractedProduct {
  const normalized = normalizeText(input);
  const tokens = tokenize(input);
  const memory = parseMemory(normalized);
  const color = COLORS.find((item) => new RegExp(`\\b${item}\\b`).test(normalized));
  const brand = detectBrand(normalized);
  const family = detectFamily(normalized);
  const modelTokens = tokens.filter((token) => {
    if (token === brand || token === family) return false;
    if (COLORS.includes(token)) return false;
    if (/^\d+(gb|tb|kva|inch)$/.test(token)) return false;
    if (["new", "used", "uk", "fairly", "samsung"].includes(token)) return false;
    return /^(?:[a-z]*\d+[a-z]*|\d+[a-z]+|[a-z]{2,}|m\d)$/i.test(token);
  });

  return {
    brand,
    family,
    modelTokens: [...new Set(modelTokens)].slice(0, 8),
    storageGb: memory.storageGb,
    ramGb: memory.ramGb,
    capacityKva: numberBefore(normalized, "kva"),
    screenInches: numberBefore(normalized, "inch"),
    color,
    condition: detectCondition(normalized),
    tokens,
  };
}

export function productToExtracted(input: {
  brand: string;
  model: string;
  family?: string;
  title: string;
  attributes: {
    storageGb?: number;
    ramGb?: number;
    capacityKva?: number;
    screenInches?: number;
    color?: string;
  };
}): ExtractedProduct {
  const fromTitle = extractProduct(
    [
      input.brand,
      input.model,
      input.family,
      input.title,
      input.attributes.storageGb ? `${input.attributes.storageGb}gb` : "",
      input.attributes.ramGb ? `${input.attributes.ramGb}gb ram` : "",
      input.attributes.capacityKva ? `${input.attributes.capacityKva}kva` : "",
      input.attributes.screenInches ? `${input.attributes.screenInches}inch` : "",
      input.attributes.color ?? "",
    ].join(" "),
  );

  return {
    ...fromTitle,
    brand: input.brand.toLowerCase() === "apple" ? "apple" : input.brand.toLowerCase(),
    family: input.family?.toLowerCase() ?? fromTitle.family,
    storageGb: input.attributes.storageGb ?? fromTitle.storageGb,
    ramGb: input.attributes.ramGb ?? fromTitle.ramGb,
    capacityKva: input.attributes.capacityKva ?? fromTitle.capacityKva,
    screenInches: input.attributes.screenInches ?? fromTitle.screenInches,
    color: input.attributes.color?.toLowerCase() ?? fromTitle.color,
  };
}
