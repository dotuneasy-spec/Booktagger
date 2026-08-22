import type {
  CanonicalProduct,
  CategoryId,
  Offer,
  PricePoint,
  Store,
} from "../lib/types";
import { SEED_SITES } from "./directory";

const LIVE_AT_BOOT: Store[] = SEED_SITES.filter((site) => site.status === "live");

export const CATEGORIES: Array<{
  id: CategoryId;
  name: string;
  blurb: string;
}> = [
  { id: "phones", name: "Phones", blurb: "Tecno, Infinix, Samsung, iPhone" },
  { id: "laptops", name: "Laptops", blurb: "Work, school, and content kits" },
  { id: "power", name: "Power", blurb: "Generators, inverters, solar" },
  { id: "home", name: "Home", blurb: "TVs, fridges, fans, washers" },
  { id: "audio", name: "Audio", blurb: "Oraimo, Sony, and more" },
  { id: "beauty", name: "Beauty", blurb: "Everyday Naija staples" },
  { id: "fashion", name: "Fashion", blurb: "Sneakers and ready-to-wear" },
  { id: "groceries", name: "Groceries", blurb: "Carton prices that add up" },
];

export const PRODUCTS: CanonicalProduct[] = [
  {
    id: "samsung-a55-256",
    slug: "samsung-galaxy-a55-5g-8-256",
    title: "Samsung Galaxy A55 5G 8GB/256GB",
    brand: "Samsung",
    model: "Galaxy A55 5G",
    family: "galaxy",
    category: "phones",
    attributes: { storageGb: 256, ramGb: 8, color: "navy" },
    description:
      "The volume A-series phone in Nigeria right now. Same 8/256 unit shows up under six different title styles.",
    hue: 230,
    popular: true,
  },
  {
    id: "samsung-a16-128",
    slug: "samsung-galaxy-a16-6-128",
    title: "Samsung Galaxy A16 6GB/128GB",
    brand: "Samsung",
    model: "Galaxy A16",
    family: "galaxy",
    category: "phones",
    attributes: { storageGb: 128, ramGb: 6, color: "black" },
    description: "Entry Samsung. Easy to confuse with A55 in raw keyword search — Oja keeps them apart.",
    hue: 210,
  },
  {
    id: "iphone-13-128",
    slug: "iphone-13-128gb",
    title: "Apple iPhone 13 128GB",
    brand: "Apple",
    model: "iPhone 13",
    family: "iphone",
    category: "phones",
    attributes: { storageGb: 128, color: "midnight" },
    description:
      "Still the most shopped iPhone in Nigeria. New vs UK used is a ₦150k+ swing — we label both.",
    hue: 200,
    popular: true,
  },
  {
    id: "iphone-15-128",
    slug: "iphone-15-128gb",
    title: "Apple iPhone 15 128GB",
    brand: "Apple",
    model: "iPhone 15",
    family: "iphone",
    category: "phones",
    attributes: { storageGb: 128, color: "blue" },
    description: "Current mainstream iPhone. Grey-market and official stock sit side by side.",
    hue: 190,
    sponsored: true,
    popular: true,
  },
  {
    id: "tecno-camon-30-premier",
    slug: "tecno-camon-30-premier-512",
    title: "Tecno Camon 30 Premier 512GB",
    brand: "Tecno",
    model: "Camon 30 Premier",
    family: "camon",
    category: "phones",
    attributes: { storageGb: 512, ramGb: 12, color: "black" },
    description: "Transsion flagship energy. Camera-led, sold everywhere from Slot to Jiji.",
    hue: 28,
    popular: true,
  },
  {
    id: "tecno-spark-20-pro",
    slug: "tecno-spark-20-pro-256",
    title: "Tecno Spark 20 Pro 256GB",
    brand: "Tecno",
    model: "Spark 20 Pro",
    family: "spark",
    category: "phones",
    attributes: { storageGb: 256, ramGb: 8, color: "gold" },
    description: "Budget volume seller. Titles often drop Tecno and just say Spark 20 Pro.",
    hue: 38,
  },
  {
    id: "infinix-note-40-pro",
    slug: "infinix-note-40-pro-256",
    title: "Infinix Note 40 Pro 256GB",
    brand: "Infinix",
    model: "Note 40 Pro",
    family: "note",
    category: "phones",
    attributes: { storageGb: 256, ramGb: 8, color: "green" },
    description: "A matching test case: Note 40 vs Note 40 Pro vs Hot 40i.",
    hue: 150,
    popular: true,
  },
  {
    id: "infinix-hot-40i",
    slug: "infinix-hot-40i-128",
    title: "Infinix Hot 40i 128GB",
    brand: "Infinix",
    model: "Hot 40i",
    family: "hot",
    category: "phones",
    attributes: { storageGb: 128, ramGb: 8, color: "blue" },
    description: "Entry Infinix. Must not collapse into Note 40 Pro.",
    hue: 168,
  },
  {
    id: "itel-s24",
    slug: "itel-s24-128",
    title: "Itel S24 128GB",
    brand: "Itel",
    model: "S24",
    category: "phones",
    attributes: { storageGb: 128, ramGb: 4, color: "black" },
    description: "Sub-₦150k smartphone. High search volume, thin retail margins.",
    hue: 12,
  },
  {
    id: "redmi-note-13-pro",
    slug: "xiaomi-redmi-note-13-pro-256",
    title: "Xiaomi Redmi Note 13 Pro 256GB",
    brand: "Xiaomi",
    model: "Redmi Note 13 Pro",
    family: "note",
    category: "phones",
    attributes: { storageGb: 256, ramGb: 8, color: "purple" },
    description: "People search Redmi, Xiaomi, or just Note 13 Pro. We resolve all three.",
    hue: 270,
  },
  {
    id: "hp-15-i5",
    slug: "hp-15-core-i5-8-512",
    title: "HP 15 Intel Core i5 8GB/512GB",
    brand: "HP",
    model: "15 Intel Core i5",
    category: "laptops",
    attributes: { storageGb: 512, ramGb: 8 },
    description: "The default office laptop in Lagos. Specs get shuffled in titles.",
    hue: 210,
    popular: true,
  },
  {
    id: "dell-inspiron-i7",
    slug: "dell-inspiron-15-i7-16-512",
    title: "Dell Inspiron 15 Intel Core i7 16GB/512GB",
    brand: "Dell",
    model: "Inspiron 15 i7",
    family: "inspiron",
    category: "laptops",
    attributes: { storageGb: 512, ramGb: 16 },
    description: "Heavier work machine. Watch RAM — 8GB listings are a different SKU.",
    hue: 220,
  },
  {
    id: "macbook-air-m2",
    slug: "macbook-air-m2-8-256",
    title: "Apple MacBook Air M2 8GB/256GB",
    brand: "Apple",
    model: "MacBook Air M2",
    category: "laptops",
    attributes: { storageGb: 256, ramGb: 8, color: "midnight" },
    description: "Premium laptop. Official vs grey import pricing is the whole game.",
    hue: 215,
    sponsored: true,
    popular: true,
  },
  {
    id: "lenovo-ideapad-slim3",
    slug: "lenovo-ideapad-slim-3-8-256",
    title: "Lenovo IdeaPad Slim 3 8GB/256GB",
    brand: "Lenovo",
    model: "IdeaPad Slim 3",
    family: "ideapad",
    category: "laptops",
    attributes: { storageGb: 256, ramGb: 8 },
    description: "Student laptop. Often bundled with a mouse on Konga.",
    hue: 255,
  },
  {
    id: "oraimo-freepods-4",
    slug: "oraimo-freepods-4",
    title: "Oraimo FreePods 4",
    brand: "Oraimo",
    model: "FreePods 4",
    family: "freepods",
    category: "audio",
    attributes: { color: "black" },
    description: "Nigeria's default earbuds. Counterfeits exist — we surface store rating.",
    hue: 145,
    popular: true,
  },
  {
    id: "sony-wh1000xm5",
    slug: "sony-wh-1000xm5",
    title: "Sony WH-1000XM5",
    brand: "Sony",
    model: "WH-1000XM5",
    category: "audio",
    attributes: { color: "black" },
    description: "Flagship ANC. High ticket, high affiliate value.",
    hue: 0,
  },
  {
    id: "firman-2-5kva",
    slug: "sumec-firman-2-5kva-generator",
    title: "Sumec Firman 2.5kVA Generator",
    brand: "Firman",
    model: "2.5kVA",
    category: "power",
    attributes: { capacityKva: 2.5 },
    description:
      "The most searched generator class. 2.5kVA must never match a 3.5kVA listing.",
    hue: 48,
    popular: true,
  },
  {
    id: "elepaq-3-5kva",
    slug: "elepaq-3-5kva-generator",
    title: "Elepaq 3.5kVA Generator",
    brand: "Elepaq",
    model: "3.5kVA",
    category: "power",
    attributes: { capacityKva: 3.5 },
    description: "Next step up from 2.5kVA. Fuel appetite and price both jump.",
    hue: 42,
  },
  {
    id: "luminous-2kva",
    slug: "luminous-2kva-inverter",
    title: "Luminous 2kVA Inverter + Battery",
    brand: "Luminous",
    model: "2kVA Inverter",
    category: "power",
    attributes: { capacityKva: 2 },
    description: "Inverter + tubular battery bundles are titled ten different ways.",
    hue: 55,
    popular: true,
  },
  {
    id: "felicity-5kwh",
    slug: "felicity-5kwh-solar-hybrid",
    title: "Felicity 5kWh Solar Hybrid System",
    brand: "Felicity",
    model: "5kWh Hybrid",
    category: "power",
    attributes: {},
    description: "High-ticket solar. Lead-gen territory for local installers.",
    hue: 70,
    sponsored: true,
  },
  {
    id: "hisense-43",
    slug: "hisense-43-smart-tv",
    title: 'Hisense 43" Smart TV',
    brand: "Hisense",
    model: "43 Smart TV",
    category: "home",
    attributes: { screenInches: 43 },
    description: "43-inch is the volume TV size. 32 and 55 are different products.",
    hue: 205,
    popular: true,
  },
  {
    id: "thermocool-200l",
    slug: "thermocool-200l-fridge",
    title: "Haier Thermocool 200L Fridge",
    brand: "Thermocool",
    model: "200L Fridge",
    category: "home",
    attributes: {},
    description: "The fridge brand Nigerians actually search. Service network matters.",
    hue: 198,
  },
  {
    id: "binatone-stand-fan",
    slug: "binatone-standing-fan",
    title: "Binatone Standing Fan",
    brand: "Binatone",
    model: "Standing Fan",
    category: "home",
    attributes: {},
    description: "Seasonal spike every harmattan and blackout week.",
    hue: 175,
  },
  {
    id: "nexus-6kg-washer",
    slug: "nexus-6kg-washing-machine",
    title: "Nexus 6kg Washing Machine",
    brand: "Nexus",
    model: "6kg Washer",
    category: "home",
    attributes: { weightKg: 6 },
    description: "Compact washer for estates and small flats.",
    hue: 188,
  },
  {
    id: "nivea-perfect-radiant",
    slug: "nivea-perfect-and-radiant",
    title: "Nivea Perfect & Radiant Lotion",
    brand: "Nivea",
    model: "Perfect & Radiant",
    category: "beauty",
    attributes: { size: "400ml" },
    description: "Repeat-purchase beauty. Affiliate on volume, not ticket size.",
    hue: 330,
  },
  {
    id: "nike-revolution-7",
    slug: "nike-revolution-7",
    title: "Nike Revolution 7",
    brand: "Nike",
    model: "Revolution 7",
    family: "revolution",
    category: "fashion",
    attributes: { size: "UK 8" },
    description: "Sneaker listings mix US/UK sizes. We compare the same model first.",
    hue: 350,
    popular: true,
  },
  {
    id: "adidas-samba",
    slug: "adidas-samba-og",
    title: "Adidas Samba OG",
    brand: "Adidas",
    model: "Samba OG",
    family: "samba",
    category: "fashion",
    attributes: { color: "white" },
    description: "Fashion drop with wild price spreads between official and Jiji.",
    hue: 10,
  },
  {
    id: "peak-milk-400",
    slug: "peak-milk-400g-carton",
    title: "Peak Milk 400g Tin (Carton)",
    brand: "Peak",
    model: "400g Carton",
    category: "groceries",
    attributes: { size: "carton" },
    description: "Carton vs single tin is the matching trap. We lock to carton SKUs.",
    hue: 40,
  },
  {
    id: "indomie-hungry-man",
    slug: "indomie-hungry-man-carton",
    title: "Indomie Hungry Man Carton",
    brand: "Indomie",
    model: "Hungry Man Carton",
    category: "groceries",
    attributes: { size: "carton" },
    description: "The carton Nigeria actually buys. Hungry Man vs regular must stay split.",
    hue: 25,
    popular: true,
  },
  {
    id: "hollandia-yoghurt",
    slug: "hollandia-yoghurt-pack",
    title: "Hollandia Yoghurt 1L Pack of 6",
    brand: "Hollandia",
    model: "Yoghurt 1L x6",
    category: "groceries",
    attributes: { size: "6x1L" },
    description: "Pack vs single bottle. Another grocery matching edge case.",
    hue: 320,
  },
];

