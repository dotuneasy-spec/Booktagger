import Link from "next/link";
import { CATEGORIES, STORES } from "../../data/catalog";
import { ProductCard } from "../../components/ProductCard";
import { SearchBox } from "../../components/SearchBox";
import { searchProducts } from "../../lib/search";
import type { SearchFilters } from "../../lib/search";

function first(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const query = first(params.q) ?? "";
  const filters: SearchFilters = {
    storeId: first(params.store),
    condition: first(params.condition),
    category: first(params.category),
    maxPrice: first(params.max) ? Number(first(params.max)) : undefined,
    inStockOnly: first(params.stock) === "1",
    sort: (first(params.sort) as SearchFilters["sort"]) ?? "match",
  };
  const result = searchProducts(query, filters);

  function href(next: Record<string, string | undefined>) {
    const merged = new URLSearchParams();
    const all = {
      q: query,
      store: filters.storeId,
      condition: filters.condition,
      category: filters.category,
      max: filters.maxPrice ? String(filters.maxPrice) : undefined,
      stock: filters.inStockOnly ? "1" : undefined,
      sort: filters.sort === "match" ? undefined : filters.sort,
      ...next,
    };
    Object.entries(all).forEach(([key, value]) => {
      if (value) merged.set(key, value);
    });
    return `/search?${merged.toString()}`;
  }

  return (
    <div className="py-8">
      <SearchBox initialQuery={query} />
      <div className="mt-6 flex flex-wrap items-center gap-2 text-sm">
        <p className="text-muted">
          {result.hits.length} matched products · {result.totalOffers} offers
        </p>
        {result.query.extracted.brand ? (
          <span className="chip rounded-full px-3 py-1">Brand {result.query.extracted.brand}</span>
        ) : null}
        {result.query.extracted.family ? (
          <span className="chip rounded-full px-3 py-1">Family {result.query.extracted.family}</span>
        ) : null}
        {result.query.extracted.storageGb ? (
          <span className="chip rounded-full px-3 py-1">{result.query.extracted.storageGb}GB</span>
        ) : null}
        {result.query.extracted.capacityKva ? (
          <span className="chip rounded-full px-3 py-1">{result.query.extracted.capacityKva}kVA</span>
        ) : null}
        {result.query.extracted.condition !== "new" ? (
          <span className="chip rounded-full px-3 py-1">{result.query.extracted.condition}</span>
        ) : null}
      </div>

      <div className="mt-5 flex flex-wrap gap-2 text-sm">
        {STORES.map((store) => (
          <Link
            className={`chip rounded-full px-3 py-1 ${filters.storeId === store.id ? "border-green bg-green/10" : ""}`}
            href={href({ store: filters.storeId === store.id ? undefined : store.id })}
            key={store.id}
          >
            {store.name}
          </Link>
        ))}
        {CATEGORIES.map((category) => (
          <Link
            className={`chip rounded-full px-3 py-1 ${filters.category === category.id ? "border-green bg-green/10" : ""}`}
            href={href({ category: filters.category === category.id ? undefined : category.id })}
            key={category.id}
          >
            {category.name}
          </Link>
        ))}
        <Link className={`chip rounded-full px-3 py-1 ${filters.condition === "uk-used" ? "border-green bg-green/10" : ""}`} href={href({ condition: filters.condition === "uk-used" ? undefined : "uk-used" })}>
          UK used
        </Link>
        <Link className={`chip rounded-full px-3 py-1 ${filters.sort === "price" ? "border-green bg-green/10" : ""}`} href={href({ sort: filters.sort === "price" ? undefined : "price" })}>
          Lowest price
        </Link>
      </div>

      <div className="mt-8 space-y-4">
        {result.hits.length === 0 ? (
          <div className="card rounded-3xl p-8">
            <p className="text-lg font-medium">No confident matches.</p>
            <p className="mt-2 text-sm text-muted">
              Try a brand plus a model, like “Tecno Camon 30” or “Hisense 43”.
            </p>
          </div>
        ) : (
          result.hits.map((hit) => <ProductCard hit={hit} key={hit.product.id} source="search" />)
        )}
      </div>
    </div>
  );
}
