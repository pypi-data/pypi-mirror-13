# -*- coding:utf-8 -*-
import os.path
from cached_property import cached_property as reify
from cctm.path import safe_listdir
from . import packages_store, aliases_store


def normalize(name):
    return name.lower().replace("_", "").replace("-", "")


class InstalledPackageLookup(object):
    def __init__(self, config):
        self.config = config

    @reify
    def aliases(self):
        return aliases_store(self.config).load()

    def load(self):
        r = []
        for path in safe_listdir(self.config.store_dir):
            basename = path.replace(".", "/")
            r.append({
                "name": basename,
                "path": os.path.join(self.config.store_dir, path)
            })
        return r

    def lookup_loose(self, name, exists_data=None):
        name = get_name(name, self.aliases)
        exists_data = exists_data or self.load()
        return lookup_loose(name, exists_data)

    def lookup(self, name, exists_data=None):
        name = get_name(name, self.aliases)
        exists_data = exists_data or self.load()
        return lookup(name, exists_data)


class PackageLookup(object):
    def __init__(self, config):
        self.config = config

    @reify
    def aliases(self):
        return aliases_store(self.config).load()

    def load(self):
        return packages_store(self.config).load()

    def lookup_loose(self, name, exists_data=None):
        name = get_name(name, self.aliases)
        exists_data = exists_data or self.load()
        return lookup_loose(name, exists_data)

    def lookup(self, name, exists_data=None):
        name = get_name(name, self.aliases)
        exists_data = exists_data or self.load()
        return lookup(name, exists_data)


def get_name(name_or_alias, exists_data):
    alias = lookup_loose(name_or_alias, exists_data)
    if alias is not None:
        return alias["link"]
    return name_or_alias


def lookup(name, exists_data):
    for d in exists_data:
        package_name = d["name"]
        if package_name == name:
            return d


def lookup_loose(name, exists_data):
    name = normalize(name)
    for d in exists_data:
        package_name = normalize(d["name"])
        if package_name == name:
            return d
        try:
            if package_name.split("/")[1] == name:
                return d
        except IndexError:
            pass
