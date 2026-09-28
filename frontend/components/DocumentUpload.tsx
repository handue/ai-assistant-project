"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { uploadPdf } from "@/lib/api";

export default function DocumentUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [validationError, setValidationError] = useState("");
  const uploadMutation = useMutation({ mutationFn: uploadPdf });

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file || uploadMutation.isPending) return;
    if (!file.name.toLowerCase().endsWith(".pdf") || file.size > 20 * 1024 * 1024) {
      setValidationError("Select a PDF of 20 MB or less.");
      return;
    }
    setValidationError("");
    uploadMutation.mutate(file);
  }

  return (
    <section className="mb-8 border rounded-lg p-4">
      <h2 className="font-semibold mb-2">Upload a PDF</h2>
      <p className="text-sm mb-3">Text PDFs only, up to 20 MB. Wait for indexing to finish before asking.</p>
      <form onSubmit={handleSubmit} className="flex flex-wrap gap-3">
        <input
          aria-label="PDF file"
          type="file"
          accept=".pdf,application/pdf"
          disabled={uploadMutation.isPending}
          onChange={(event) => {
            setFile(event.target.files?.[0] ?? null);
            setValidationError("");
            uploadMutation.reset();
          }}
          className="max-w-full"
        />
        <button type="submit" disabled={!file || uploadMutation.isPending} className="border rounded-lg px-4 py-2 disabled:opacity-50">
          {uploadMutation.isPending ? "Uploading and indexing..." : "Upload"}
        </button>
      </form>
      {uploadMutation.isSuccess && (
        <p role="status" className="mt-3 text-sm">
          {uploadMutation.data.duplicate ? "Already indexed" : "Ready"}: {uploadMutation.data.document.title} ({uploadMutation.data.chunk_count} chunks).
        </p>
      )}
      {(validationError || uploadMutation.isError) && (
        <p role="alert" className="mt-3 text-sm">{validationError || uploadMutation.error?.message}</p>
      )}
    </section>
  );
}
