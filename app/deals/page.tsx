import { ProductCard } from "../../components/ProductCard";
import { searchProducts } from "../../lib/search";
import { savingsPercent } from "../../lib/money";

export default function DealsPage() {
  const deals = searchProducts("", { sort: "savings" }).hits.filter(
    (hit) => savingsPercent(hit.lowestPrice, hit.highestPrice) >= 8,
  );

  return (
    <div className="py-8">
      <h1 className="display text-4xl">Today&apos;s spreads</h1>
      <p className="mt-2 max-w-2xl text-muted">
        Products where the same SKU is at least 8% cheaper in one Nigerian store than another.
        That gap is both the shopper hook and the affiliate click.
      </p>
      <div className="mt-8 space-y-4">
        {deals.map((hit) => (
          <ProductCard hit={hit} key={hit.product.id} source="deals" />
        ))}
      </div>
    </div>
  );
}
