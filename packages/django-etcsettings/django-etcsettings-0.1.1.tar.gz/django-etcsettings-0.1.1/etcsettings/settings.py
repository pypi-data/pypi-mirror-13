# coding: utf-8

from . import load_settings


__all__ = []


for k, v in load_settings().items():
    globals()[k] = v
    __all__.append(k)
