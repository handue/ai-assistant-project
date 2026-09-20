"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { apiPost } from "../lib/api";

type AskRequest = {
  question: string;
};

type AskResponse = {
  answer: string;
}

export default function AskForm() {
  const [question, setQuestion] = useState("");
  const [submittedQuestion, setSubmittedQuestion] = useState("");

  const askMutation = useMutation({
    mutationFn: (request: AskRequest) => apiPost<AskRequest, AskResponse>("/ask", request),
  });

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!question.trim()) {
      return;
    }
    // useQuery = auto fetch data from backend,
    // useMutation = manually trigger a request to the backend, usually for creating, updating, or deleting data.
    
    askMutation.mutate({
      question: question,
    });
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

      {askMutation.data && (
        <div className="mt-8 border rounded-lg p-4">
          <p className="font-semibold">Answer</p>
          <p>{askMutation.data.answer}</p>
        </div>
      )}
    </>
  );
}