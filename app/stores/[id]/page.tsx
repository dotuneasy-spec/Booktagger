import Link from "next/link";
import { notFound } from "next/navigation";
import { PRODUCTS } from "../../../data/catalog";
import { SEED_SITES } from "../../../data/directory";
import { IntegrateStoreForm } from "../../../components/IntegrateStoreForm";
import { formatNaira } from "../../../lib/money";
import { findSite, offersForSite } from "../../../lib/registry";

export function generateStaticParams() {
  return SEED_SITES.map((site) => ({ id: site.id }));
}

export default async function StorePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const site = findSite(id);
  if (!site) notFound();
  const offers = offersForSite(site.id);
  const aisleProducts = PRODUCTS.filter(
    (product) =>
      site.kind === "marketplace" ||
      site.kind === "classifieds" ||
      site.categories.includes(product.category),
  ).slice(0, 6);

  return (
    <div className="py-8">
      <p className="text-sm text-muted">
        <Link href="/stores">Directory</Link> / {site.kind}
      </p>
      <div className="mt-3 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="display text-4xl">{site.name}</h1>
          <p className="mt-2 text-muted">{site.blurb}</p>
          <p className="mt-2 text-sm">
            <a className="text-green" href={site.homepage} rel="noreferrer" target="_blank">
              {site.domain}
            </a>
            {" · "}
            {site.city}
            {site.nationwide ? " · Nationwide" : ""}
          </p>
        </div>
        <span className="rounded-full bg-green/10 px-3 py-1 text-sm text-green-ink">{site.status}</span>
      </div>

      <dl className="mt-8 grid gap-3 md:grid-cols-4">
        {[
          ["Kind", site.kind],
          ["Platform", site.platform],
          ["Integration", site.integrationMethod],
          ["Affiliate take", `${Math.round(site.affiliateRate * 100)}%`],
          ["Checkout", site.checkout.join(", ")],
          ["Signals", site.ecommerceSignals.join(", ")],
          ["Aisles", site.categories.length ? site.categories.join(", ") : "Outside SKU compare"],
          ["Source", site.source],
        ].map(([label, value]) => (
          <div className="card rounded-3xl p-4" key={label}>
            <dt className="text-xs uppercase tracking-[0.14em] text-muted">{label}</dt>
            <dd className="mt-1 text-sm">{value}</dd>
          </div>
        ))}
      </dl>

      <section className="mt-10">
        <h2 className="display text-2xl">
          {site.status === "live" ? "Live offers on the engine" : "What would attach if you connect"}
        </h2>
        {site.status === "live" && offers.length > 0 ? (
          <ul className="mt-4 divide-y divide-line card rounded-3xl">
            {offers.slice(0, 8).map((offer) => {
              const product = PRODUCTS.find((item) => item.id === offer.productId);
              return (
                <li className="flex items-center justify-between gap-3 px-5 py-3 text-sm" key={offer.id}>
                  <Link href={`/product/${product?.slug ?? ""}`}>{product?.title ?? offer.title}</Link>
                  <span className="font-medium">{formatNaira(offer.priceNgn)}</span>
                </li>
              );
            })}
          </ul>
        ) : (
          <div className="card mt-4 rounded-3xl p-5 text-sm text-muted">
            {aisleProducts.length > 0
              ? `Connecting this shop would attach sample prices on ${aisleProducts.map((item) => item.title).join(", ")}.`
              : "This site is in the ecommerce collection but sits outside the current SKU aisles (cars, print, B2B)."}
          </div>
        )}
      </section>

      {site.status !== "live" ? (
        <div className="mt-8">
          <IntegrateStoreForm />
        </div>
      ) : (
        <p className="mt-8 text-sm">
          Filter compare to this shop:{" "}
          <Link className="text-green" href={`/search?store=${site.id}`}>
            Search offers from {site.name}
          </Link>
        </p>
      )}
    </div>
  );
}
