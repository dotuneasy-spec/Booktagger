import Link from "next/link";

export default function NotFound() {
  return (
    <div className="py-20 text-center">
      <h1 className="display text-4xl">That product is not on the engine yet.</h1>
      <p className="mt-3 text-muted">Try a search or go back to the market.</p>
      <Link className="mt-6 inline-block text-green" href="/">
        Return to Oja
      </Link>
    </div>
  );
}
