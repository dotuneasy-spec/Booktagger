import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="mt-16 border-t border-line">
      <div className="mx-auto grid max-w-6xl gap-8 px-4 py-10 md:grid-cols-4">
        <div>
          <p className="display text-2xl">Oja</p>
          <p className="mt-2 text-sm text-muted">
            A Naija price engine. Same product, every store, one search.
          </p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-[0.16em] text-muted">Product</p>
          <ul className="mt-3 space-y-2 text-sm">
            <li>
              <Link href="/deals">Today&apos;s deals</Link>
            </li>
            <li>
              <Link href="/how-it-works">How matching works</Link>
            </li>
            <li>
              <Link href="/alerts">Price alerts</Link>
            </li>
          </ul>
        </div>
        <div>
          <p className="text-xs uppercase tracking-[0.16em] text-muted">Money</p>
          <ul className="mt-3 space-y-2 text-sm">
            <li>
              <Link href="/merchants">Merchant plans</Link>
            </li>
            <li>
              <Link href="/merchants#affiliate">Affiliate model</Link>
            </li>
          </ul>
        </div>
        <div className="text-sm text-muted">
          <p>Sample catalog for product matching. Outbound links are tracked affiliate-style redirects.</p>
          <p className="mt-3">Lagos · 2026</p>
        </div>
      </div>
    </footer>
  );
}
