import { PRODUCTS } from "../../data/catalog";
import { AlertForm } from "../../components/AlertForm";

export default function AlertsPage() {
  const featured = PRODUCTS.find((product) => product.id === "macbook-air-m2") ?? PRODUCTS[0];

  return (
    <div className="py-8">
      <h1 className="display text-4xl">Price alerts</h1>
      <p className="mt-3 max-w-2xl text-muted">
        Naira moves weekly. Free alerts go to email. WhatsApp delivery is the paid wedge —
        same matching engine, just faster when Jumia drops an iPhone.
      </p>
      <div className="mt-8 max-w-2xl">
        <AlertForm productId={featured.id} productTitle={featured.title} />
      </div>
    </div>
  );
}
