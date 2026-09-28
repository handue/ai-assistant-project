"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { apiPost, type AskRequest, type AskResponse } from "@/lib/api";
import { useChatStore } from "@/store/chatStore";

export default function AskForm() {
  const [question, setQuestion] = useState("");
  const previousResponseId = useChatStore((state) => state.previousResponseId);
  const setPreviousResponseId = useChatStore((state) => state.setPreviousResponseId);
  const addMessage = useChatStore((state) => state.addMessage);
  const resetChat = useChatStore((state) => state.resetChat);

  const askMutation = useMutation({
    mutationFn: (request: AskRequest) => apiPost<AskRequest, AskResponse>("/ask", request),
    onSuccess: (data) => {
      addMessage({ id: crypto.randomUUID(), role: "assistant", content: data.answer, sources: data.sources });
      setPreviousResponseId(data.response_id);
    },
  });

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedQuestion = question.trim();
    if (!trimmedQuestion || askMutation.isPending) return;
    addMessage({ id: crypto.randomUUID(), role: "user", content: trimmedQuestion });
    askMutation.mutate({ question: trimmedQuestion, previous_response_id: previousResponseId });
    setQuestion("");
  }

  return (
    <>
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          aria-label="Question about your PDFs"
          type="text"
          value={question}
          maxLength={4000}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask a question about your PDFs..."
          className="min-w-0 flex-1 border rounded-lg px-4 py-3"
        />
        <button type="submit" disabled={askMutation.isPending || !question.trim()} className="border rounded-lg px-5 py-3 disabled:opacity-50">
          {askMutation.isPending ? "Asking..." : "Ask"}
        </button>
      </form>
      <button
        type="button"
        disabled={askMutation.isPending}
        onClick={() => { resetChat(); askMutation.reset(); }}
        className="mt-2 text-sm underline disabled:opacity-50"
      >
        New chat
      </button>
      {askMutation.isError && <p role="alert" className="mt-4">Error: {askMutation.error.message} Enter your question again to retry.</p>}
    </>
  );
}
