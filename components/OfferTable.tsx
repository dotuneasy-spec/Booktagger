import Link from "next/link";
import { getStore } from "../lib/registry";
import { conditionLabel } from "../lib/copy";
import { formatNaira } from "../lib/money";
import type { RankedOffer } from "../lib/types";

export function OfferTable({
  offers,
  source,
}: {
  offers: RankedOffer[];
  source: string;
}) {
  return (
    <div className="card overflow-hidden rounded-3xl">
      <div className="grid grid-cols-[1.2fr_1fr_1fr_auto] gap-3 border-b border-line px-5 py-3 text-xs uppercase tracking-[0.14em] text-muted">
        <span>Store</span>
        <span>Price</span>
        <span>Condition</span>
        <span />
      </div>
      {offers.map((offer) => {
        const store = getStore(offer.storeId);
        return (
          <div
            className="grid grid-cols-[1.2fr_1fr_1fr_auto] items-center gap-3 border-b border-line/70 px-5 py-4 last:border-0"
            key={offer.id}
          >
            <div>
              <div className="flex items-center gap-2">
                <span
                  className="h-2.5 w-2.5 rounded-full"
                  style={{ background: store.color }}
                />
                <p className="font-medium">{store.name}</p>
                {offer.sponsored ? (
                  <span className="rounded-full bg-gold/20 px-2 py-0.5 text-[11px] text-ink">
                    Sponsored
                  </span>
                ) : null}
                {offer.isBestPrice ? (
                  <span className="rounded-full bg-green/10 px-2 py-0.5 text-[11px] text-green-ink">
                    Best price
                  </span>
                ) : null}
              </div>
              <p className="mt-1 line-clamp-1 text-xs text-muted">{offer.title}</p>
              <p className="text-xs text-muted">{offer.sellerName}</p>
            </div>
            <div>
              <p className="text-lg font-semibold">{formatNaira(offer.priceNgn)}</p>
              {offer.previousPriceNgn ? (
                <p className="text-xs text-muted line-through">
                  {formatNaira(offer.previousPriceNgn)}
                </p>
              ) : null}
            </div>
            <div className="text-sm">
              <p>{conditionLabel(offer.condition)}</p>
              <p className="text-xs text-muted">
                {offer.inStock ? `${offer.deliveryLagDays} day delivery` : "Out of stock"}
              </p>
            </div>
            <Link
              className="rounded-full bg-ink px-4 py-2 text-sm text-white hover:bg-green-ink"
              href={`/go/${offer.id}?src=${source}`}
              rel="nofollow sponsored"
            >
              Go to {store.name}
            </Link>
          </div>
        );
      })}
    </div>
  );
}
