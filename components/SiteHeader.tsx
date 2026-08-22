import Link from "next/link";
import { SearchBox } from "./SearchBox";

export function SiteHeader({ compact = false }: { compact?: boolean }) {
  return (
    <header className="sticky top-0 z-30 border-b border-line/80 bg-paper/85 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center gap-4 px-4 py-3">
        <Link className="display text-2xl tracking-tight" href="/">
          Oja
        </Link>
        {compact ? (
          <div className="hidden min-w-0 flex-1 md:block">
            <SearchBox size="sm" />
          </div>
        ) : null}
        <nav className="ml-auto flex items-center gap-4 text-sm">
          <Link className="hover:text-green" href="/stores">
            Stores
          </Link>
          <Link className="hover:text-green" href="/deals">
            Deals
          </Link>
          <Link className="hover:text-green" href="/how-it-works">
            Matching
          </Link>
          <Link className="hidden hover:text-green sm:inline" href="/merchants">
            For merchants
          </Link>
        </nav>
      </div>
    </header>
  );
}
