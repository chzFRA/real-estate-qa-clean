from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT
from whoosh.qparser import QueryParser
import os

class BM25Retriever:
    def __init__(self, index_dir="bm25_index"):
        self.index_dir = index_dir
        if not os.path.exists(index_dir):
            os.makedirs(index_dir)
        self.schema = Schema(id=TEXT(stored=True), content=TEXT(stored=True))

    def build_index(self, docs):
        """
        docs: List of tuples (doc_id, doc_text)
        """
        ix = create_in(self.index_dir, self.schema)
        writer = ix.writer()
        for doc_id, content in docs:
            writer.add_document(id=str(doc_id), content=content)
        writer.commit()

    def search(self, query_text, top_k=5):
        ix = open_dir(self.index_dir)
        qp = QueryParser("content", schema=ix.schema)
        q = qp.parse(query_text)
        
        with ix.searcher() as searcher:
            results = searcher.search(q, limit=top_k)
            return [(r['id'], r.score) for r in results]
