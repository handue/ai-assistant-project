"use client";

import { useState } from "react";

export default function Home() {
  const [question, setQuestion] = useState("");
  const [submittedQuestion, setSubmittedQuestion] = useState("");

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setSubmittedQuestion(question);
    setQuestion("");
  }

  return (
    <main className="min-h-screen flex items-center justify-center">
      <div className="w-full max-w-2xl p-8">
        <h1 className="text-3xl font-bold mb-2">
          AI Infrastructure Research Assistant
        </h1>

        <p className="text-gray-500 mb-8">
          Ask questions about AI infrastructure companies and documents.
        </p>

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
      </div>
    </main>
  );
}