type OfferSeed = {
  productId: string;
  basePrice: number;
  previousDelta?: number;
};

const OFFER_SEEDS: OfferSeed[] = [
  { productId: "samsung-a55-256", basePrice: 448000, previousDelta: 22000 },
  { productId: "samsung-a16-128", basePrice: 198000, previousDelta: 12000 },
  { productId: "iphone-13-128", basePrice: 640000, previousDelta: 35000 },
  { productId: "iphone-15-128", basePrice: 1140000, previousDelta: 60000 },
  { productId: "tecno-camon-30-premier", basePrice: 405000, previousDelta: 18000 },
  { productId: "tecno-spark-20-pro", basePrice: 198000, previousDelta: 10000 },
  { productId: "infinix-note-40-pro", basePrice: 305000, previousDelta: 15000 },
  { productId: "infinix-hot-40i", basePrice: 148000, previousDelta: 8000 },
  { productId: "itel-s24", basePrice: 118000, previousDelta: 5000 },
  { productId: "redmi-note-13-pro", basePrice: 328000, previousDelta: 14000 },
  { productId: "hp-15-i5", basePrice: 685000, previousDelta: 25000 },
  { productId: "dell-inspiron-i7", basePrice: 980000, previousDelta: 40000 },
  { productId: "macbook-air-m2", basePrice: 1580000, previousDelta: 70000 },
  { productId: "lenovo-ideapad-slim3", basePrice: 548000, previousDelta: 20000 },
  { productId: "oraimo-freepods-4", basePrice: 32500, previousDelta: 2500 },
  { productId: "sony-wh1000xm5", basePrice: 385000, previousDelta: 20000 },
  { productId: "firman-2-5kva", basePrice: 318000, previousDelta: 15000 },
  { productId: "elepaq-3-5kva", basePrice: 428000, previousDelta: 18000 },
  { productId: "luminous-2kva", basePrice: 540000, previousDelta: 25000 },
  { productId: "felicity-5kwh", basePrice: 2850000, previousDelta: 120000 },
  { productId: "hisense-43", basePrice: 312000, previousDelta: 18000 },
  { productId: "thermocool-200l", basePrice: 268000, previousDelta: 12000 },
  { productId: "binatone-stand-fan", basePrice: 38500, previousDelta: 3000 },
  { productId: "nexus-6kg-washer", basePrice: 178000, previousDelta: 8000 },
  { productId: "nivea-perfect-radiant", basePrice: 6200, previousDelta: 800 },
  { productId: "nike-revolution-7", basePrice: 62000, previousDelta: 7000 },
  { productId: "adidas-samba", basePrice: 145000, previousDelta: 12000 },
  { productId: "peak-milk-400", basePrice: 28500, previousDelta: 2000 },
  { productId: "indomie-hungry-man", basePrice: 14200, previousDelta: 1200 },
  { productId: "hollandia-yoghurt", basePrice: 9800, previousDelta: 600 },
];

