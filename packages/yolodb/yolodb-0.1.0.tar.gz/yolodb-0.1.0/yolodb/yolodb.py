import asyncio
import json
import logging
import os


log = logging.getLogger(__name__)


def load(dbfile, save_delay=2, loop=None):
    """
    Returns a YoloDB object
    """
    return YoloDB(dbfile, save_delay=save_delay, loop=loop)


class YoloDB(object):

    def __init__(self, dbfile, save_delay=2, loop=None):
        self.loop = loop or asyncio.get_event_loop()

        # DB stuff
        self.db = dict()
        self.dbfile = dbfile

        # Saving stuff
        self.save_delay = save_delay
        self._request_save = asyncio.Event()
        self._save_future = asyncio.ensure_future(self._schedule_save())

        # Immediately load the DB
        asyncio.ensure_future(self._load())

    def put(self, key, value):
        """
        Put value on a key
        """
        self.db[key] = value
        self._request_save.set()

    def pop(self, key):
        """
        Pop the value of a key
        """
        self._request_save.set()
        return self.db.pop(key)

    def get(self, key):
        """
        Get the value of a key
        """
        return self.db.get(key)

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

    @asyncio.coroutine
    def _load(self):
        """
        Fills self.db with the content the DB file
        """
        def loadfile():
            with open(self.dbfile, 'r') as f:
                self.db = json.loads(f.read())
        if os.path.exists(self.dbfile):
            yield from self.loop.run_in_executor(None, loadfile)
        else:
            self.db = dict()

    @asyncio.coroutine
    def _save(self):
        """
        Dumps self.db into the DB file
        """
        def savefile():
            with open(self.dbfile, 'w') as f:
                f.write(json.dumps(self.db))
        yield from self.loop.run_in_executor(None, savefile)
