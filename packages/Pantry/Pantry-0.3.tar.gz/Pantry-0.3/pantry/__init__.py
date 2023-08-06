import os.path
import pickle

class pantry(object):

    def __init__(self, filename):
        self.filename = filename

    @classmethod
    def open(cls, filename):
        p = cls(filename)
        p._open_pantry()
        return p

    def close(self):
        self._close_pantry()
        
    def __enter__(self):
        self._open_pantry()
        return self.db

    def __exit__(self, *args, **kwargs):
        self._close_pantry()


    def _open_pantry(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'rb') as f:
                data = f.read()
                if data:
                    self.db = pickle.loads(data)
                else:
                    self.db = {}
        else:
            self.db = {}

    def _close_pantry(self):
        with open(self.filename, 'wb') as f:
            data = pickle.dumps(self.db)
            f.write(data)
