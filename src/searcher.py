import whoosh.index as index
from whoosh.query import Phrase, Query
from whoosh.qparser import QueryParser

class Searcher:
    def __init__(self, index_folder):
        self.ix = index.open_dir(index_folder)
        self.search_index = "subjects"

    def change_search_index(self, new_search_index):
        self.search_index = new_search_index

    def process_query(self, query):
        query = query.replace("-", " ")
        return query.split(" ")

    def search(self, 
               q: str):
        res = None

        with self.ix.searcher() as searcher:
            query = Phrase(self.search_index, self.process_query(q))
            #query = QueryParser(self.search_index, self.ix.schema).parse(self.process_query(q))
            results = searcher.search(query)
            res = list(results)
            res = [item.fields() for item in res]

        return res