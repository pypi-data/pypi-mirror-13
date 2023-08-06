# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from poort import Request
from utils import get_base_environ


class TestRequest(object):
    def test_basics(self):
        environ = get_base_environ()
        request = Request(environ)

        assert request
