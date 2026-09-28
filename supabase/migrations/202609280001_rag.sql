-- Run in the Supabase SQL editor. Safe to rerun; existing documents are preserved.
begin;
create schema if not exists extensions;
create extension if not exists vector with schema extensions;
set local search_path = public, extensions;

create table if not exists public.documents (
    id uuid primary key default gen_random_uuid(),
    title text not null,
    original_filename text not null,
    storage_path text not null,
    mime_type text not null default 'application/pdf',
    created_at timestamptz not null default now()
);
create table if not exists public.document_chunks (
    id uuid primary key default gen_random_uuid(),
    document_id uuid not null references public.documents(id) on delete cascade,
    chunk_index integer not null,
    content text not null,
    embedding vector(1536),
    created_at timestamptz not null default now()
);
alter table public.documents add column if not exists content_hash text;
alter table public.documents add column if not exists ingestion_status text not null default 'ready'
    check (ingestion_status in ('processing', 'ready'));
alter table public.document_chunks add column if not exists embedding vector(1536);
create unique index if not exists documents_content_hash_key on public.documents(content_hash);
create unique index if not exists document_chunks_document_index_key
    on public.document_chunks(document_id, chunk_index);

create or replace function public.match_document_chunks(
    query_embedding vector(1536),
    match_count integer default 5,
    match_threshold double precision default 0.3
)
returns table (
    document_id uuid,
    document_title text,
    chunk_index integer,
    content text,
    similarity double precision
)
language sql stable security invoker
set search_path = public, extensions
as $$
    select c.document_id, d.title, c.chunk_index, c.content,
           1 - (c.embedding <=> query_embedding) as similarity
    from public.document_chunks c
    join public.documents d on d.id = c.document_id
    where c.embedding is not null and d.ingestion_status = 'ready'
      and 1 - (c.embedding <=> query_embedding) >= match_threshold
    order by c.embedding <=> query_embedding
    limit least(greatest(match_count, 1), 20);
$$;

-- Exact cosine search is sufficient for the small MVP corpus; no ANN index needed.
alter table public.documents enable row level security;
alter table public.document_chunks enable row level security;
grant select, insert, update, delete on public.documents, public.document_chunks to service_role;
revoke all on function public.match_document_chunks(vector, integer, double precision) from public, anon, authenticated;
grant execute on function public.match_document_chunks(vector, integer, double precision) to service_role;

insert into storage.buckets (id, name, public)
values ('documents', 'documents', false) on conflict (id) do nothing;
notify pgrst, 'reload schema';
commit;
