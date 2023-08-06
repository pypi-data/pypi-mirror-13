__author__ = 'dcortes'

from pymongo import MongoClient, errors


class MongoManagement():

    def __init__(self, config):
        self._init_mongo_db(config)

    def _init_mongo_db(self, config):
        try:
            self._client = MongoClient(config["host"],
                                       config.get("port", 6379),
                                       maxPoolSize=config.get('max_pool_size', 4),
                                       waitQueueTimeoutMS=config.get('wait_conn_time', 30000),
                                       socketTimeoutMS=config.get('socket_timeout', 30000),
                                       w=config.get("w", 1),
                                       wtimeout=config.get('wc_timeout', 60000))
            if self._client[config["bd"]].authenticate(config['user'],config['password']):
                self._db = self._client[config["bd"]]
        except errors.ConnectionFailure, e:
            raise Exception("dexma_drivers - mongo - could not connect to MongoDB: %s" %e)

    def insert_object(self, collection, document):
        try:
            collection = self._db[collection]
            return collection.insert_one(document)
        except Exception as e:
            raise Exception("dexma_drivers - mongo - problem with insert to mongodb, error {}".format(e.message))

    def update_object(self, collection, document, search_args, upsert=False):
        try:
            collection = self._db[collection]
            return collection.update(search_args, document, upsert=upsert)
        except Exception as e:
            raise Exception("dexma_drivers - mongo - problem with update to mongodb, error {}".format(e.message))

    def replace_object(self, collection, document, search_args):
        try:
            collection = self._db[collection]
            return collection.replace_one(search_args, document)
        except Exception as e:
            raise Exception("dexma_drivers - mongo - problem with replace to mongodb, error {}".format(e.message))


    def delete_object(self, collection, search_args):
        try:
            collection = self._db[collection]
            return collection.remove(search_args, w=1)
        except Exception as e:
            raise Exception("dexma_drivers - mongo - problem with delete to mongodb, error {}".format(e.message))

    def find_object(self, collection, search_args):
        try:
            collection = self._db[collection]
            return collection.find_one(search_args, {"_id": 0})
        except Exception as e:
            raise Exception("dexma_drivers - mongo - problem with find one to mongodb, error {}".format(e.message))

    def find_objects(self, collection, search_args, query_args=None,skip=0,limit=0):
        try:
            collection = self._db[collection]
            documents = collection.find(search_args) if query_args is None else collection.find(search_args, query_args,skip=skip,limit=limit)
            return list(documents)
        except Exception as e:
            raise Exception("dexma_drivers - mongo - problem with find various to mongodb, error {}".format(e.message))

    def count_objects(self, collection, search_args, skip_documents):
        try:
            collection = self._db[collection]
            return collection.find(search_args, {"_id":0}, skip=skip_documents).count(True)
        except Exception as e:
            raise Exception("dexma_drivers - mongo - problem with find various to mongodb, error {}".format(e.message))

    def aggregate_find_object(self, collection, agreggation):
        try:
            collection = self._db[collection]
            return list(collection.aggregate(agreggation))
        except Exception as e:
            raise Exception("dexma_drivers - mongo - problem aggregating various to mongodb, error {}".format(e.message))

    def get_collections(self):
        try:
            return self._db.collection_names()
        except Exception as e:
            raise Exception("problem with find various to mongodb, error {}".format(e.message))

    def get_document_exists(self, collection, search_args):
        try:
            collection = self._db[collection]
            count = collection.find(filter=search_args).limit(1).count(True)
            return True if count == 1 else False
        except Exception as e:
            raise Exception("dexma_drivers - mongo - problem with checking existence of document, error {}".format(e.message))

    def exists_collection(self, name):
        try:
            collections = self._db.collection_names()
            return True if name in collections else False
        except Exception as e:
            raise Exception("dexma_drivers - mongo - problem with checking existence of collection, error {}".format(e.message))

    def create_capped_collection(self, name, size=50000, max_docs=100):
        try:
            ## even if we set the max_docs the size argument is not optional
            if not self.exists_collection(name):
                status = self._db.create_collection(name, capped=True, size=size, max=max_docs)
                return True if status is not None and status.get("name", "--") == name else False
            return True
        except Exception as e:
            raise Exception("dexma_drivers - mongo - problem with checking existence of document, error {}".format(e.message))