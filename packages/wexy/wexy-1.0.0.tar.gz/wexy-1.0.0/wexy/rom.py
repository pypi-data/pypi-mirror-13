# coding:utf-8

from collections import Mapping


class Rom(Mapping):
    def __init__(self, env):
        self._env = env

    def __len__(self):
        return self._env.__len__()

    def __iter__(self):
        return self._env.__iter__()

    def __getitem__(self, key):
        return self._env.__getitem__(key)
