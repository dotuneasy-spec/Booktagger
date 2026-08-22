import { NextResponse } from "next/server";
import { suggest } from "../../../lib/search";

export async function GET(request: Request) {
  const query = new URL(request.url).searchParams.get("q") ?? "";
  return NextResponse.json({ suggestions: suggest(query) });
}
