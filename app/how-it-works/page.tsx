import { extractProduct } from "../../lib/extract";
import { clusterListings, scoreMatch } from "../../lib/match";

const demos = [
  "Samsung Galaxy A55 5G 8/256 - Official Store",
  "A55 256gb jumia promo",
  "UK Used iPhone 13 128GB Face ID intact",
  "Sumec Firman 2.5kVA generator brand new",
  "Elepaq 3.5 KVA",
];

export default function HowItWorksPage() {
  const pairs = [
    ["samsung a55 256", "Samsung Galaxy A55 5G 8GB RAM 256GB ROM"],
    ["infinix note 40 pro", "Infinix Hot 40i 128GB"],
    ["firman 2.5kva", "Elepaq 3.5kVA Generator"],
  ].map(([query, listing]) => ({
    query,
    listing,
    match: scoreMatch(extractProduct(query), extractProduct(listing)),
  }));

  const clusters = clusterListings(
    demos.map((title, index) => ({ id: String(index), extracted: extractProduct(title), title })),
  );

  return (
    <div className="py-8">
      <h1 className="display text-4xl">How Oja decides two listings are the same product</h1>
      <p className="mt-3 max-w-2xl text-lg text-muted">
        Nigerian store titles are chaotic. The engine does not keyword-dump. It extracts a
        product identity, then scores and clusters.
      </p>

      <ol className="mt-8 grid gap-4 md:grid-cols-2">
        {[
          ["1. Normalize", "Lowercase, expand 8/256 into RAM/storage, map tokunbo → UK used, collapse brand aliases."],
          ["2. Extract", "Brand, family (Camon, Note, Galaxy), model tokens, GB, kVA, inches, condition."],
          ["3. Score", "Weighted brand, family, model overlap, specs, title Jaccard. Hard fail on brand or kVA clash."],
          ["4. Cluster", "Union-find over listings above the threshold, then attach the cluster to a canonical SKU."],
        ].map(([title, body]) => (
          <li className="card rounded-3xl p-5" key={title}>
            <p className="font-semibold">{title}</p>
            <p className="mt-2 text-sm text-muted">{body}</p>
          </li>
        ))}
      </ol>

      <section className="mt-10">
        <h2 className="display text-2xl">Live scores</h2>
        <div className="mt-4 space-y-3">
          {pairs.map((item) => (
            <div className="card rounded-3xl p-5" key={item.query}>
              <p className="text-sm">
                <span className="font-medium">{item.query}</span>
                <span className="text-muted"> vs </span>
                <span className="font-medium">{item.listing}</span>
              </p>
              <p className="mt-2 text-2xl font-semibold">{Math.round(item.match.score * 100)}%</p>
              <ul className="mt-2 text-sm text-muted">
                {item.match.reasons.slice(0, 4).map((reason) => (
                  <li key={reason.label}>{reason.label}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      <section className="mt-10">
        <h2 className="display text-2xl">Clusters from messy titles</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          {clusters.map((group, index) => (
            <div className="card rounded-3xl p-5" key={index}>
              <p className="text-xs uppercase tracking-[0.14em] text-muted">Cluster {index + 1}</p>
              <ul className="mt-3 space-y-2 text-sm">
                {group.map((item) => (
                  <li key={item.id}>{item.title}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
