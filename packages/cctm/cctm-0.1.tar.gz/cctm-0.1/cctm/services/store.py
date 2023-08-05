# -*- coding:utf-8 -*-
import logging
from collections import OrderedDict
from cctm import json
from cctm.path import safe_open
from .resolver import Resolver
logger = logging.getLogger(__name__)


class FileStore(object):
    def __init__(self, config, path):
        self.config = config
        self.path = path

    def load(self):
        try:
            with safe_open(self.path, "r") as rf:
                return json.load(rf)
        except FileNotFoundError:
            return []

    def update(self, data, exists_data=None):
        exists_data = exists_data or self.load()
        store_data = [data]
        store_data.extend(self.remove(data["name"], exists_data))
        return store_data

    def remove(self, name, exists_data=None):
        exists_data = exists_data or self.load()
        return [d for d in exists_data if d["name"] != name]

    def save(self, store_data):
        with open(self.path, "w") as wf:
            json.dump(store_data, wf)


class RepositoriesStore(object):
    def __init__(self, config):
        self.config = config
        self.resolver = Resolver(self.config)

    def extract_packages(self, repositories=None):
        repositories = repositories or self.load()
        d = OrderedDict()

        for stored_url in repositories:
            logger.info("merging %s", stored_url)
            asset = self.resolver.resolve(stored_url)
            for data in asset.json():
                d[data["name"]] = data
        return list(d.values())


def packages_store(config, path=None):
    return FileStore(config, path=path or config.store_path)


def aliases_store(config, path=None):
    return FileStore(config, path=path or config.alias_path)
