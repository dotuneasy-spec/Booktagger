import { NextResponse } from "next/server";
import { recordLead } from "../../../lib/affiliate";

export async function POST(request: Request) {
  const body = (await request.json()) as {
    business?: string;
    email?: string;
    plan?: "starter" | "growth" | "intelligence";
    message?: string;
  };
  if (!body.business || !body.email) {
    return NextResponse.json({ error: "business and email required" }, { status: 400 });
  }
  const lead = recordLead({
    business: body.business,
    email: body.email,
    plan: body.plan ?? "growth",
    message: body.message ?? "",
  });
  return NextResponse.json(lead);
}
