"use client";

import { useState, type FormEvent } from "react";

type ClassifyResult = {
  host: string;
  homepage: string;
  suggestedName: string;
  isNigerianWeb: boolean;
  isEcommerce: boolean;
  accepted: boolean;
  confidence: number;
  kind: string;
  categories: string[];
  reasons: string[];
  rejectReason?: string;
};

type IntegrateResult = {
  classification: ClassifyResult;
  site?: { id: string; name: string; status: string; domain: string };
  offersAdded: number;
  alreadyLive: boolean;
};

export function IntegrateStoreForm() {
  const [url, setUrl] = useState("");
  const [name, setName] = useState("");
  const [preview, setPreview] = useState<ClassifyResult | null>(null);
  const [result, setResult] = useState<IntegrateResult | null>(null);
  const [busy, setBusy] = useState(false);

  async function classify(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setResult(null);
    const response = await fetch("/api/stores/classify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });
    const data = (await response.json()) as ClassifyResult;
    setPreview(data);
    if (!name && data.suggestedName) setName(data.suggestedName);
    setBusy(false);
  }

  async function integrate() {
    setBusy(true);
    const response = await fetch("/api/stores/integrate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, name }),
    });
    const data = (await response.json()) as IntegrateResult;
    setResult(data);
    setPreview(data.classification);
    setBusy(false);
  }

  return (
    <div className="card rounded-3xl p-6">
      <p className="text-xs uppercase tracking-[0.16em] text-muted">Add a Nigerian ecommerce site</p>
      <h2 className="mt-1 text-xl font-semibold">Classify, then connect</h2>
      <p className="mt-2 text-sm text-muted">
        Paste a URL. Oja checks the directory first, then Nigerian and ecommerce signals. We do
        not scrape the live shop — a connected store gets a feed slot and sample offers on
        overlapping aisles.
      </p>
      <form className="mt-4 flex flex-col gap-3 md:flex-row" onSubmit={classify}>
        <input
          className="flex-1 rounded-2xl border border-line px-3 py-3 text-sm"
          onChange={(event) => setUrl(event.target.value)}
          placeholder="payporte.com or https://justgadgets.com.ng"
          value={url}
        />
        <button className="rounded-full bg-ink px-4 py-3 text-sm text-white" disabled={busy} type="submit">
          {busy ? "Checking…" : "Classify"}
        </button>
      </form>

      {preview ? (
        <div className="mt-5 rounded-2xl bg-paper p-4 text-sm">
          <p className="font-medium">
            {preview.host || url} · {Math.round(preview.confidence * 100)}% confidence
          </p>
          <p className="mt-1 text-muted">
            {preview.isNigerianWeb ? "Nigerian web" : "Not Nigerian"} ·{" "}
            {preview.isEcommerce ? "Ecommerce" : "Not ecommerce"} · {preview.kind}
          </p>
          <ul className="mt-2 list-disc pl-5 text-muted">
            {preview.reasons.map((reason) => (
              <li key={reason}>{reason}</li>
            ))}
          </ul>
          {preview.rejectReason ? <p className="mt-2 text-clay">{preview.rejectReason}</p> : null}
          {preview.accepted ? (
            <div className="mt-4 flex flex-col gap-3 md:flex-row">
              <input
                className="flex-1 rounded-2xl border border-line bg-white px-3 py-2"
                onChange={(event) => setName(event.target.value)}
                placeholder="Display name"
                value={name}
              />
              <button
                className="rounded-full bg-green px-4 py-2 text-sm font-semibold text-white"
                disabled={busy}
                onClick={integrate}
                type="button"
              >
                Integrate into compare
              </button>
            </div>
          ) : null}
        </div>
      ) : null}

      {result?.site ? (
        <p className="mt-4 text-sm">
          {result.alreadyLive
            ? `${result.site.name} is already live on the engine.`
            : `Connected ${result.site.name}. ${result.offersAdded} sample offers attached.`}{" "}
          <a className="text-green" href={`/stores/${result.site.id}`}>
            Open store
          </a>
        </p>
      ) : null}
    </div>
  );
}
