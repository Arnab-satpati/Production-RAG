"use client";

import ReactMarkdown from "react-markdown";
import type { QueryResponse } from "@/lib/api";

interface Props {
  role: "user" | "assistant";
  content: string;
  response?: QueryResponse;
}

export function ChatMessage({ role, content, response }: Props) {
  return (
    <div className={`flex gap-3 ${role === "user" ? "flex-row-reverse" : ""}`}>
      <div
        className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm font-semibold shrink-0 ${
          role === "assistant"
            ? "bg-blue-600 text-white"
            : "bg-zinc-800 text-zinc-200"
        }`}
      >
        {role === "assistant" ? "R" : "U"}
      </div>
      <div
        className={`max-w-[80%] rounded-xl px-4 py-3 text-sm leading-relaxed ${
          role === "assistant"
            ? "bg-zinc-900 border border-zinc-800"
            : "bg-blue-600 text-white"
        }`}
      >
        {role === "assistant" ? (
          <div className="prose prose-invert prose-sm max-w-none">
            <ReactMarkdown>{content}</ReactMarkdown>
          </div>
        ) : (
          <p>{content}</p>
        )}
        {response && response.sources.length > 0 && (
          <div className="mt-3 pt-3 border-t border-zinc-800 text-xs text-zinc-500">
            <span>Sources: </span>
            {response.sources.map((s, i) => (
              <span
                key={i}
                className="inline-block bg-zinc-800 px-2 py-0.5 rounded mr-1 mb-1"
              >
                {s.source.split("/").pop()} ({(s.score * 100).toFixed(0)}%)
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
