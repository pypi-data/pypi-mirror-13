# -*- coding: utf-8 -*-

from copy import copy
import json
from pyrocumulus.conf import settings
from pyrocumulus.web.applications import Application, URLSpec
from tornado import gen
from tornado.web import RequestHandler
from jaobi.models import ContentConsumption


class _SizedConsumptionCache:

    def __init__(self):
        self.cache = []
        self.cache_size = settings.CONSUMPTION_CACHE_SIZE
        self.lock = None

    @gen.coroutine
    def add(self, obj):
        """Adds a ContentConsumption to the cache queue."""

        consumer = yield obj.consumer
        # when we get undefined consumer on fe, its id is None here.
        if consumer.id is None:
            yield consumer.save()
            # To not get a db ref
            consumer = yield type(consumer).objects.get(id=consumer.id)
            obj.consumer = consumer

        content = yield obj.content

        if content.id is None:
            yield content.save()
            content = yield type(content).objects.get(id=content.id)
            obj.content = content

        self.cache.append(obj)

        if len(self.cache) >= self.cache_size and not self.lock:
            self.lock = 'lóqui'
            to_insert = copy(self.cache)
            self.cache = []
            yield self.insert(to_insert)
            for cc in to_insert:
                consumer = yield cc.consumer
                yield consumer.generate_similar_consumers(quantity=10,
                                                          depth=10)

        self.lock = None

    @gen.coroutine
    def insert(self, obj_list):
        yield ContentConsumption.objects.insert(obj_list)


sized_cache = _SizedConsumptionCache()


def get_cache(cache_type='sized'):
    return sized_cache


# Here a simple app to show the size of the cache queue
# Mainly used for testing and debugging
class SpyHandler(RequestHandler):

    def get(self):
        mydict = {'size': len(sized_cache.cache),
                  'locked': bool(sized_cache.lock)}
        self.write(json.dumps(mydict))


spy = URLSpec('/cache/spy', SpyHandler)
spyapp = Application(url_prefix='', extra_urls=[spy])