const STORE_PRICE_BIAS: Record<string, number> = {
  jumia: 0.03,
  konga: 0.015,
  jiji: -0.11,
  slot: -0.025,
  kara: 0.01,
  pointek: -0.04,
};

const TITLE_STYLES: Record<
  string,
  (product: CanonicalProduct, condition: Offer["condition"]) => string
> = {
  jumia: (product, condition) =>
    `${product.brand} ${product.model} ${specTail(product)} - ${condition === "new" ? "Official Store" : conditionLabel(condition)}`,
  konga: (product, condition) =>
    `${product.model} ${specTail(product)} ${product.brand} ${condition === "new" ? "Brand New" : conditionLabel(condition)}`,
  jiji: (product, condition) =>
    `${conditionLabel(condition)} ${product.model} ${specTail(product)} ${product.attributes.color ?? ""} Lagos`.trim(),
  slot: (product) =>
    `${product.brand} ${product.model} ${compactSpecs(product)}`,
  kara: (product, condition) =>
    `Buy ${product.title} ${condition === "new" ? "with warranty" : conditionLabel(condition)}`,
  pointek: (product) =>
    `${product.model} ${compactSpecs(product)} ${product.brand}`.trim(),
};

function specTail(product: CanonicalProduct): string {
  const parts: string[] = [];
  if (product.attributes.ramGb && product.attributes.storageGb) {
    parts.push(`${product.attributes.ramGb}/${product.attributes.storageGb}`);
  } else if (product.attributes.storageGb) {
    parts.push(`${product.attributes.storageGb}GB`);
  }
  if (product.attributes.capacityKva) parts.push(`${product.attributes.capacityKva}kVA`);
  if (product.attributes.screenInches) parts.push(`${product.attributes.screenInches}"`);
  return parts.join(" ");
}

