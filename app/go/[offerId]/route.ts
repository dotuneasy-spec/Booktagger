import { NextResponse } from "next/server";
import { outboundUrl, recordClick } from "../../../lib/affiliate";

export async function GET(
  request: Request,
  context: { params: Promise<{ offerId: string }> },
) {
  const { offerId } = await context.params;
  const source = new URL(request.url).searchParams.get("src") ?? "web";
  const click = recordClick(offerId, source);
  const target = outboundUrl(offerId, source);
  if (!click || !target) {
    return NextResponse.json({ error: "Unknown offer" }, { status: 404 });
  }
  return NextResponse.redirect(target, 302);
}
