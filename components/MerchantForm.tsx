"use client";

import { useState } from "react";

export function MerchantForm() {
  const [status, setStatus] = useState<"idle" | "saving" | "done">("idle");

  async function onSubmit(formData: FormData) {
    setStatus("saving");
    await fetch("/api/leads", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        business: formData.get("business"),
        email: formData.get("email"),
        plan: formData.get("plan"),
        message: formData.get("message"),
      }),
    });
    setStatus("done");
  }

  if (status === "done") {
    return (
      <p className="card rounded-3xl p-6">
        Received. A merchant success note will go to that inbox — in production this opens a
        Paystack subscription and a sponsored-slot calendar.
      </p>
    );
  }

  return (
    <form action={onSubmit} className="card grid gap-3 rounded-3xl p-6 md:grid-cols-2" id="contact">
      <input
        className="rounded-2xl border border-line px-3 py-3 text-sm"
        name="business"
        placeholder="Store or brand name"
        required
      />
      <input
        className="rounded-2xl border border-line px-3 py-3 text-sm"
        name="email"
        placeholder="Work email"
        required
        type="email"
      />
      <select className="rounded-2xl border border-line px-3 py-3 text-sm" defaultValue="growth" name="plan">
        <option value="starter">Starter · ₦45,000/mo</option>
        <option value="growth">Growth · ₦120,000/mo</option>
        <option value="intelligence">Intelligence · ₦350,000/mo</option>
      </select>
      <textarea
        className="rounded-2xl border border-line px-3 py-3 text-sm md:col-span-2"
        name="message"
        placeholder="What do you want to promote — phones, power, a category takeover?"
        rows={3}
      />
      <button className="rounded-full bg-green px-4 py-3 text-sm font-semibold text-white md:col-span-2" type="submit">
        {status === "saving" ? "Sending…" : "Request a merchant slot"}
      </button>
    </form>
  );
}
