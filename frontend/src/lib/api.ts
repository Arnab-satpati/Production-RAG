export const RAG_API_URL = process.env.RAG_API_URL || "http://127.0.0.1:8000";

export interface QueryRequest {
  question: string;
  top_k?: number;
  filter_source?: string;
}

export interface SourceChunk {
  content: string;
  score: number;
  source: string;
  chunk_id: string;
}

export interface QueryResponse {
  answer: string;
  sources: SourceChunk[];
  metadata: {
    latency_ms: number;
    model: string;
    tokens_generated: number;
    retrieved_chunks: number;
  };
}

export interface IngestResponse {
  chunks_ingested: number;
  source: string;
  status: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  services: Record<string, string>;
}

export async function queryRAG(req: QueryRequest): Promise<QueryResponse> {
  const res = await fetch("/api/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(err.detail || "Query failed");
  }
  return res.json();
}

export async function ingestText(
  text: string,
  metadata?: Record<string, string>
): Promise<IngestResponse> {
  const res = await fetch("/api/ingest", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, metadata }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Ingest failed" }));
    throw new Error(err.detail || "Ingest failed");
  }
  return res.json();
}

export async function getHealth(): Promise<HealthResponse> {
  const res = await fetch("/api/health");
  if (!res.ok) throw new Error("Health check failed");
  return res.json();
}
