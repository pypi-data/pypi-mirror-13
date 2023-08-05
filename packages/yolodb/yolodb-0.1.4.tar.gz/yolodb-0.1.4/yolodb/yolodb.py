import asyncio
import ujson as json
import logging
import os


log = logging.getLogger(__name__)


def load(*args, **kwargs):
    """
    Returns a YoloDB object
    """
    return YoloDB(*args, **kwargs)


class YoloDB(object):

    def __init__(self, dbfile, load_now=True, save_delay=2, loop=None):
        self.loop = loop or asyncio.get_event_loop()

        # DB stuff
        self._db = dict()
        self._dbfile = dbfile

        # Saving stuff
        self.save_delay = save_delay
        self._request_save = asyncio.Event()
        self._save_future = asyncio.ensure_future(self._schedule_save())

        # Immediately load the DB
        if load_now:
            self._load_from_file()
        else:
            asyncio.ensure_future(self._load_async())

    def put(self, key, value):
        """
        Put value on a key
        """
        self._db[key] = value
        self._request_save.set()

    def pop(self, *args, **kwargs):
        """
        Pop the value of a key
        """
        item = self._db.pop(*args, **kwargs)
        self._request_save.set()
        return item

    def get(self, *args, **kwargs):
        """
        Get the value of a key
        """
        return self._db.get(*args, **kwargs)

    @property
    def all(self):
        """
        Return a copy of the whole db as dict
        """
        return self._db.copy()

    @asyncio.coroutine
    def close(self):
        """
        Save and end self._save_future
        """
        self._save_future.cancel()
        yield from self._save_future

    @asyncio.coroutine
    def _schedule_save(self):
        """
        On event set, wait for self.save_delay and save the DB into its file
        """
        while True:
            try:
                yield from self._request_save.wait()
                yield from asyncio.sleep(self.save_delay)
            except asyncio.CancelledError:
                log.warning('save schedule cancelled')
                break
            finally:
                yield from self._save()

            self._request_save.clear()

    def _load_from_file(self):
        """
        Fill self._db with the content the DB file
        """
        if os.path.exists(self._dbfile):
            with open(self._dbfile, 'r') as f:
                self._db = json.loads(f.read())
        else:
            self._db = dict()
            self._request_save.set()

    @asyncio.coroutine
    def _load_async(self):
        """
        Call for _load_from_file asynchronously
        """
        yield from self.loop.run_in_executor(None, self._load_from_file)

    @asyncio.coroutine
    def _save(self):
        """
        Dump self._db into the DB file
        """
        def savefile():
            with open(self._dbfile, 'w') as f:
                f.write(json.dumps(self._db))
        yield from self.loop.run_in_executor(None, savefile)
