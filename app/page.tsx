import Link from "next/link";
import { CATEGORIES, PRODUCTS } from "../data/catalog";
import { directoryStats, liveStores } from "../lib/registry";
import { SearchBox } from "../components/SearchBox";
import { ProductCard } from "../components/ProductCard";
import { BoltIcon, ShieldIcon, TagIcon } from "../components/icons";
import { searchProducts } from "../lib/search";
import { formatNaira } from "../lib/money";

export default function HomePage() {
  const popular = searchProducts("").hits
    .filter((hit) => hit.product.popular)
    .slice(0, 4);
  const samples = ["Infinix Note 40 Pro 256", "Firman 2.5kVA", "iPhone 13 128 UK used", "Oraimo FreePods 4"];
  const live = liveStores();
  const stats = directoryStats();

  return (
    <div className="pb-16">
      <section className="grid items-end gap-10 pt-10 md:grid-cols-[1.2fr_0.8fr] md:pt-16">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-clay">Naija price engine</p>
          <h1 className="display mt-3 max-w-xl text-5xl leading-[1.05] md:text-6xl">
            Stop paying Jumia prices when Slot has the same phone.
          </h1>
          <p className="mt-5 max-w-xl text-lg text-muted">
            Oja matches the same product across Nigerian stores — even when the titles
            disagree — then sends you out through a tracked buy link.
          </p>
          <div className="mt-8 max-w-2xl">
            <SearchBox autoFocus />
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            {samples.map((sample) => (
              <Link
                className="chip rounded-full px-3 py-1 text-sm hover:border-green"
                href={`/search?q=${encodeURIComponent(sample)}`}
                key={sample}
              >
                {sample}
              </Link>
            ))}
          </div>
        </div>
        <div className="card rounded-3xl p-6">
          <p className="text-xs uppercase tracking-[0.16em] text-muted">Nigerian ecommerce collection</p>
          <p className="mt-3 text-3xl font-semibold">{stats.total} sites</p>
          <p className="text-sm text-muted">
            {stats.live} live on compare · {stats.feedReady} feed-ready
          </p>
          <ul className="mt-4 space-y-3">
            {live.map((store) => (
              <li className="flex items-center justify-between text-sm" key={store.id}>
                <Link className="flex items-center gap-2 hover:text-green" href={`/stores/${store.id}`}>
                  <span className="h-2.5 w-2.5 rounded-full" style={{ background: store.color }} />
                  {store.name}
                </Link>
                <span className="text-muted">live</span>
              </li>
            ))}
          </ul>
          <Link className="mt-4 inline-block text-sm text-green" href="/stores">
            Search the full directory
          </Link>
        </div>
      </section>

      <section className="mt-14 grid gap-4 md:grid-cols-3">
        {[
          {
            icon: <TagIcon className="h-5 w-5" />,
            title: "Same product, messy titles",
            body: "8/256, 8GB RAM 256GB ROM, and “A55 official store” collapse into one card.",
          },
          {
            icon: <BoltIcon className="h-5 w-5" />,
            title: "Naija-specific attributes",
            body: "UK used, kVA, carton vs tin, Tecno/Infinix families — not a generic EU scraper.",
          },
          {
            icon: <ShieldIcon className="h-5 w-5" />,
            title: "Money on the click",
            body: "Affiliate outbound, sponsored slots, price-alert upsell, merchant intel plans.",
          },
        ].map((item) => (
          <div className="card rounded-3xl p-5" key={item.title}>
            <div className="text-green">{item.icon}</div>
            <h2 className="mt-3 text-lg font-semibold">{item.title}</h2>
            <p className="mt-2 text-sm text-muted">{item.body}</p>
          </div>
        ))}
      </section>

      <section className="mt-14">
        <div className="flex items-end justify-between">
          <h2 className="display text-3xl">Shop by aisle</h2>
          <Link className="text-sm text-green" href="/deals">
            See all deals
          </Link>
        </div>
        <div className="mt-5 grid grid-cols-2 gap-3 md:grid-cols-4">
          {CATEGORIES.map((category) => {
            const count = PRODUCTS.filter((product) => product.category === category.id).length;
            return (
              <Link
                className="card rounded-3xl p-4 hover:border-green"
                href={`/category/${category.id}`}
                key={category.id}
              >
                <p className="font-semibold">{category.name}</p>
                <p className="mt-1 text-sm text-muted">{category.blurb}</p>
                <p className="mt-3 text-xs uppercase tracking-[0.14em] text-muted">{count} products</p>
              </Link>
            );
          })}
        </div>
      </section>

      <section className="mt-14 space-y-4">
        <h2 className="display text-3xl">Popular matches today</h2>
        {popular.map((hit) => (
          <ProductCard hit={hit} key={hit.product.id} source="home" />
        ))}
      </section>

      <section className="card mt-14 rounded-3xl p-8 md:flex md:items-center md:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.16em] text-muted">Monetize the comparison</p>
          <h2 className="display mt-2 text-3xl">Sell the last click, not the pageview.</h2>
          <p className="mt-2 max-w-xl text-muted">
            Plans from {formatNaira(45000)}/mo. Affiliates pay on every outbound. Intelligence
            sells the price feed back to the stores you just compared.
          </p>
        </div>
        <Link className="mt-5 inline-flex rounded-full bg-green px-5 py-3 text-sm font-semibold text-white md:mt-0" href="/merchants">
          See merchant plans
        </Link>
      </section>
    </div>
  );
}
