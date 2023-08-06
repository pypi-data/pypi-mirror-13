# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from os import path
from poort.utils import environ_from_yaml

HERE = path.abspath(path.dirname(__file__))


def get_base_environ():
    return environ_from_yaml(path.join(HERE, 'environ.yaml'))
