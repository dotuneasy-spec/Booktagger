import Link from "next/link";
import { notFound } from "next/navigation";
import { priceHistoryForProduct, relatedProducts } from "../../../data/catalog";
import { AlertForm } from "../../../components/AlertForm";
import { OfferTable } from "../../../components/OfferTable";
import { PriceSpark } from "../../../components/PriceSpark";
import { ProductArt } from "../../../components/ProductArt";
import { WhatsAppIcon } from "../../../components/icons";
import { getProductPage } from "../../../lib/search";
import { formatNaira, savingsPercent } from "../../../lib/money";

export async function generateStaticParams() {
  const { PRODUCTS } = await import("../../../data/catalog");
  return PRODUCTS.map((product) => ({ slug: product.slug }));
}

export default async function ProductPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const page = getProductPage(slug);
  if (!page) notFound();
  const { product, offers, reasons, lowestPrice, highestPrice } = page;
  const save = savingsPercent(lowestPrice, highestPrice);
  const related = relatedProducts(product);
  const share = `https://wa.me/?text=${encodeURIComponent(`${product.title} from ${formatNaira(lowestPrice)} on Oja`)}`;

  return (
    <div className="py-8">
      <p className="text-sm text-muted">
        <Link href={`/category/${product.category}`}>{product.category}</Link>
        {" / "}
        {product.brand}
      </p>
      <div className="mt-4 grid gap-6 md:grid-cols-[280px_1fr]">
        <ProductArt
          brand={product.brand}
          className="h-72 rounded-3xl"
          hue={product.hue}
          title={product.title}
        />
        <div>
          <h1 className="display text-4xl">{product.title}</h1>
          <p className="mt-3 max-w-2xl text-muted">{product.description}</p>
          <div className="mt-5 flex flex-wrap items-end gap-6">
            <div>
              <p className="text-xs uppercase tracking-[0.14em] text-muted">Lowest now</p>
              <p className="text-3xl font-semibold">{formatNaira(lowestPrice)}</p>
            </div>
            <p className="text-sm text-green-ink">
              {save > 0
                ? `${save}% below the dearest listing (${formatNaira(highestPrice)})`
                : "Prices are tight across stores"}
            </p>
            <a className="inline-flex items-center gap-2 text-sm text-green" href={share}>
              <WhatsAppIcon className="h-4 w-4" />
              Share on WhatsApp
            </a>
          </div>
        </div>
      </div>

      <section className="mt-8">
        <h2 className="mb-3 text-lg font-semibold">Where to buy</h2>
        <OfferTable offers={offers} source="pdp" />
        <p className="mt-3 text-xs text-muted">
          Affiliate disclosure: Oja may earn a commission when you buy through these buttons. It
          does not change the store price.
        </p>
      </section>

      <section className="mt-8 grid gap-4 md:grid-cols-2">
        <PriceSpark points={priceHistoryForProduct(product.id)} />
        <div className="card rounded-3xl p-5">
          <p className="text-xs uppercase tracking-[0.16em] text-muted">Why these listings matched</p>
          <ul className="mt-4 space-y-2 text-sm">
            {reasons.slice(0, 5).map((reason) => (
              <li className="flex justify-between gap-4" key={reason.label}>
                <span>{reason.label}</span>
                <span className="text-muted">{reason.weight > 0 ? "+" : ""}{reason.weight.toFixed(2)}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <div className="mt-8">
        <AlertForm productId={product.id} productTitle={product.title} />
      </div>

      {related.length > 0 ? (
        <section className="mt-10">
          <h2 className="display text-2xl">Nearby in {product.category}</h2>
          <div className="mt-4 grid gap-3 md:grid-cols-3">
            {related.map((item) => (
              <Link className="card rounded-3xl p-4" href={`/product/${item.slug}`} key={item.id}>
                <p className="text-xs uppercase text-muted">{item.brand}</p>
                <p className="mt-1 font-medium">{item.title}</p>
              </Link>
            ))}
          </div>
        </section>
      ) : null}
    </div>
  );
}
