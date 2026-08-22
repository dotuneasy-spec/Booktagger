import { STORES } from "../../data/catalog";
import { MerchantForm } from "../../components/MerchantForm";
import { monetizationSnapshot } from "../../lib/affiliate";
import { formatNaira } from "../../lib/money";

export default function MerchantsPage() {
  const snapshot = monetizationSnapshot();

  return (
    <div className="py-8">
      <p className="text-xs uppercase tracking-[0.16em] text-clay">Monetization</p>
      <h1 className="display mt-2 max-w-3xl text-5xl leading-tight">
        Shoppers come for the match. You get paid on the click.
      </h1>
      <p className="mt-4 max-w-2xl text-lg text-muted">
        Oja is not a store. It is the last comparison before someone opens Jumia, Konga, Slot,
        or a Jiji seller. That position is the product.
      </p>

      <section className="mt-10 grid gap-4 md:grid-cols-3" id="affiliate">
        {snapshot.plans.map((plan) => (
          <article className="card rounded-3xl p-6" key={plan.id}>
            <p className="text-xs uppercase tracking-[0.14em] text-muted">{plan.name}</p>
            <p className="mt-2 display text-3xl">{formatNaira(plan.priceNgn)}</p>
            <p className="text-sm text-muted">per month</p>
            <p className="mt-3 text-sm">{plan.blurb}</p>
            <ul className="mt-4 space-y-2 text-sm text-muted">
              {plan.features.map((feature) => (
                <li key={feature}>{feature}</li>
              ))}
            </ul>
          </article>
        ))}
      </section>

      <section className="mt-12 grid gap-6 md:grid-cols-2">
        <div>
          <h2 className="display text-3xl">Four revenue lines</h2>
          <ol className="mt-4 space-y-4 text-sm">
            <li>
              <strong>Affiliate CPA/CPC.</strong> Every “Go to Jumia” pass through{" "}
              <code>/go/:offerId</code>. Demo rates sit on each store — Jumia 6%, Konga 5%,
              Jiji 3%.
            </li>
            <li>
              <strong>Sponsored comparison slots.</strong> A merchant pays to sit above organic
              price sort, still labeled Sponsored.
            </li>
            <li>
              <strong>Price-alert premium.</strong> Email is free. Instant WhatsApp is the
              upgrade — the channel Nigerians actually read.
            </li>
            <li>
              <strong>Intelligence.</strong> Sell the matched price feed back to retailers and
              importers who want to know when Slot undercuts them.
            </li>
          </ol>
        </div>
        <div className="card rounded-3xl p-6">
          <p className="text-xs uppercase tracking-[0.16em] text-muted">Session ledger</p>
          <p className="mt-2 text-3xl font-semibold">{snapshot.clickCount} clicks</p>
          <p className="text-sm text-muted">
            Est. commission {formatNaira(snapshot.estimatedCommission)} · {snapshot.leads} leads
          </p>
          <ul className="mt-4 space-y-2 text-sm">
            {STORES.map((store) => (
              <li className="flex justify-between" key={store.id}>
                <span>{store.name}</span>
                <span className="text-muted">{Math.round(store.affiliateRate * 100)}% take</span>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="mt-12">
        <h2 className="display text-3xl">Book a slot</h2>
        <p className="mt-2 mb-5 max-w-xl text-muted">
          This writes a lead into the in-memory merchant queue. Wire Paystack or Flutterwave
          when you take it live.
        </p>
        <MerchantForm />
      </section>
    </div>
  );
}
