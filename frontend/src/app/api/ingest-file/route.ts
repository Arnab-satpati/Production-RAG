import { NextRequest, NextResponse } from "next/server";
import { RAG_API_URL } from "@/lib/api";

export async function POST(req: NextRequest) {
  const formData = await req.formData();

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 120_000);

  try {
    const res = await fetch(`${RAG_API_URL}/api/v1/ingest/file`, {
      method: "POST",
      body: formData,
      signal: controller.signal,
    });
    clearTimeout(timeout);
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (e) {
    clearTimeout(timeout);
    return NextResponse.json(
      { detail: "Upload timed out or failed" },
      { status: 504 }
    );
  }
}
