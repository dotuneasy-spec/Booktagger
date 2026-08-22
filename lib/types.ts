export type Condition = "new" | "uk-used" | "fairly-used";

export type StoreId = "jumia" | "konga" | "jiji" | "slot" | "kara" | "pointek";

export type CategoryId =
  | "phones"
  | "laptops"
  | "audio"
  | "power"
  | "home"
  | "beauty"
  | "fashion"
  | "groceries";

export type Store = {
  id: StoreId;
  name: string;
  domain: string;
  color: string;
  affiliateRate: number;
  featured: boolean;
  blurb: string;
};

export type ProductAttributes = {
  storageGb?: number;
  ramGb?: number;
  capacityKva?: number;
  screenInches?: number;
  color?: string;
  size?: string;
  weightKg?: number;
};

export type CanonicalProduct = {
  id: string;
  slug: string;
  title: string;
  brand: string;
  model: string;
  family?: string;
  category: CategoryId;
  attributes: ProductAttributes;
  description: string;
  hue: number;
  sponsored?: boolean;
  popular?: boolean;
};

export type Offer = {
  id: string;
  productId: string;
  storeId: StoreId;
  title: string;
  priceNgn: number;
  previousPriceNgn?: number;
  url: string;
  condition: Condition;
  inStock: boolean;
  rating: number;
  reviewCount: number;
  deliveryLagDays: number;
  sponsored?: boolean;
  sellerName: string;
  updatedAt: string;
};

export type PricePoint = {
  date: string;
  priceNgn: number;
};

export type ExtractedProduct = {
  brand?: string;
  family?: string;
  modelTokens: string[];
  storageGb?: number;
  ramGb?: number;
  capacityKva?: number;
  screenInches?: number;
  color?: string;
  condition: Condition;
  tokens: string[];
};

export type MatchReason = {
  label: string;
  weight: number;
};

export type ScoredMatch = {
  score: number;
  reasons: MatchReason[];
};

export type ProductSearchHit = {
  product: CanonicalProduct;
  score: number;
  reasons: MatchReason[];
  offers: RankedOffer[];
  lowestPrice: number;
  highestPrice: number;
  storeCount: number;
};

export type RankedOffer = Offer & {
  matchScore: number;
  savingsVsHigh: number;
  estimatedCommission: number;
  isBestPrice: boolean;
};

export type SearchInterpretation = {
  raw: string;
  extracted: ExtractedProduct;
};

export type SearchResult = {
  query: SearchInterpretation;
  hits: ProductSearchHit[];
  totalOffers: number;
};

export type ClickEvent = {
  id: string;
  offerId: string;
  productId: string;
  storeId: StoreId;
  priceNgn: number;
  estimatedCommission: number;
  source: string;
  createdAt: string;
};

export type PriceAlert = {
  id: string;
  productId: string;
  email: string;
  targetPriceNgn?: number;
  channel: "email" | "whatsapp";
  createdAt: string;
};

export type MerchantLead = {
  id: string;
  business: string;
  email: string;
  plan: "starter" | "growth" | "intelligence";
  message: string;
  createdAt: string;
};