function defaultTitle(product: CanonicalProduct, condition: Offer["condition"]): string {
  return `${product.title} ${conditionLabel(condition)}`;
}

function compactSpecs(product: CanonicalProduct): string {
  if (product.attributes.ramGb && product.attributes.storageGb) {
    return `${product.attributes.ramGb}GB RAM ${product.attributes.storageGb}GB ROM`;
  }
  return specTail(product);
}

function conditionLabel(condition: Offer["condition"]): string {
  if (condition === "uk-used") return "UK Used";
  if (condition === "fairly-used") return "Fairly Used";
  return "Brand New";
}

function hash(value: string): number {
  let total = 0;
  for (let i = 0; i < value.length; i += 1) total += value.charCodeAt(i) * (i + 1);
  return total;
}

function buildOffers(): Offer[] {
  const offers: Offer[] = [];

  for (const seed of OFFER_SEEDS) {
    const product = PRODUCTS.find((item) => item.id === seed.productId);
    if (!product) continue;

    for (const store of LIVE_AT_BOOT) {
      const includeUk =
        product.category === "phones" &&
        (store.id === "jiji" || store.id === "pointek") &&
        (product.brand === "Apple" || product.brand === "Samsung");

      const condition: Offer["condition"] = includeUk && store.id === "jiji" ? "uk-used" : "new";
      const conditionBias = condition === "uk-used" ? 0.78 : 1;
      const jitter = ((hash(`${seed.productId}-${store.id}`) % 17) - 8) / 100;
      const price = Math.round(
        seed.basePrice * (1 + (STORE_PRICE_BIAS[store.id] ?? 0) + jitter) * conditionBias,
      );

      const skipPointek = store.id === "pointek" && ["beauty", "groceries", "fashion"].includes(product.category);
      if (skipPointek) continue;

      const inStock = !(store.id === "kara" && hash(product.id) % 7 === 0);
      const sponsored = product.sponsored && store.featured && store.id === "jumia";

      offers.push({
        id: `${product.id}-${store.id}-${condition}`,
        productId: product.id,
        storeId: store.id,
        title: (TITLE_STYLES[store.id] ?? defaultTitle)(product, condition),
        priceNgn: price,
        previousPriceNgn: seed.previousDelta ? price + seed.previousDelta : undefined,
        url: `https://${store.domain}/catalog/${product.slug}`,
        condition,
        inStock,
        rating: 3.6 + ((hash(store.id + product.id) % 14) / 10),
        reviewCount: 12 + (hash(product.id + store.id) % 480),
        deliveryLagDays: store.id === "jiji" ? 0 : 1 + (hash(store.id) % 4),
        sponsored,
        sellerName:
          store.id === "jiji"
            ? ["Wale Gadgets", "Ikeja Phones", "Abuja Gizmo"][hash(product.id) % 3]
            : `${store.name} Official`,
        updatedAt: "2026-08-21T09:00:00.000Z",
      });
    }
  }

  return offers;
}

