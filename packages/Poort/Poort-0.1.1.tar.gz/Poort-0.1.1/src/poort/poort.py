from __future__ import absolute_import, division, print_function

from .utils import FileStorage
from .utils import flatten_multidict
from os import path
from werkzeug.datastructures import Headers
from werkzeug.formparser import parse_form_data
from werkzeug.http import HTTP_STATUS_CODES
from werkzeug.http import parse_cookie
from werkzeug.urls import url_decode
import jinja2
import json


class Request(object):
    def __init__(self, environ):
        self.environ = environ

        self.host = environ['HTTP_HOST']
        self.path = environ['PATH_INFO']
        self.method = environ['REQUEST_METHOD']
        self.ip_address = environ.get('REMOTE_ADDR', None)
        self.accept_type = environ.get('HTTP_ACCEPT', '')
        self.content_type = environ.get('HTTP_CONTENT_TYPE', '')

        self.want_json = 'application/json' in self.accept_type
        self.want_html = 'text/html' in self.accept_type

        stream, form, files = parse_form_data(environ)

        self.query = flatten_multidict(url_decode(environ['QUERY_STRING']))
        self.form = flatten_multidict(form)
        self.files = flatten_multidict(files, lambda v: len(v.filename),
                                       FileStorage.from_original)

        self.cookies = parse_cookie(environ)

        self.params = dict()
        self.params.update(self.query)
        self.params.update(self.form)
        self.params.update(self.files)

        if 'application/json' in self.content_type:
            self.json = json.loads(stream.read())
            self.params.update(self.json)
        else:
            self.json = None

    def as_dict(self):
        return {
            'host': self.host,
            'path': self.path,
            'method': self.method,

            'ip_address': self.ip_address,

            'accept_type': self.accept_type,
            'content_type': self.content_type,

            'want_json': self.want_json,
            'want_html': self.want_html,

            'query': self.query,
            'form': self.form,
            'files': self.files,
            'cookies': self.cookies,
            'json': self.json,

            'params': self.params,
        }


class Response(object):
    def __init__(self, body, headers=None, status_code=200):
        self.status_code = status_code
        self.headers = Headers(headers)
        self.body = body

    def get_status(self):
        return '{:d} {:s}'.format(self.status_code,
                                  HTTP_STATUS_CODES[self.status_code])

    def get_body(self):
        return self.body

    def __call__(self, start_response):
        start_response(self.get_status(), self.headers.to_wsgi_list())
        return [self.get_body().encode('utf-8')]


class JsonResponse(Response):
    def __init__(self, data, headers=None, status_code=200):
        self.data = data
        super(JsonResponse, self).__init__('', headers, status_code)
        self.headers.add('Content-Type', 'application/json')

    def get_body(self):
        return json.dumps(self.data, default=lambda v: repr(v))


class HtmlResponse(Response):
    def __init__(self, body, headers=None, status_code=200):
        super(HtmlResponse, self).__init__(body, headers, status_code)
        self.headers.add('Content-Type', 'text/html')


class TemplateResponse(HtmlResponse):
    jinja = jinja2.Environment(
        loader=jinja2.FileSystemLoader(path.abspath('.')))

    def __init__(self, template, context, headers=None, status_code=200):
        self.template = template
        self.context = context

        super(HtmlResponse, self).__init__('', headers, status_code)

    def get_body(self):
        return self.jinja.get_template(self.template).render(**self.context)


def template_or_json_response(request, template, context, headers=None,
                              status_code=200, template_response_class=None,
                              json_response_class=None):
    if template_response_class is None:
        template_response_class = TemplateResponse
    if json_response_class is None:
        json_response_class = JsonResponse

    if request.want_json:
        return json_response_class(context, headers, status_code)
    else:
        return template_response_class(template, context, headers, status_code)
