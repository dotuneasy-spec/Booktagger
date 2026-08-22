import Link from "next/link";
import { SITE_KINDS } from "../../data/directory";
import { IntegrateStoreForm } from "../../components/IntegrateStoreForm";
import { directoryStats, searchSites } from "../../lib/registry";

function first(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}

const STATUSES = ["live", "feed-ready", "pending", "watchlist"] as const;

export default async function StoresPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const query = first(params.q) ?? "";
  const kind = first(params.kind);
  const status = first(params.status);
  const sites = searchSites({ query, kind, status });
  const stats = directoryStats();

  function href(next: Record<string, string | undefined>) {
    const merged = new URLSearchParams();
    const all = { q: query, kind, status, ...next };
    Object.entries(all).forEach(([key, value]) => {
      if (value) merged.set(key, value);
    });
    const qs = merged.toString();
    return qs ? `/stores?${qs}` : "/stores";
  }

  return (
    <div className="py-8">
      <p className="text-xs uppercase tracking-[0.16em] text-clay">Ecommerce directory</p>
      <h1 className="display mt-2 max-w-3xl text-4xl">
        A collection of Nigerian web shops — not just the six big logos.
      </h1>
      <p className="mt-3 max-w-2xl text-muted">
        {stats.total} sites classified as ecommerce on the Nigerian web. {stats.live} are live on
        price compare. The rest are feed-ready, pending a merchant file, or watchlisted.
      </p>

      <div className="mt-6 grid gap-3 md:grid-cols-4">
        {[
          ["In directory", stats.total],
          ["Live on compare", stats.live],
          ["Feed ready", stats.feedReady],
          ["Kinds", stats.kinds],
        ].map(([label, value]) => (
          <div className="card rounded-3xl p-4" key={label}>
            <p className="text-xs uppercase tracking-[0.14em] text-muted">{label}</p>
            <p className="mt-1 text-2xl font-semibold">{value}</p>
          </div>
        ))}
      </div>

      <form className="card mt-8 flex flex-col gap-3 rounded-full px-4 py-3 md:flex-row md:items-center">
        <input
          className="flex-1 bg-transparent py-2 text-sm outline-none"
          defaultValue={query}
          name="q"
          placeholder="Search Slot, pharmacy, Lagos, WooCommerce, Paystack…"
        />
        {kind ? <input name="kind" type="hidden" value={kind} /> : null}
        {status ? <input name="status" type="hidden" value={status} /> : null}
        <button className="rounded-full bg-green px-4 py-2 text-sm font-semibold text-white" type="submit">
          Search directory
        </button>
      </form>

      <div className="mt-4 flex flex-wrap gap-2 text-sm">
        {SITE_KINDS.map((item) => (
          <Link
            className={`chip rounded-full px-3 py-1 ${kind === item.id ? "border-green bg-green/10" : ""}`}
            href={href({ kind: kind === item.id ? undefined : item.id })}
            key={item.id}
          >
            {item.label}
          </Link>
        ))}
        {STATUSES.map((item) => (
          <Link
            className={`chip rounded-full px-3 py-1 ${status === item ? "border-green bg-green/10" : ""}`}
            href={href({ status: status === item ? undefined : item })}
            key={item}
          >
            {item}
          </Link>
        ))}
      </div>

      <p className="mt-6 text-sm text-muted">{sites.length} sites</p>
      <div className="mt-3 grid gap-3 md:grid-cols-2">
        {sites.map((site) => (
          <Link className="card rounded-3xl p-5 hover:border-green" href={`/stores/${site.id}`} key={site.id}>
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="flex items-center gap-2 font-semibold">
                  <span className="h-2.5 w-2.5 rounded-full" style={{ background: site.color }} />
                  {site.name}
                </p>
                <p className="mt-1 text-sm text-muted">{site.domain}</p>
              </div>
              <span className="rounded-full bg-paper px-2 py-0.5 text-xs">{site.status}</span>
            </div>
            <p className="mt-3 text-sm text-muted">{site.blurb}</p>
            <p className="mt-3 text-xs uppercase tracking-[0.12em] text-muted">
              {site.kind} · {site.city}
              {site.nationwide ? " · Nationwide" : ""} · {site.platform}
            </p>
          </Link>
        ))}
      </div>

      <div className="mt-10">
        <IntegrateStoreForm />
      </div>
    </div>
  );
}
