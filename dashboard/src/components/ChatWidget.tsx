"use client";

import { useEffect, useRef, useState } from "react";
import { Send, Trash2, Sparkles, MessageCircle, X } from "lucide-react";
import { api } from "@/lib/api";
import { useSettings } from "@/lib/useSettings";

type Msg = { role: "user" | "assistant"; content: string };

const SUGGESTIONS = [
  "Should I water today?",
  "Why are my leaves yellowing?",
  "When should I repot?",
];

export default function ChatWidget() {
  const { settings } = useSettings();
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, open]);

  async function send() {
    const text = input.trim();
    if (!text || sending) return;
    setSending(true);
    setMessages((m) => [...m, { role: "user", content: text }]);
    setInput("");
    try {
      const { reply } = await api.chat(text, {
        plant_name: settings.plantName,
        species: settings.species === "Unspecified" ? undefined : settings.species,
      });
      setMessages((m) => [...m, { role: "assistant", content: reply }]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: `Error: ${err instanceof Error ? err.message : "unknown"}` },
      ]);
    } finally {
      setSending(false);
    }
  }

  async function clear() {
    setMessages([]);
    try { await api.resetChat(); } catch { /* ignore */ }
  }

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        aria-label="Open Bonsai Assistant chat"
        className="fixed bottom-24 right-4 z-50 flex items-center gap-2 rounded-full bg-[var(--green)] text-black font-semibold pl-4 pr-5 py-3 shadow-lg shadow-black/40 active:scale-95 transition-transform"
      >
        <MessageCircle size={20} />
        Ask
      </button>
    );
  }

  return (
    <>
      <div
        onClick={() => setOpen(false)}
        className="fixed inset-0 z-[60] bg-black/50 backdrop-blur-[2px]"
        aria-hidden
      />
      <div
        role="dialog"
        aria-label="Bonsai Assistant chat"
        className="fixed z-[70] inset-x-3 bottom-3 sm:inset-x-auto sm:right-4 sm:bottom-4 sm:w-[380px] flex flex-col h-[70vh] sm:h-[560px] bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl shadow-2xl shadow-black/50 overflow-hidden animate-[chatIn_0.18s_ease]"
      >
        <header className="flex items-center justify-between px-4 py-3 border-b border-[var(--border)]">
          <div>
            <p className="text-[11px] text-[var(--text-muted)] flex items-center gap-1">
              <Sparkles size={11} /> Powered by Claude
            </p>
            <h2 className="text-base font-bold leading-tight">🌱 Bonsai Assistant</h2>
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={clear}
              className="text-[var(--text-muted)] hover:text-[var(--red)] p-2 rounded-lg transition-colors"
              aria-label="Clear conversation"
            >
              <Trash2 size={17} />
            </button>
            <button
              onClick={() => setOpen(false)}
              className="text-[var(--text-muted)] hover:text-[var(--text)] p-2 rounded-lg transition-colors"
              aria-label="Close chat"
            >
              <X size={18} />
            </button>
          </div>
        </header>

        <div ref={scrollRef} className="flex-1 overflow-y-auto px-3 py-3 space-y-3">
          {messages.length === 0 && (
            <div className="text-center text-[var(--text-muted)] mt-6 px-3">
              <p className="text-sm leading-relaxed">
                Ask anything about {settings.plantName || "your bonsai"}. I can see its live
                moisture, watering history, and current state.
              </p>
              <div className="mt-5 space-y-2 text-xs">
                {SUGGESTIONS.map((q) => (
                  <button
                    key={q}
                    onClick={() => setInput(q)}
                    className="block w-full bg-[var(--bg)] border border-[var(--border)] rounded-xl px-4 py-2 text-[var(--text-dim)] hover:bg-[var(--bg-card-hover)] transition-colors"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}
          {messages.map((m, i) => (
            <div
              key={i}
              className={`max-w-[85%] rounded-2xl px-4 py-2 text-sm leading-relaxed whitespace-pre-wrap ${
                m.role === "user"
                  ? "ml-auto bg-[var(--green)] text-black"
                  : "mr-auto bg-[var(--bg)] border border-[var(--border)]"
              }`}
            >
              {m.content}
            </div>
          ))}
          {sending && (
            <div className="mr-auto bg-[var(--bg)] border border-[var(--border)] rounded-2xl px-4 py-2 text-sm text-[var(--text-muted)]">
              thinking…
            </div>
          )}
        </div>

        <div className="px-3 py-3 border-t border-[var(--border)]">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && send()}
              placeholder="Ask about your bonsai…"
              disabled={sending}
              autoFocus
              className="flex-1 bg-[var(--bg)] border border-[var(--border)] rounded-xl px-4 py-3 text-sm placeholder:text-[var(--text-muted)] focus:outline-none focus:border-[var(--green)]"
            />
            <button
              onClick={send}
              disabled={sending || !input.trim()}
              className="bg-[var(--green)] text-black rounded-xl px-4 disabled:opacity-40"
              aria-label="Send"
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
