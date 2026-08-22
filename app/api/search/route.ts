import { NextResponse } from "next/server";
import { searchProducts } from "../../../lib/search";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const result = searchProducts(searchParams.get("q") ?? "", {
    storeId: searchParams.get("store") ?? undefined,
    condition: searchParams.get("condition") ?? undefined,
    category: searchParams.get("category") ?? undefined,
    sort: (searchParams.get("sort") as "match" | "price" | "savings") ?? "match",
  });
  return NextResponse.json(result);
}
