import { NextResponse } from "next/server";
import { recordAlert } from "../../../lib/affiliate";

export async function POST(request: Request) {
  const body = (await request.json()) as {
    productId?: string;
    email?: string;
    targetPriceNgn?: number;
    channel?: "email" | "whatsapp";
  };
  if (!body.productId || !body.email) {
    return NextResponse.json({ error: "productId and email required" }, { status: 400 });
  }
  const alert = recordAlert({
    productId: body.productId,
    email: body.email,
    targetPriceNgn: body.targetPriceNgn,
    channel: body.channel === "whatsapp" ? "whatsapp" : "email",
  });
  return NextResponse.json(alert);
}
