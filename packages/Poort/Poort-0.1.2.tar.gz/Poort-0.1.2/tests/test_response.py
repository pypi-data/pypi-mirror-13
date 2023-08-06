# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from os import path
from poort import FileResponse
from poort import HtmlResponse
from poort import JsonResponse
from poort import Request
from poort import Response
from poort import template_or_json_response
from poort import TemplateResponse
from pytest import raises
from utils import get_environ
from utils import HERE
import jinja2


class TemplateResponseTest(TemplateResponse):
    jinja = jinja2.Environment(
        loader=jinja2.FileSystemLoader(HERE))


class DummyRequest(object):
    def __init__(self, environ):
        self.environ = environ


class TestRequest(object):
    def test_basics(self):
        data = 'Hello world!'

        response = Response(data)
        response.set_cookie('some-cookie', 'test')
        response.del_cookie('another-cookie')

        assert response.get_status() == '200 OK'
        assert response.get_body() == 'Hello world!'
        assert response.prepare_response() == [b'Hello world!']

        result = list()

        def start_response(status, headers):
            result.append(status)
            result.append(headers)

        result.append(response(None, start_response))

        del_cookie = result[1][1][1]

        assert result == [
            '200 OK',
            [
                ('Set-Cookie', 'some-cookie=test; HttpOnly; Path=/'),
                ('Set-Cookie', del_cookie),
            ],
            [b'Hello world!'],
        ]

        assert 'another-cookie=;' in del_cookie
        assert 'Max-Age=0;' in del_cookie

    def test_json(self):
        data = {
            'message': 'Hello world!'
        }

        response = JsonResponse(data)

        assert response.get_body() == '{"message": "Hello world!"}'

    def test_html(self):
        data = '<p>Hello world!</p>'

        response = HtmlResponse(data)

        assert response.get_body() == '<p>Hello world!</p>'

    def test_template(self):
        data = {
            'message': 'Hello world!'
        }

        response = TemplateResponseTest('index.html', data)

        assert response.get_body() == '<p>Hello world!</p>'

    def test_file(self):
        filename = path.join(HERE, 'environs', 'attachment.txt')
        response = FileResponse(filename)

        assert response.filename == filename
        assert response.as_attachment is False
        assert response.attachment_filename is None
        assert response.size == 19
        assert response.etag.startswith('etag-')
        assert response.etag.endswith('-19-2870615693')

        response.headers.clear()
        response.prepare_response()

        wsgi_list = response.headers.to_wsgi_list()
        assert wsgi_list[1:4] == [
            ('Cache-Control', 'public'),
            ('Content-Type', 'text/plain'),
            ('Content-Length', '19')
        ]

        response.headers.clear()
        response.prepare_response(DummyRequest({
            'REQUEST_METHOD': 'GET'
        }))

        wsgi_list = response.headers.to_wsgi_list()
        assert wsgi_list[1:3] == [
            ('Etag', '"' + response.etag + '"'),
            ('Cache-Control', 'max-age=43200, public'),
        ]
        assert wsgi_list[4:-1] == [
            ('Content-Type', 'text/plain'),
            ('Content-Length', '19'),
        ]

        response.headers.clear()
        response.prepare_response(DummyRequest({
            'REQUEST_METHOD': 'GET',
            'HTTP_IF_NONE_MATCH': response.etag,
        }))

        wsgi_list = response.headers.to_wsgi_list()
        assert wsgi_list[1:] == [
            ('Etag', '"' + response.etag + '"'),
            ('Cache-Control', 'max-age=43200, public'),
        ]

        response = FileResponse(filename, as_attachment=True)

        assert response.as_attachment is True
        assert response.attachment_filename == 'attachment.txt'

        response.headers.clear()
        response.prepare_response()

        wsgi_list = response.headers.to_wsgi_list()
        assert wsgi_list[1:4] == [
            ('Cache-Control', 'public'),
            ('Content-Type', 'text/plain'),
            ('Content-Length', '19'),
        ]
        assert wsgi_list[-1] == ('Content-Disposition',
                                 'attachment; filename=attachment.txt')

        response = FileResponse(filename, as_attachment='download.txt')

        assert response.as_attachment is True
        assert response.attachment_filename == 'download.txt'

        with raises(ValueError):
            FileResponse(filename + '-error-please')

    def test_template_or_json(self):
        data = {
            'message': 'Hello world!'
        }

        environ = get_environ('base')
        request = Request(environ)

        response = template_or_json_response(
            request,
            data, 'index.html',
            template_response_class=TemplateResponseTest)

        assert response

        environ = get_environ('json-post')
        request = Request(environ)

        response = template_or_json_response(
            request,
            data, 'index.html',
            json_response_class=JsonResponse)

        assert response
