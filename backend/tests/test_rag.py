"""Offline integration checks: real PDF parsing/API, in-memory external services."""
import math
import os
import sys
import unittest
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from openai import RateLimitError
from postgrest.exceptions import APIError
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject
import httpx

# Tests work without local secrets. Construct SDK clients with dummy configuration;
# every external method used by the tests is replaced before requests run.
with patch.dict(os.environ, {
    'OPENAI_API_KEY': 'offline-test-key',
    'SUPABASE_URL': 'https://example.invalid',
    'SUPABASE_SECRET_KEY': 'sb_secret_offline_test',
}):
    import ai_client
    import document_service
    import rag_service
    from main import app


def make_pdf(text="Orion's annual revenue is 42 million dollars."):
    writer = PdfWriter()
    page = writer.add_blank_page(width=600, height=800)
    font = DictionaryObject({NameObject('/Type'): NameObject('/Font'),
                             NameObject('/Subtype'): NameObject('/Type1'),
                             NameObject('/BaseFont'): NameObject('/Helvetica')})
    page[NameObject('/Resources')] = DictionaryObject({NameObject('/Font'): DictionaryObject({NameObject('/F1'): font})})
    stream = DecodedStreamObject()
    stream.set_data(f"BT /F1 12 Tf 50 750 Td ({text}) Tj ET".encode())
    page[NameObject('/Contents')] = writer._add_object(stream)
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def embed(texts):
    # Tiny deterministic semantic fixture padded to the production dimension.
    return [[float('orion' in text.lower()), float('revenue' in text.lower()),
             float('volcano' in text.lower())] + [0.0] * 1533 for text in texts]


class MemorySupabase:
    def __init__(self):
        self.rows = {'documents': [], 'document_chunks': []}
        self.files = {}
        self.fail_chunks = False
        self.rpc_params = None
        self.storage = SimpleNamespace(from_=lambda name: self)

    def table(self, name):
        return Query(self, name)

    def upload(self, path, file, options):
        self.files[path] = file

    def remove(self, paths):
        for path in paths:
            self.files.pop(path, None)

    def rpc(self, name, params):
        assert name == 'match_document_chunks'
        self.rpc_params = params
        query = params['query_embedding']
        matches = []
        for chunk in self.rows['document_chunks']:
            doc = next(d for d in self.rows['documents'] if d['id'] == chunk['document_id'])
            vector = chunk['embedding']
            if doc['ingestion_status'] != 'ready' or not vector:
                continue
            denominator = math.sqrt(sum(x*x for x in query) * sum(x*x for x in vector))
            similarity = sum(a*b for a, b in zip(query, vector)) / denominator if denominator else 0
            if similarity >= params['match_threshold']:
                matches.append({'document_id': doc['id'], 'document_title': doc['title'],
                                'chunk_index': chunk['chunk_index'], 'content': chunk['content'],
                                'similarity': similarity})
        matches.sort(key=lambda row: row['similarity'], reverse=True)
        return SimpleNamespace(execute=lambda: SimpleNamespace(data=matches[:params['match_count']]))


class Query:
    def __init__(self, db, name):
        self.db, self.name = db, name
        self.action, self.payload, self.filters = 'select', None, {}

    def select(self, *args, **kwargs):
        return self

    def eq(self, key, value):
        self.filters[key] = value
        return self

    def insert(self, payload):
        self.action, self.payload = 'insert', payload
        return self

    def update(self, payload):
        self.action, self.payload = 'update', payload
        return self

    def delete(self):
        self.action = 'delete'
        return self

    def execute(self):
        rows = self.db.rows[self.name]
        matched = [row for row in rows if all(row.get(k) == v for k, v in self.filters.items())]
        if self.action == 'insert':
            if self.name == 'document_chunks' and self.db.fail_chunks:
                raise RuntimeError('simulated database failure')
            matched = self.payload if isinstance(self.payload, list) else [self.payload]
            if self.name == 'documents' and any(d['content_hash'] == matched[0]['content_hash'] for d in rows):
                raise APIError({'code': '23505', 'message': 'duplicate hash'})
            rows.extend(matched)
        elif self.action == 'update':
            for row in matched:
                row.update(self.payload)
        elif self.action == 'delete':
            self.db.rows[self.name] = [row for row in rows if row not in matched]
        return SimpleNamespace(data=matched, count=len(matched))


class RagIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.db = MemorySupabase()
        self.model = MagicMock()
        self.model.responses.create.return_value = SimpleNamespace(output_text='Orion has annual revenue of 42 million dollars [1].', id='resp_test')
        self.patches = [patch.object(document_service, 'supabase', self.db),
                        patch.object(rag_service, 'supabase', self.db),
                        patch.object(document_service, 'create_embeddings', side_effect=embed),
                        patch.object(rag_service, 'create_embeddings', side_effect=embed),
                        patch.object(rag_service, 'client', self.model)]
        for mock in self.patches:
            mock.start()
            self.addCleanup(mock.stop)
        self.api = TestClient(app)
        self.addCleanup(self.api.close)

    def upload(self, pdf=None):
        return self.api.post('/documents/upload', files={'file': ('orion.pdf', pdf or make_pdf(), 'application/pdf')})

    def test_pdf_to_grounded_answer_sources_and_followup(self):
        pdf = make_pdf("Orion annual revenue is 42 million dollars. " * 90)
        result = self.upload(pdf)
        self.assertEqual(result.status_code, 200, result.text)
        data = result.json()
        self.assertGreater(data['chunk_count'], 1)
        self.assertEqual(self.db.files[data['document']['storage_path']], pdf)
        self.assertTrue(all(len(row['embedding']) == 1536 for row in self.db.rows['document_chunks']))
        answer = self.api.post('/ask', json={'question': 'What is Orion revenue?'})
        self.assertEqual(answer.status_code, 200, answer.text)
        source = answer.json()['sources'][0]
        self.assertEqual(source['document_id'], data['document']['id'])
        self.assertEqual(source['document_title'], 'orion.pdf')
        self.assertIn('42 million', source['content'])
        self.assertGreater(source['similarity'], 0.9)
        request = self.model.responses.create.call_args.kwargs
        self.assertIn(source['content'], request['input'])
        self.assertIn('untrusted', request['instructions'])
        followup = self.api.post('/ask', json={'question': 'Explain Orion revenue again', 'previous_response_id': 'resp_test'})
        self.assertEqual(followup.status_code, 200)
        self.assertEqual(self.model.responses.create.call_args.kwargs['previous_response_id'], 'resp_test')

    def test_duplicate_is_reused_without_reembedding(self):
        original = self.upload().json()
        duplicate = self.upload().json()
        self.assertTrue(duplicate['duplicate'])
        self.assertEqual(original['document']['id'], duplicate['document']['id'])
        self.assertEqual(len(self.db.rows['documents']), 1)
        document_service.create_embeddings.assert_called_once()

    def test_unmatched_question_and_empty_corpus_do_not_generate_answer(self):
        response = self.api.post('/ask', json={'question': 'Volcano eruption?'})
        self.assertEqual(response.json()['sources'], [])
        self.upload()
        response = self.api.post('/ask', json={'question': 'Volcano eruption?'})
        self.assertEqual(response.json()['sources'], [])
        self.assertIn('not provide enough', response.json()['answer'])
        self.model.responses.create.assert_not_called()

    def test_processing_document_is_not_retrieved(self):
        self.upload()
        self.db.rows['documents'][0]['ingestion_status'] = 'processing'
        self.assertEqual(self.upload().status_code, 409)
        response = self.api.post('/ask', json={'question': 'Orion revenue?'})
        self.assertEqual(response.json()['sources'], [])

    def test_failed_ingestion_cleans_up_and_can_retry(self):
        self.db.fail_chunks = True
        self.assertEqual(self.upload().status_code, 502)
        self.assertEqual(self.db.files, {})
        self.assertEqual(self.db.rows, {'documents': [], 'document_chunks': []})
        self.db.fail_chunks = False
        self.assertEqual(self.upload().status_code, 200)

    def test_invalid_and_scanned_pdfs_and_blank_question(self):
        self.assertEqual(self.upload(b'not a pdf').status_code, 400)
        self.assertEqual(self.upload(b'%PDF-broken').status_code, 422)
        self.assertEqual(self.upload(make_pdf('')).status_code, 422)
        self.assertEqual(self.api.post('/ask', json={'question': '   '}).status_code, 422)
        self.assertEqual(self.db.files, {})

    def test_rate_limit_is_safe_and_actionable(self):
        self.upload()
        response = httpx.Response(429, request=httpx.Request('POST', 'https://example.invalid'))
        self.model.responses.create.side_effect = RateLimitError('private upstream error', response=response, body=None)
        result = self.api.post('/ask', json={'question': 'Orion revenue?'})
        self.assertEqual(result.status_code, 429)
        self.assertNotIn('private upstream error', result.text)


class EmbeddingTests(unittest.TestCase):
    def test_batch_order_and_dimensions(self):
        def respond(**kwargs):
            return SimpleNamespace(data=[SimpleNamespace(index=i, embedding=[float(i)] * 1536)
                                         for i in reversed(range(len(kwargs['input'])))])
        with patch.object(ai_client.client.embeddings, 'create', side_effect=respond) as mock:
            result = ai_client.create_embeddings(['text'] * 65)
            self.assertEqual(mock.call_count, 2)
            self.assertEqual(result[0][0], 0)
            self.assertEqual(result[63][0], 63)
            self.assertEqual(mock.call_args.kwargs['dimensions'], 1536)

    def test_bad_embedding_count_fails_before_storage(self):
        with patch.object(ai_client.client.embeddings, 'create', return_value=SimpleNamespace(data=[])):
            with self.assertRaises(RuntimeError):
                ai_client.create_embeddings(['text'])


if __name__ == '__main__':
    unittest.main()
