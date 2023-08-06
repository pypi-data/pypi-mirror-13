import asyncio
import signal
import functools
from urllib.parse import urlparse
import logging
from aiohttp_ac_hipchat.addon import Addon

from aiohttp_ac_hipchat.cache import RedisCache
from aiohttp_ac_hipchat.store import MongoDBStore
from aiohttp_ac_hipchat.webapp import WebApp
import os
import asyncio_redis
import aiolocals

_log = logging.getLogger(__name__)

def create_addon_app(addon_key=None, addon_name=None, from_name=None, debug=False,
        vendor_name=None, vendor_url=None,
        base_url="http://localhost:5000", addon_client_store=None, scopes=None, avatar=None,
        dynamic_descriptor=False, **kwargs):
    """
    Creates an addon application

    :param addon_key: addon key
    :param addon_name: addon name
    :param from_name: from name used for notification
    :param debug: debug mode
    :param vendor_name: vendor name
    :param vendor_url: vendor url
    :param base_url: addon base url
    :param addon_client_store: store that will replace the default mongodb store to store oauth/client data
    :param scopes: scopes
    :param avatar: avatar
    :param dynamic_descriptor: Determines if the descriptor should change depending if the request comes from hipchat
    server or not.
    :param kwargs:
    :return: (aiohttp app, addon)
    """

    config = get_config(addon_key=addon_key,
                        addon_name=addon_name,
                        from_name=from_name,
                        debug=debug,
                        base_url=base_url,
                        vendor_name=vendor_name,
                        vendor_url=vendor_url)
    init_log(addon_name, config["DEBUG"])

    loop = asyncio.get_event_loop()
    app = WebApp(loop=loop, middlewares=[aiolocals.context_middleware_factory])

    app["config"] = config

    if not addon_client_store:
        mongodb = loop.run_until_complete(init_mongodb(config["MONGO_URL"]))
        app["mongodb"] = mongodb
        app["addon_client_store"] = MongoDBStore(mongodb)
    else:
        app["addon_client_store"] = addon_client_store

    redis = loop.run_until_complete(init_redis(loop, config["REDIS_URL"]))
    app["redis_pool"] = redis
    app["cache"] = RedisCache(redis)

    addon = init_addon(app, scopes, avatar, dynamic_descriptor)
    app['addon'] = addon

    return app, addon

@asyncio.coroutine
def init_mongodb(mongo_url="mongodb://localhost:27017/test"):
    from motor.motor_asyncio import AsyncIOMotorClient

    _log.info("Connecting to MongoDB %s" % mongo_url)
    c = AsyncIOMotorClient(host=mongo_url, max_pool_size=os.environ.get("MONGO_POOL_SIZE", 2))
    return c.get_default_database()

@asyncio.coroutine
def init_redis(loop, redis_url="redis://localhost:6379"):
    url = urlparse(redis_url)

    db = 0
    try:
        if url.path:
            db = int(url.path.replace('/', ''))
    except (AttributeError, ValueError):
        pass

    _log.info("Connecting to Redis %s" % redis_url)
    pool = yield from asyncio_redis.Pool.create(host=url.hostname, port=url.port, password=url.password,
                                                db=db, poolsize=os.environ.get("REDIS_POOL_SIZE", 2))

    exit_handler = functools.partial(handle_redis_exit, pool)
    loop.add_signal_handler(signal.SIGTERM, exit_handler)
    loop.add_signal_handler(signal.SIGINT, exit_handler)

    return pool


def handle_redis_exit(pool):
    _log.info("Closing Redis connection")
    pool.alive = False
    pool.close()


def init_log(addon_name, debug=False):
    aiolocals.configure_logging(addon_name)
    if debug:
        # You must initialize logging, otherwise you'll not see debug output.
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        aio_log = logging.getLogger("asyncio")
        aio_log.setLevel(logging.INFO)
        aio_log.propagate = True
    else:
        logging.basicConfig()
        aio_log = logging.getLogger("asyncio")
        aio_log.setLevel(logging.WARN)
        logging.getLogger().setLevel(logging.INFO)

def init_addon(app, scopes, avatar, dynamic_descriptor):
    return Addon(app, scopes=scopes, avatar=avatar, dynamic_descriptor=dynamic_descriptor)

def get_config(addon_key=None, addon_name=None, from_name=None, debug=False, base_url="http://localhost:5000",
        vendor_name=None, vendor_url=None):
    return {
        "DEBUG": True if "true" == os.environ.get("DEBUG", "false") else debug,
        "ADDON_KEY": os.environ.get("ADDON_KEY", addon_key),
        "ADDON_NAME": os.environ.get("ADDON_NAME", addon_name),
        "ADDON_VENDOR_NAME": os.environ.get("ADDON_VENDOR_NAME", vendor_url),
        "ADDON_VENDOR_URL": os.environ.get("ADDON_VENDOR_URL", vendor_name),
        "ADDON_FROM_NAME": os.environ.get("ADDON_FROM_NAME", from_name),
        "BASE_URL": os.environ.get("BASE_URL", base_url).rstrip("\\"),
        "REDIS_URL": os.environ.get("REDIS_URL", "redis://localhost:6379"),
        "MONGO_URL": os.environ.get("MONGO_URL", "mongodb://localhost:27017/test")
    }

