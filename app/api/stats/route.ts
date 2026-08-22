import { NextResponse } from "next/server";
import { monetizationSnapshot } from "../../../lib/affiliate";

export async function GET() {
  return NextResponse.json(monetizationSnapshot());
}
