import type { CategoryId, SiteKind } from "./types";

export type SiteClassification = {
  host: string;
  homepage: string;
  suggestedId: string;
  suggestedName: string;
  isNigerianWeb: boolean;
  isEcommerce: boolean;
  accepted: boolean;
  confidence: number;
  kind: SiteKind;
  categories: CategoryId[];
  signals: string[];
  reasons: string[];
  rejectReason?: string;
};

const NG_HOST = /(\.ng$|\.com\.ng$|\.africa$)/i;
const NG_HINTS =
  /nigeria|naija|lagos|abuja|ibadan|kano|enugu|phcity|portharcourt|naira|paystack|flutterwave|kuda|oja/;
const ECOM_HINTS =
  /shop|store|mart|mall|market|buy|cart|checkout|commerce|boutique|pharmacy|supermarket|deal|gadget|phone|fashion|beauty|grocery|solar|auto|print|payporte|jumia|konga|jiji/;
const NOT_ECOM =
  /(^|\.)(bank|bet|sportybet|bet9ja|nairaland|pulse|guardian|vanguard|punchng|bbc|cnn|gov|edu|wiki|facebook|twitter|instagram|linkedin|youtube|tiktok)\b/;

const KIND_FROM_HOST: Array<[RegExp, SiteKind, CategoryId[]]> = [
  [/pharm|drug|health|medplus|netpharm/, "pharmacy", ["beauty"]],
  [/groc|food|supermart|pally|drinks|spar|hubmart|addide/, "grocery", ["groceries"]],
  [/phone|gadget|slot|kara|laptop|tech|geek/, "electronics", ["phones", "laptops", "audio"]],
  [/solar|energy|gen|inverter|power/, "power", ["power"]],
  [/fashion|wear|cloth|folklore/, "fashion", ["fashion"]],
  [/beauty|skin|tara|cosmetic/, "beauty", ["beauty"]],
  [/car|auto|cheki/, "auto", []],
  [/print/, "print", []],
  [/jiji|olx|classified/, "classifieds", ["phones", "laptops", "home"]],
  [/shopify|woocommerce|mystore/, "social-commerce", ["fashion", "beauty"]],
];

export function parseHost(input: string): { host: string; homepage: string } | null {
  const trimmed = input.trim();
  if (!trimmed) return null;
  try {
    const url = trimmed.includes("://") ? new URL(trimmed) : new URL(`https://${trimmed}`);
    const host = url.hostname.replace(/^www\./, "").toLowerCase();
    if (!host.includes(".")) return null;
    return { host, homepage: `${url.protocol}//${host}` };
  } catch {
    return null;
  }
}

export function idFromHost(host: string): string {
  return host
    .replace(/\.com\.ng$/, "")
    .replace(/\.(com|ng|africa|net|store)$/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 40);
}

export function classifySite(input: string): SiteClassification {
  const parsed = parseHost(input);
  const reasons: string[] = [];
  const signals: string[] = [];

  if (!parsed) {
    return {
      host: "",
      homepage: "",
      suggestedId: "",
      suggestedName: input,
      isNigerianWeb: false,
      isEcommerce: false,
      accepted: false,
      confidence: 0,
      kind: "marketplace",
      categories: [],
      signals,
      reasons: ["Could not parse a hostname"],
      rejectReason: "Enter a site like slot.ng or https://payporte.com",
    };
  }

  const { host, homepage } = parsed;
  const blob = `${host} ${input}`.toLowerCase();
  const isNigerianWeb = NG_HOST.test(host) || NG_HINTS.test(blob);
  const blocked = NOT_ECOM.test(host);
  const looksEcom = ECOM_HINTS.test(blob);

  if (isNigerianWeb) {
    reasons.push("Nigerian host or local checkout/city signal");
    signals.push("nigeria");
  }
  if (looksEcom) {
    reasons.push("Ecommerce wording in the host or URL");
    signals.push("ecommerce-host");
  }
  if (blocked) {
    reasons.push("Host looks like news, betting, social, or government");
  }

  const kindHit = KIND_FROM_HOST.find(([pattern]) => pattern.test(blob));
  const kind = kindHit?.[1] ?? (looksEcom ? "marketplace" : "social-commerce");
  const categories = kindHit?.[2] ?? ["phones", "home"];

  let confidence = 0.2;
  if (isNigerianWeb) confidence += 0.35;
  if (looksEcom) confidence += 0.3;
  if (kindHit) confidence += 0.15;
  if (blocked) confidence = Math.min(confidence, 0.2);

  const accepted = !blocked && isNigerianWeb && looksEcom && confidence >= 0.55;
  const isEcommerce = !blocked && looksEcom;

  return {
    host,
    homepage,
    suggestedId: idFromHost(host),
    suggestedName: idFromHost(host)
      .split("-")
      .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
      .join(" "),
    isNigerianWeb,
    isEcommerce,
    accepted,
    confidence: Math.min(1, confidence),
    kind,
    categories,
    signals,
    reasons,
    rejectReason: accepted
      ? undefined
      : blocked
        ? "This host is not classified as ecommerce"
        : !isNigerianWeb
          ? "Needs a Nigerian signal (.ng, Lagos, Paystack, etc.)"
          : !looksEcom
            ? "No ecommerce signal in the host — add shop/store/mart or a known retailer"
            : "Confidence too low to auto-integrate",
  };
}
