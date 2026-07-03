"use client";

import { useState, useRef } from "react";
import {
  FileText,
  Upload,
  Loader2,
  CheckCircle2,
  File,
  X,
} from "lucide-react";
import { ingestText } from "@/lib/api";

interface Status {
  type: "success" | "error";
  message: string;
}

export function Sidebar() {
  const [text, setText] = useState("");
  const [status, setStatus] = useState<Status | null>(null);
  const [loading, setLoading] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleIngestText = async () => {
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

  const handleIngestFiles = async () => {
    if (files.length === 0) return;
    setLoading(true);
    setStatus(null);

    let totalChunks = 0;
    let errors = 0;

    for (const file of files) {
      try {
        const formData = new FormData();
        formData.append("file", file);

        const res = await fetch("/api/ingest-file", {
          method: "POST",
          body: formData,
        });

        if (res.ok) {
          const data = await res.json();
          totalChunks += data.chunks_ingested;
        } else {
          errors++;
        }
      } catch {
        errors++;
      }
    }

    if (errors === 0) {
      setStatus({
        type: "success",
        message: `Ingested ${totalChunks} chunk${totalChunks !== 1 ? "s" : ""} from ${files.length} file${files.length !== 1 ? "s" : ""}`,
      });
    } else {
      setStatus({
        type: "error",
        message: `${files.length - errors} succeeded, ${errors} failed`,
      });
    }

    setFiles([]);
    setLoading(false);
  };

  const addFiles = (newFiles: FileList | null) => {
    if (!newFiles) return;
    setFiles((prev) => [...prev, ...Array.from(newFiles)]);
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    addFiles(e.dataTransfer.files);
  };

  return (
    <aside className="w-72 bg-zinc-950 border-r border-zinc-800 flex flex-col p-5 gap-5 overflow-y-auto">
      <div className="flex items-center gap-2.5 text-blue-500 font-semibold">
        <FileText size={20} />
        <span>Production RAG</span>
      </div>

      {/* File Upload Section */}
      <section>
        <h3 className="text-xs uppercase tracking-wider text-zinc-500 mb-3">
          Upload Files
        </h3>
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-colors ${
            dragOver
              ? "border-blue-500 bg-blue-500/10"
              : "border-zinc-700 hover:border-zinc-500"
          }`}
        >
          <Upload size={20} className="mx-auto mb-2 text-zinc-500" />
          <p className="text-xs text-zinc-400">
            Drag & drop or <span className="text-blue-400">browse</span>
          </p>
          <p className="text-[10px] text-zinc-600 mt-1">
            PDF, DOCX, MD, TXT, HTML, CSV
          </p>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.doc,.md,.txt,.html,.htm,.csv,.xlsx,.xls,.py,.js,.ts,.go,.java,.rb"
          onChange={(e) => addFiles(e.target.files)}
          className="hidden"
        />

        {files.length > 0 && (
          <div className="mt-2 space-y-1">
            {files.map((file, i) => (
              <div
                key={i}
                className="flex items-center justify-between bg-zinc-900 rounded px-2 py-1.5 text-xs"
              >
                <div className="flex items-center gap-1.5 min-w-0">
                  <File size={12} className="text-zinc-500 shrink-0" />
                  <span className="truncate text-zinc-300">{file.name}</span>
                </div>
                <button
                  onClick={() => removeFile(i)}
                  className="text-zinc-500 hover:text-red-400 shrink-0 ml-1"
                >
                  <X size={12} />
                </button>
              </div>
            ))}
            <button
              onClick={handleIngestFiles}
              disabled={loading}
              className="w-full mt-1 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-xs font-medium transition-colors disabled:opacity-40"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <Loader2 size={12} className="animate-spin" /> Uploading...
                </span>
              ) : (
                `Upload ${files.length} file${files.length !== 1 ? "s" : ""}`
              )}
            </button>
          </div>
        )}
      </section>

      {/* Text Ingest Section */}
      <section>
        <h3 className="text-xs uppercase tracking-wider text-zinc-500 mb-3">
          Or Paste Text
        </h3>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste text to ingest..."
          className="w-full h-24 bg-zinc-900 border border-zinc-800 rounded-lg p-3 text-sm text-zinc-200 placeholder-zinc-600 resize-y outline-none focus:border-blue-600 transition-colors"
        />
        <button
          onClick={handleIngestText}
          disabled={loading || !text.trim()}
          className="w-full mt-2 py-2.5 bg-zinc-800 hover:bg-blue-600 border border-zinc-700 hover:border-blue-600 rounded-lg text-sm font-medium transition-all disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <Loader2 size={14} className="animate-spin" /> Ingesting...
            </span>
          ) : (
            "Ingest Text"
          )}
        </button>
      </section>

      {/* Status */}
      {status && (
        <div
          className={`text-xs flex items-center gap-1.5 ${
            status.type === "success" ? "text-green-500" : "text-red-500"
          }`}
        >
          {status.type === "success" && <CheckCircle2 size={12} />}
          {status.message}
        </div>
      )}

      {/* System Info */}
      <section className="mt-auto">
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
