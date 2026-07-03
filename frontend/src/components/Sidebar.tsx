"use client";

import { useState } from "react";
import { FileText, Loader2, CheckCircle2 } from "lucide-react";
import { ingestText } from "@/lib/api";

export function Sidebar() {
  const [text, setText] = useState("");
  const [status, setStatus] = useState<{
    type: "success" | "error";
    message: string;
  } | null>(null);
  const [loading, setLoading] = useState(false);

  const handleIngest = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setStatus(null);
    try {
      const res = await ingestText(text);
      setStatus({
        type: "success",
        message: `Ingested ${res.chunks_ingested} chunk${res.chunks_ingested !== 1 ? "s" : ""}`,
      });
      setText("");
    } catch (e: unknown) {
      setStatus({
        type: "error",
        message: e instanceof Error ? e.message : "Failed to ingest",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <aside className="w-72 bg-zinc-950 border-r border-zinc-800 flex flex-col p-5 gap-6 overflow-y-auto">
      <div className="flex items-center gap-2.5 text-blue-500 font-semibold">
        <FileText size={20} />
        <span>Production RAG</span>
      </div>

      <section>
        <h3 className="text-xs uppercase tracking-wider text-zinc-500 mb-3">
          Ingest Documents
        </h3>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste text to ingest..."
          className="w-full h-28 bg-zinc-900 border border-zinc-800 rounded-lg p-3 text-sm text-zinc-200 placeholder-zinc-600 resize-y outline-none focus:border-blue-600 transition-colors"
        />
        <button
          onClick={handleIngest}
          disabled={loading || !text.trim()}
          className="w-full mt-2.5 py-2.5 bg-zinc-800 hover:bg-blue-600 border border-zinc-700 hover:border-blue-600 rounded-lg text-sm font-medium transition-all disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <Loader2 size={14} className="animate-spin" /> Ingesting...
            </span>
          ) : (
            "Ingest"
          )}
        </button>
        {status && (
          <div
            className={`mt-2 text-xs flex items-center gap-1.5 ${
              status.type === "success" ? "text-green-500" : "text-red-500"
            }`}
          >
            {status.type === "success" && <CheckCircle2 size={12} />}
            {status.message}
          </div>
        )}
      </section>

      <section>
        <h3 className="text-xs uppercase tracking-wider text-zinc-500 mb-3">
          System
        </h3>
        <SystemInfo />
      </section>
    </aside>
  );
}

function SystemInfo() {
  const [info, setInfo] = useState<string | null>(null);

  useState(() => {
    fetch("/api/health")
      .then((r) => r.json())
      .then((d) => {
        const services = Object.entries(d.services)
          .map(([k, v]) => `${k}: ${v}`)
          .join("\n");
        setInfo(`Status: ${d.status}\nVersion: ${d.version}\n${services}`);
      })
      .catch(() => setInfo("API unreachable"));
  });

  return (
    <pre className="text-xs text-zinc-500 whitespace-pre-wrap leading-relaxed font-sans">
      {info || "Loading..."}
    </pre>
  );
}
