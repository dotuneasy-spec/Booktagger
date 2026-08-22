import { NextResponse } from "next/server";
import { classifyUrl } from "../../../../lib/registry";

export async function POST(request: Request) {
  const body = (await request.json()) as { url?: string };
  if (!body.url) return NextResponse.json({ error: "url required" }, { status: 400 });
  return NextResponse.json(classifyUrl(body.url));
}
