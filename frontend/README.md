# RAG MVP frontend

Next.js App Router + TypeScript. TanStack Query handles upload/question requests;
Zustand holds chat messages, source excerpts, and OpenAI response IDs in memory.

See the [project README](../README.md) for backend/Supabase setup, architecture,
API contracts, verification, and the complete manual test flow.

```bash
npm ci
npm run dev
```

Use the existing `frontend/.env`, or create it with only `NEXT_PUBLIC_API_URL=http://localhost:8000`.
Keep all OpenAI and Supabase keys in the backend.

```bash
npm run lint
npm run build
npm run start
```
