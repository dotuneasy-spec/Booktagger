import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { classifySite } from "./classify-site";
import { classifyUrl, directoryStats, integrateSite, searchSites } from "./registry";
import { searchProducts } from "./search";

describe("ecommerce directory", () => {
  it("indexes Nigerian shops by name, kind, and city", () => {
    const pharmacies = searchSites({ query: "pharmacy", kind: "pharmacy" });
    assert.ok(pharmacies.some((site) => site.id === "healthplus"));
    const slot = searchSites({ query: "slot lagos" });
    assert.equal(slot[0]?.id, "slot");
    assert.ok(directoryStats().total >= 30);
  });

  it("classifies a known directory domain as ecommerce", () => {
    const result = classifyUrl("https://payporte.com/phones");
    assert.equal(result.accepted, true);
    assert.equal(result.suggestedId, "payporte");
    assert.ok(result.signals.includes("in-directory"));
  });

  it("accepts a new .ng shop host", () => {
    const result = classifySite("https://shop.ikejaphones.ng");
    assert.equal(result.isNigerianWeb, true);
    assert.equal(result.isEcommerce, true);
    assert.equal(result.accepted, true);
    assert.equal(result.kind, "electronics");
  });

  it("rejects news and betting hosts", () => {
    const news = classifySite("https://nairaland.com");
    assert.equal(news.accepted, false);
    assert.equal(news.isEcommerce, false);
    const bet = classifySite("https://sportybet.com");
    assert.equal(bet.accepted, false);
  });

  it("integrates a feed-ready store onto price compare", () => {
    const before = searchProducts("oraimo freepods 4").hits[0];
    const storesBefore = new Set(before?.offers.map((offer) => offer.storeId) ?? []);
    const result = integrateSite("https://oraimo.com", "Oraimo Official");
    assert.ok(result.site);
    assert.equal(result.site?.status, "live");
    assert.ok(result.offersAdded > 0 || result.alreadyLive);
    const after = searchProducts("oraimo freepods 4").hits[0];
    const storesAfter = new Set(after?.offers.map((offer) => offer.storeId) ?? []);
    assert.ok(storesAfter.has("oraimo") || storesBefore.has("oraimo"));
    assert.ok(storesAfter.size >= storesBefore.size);
  });
});