export const SEED_OFFERS: Offer[] = buildOffers();
export const OFFERS = SEED_OFFERS;

const runtimeOffers: Offer[] = [];

export function addRuntimeOffers(offers: Offer[]) {
  for (const offer of offers) {
    if (!runtimeOffers.some((item) => item.id === offer.id) && !SEED_OFFERS.some((item) => item.id === offer.id)) {
      runtimeOffers.push(offer);
    }
  }
}

export function getOffers(): Offer[] {
  return [...SEED_OFFERS, ...runtimeOffers];
}

export function basePriceFor(productId: string): number | undefined {
  return OFFER_SEEDS.find((seed) => seed.productId === productId)?.basePrice;
}

export function getProduct(idOrSlug: string): CanonicalProduct | undefined {
  return PRODUCTS.find((item) => item.id === idOrSlug || item.slug === idOrSlug);
}

export function offersForProduct(productId: string): Offer[] {
  return getOffers().filter((offer) => offer.productId === productId);
}

export function priceHistoryForProduct(productId: string): PricePoint[] {
  const offers = offersForProduct(productId);
  if (offers.length === 0) return [];
  const low = Math.min(...offers.map((offer) => offer.priceNgn));
  const days = [
    "2026-07-11",
    "2026-07-18",
    "2026-07-25",
    "2026-08-01",
    "2026-08-08",
    "2026-08-15",
    "2026-08-22",
  ];
  return days.map((date, index) => ({
    date,
    priceNgn: Math.round(low * (1.12 - index * 0.018) + (hash(productId + date) % 4000)),
  }));
}

export function relatedProducts(product: CanonicalProduct, limit = 3): CanonicalProduct[] {
  return PRODUCTS.filter(
    (item) => item.category === product.category && item.id !== product.id,
  ).slice(0, limit);
}
