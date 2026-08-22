import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { extractProduct } from "./extract";
import { clusterListings, sameProduct, scoreMatch } from "./match";
import { searchProducts } from "./search";

describe("product matching", () => {
  it("treats messy A55 titles as the same phone", () => {
    const query = extractProduct("samsung a55 256gb");
    const jumia = extractProduct("Samsung Galaxy A55 5G 8/256 - Official Store");
    const jiji = extractProduct("Brand New A55 8GB RAM 256GB ROM Navy Lagos");
    const slot = extractProduct("Samsung Galaxy A55 5G 8GB RAM 256GB ROM");

    assert.ok(sameProduct(query, jumia));
    assert.ok(sameProduct(query, jiji));
    assert.ok(sameProduct(query, slot));
    assert.ok(scoreMatch(query, jumia).score > 0.5);
  });

  it("does not collapse Galaxy A55 into A16", () => {
    const a55 = extractProduct("Samsung Galaxy A55 8GB 256GB");
    const a16 = extractProduct("Samsung Galaxy A16 6GB 128GB");
    assert.equal(sameProduct(a55, a16), false);
  });

  it("keeps Infinix Note 40 Pro away from Hot 40i", () => {
    const note = extractProduct("infinix note 40 pro 256");
    const hot = extractProduct("Infinix Hot 40i 128GB");
    assert.equal(sameProduct(note, hot), false);
    const results = searchProducts("infinix note 40 pro 256");
    assert.equal(results.hits[0]?.product.id, "infinix-note-40-pro");
    assert.ok(!results.hits.some((hit) => hit.product.id === "infinix-hot-40i" && hit.score > 0.7));
  });

  it("separates 2.5kVA generators from 3.5kVA", () => {
    const query = extractProduct("firman 2.5kva generator");
    const match = extractProduct("Sumec Firman 2.5kVA Generator Brand New");
    const other = extractProduct("Elepaq 3.5kVA Generator");
    assert.ok(sameProduct(query, match));
    assert.equal(sameProduct(query, other), false);
  });

  it("prefers UK used when the shopper asks for tokunbo", () => {
    const results = searchProducts("uk used iphone 13 128");
    assert.ok(results.hits.length > 0);
    assert.equal(results.query.extracted.condition, "uk-used");
    const first = results.hits.find((hit) => hit.product.id === "iphone-13-128");
    assert.ok(first);
    assert.ok(first.offers.some((offer) => offer.condition === "uk-used"));
  });

  it("clusters store-specific titles into one product family", () => {
    const listings = [
      "Samsung Galaxy A55 5G 8/256 - Official Store",
      "A55 256gb jumia promo",
      "Galaxy A55 8GB RAM 256GB ROM",
      "Elepaq 3.5kVA Generator",
    ].map((title, index) => ({
      id: String(index),
      extracted: extractProduct(title),
    }));

    const clusters = clusterListings(listings);
    const a55Cluster = clusters.find((group) => group.length >= 3);
    assert.ok(a55Cluster);
    assert.equal(a55Cluster?.length, 3);
  });

  it("returns multiple Nigerian stores for a popular query", () => {
    const results = searchProducts("oraimo freepods 4");
    const hit = results.hits[0];
    assert.ok(hit);
    assert.ok(hit.storeCount >= 4);
    assert.ok(hit.lowestPrice < hit.highestPrice);
  });
});
