"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { apiPost } from "../lib/api";
import { useChatStore } from "../store/chatStore";

type AskRequest = {
  question: string;
  previous_response_id: string | null;
};

type AskResponse = {
  answer: string;
  response_id: string;
}

export default function AskForm() {
  const [question, setQuestion] = useState("");
  // const [submittedQuestion, setSubmittedQuestion] = useState("");

  const previousResponseId = useChatStore((state) => state.previousResponseId);
  const setPreviousResponseId = useChatStore((state) => state.setPrviousResponseId);

  const addMessage = useChatStore((state) => state.addMessage);

  const askMutation = useMutation({
    mutationFn: (request: AskRequest) => apiPost<AskRequest, AskResponse>("/ask", request),

    onSuccess: (data) => {
      addMessage({
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.answer,
      });
      setPreviousResponseId(data.response_id);
    }
  });

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion) {
      return;
    }
    // useQuery = auto fetch data from backend,
    // useMutation = manually trigger a request to the backend, usually for creating, updating, or deleting data.

    addMessage({
      id: crypto.randomUUID(),
      role: "user",
      content: trimmedQuestion,
    });

    askMutation.mutate({
      question: trimmedQuestion,
      previous_response_id: previousResponseId,
    });

    setQuestion("");
  }

  return (
    <>
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask a question..."
          className="flex-1 border rounded-lg px-4 py-3"
        />

        <button
          type="submit"
          disabled={askMutation.isPending}
          className="border rounded-lg px-5 py-3"
        >
          {askMutation.isPending ? "Asking..." : "Ask"}
        </button>
      </form>

      {askMutation.isError && (
        <p className="mt-4">
          Error: {askMutation.error.message}
        </p>
      )}


    </>
  );
}