"use client";

import { useChatStore } from "@/store/chatStore";

export default function ChatMessages() {
  const messages = useChatStore((state) => state.messages);
  return (
    <div className="mt-8 space-y-4" aria-live="polite">
      {messages.map((message) => (
        <div key={message.id} className="border rounded-lg p-4">
          <p className="font-semibold">{message.role === "user" ? "You" : "AI"}</p>
          <p className="whitespace-pre-wrap">{message.content}</p>
          {message.role === "assistant" && (
            <div className="mt-4 border-t pt-3">
              <p className="text-sm font-semibold">Sources</p>
              {message.sources?.length ? (
                <ol className="mt-2 space-y-2 text-sm">
                  {message.sources.map((source, index) => (
                    <li key={`${source.document_id}:${source.chunk_index}`}>
                      <details>
                        <summary className="cursor-pointer">
                          [{index + 1}] {source.document_title} · Chunk {source.chunk_index} · Similarity {source.similarity.toFixed(3)}
                        </summary>
                        <p className="mt-1 text-xs break-all">Document: {source.document_id}</p>
                        <p className="mt-1 whitespace-pre-wrap">{source.content}</p>
                      </details>
                      <p className="mt-1">{source.content.slice(0, 180)}{source.content.length > 180 ? "…" : ""}</p>
                    </li>
                  ))}
                </ol>
              ) : <p className="text-sm">No relevant document excerpts found.</p>}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
