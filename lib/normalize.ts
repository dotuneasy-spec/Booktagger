const ALIASES: Array<[RegExp, string]> = [
  [/\bi[\s-]?phone\b/g, "iphone"],
  [/\bgalaxy\b/g, "samsung galaxy"],
  [/\bredmi\b/g, "xiaomi redmi"],
  [/\bhaier[\s-]?thermocool\b/g, "thermocool"],
  [/\bsumec[\s-]?firman\b/g, "firman"],
  [/\bfirman\b/g, "firman"],
  [/\belepaq\b/g, "elepaq"],
  [/\bqasa\b/g, "qasa"],
  [/\btokunbo\b/g, "uk used"],
  [/\bukused\b/g, "uk used"],
  [/\bfairly[\s-]?used\b/g, "fairly used"],
  [/\bbrand[\s-]?new\b/g, "new"],
  [/\bsealed\b/g, "new"],
  [/\bfreepods\b/g, "freepods"],
  [/\bmac[\s-]?book\b/g, "macbook"],
  [/\bnote\s*40\s*pro\b/g, "note 40 pro"],
  [/\bcamon\s*30\b/g, "camon 30"],
];

export const STOPWORDS = new Set([
  "the",
  "and",
  "with",
  "for",
  "official",
  "store",
  "authentic",
  "original",
  "rom",
  "ram",
  "nigeria",
  "lagos",
  "abuja",
  "warranty",
  "promo",
  "sale",
  "free",
  "delivery",
  "shipped",
  "from",
  "plus",
  "only",
  "best",
  "deal",
  "price",
  "buy",
  "shop",
  "online",
  "version",
  "global",
  "dual",
  "sim",
  "combo",
  "bundle",
  "set",
  "jumia",
  "konga",
  "jiji",
  "slot",
  "kara",
  "pointek",
  "5g",
  "4g",
  "lte",
  "generator",
]);

export function normalizeText(input: string): string {
  let text = input.toLowerCase().normalize("NFKD");
  text = text.replace(/[₦]/g, " ");
  text = text.replace(/\bnaira\b/g, " ");
  text = text.replace(/\b(\d+)\s*\/\s*(\d+)\b/g, "$1gb $2gb");
  text = text.replace(/\b(2|3|4|6|8|12|16|24|32|64|128|256|512|1024)\s*g\b/g, "$1gb");
  text = text.replace(/(\d+)\s*(gb|tb|kva|inch|in)\b/g, "$1$2");
  text = text.replace(/(\d+)\s*["”]/g, "$1inch");
  text = text.replace(/(\d+(?:\.\d+)?)\s*kva\b/g, "$1kva");

  for (const [pattern, replacement] of ALIASES) {
    text = text.replace(pattern, replacement);
  }

  text = text.replace(/[^\p{L}\p{N}.+\s-]/gu, " ");
  return text.replace(/\s+/g, " ").trim();
}

export function tokenize(input: string): string[] {
  return normalizeText(input)
    .split(/\s+/)
    .map((token) => token.replace(/^-+|-+$/g, ""))
    .filter((token) => token.length > 0 && !STOPWORDS.has(token));
}

export function uniqueTokens(input: string): string[] {
  return [...new Set(tokenize(input))];
}

export function jaccard(a: string[], b: string[]): number {
  if (a.length === 0 && b.length === 0) return 1;
  const setA = new Set(a);
  const setB = new Set(b);
  let intersection = 0;
  for (const token of setA) {
    if (setB.has(token)) intersection += 1;
  }
  const union = new Set([...setA, ...setB]).size;
  return union === 0 ? 0 : intersection / union;
}
