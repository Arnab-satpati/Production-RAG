import { NextResponse } from "next/server";
import { RAG_API_URL } from "@/lib/api";

export async function GET() {
  try {
    const res = await fetch(`${RAG_API_URL}/health`);
    const data = await res.json();
    return NextResponse.json(data);
  } catch {
    return NextResponse.json(
      { status: "unreachable", version: "unknown", services: {} },
      { status: 503 }
    );
  }
}
