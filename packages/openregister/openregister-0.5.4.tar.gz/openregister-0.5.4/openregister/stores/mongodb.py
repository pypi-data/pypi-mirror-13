import math
from ..store import Store
from ..item import Item
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError


class MongoStore(Store):

    """MongoDB storage for Items."""

    def __init__(self, mongo_uri, collection="entries"):
        client = MongoClient(mongo_uri)
        self.db = client.get_default_database()
        self.entries = self.db[collection]

    def put(self, item):
        doc = item.primitive
        doc['_id'] = item.hash
        try:
            self.entries.insert(doc)
        except DuplicateKeyError:
            pass

    def get(self, hash):
        doc = self.entries.find_one({'_id': hash})
        if doc is None:
            return None

        del doc['_id']

        item = Item()
        item.primitive = doc
        return item

    def find(self, query={}, page=1, page_size=50,
             paginate_if_longer_than=10000):

        total = self.entries.find(query).count()
        if total < paginate_if_longer_than:
            page_size = total
            pages = 1
        else:
            pages = math.ceil(total/page_size)
        if page == 1:
            start = page - 1
        else:
            start = (page - 1) * page_size

        cursor = self.entries.find(query)[start: start+page_size]
        entries = [Item(**record) for record in cursor]

        meta = {
            "query": query,
            "total": total,
            "page":  page,
            "pages": pages,
        }

        return meta, entries

    def find_all(self, query):
        cursor = self.entries.find(query)
        entries = [Item(**record) for record in cursor]
        return entries
