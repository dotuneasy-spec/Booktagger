"use client";

import { useState } from "react";

export function AlertForm({
  productId,
  productTitle,
}: {
  productId: string;
  productTitle: string;
}) {
  const [status, setStatus] = useState<"idle" | "saving" | "done">("idle");

  async function onSubmit(formData: FormData) {
    setStatus("saving");
    await fetch("/api/alerts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        productId,
        email: formData.get("email"),
        targetPriceNgn: Number(formData.get("targetPrice")) || undefined,
        channel: formData.get("channel"),
      }),
    });
    setStatus("done");
  }

  if (status === "done") {
    return (
      <p className="card rounded-3xl p-5 text-sm">
        Alert set for {productTitle}. We will ping you when a store undercuts your number.
      </p>
    );
  }

  return (
    <form action={onSubmit} className="card rounded-3xl p-5">
      <p className="text-xs uppercase tracking-[0.16em] text-muted">Price alert</p>
      <p className="mt-1 font-medium">Get this cheaper. Free email, WhatsApp on Growth.</p>
      <div className="mt-4 grid gap-3 md:grid-cols-3">
        <input
          className="rounded-2xl border border-line bg-white px-3 py-3 text-sm outline-none"
          name="email"
          placeholder="you@email.com"
          required
          type="email"
        />
        <input
          className="rounded-2xl border border-line bg-white px-3 py-3 text-sm outline-none"
          name="targetPrice"
          placeholder="Target ₦ price"
          type="number"
        />
        <select
          className="rounded-2xl border border-line bg-white px-3 py-3 text-sm outline-none"
          defaultValue="email"
          name="channel"
        >
          <option value="email">Email</option>
          <option value="whatsapp">WhatsApp (premium)</option>
        </select>
      </div>
      <button
        className="mt-4 rounded-full bg-green px-4 py-2 text-sm font-semibold text-white"
        disabled={status === "saving"}
        type="submit"
      >
        {status === "saving" ? "Saving…" : "Watch this price"}
      </button>
    </form>
  );
}
