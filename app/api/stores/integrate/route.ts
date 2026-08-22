import { NextResponse } from "next/server";
import { integrateSite } from "../../../../lib/registry";

export async function POST(request: Request) {
  const body = (await request.json()) as { url?: string; name?: string };
  if (!body.url) return NextResponse.json({ error: "url required" }, { status: 400 });
  const result = integrateSite(body.url, body.name);
  if (!result.site) {
    return NextResponse.json(result, { status: 422 });
  }
  return NextResponse.json(result);
}
