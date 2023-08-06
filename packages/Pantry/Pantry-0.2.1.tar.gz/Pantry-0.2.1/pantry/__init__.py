import os.path
import pickle

from contextlib import contextmanager


@contextmanager
def pantry(filename):
    if not os.path.exists(filename):
        db = {}
    else:
        with open(filename, 'rb') as f:
            data = f.read()
            if data:
                db = pickle.loads(data)
            else:
                db = {}

    yield db

    with open(filename, 'wb') as f:
        data = pickle.dumps(db)
        f.write(data)
