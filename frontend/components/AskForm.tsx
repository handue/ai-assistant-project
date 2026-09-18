"use client";

import { useState } from "react";

export default function AskForm() {
  const [question, setQuestion] = useState("");
  const [submittedQuestion, setSubmittedQuestion] = useState("");

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setSubmittedQuestion(question);
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
          className="border rounded-lg px-5 py-3"
        >
          Ask
        </button>
      </form>

      {submittedQuestion && (
        <div className="mt-8 border rounded-lg p-4">
          <p className="font-semibold">Your question</p>
          <p>{submittedQuestion}</p>
        </div>
      )}
    </>
  );
}