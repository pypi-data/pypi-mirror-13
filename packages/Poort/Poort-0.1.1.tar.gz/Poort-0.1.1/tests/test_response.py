# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from poort import HtmlResponse
from poort import JsonResponse
from poort import Request
from poort import Response
from poort import template_or_json_response
from poort import TemplateResponse
from utils import get_base_environ
from utils import HERE
import jinja2


class TestTemplateResponse(TemplateResponse):
    jinja = jinja2.Environment(
        loader=jinja2.FileSystemLoader(HERE))


class TestRequest(object):
    def test_basics(self):
        data = 'Hello world!'

        response = Response(data)

        assert response

    def test_json(self):
        data = {
            'message': 'Hello world!'
        }

        response = JsonResponse(data)

        assert response

    def test_html(self):
        data = '<p>Hello world!</p>'

        response = HtmlResponse(data)

        assert response

    def test_template(self):
        data = {
            'message': 'Hello world!'
        }

        response = TestTemplateResponse(data, 'index.html')

        assert response

    def test_template_or_json(self):
        data = {
            'message': 'Hello world!'
        }

        environ = get_base_environ()
        request = Request(environ)

        response = template_or_json_response(
            request,
            data, 'index.html',
            template_response_class=TestTemplateResponse)

        assert response
