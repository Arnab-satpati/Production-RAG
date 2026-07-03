"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Loader2 } from "lucide-react";
import { ChatMessage } from "./ChatMessage";
import { queryRAG, type QueryResponse } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  response?: QueryResponse;
}

export function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hello! I can answer questions based on your ingested documents. Try asking something, or paste text in the sidebar to ingest first.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const q = input.trim();
    if (!q || loading) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: q }]);
    setLoading(true);

    try {
      const res = await queryRAG({ question: q, top_k: 5 });
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.answer, response: res },
      ]);
    } catch (e: unknown) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Error: ${e instanceof Error ? e.message : "Query failed"}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex-1 flex flex-col min-w-0">
      <div className="px-6 py-5 border-b border-zinc-800">
        <h1 className="text-lg font-medium">
          Ask anything about your documents
        </h1>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-6 flex flex-col gap-6">
        {messages.map((msg, i) => (
          <ChatMessage key={i} {...msg} />
        ))}
        {loading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-sm font-semibold text-white shrink-0">
              R
            </div>
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl px-4 py-3">
              <div className="flex gap-1.5">
                <span className="w-1.5 h-1.5 bg-zinc-600 rounded-full animate-bounce [animation-delay:0ms]" />
                <span className="w-1.5 h-1.5 bg-zinc-600 rounded-full animate-bounce [animation-delay:200ms]" />
                <span className="w-1.5 h-1.5 bg-zinc-600 rounded-full animate-bounce [animation-delay:400ms]" />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <form
        onSubmit={handleSubmit}
        className="px-6 py-5 border-t border-zinc-800 bg-zinc-950 flex gap-3"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question..."
          disabled={loading}
          className="flex-1 bg-zinc-900 border border-zinc-800 rounded-xl px-4 py-3 text-sm text-zinc-200 placeholder-zinc-600 outline-none focus:border-blue-600 transition-colors disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="w-11 h-11 bg-blue-600 hover:bg-blue-500 rounded-xl flex items-center justify-center text-white transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {loading ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
        </button>
      </form>
    </main>
  );
}
