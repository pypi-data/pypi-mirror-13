# -*- coding:utf-8 -*-
import os.path
import contextlib


def pickup_path_generate_candidates(src, target_file=""):
    path_list = src.split(os.path.sep)
    return [os.path.join(os.path.sep.join(path_list[:-i]), target_file) for i in range(1, len(path_list))]


def pickup_file(src, target_file):
    candidates = pickup_path_generate_candidates(src, target_file)
    for path in candidates:
        if os.path.exists(path):
            return path


@contextlib.contextmanager
def safe_open(path, *args, **kwargs):
    dirpath = os.path.dirname(path)
    if dirpath and not os.path.exists(dirpath):
        os.makedirs(dirpath)

    with open(path, *args, **kwargs) as ref:
        yield ref


def safe_listdir(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return os.listdir(path)
