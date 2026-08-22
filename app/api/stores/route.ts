import { NextResponse } from "next/server";
import { directoryStats, searchSites } from "../../../lib/registry";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const sites = searchSites({
    query: searchParams.get("q") ?? undefined,
    kind: searchParams.get("kind") ?? undefined,
    status: searchParams.get("status") ?? undefined,
    city: searchParams.get("city") ?? undefined,
  });
  return NextResponse.json({ stats: directoryStats(), sites });
}
