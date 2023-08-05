from cctm import json


class DumpOrSaveWrapper(object):
    def __init__(self, store, save=False):
        self.store = store
        self.if_save = save

    def save(self, data):
        if self.if_save:
            self.store.save(data)
        else:
            self.dump(data)

    def dump(self, data):
        print(json.dumps(data))

    def __getattr__(self, k):
        return getattr(self.store, k)
