# -*- coding:utf-8 -*-
import os.path
import requests
from cctm import json
from cctm.path import safe_open


class Resolver(object):
    def __init__(self, config):
        self.config = config

    def resolve(self, path):
        if path.startswith("file://"):
            return File(path[7:])
        elif path.startswith(("http://", "https://")):
            return URL(path)
        else:
            return File(path)


class Asset(object):
    def __init__(self, path):
        self.path = os.path.expanduser(path)


class File(Asset):
    def json(self):
        try:
            with open(self.path) as rf:
                return json.load(rf)
        except FileNotFoundError:
            data = []
            with safe_open(self.path, "w") as wf:
                json.dump(data, wf)
            return data


class URL(Asset):
    def json(self):
        return requests.get(self.path).json()
