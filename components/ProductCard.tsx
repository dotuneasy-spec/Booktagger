import Link from "next/link";
import { formatNaira, savingsPercent } from "../lib/money";
import { confidenceLabel } from "../lib/copy";
import type { ProductSearchHit } from "../lib/types";
import { ProductArt } from "./ProductArt";

export function ProductCard({ hit, source }: { hit: ProductSearchHit; source: string }) {
  const save = savingsPercent(hit.lowestPrice, hit.highestPrice);
  return (
    <article className="card overflow-hidden rounded-3xl">
      <div className="grid md:grid-cols-[220px_1fr]">
        <ProductArt
          brand={hit.product.brand}
          className="h-44 md:h-full"
          hue={hit.product.hue}
          title={hit.product.title}
        />
        <div className="p-5">
          <div className="flex flex-wrap items-center gap-2 text-xs">
            {hit.product.sponsored ? (
              <span className="rounded-full bg-gold/25 px-2 py-0.5">Sponsored</span>
            ) : null}
            <span className="rounded-full bg-green/10 px-2 py-0.5 text-green-ink">
              {confidenceLabel(hit.score)} · {Math.round(hit.score * 100)}%
            </span>
            <span className="text-muted">{hit.storeCount} stores</span>
          </div>
          <h2 className="mt-2 text-xl font-semibold">
            <Link href={`/product/${hit.product.slug}`}>{hit.product.title}</Link>
          </h2>
          <p className="mt-1 text-sm text-muted">{hit.product.description}</p>
          <div className="mt-4 flex flex-wrap items-end justify-between gap-3">
            <div>
              <p className="text-xs uppercase tracking-[0.14em] text-muted">From</p>
              <p className="text-2xl font-semibold">{formatNaira(hit.lowestPrice)}</p>
              {save > 0 ? (
                <p className="text-sm text-green-ink">Save up to {save}% vs highest listing</p>
              ) : null}
            </div>
            <Link
              className="rounded-full bg-ink px-4 py-2 text-sm text-white"
              href={`/product/${hit.product.slug}?src=${source}`}
            >
              Compare {hit.offers.length} offers
            </Link>
          </div>
        </div>
      </div>
    </article>
  );
}
