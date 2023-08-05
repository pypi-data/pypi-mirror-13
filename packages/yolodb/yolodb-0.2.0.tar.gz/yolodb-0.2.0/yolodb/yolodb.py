import asyncio
import json
import logging


log = logging.getLogger(__name__)


def load(*args, **kwargs):
    """
    Returns a YoloDB object
    """
    return YoloDB(*args, **kwargs)


class YoloDB(object):

    def __init__(self, dbfile, load_now=True, save_delay=2, loop=None):
        self._loop = loop or asyncio.get_event_loop()

        # DB stuff
        self._db = dict()
        self._dbfile = dbfile

        # Saving stuff
        self.save_delay = save_delay
        self._request_save = asyncio.Event()
        self._save_future = asyncio.ensure_future(
            self._schedule_save(), loop=self._loop)

        # Immediately load the DB
        if load_now:
            self._load_from_file()
        else:
            asyncio.ensure_future(self._load_async(), loop=self._loop)

    def __getitem__(self, key):
        """
        Allow 'var = db[key]'
        """
        return self._db[key]

    def __setitem__(self, key, value):
        """
        Allow 'db[key] = value'
        """
        self.put(key, value)

    def __delitem__(self, key):
        """
        Allow 'del db[key]'
        """
        self.pop(key)

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

    async def close(self):
        """
        Save and end self._save_future
        """
        self._save_future.cancel()
        await self._save_future

    async def _schedule_save(self):
        """
        On event set, wait for self.save_delay and save the DB into its file
        """
        while True:
            try:
                await self._request_save.wait()
                await asyncio.sleep(self.save_delay)
            except asyncio.CancelledError:
                log.warning('save schedule cancelled')
                break
            finally:
                log.debug("Saving DB '%s'", self._dbfile)
                await self._save()

            self._request_save.clear()

    def _load_from_file(self):
        """
        Fill self._db with the content the DB file
        """
        try:
            with open(self._dbfile, 'r') as f:
                self._db = json.loads(f.read())
        except FileNotFoundError:
            log.warning("Could not find DB '%s', creating it", self._dbfile)
            self._db = dict()
            self._request_save.set()

    async def _load_async(self):
        """
        Call for _load_from_file asynchronously
        """
        await self._loop.run_in_executor(None, self._load_from_file)

    async def _save(self):
        """
        Dump self._db into the DB file
        """
        def savefile():
            with open(self._dbfile, 'w') as f:
                f.write(json.dumps(self._db))
        await self._loop.run_in_executor(None, savefile)
