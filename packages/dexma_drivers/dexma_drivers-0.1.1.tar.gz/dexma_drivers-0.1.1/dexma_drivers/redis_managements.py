__author__ = 'dcortes'

import redis

from bson.json_util import loads, dumps


class RedisManagement():

    def __init__(self, config):
        self._init_redis_db(config)
        self.name = config["name"]

    def _get_true_false_values(self, value):
        return True if value == "True" else False if value == "False" else None if value == "None" else value

    def _init_redis_db(self, config):
        try:
            self._db = redis.StrictRedis(host=config['host'],
                                         port=config.get('port', 6379),
                                         db=config['db'],
                                         password=config['password'],
                                         socket_timeout=config.get("socket_timeout", 30000),
                                         socket_connect_timeout=config.get('socket_connect_timeout', 50000),
                                         socket_timeout=config.get("socket_keepalive", 60),
                                         socket_keepalive_options=config.get("socket_keepalive_options", None),
                                         connection_pool=config.get("connection_pool", None),
                                         encoding=config.get("encoding", "utf-8"),
                                         encoding_errors= config.get("encoding_errors", "strict"),
                                         unix_socket_path=config.get("unix_socket_path", None),
                                         decode_responses=config.get("decode_responses", False),
                                         retry_on_timeout=config.get("retry_on_timeout", True),
                                         ssl=config.get("ssl", False),
                                         ssl_keyfile=config.get("ssl_keyfile", None),
                                         ssl_cert_reqs=config.get("ssl_cert_reqs", None),
                                         ssl_ca_certs=config.get("ssl_ca_certs", None)
                                         )
        except redis.exceptions.ConnectionError:
            raise Exception("dexma_drivers - redis - problem with redis Connection")
        except:
            raise Exception("dexma_drivers - redis - unknown problem with redis Connection")

    def insert(self, dep_id, key, value):
        try:
            return self._db.set("app:%s:%s:%s" % (self.name, key, dep_id), dumps(value))
        except Exception as e:
            raise Exception("dexma_drivers - redis - problem with insert redis, {}".format(e.message))

    def update(self, dep_id, key, value):
        try:
            return self._db.set("app:%s:%s:%s" % (self.name, key, dep_id), dumps(value))
        except Exception as e:
            raise Exception("dexma_drivers - redis - problem with updating redis, {}".format(e.message))

    def delete(self, dep_id, key):
        try:
            return self._db.delete("app:%s:%s:%s" % (self.name, key, dep_id))
        except Exception as e:
            raise Exception("dexma_drivers - redis - problem with deleting redis, {}".format(e.message))

    def get(self, dep_id, key):
        try:
            return loads(self._db.get("app:%s:%s:%s" % (self.name, key, dep_id)))
        except Exception as e:
            raise Exception("dexma_drivers - redis - problem with find redis, {}".format(e.message))

    def fetch(self, dep_id, key):
        try:
            return loads(self._db.get("app:%s:%s:%s" % (self.name, key, dep_id)))
        except Exception as e:
            raise Exception("dexma_drivers - redis - problem with find various redis, {}".format(e.message))

