"use client";

import { useRouter } from "next/navigation";
import { useEffect, useId, useState } from "react";
import { SearchIcon } from "./icons";

type Suggestion = {
  slug: string;
  title: string;
  brand: string;
  lowestPrice: number;
  score: number;
};

export function SearchBox({
  initialQuery = "",
  size = "lg",
  autoFocus = false,
}: {
  initialQuery?: string;
  size?: "lg" | "sm";
  autoFocus?: boolean;
}) {
  const router = useRouter();
  const listId = useId();
  const [query, setQuery] = useState(initialQuery);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (query.trim().length < 2) return;
    const handle = window.setTimeout(async () => {
      const response = await fetch(`/api/suggest?q=${encodeURIComponent(query)}`);
      if (!response.ok) return;
      const data = (await response.json()) as { suggestions: Suggestion[] };
      setSuggestions(data.suggestions);
      setOpen(true);
    }, 160);
    return () => window.clearTimeout(handle);
  }, [query]);

  const visibleSuggestions = query.trim().length < 2 ? [] : suggestions;

  function go(next = query) {
    const value = next.trim();
    if (!value) return;
    setOpen(false);
    router.push(`/search?q=${encodeURIComponent(value)}`);
  }

  return (
    <div className="relative w-full">
      <form
        className={`card flex items-center gap-3 rounded-full px-4 ${size === "lg" ? "h-16" : "h-12"}`}
        onSubmit={(event) => {
          event.preventDefault();
          go();
        }}
      >
        <SearchIcon className="h-5 w-5 shrink-0 text-muted" />
        <input
          aria-autocomplete="list"
          aria-controls={listId}
          autoFocus={autoFocus}
          className="h-full w-full bg-transparent text-base outline-none placeholder:text-muted"
          onChange={(event) => setQuery(event.target.value)}
          onFocus={() => visibleSuggestions.length > 0 && setOpen(true)}
          placeholder="Try Infinix Note 40 Pro, Firman 2.5kVA, Oraimo FreePods 4"
          value={query}
        />
        <button
          className="rounded-full bg-green px-4 py-2 text-sm font-semibold text-white hover:bg-green-ink"
          type="submit"
        >
          Compare
        </button>
      </form>
      {open && visibleSuggestions.length > 0 ? (
        <ul
          className="card absolute z-20 mt-2 w-full overflow-hidden rounded-2xl"
          id={listId}
        >
          {visibleSuggestions.map((item) => (
            <li key={item.slug}>
              <button
                className="flex w-full items-center justify-between px-4 py-3 text-left hover:bg-paper"
                onClick={() => {
                  setQuery(item.title);
                  router.push(`/product/${item.slug}`);
                }}
                type="button"
              >
                <span>
                  <span className="block text-sm font-medium">{item.title}</span>
                  <span className="text-xs text-muted">{item.brand}</span>
                </span>
                <span className="text-xs text-green">
                  {Math.round(item.score * 100)}% match
                </span>
              </button>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}
