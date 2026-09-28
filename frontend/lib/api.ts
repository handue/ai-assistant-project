const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Source = {
  document_id: string;
  document_title: string;
  chunk_index: number;
  content: string;
  similarity: number;
};

export type AskRequest = {
  question: string;
  previous_response_id: string | null;
};

export type AskResponse = {
  answer: string;
  sources: Source[];
  response_id: string | null;
};

export type UploadResponse = {
  document: { id: string; title: string };
  chunk_count: number;
  duplicate: boolean;
};

async function readResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const detail = body?.detail;
    const message = typeof detail === "string"
      ? detail
      : Array.isArray(detail)
        ? detail.map((item: { msg?: string }) => item.msg).filter(Boolean).join("; ")
        : `API request failed (${response.status}).`;
    throw new Error(message || `API request failed (${response.status}).`);
  }
  return response.json();
}

export async function apiPost<TRequest, TResponse>(path: string, body: TRequest): Promise<TResponse> {
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return readResponse<TResponse>(response);
}

export async function uploadPdf(file: File): Promise<UploadResponse> {
  const body = new FormData();
  body.append("file", file);
  const response = await fetch(`${API_URL}/documents/upload`, { method: "POST", body });
  return readResponse<UploadResponse>(response);
}
