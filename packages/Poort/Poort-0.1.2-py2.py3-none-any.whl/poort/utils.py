# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from copy import deepcopy
from io import BytesIO
from pandora.compat import PY2
from pandora.compat import string_types
from werkzeug.datastructures import FileStorage as WerkzeugFileStorage
from werkzeug.utils import secure_filename
from werkzeug.wsgi import FileWrapper
import re


def flatten_multidict(data, validate=None, wrap=None):
    result = {}
    for key, values in data.lists():
        if validate is not None:
            values = list(filter(validate, values))
        if wrap is not None:
            values = list(map(wrap, values))
        result[key] = values[0] if len(values) == 1 else values
    return result


class FileStorage(WerkzeugFileStorage):
    @classmethod
    def from_original(cls, original):
        return cls(stream=original.stream, filename=original.filename,
                   name=original.name, content_type=original.content_type,
                   content_length=original.content_length,
                   headers=original.headers)

    @property
    def secure_filename(self):
        filename = re.split(r'[\\/]', self.filename)[-1]
        return secure_filename(filename)

    def __eq__(self, other):
        return (self.content_type == other.content_type and
                self.content_length == other.content_length and
                self.mimetype == other.mimetype and
                self.mimetype_params == other.mimetype_params and
                self.filename == other.filename and
                self.secure_filename == other.secure_filename)


def copy_request_environ(environ):
    copy = deepcopy(environ)

    # copy the input and place it back
    copy['INPUT'] = environ['wsgi.input'].read()

    if type(copy['INPUT']) in string_types:
        if PY2:
            environ['wsgi.input'] = BytesIO(bytearray(copy['INPUT'], 'UTF8'))
        else:
            environ['wsgi.input'] = BytesIO(bytes(copy['INPUT'], 'UTF8'))
    else:
        environ['wsgi.input'] = BytesIO(copy['INPUT'])

    del copy['wsgi.errors']
    del copy['wsgi.file_wrapper']
    del copy['wsgi.input']

    if 'gunicorn.socket' in copy:
        del copy['gunicorn.socket']

    return copy


def environ_from_dict(base):
    environ = deepcopy(base)

    environ['wsgi.file_wrapper'] = FileWrapper
    environ['wsgi.errors'] = BytesIO()

    if 'INPUT' in environ:
        if 'CONTENT_LENGTH' not in environ:
            environ['CONTENT_LENGTH'] = str(len(environ['INPUT']))

        if PY2:
            environ['wsgi.input'] = BytesIO(
                bytearray(environ['INPUT'], 'UTF8'))
        else:
            environ['wsgi.input'] = BytesIO(bytes(environ['INPUT'], 'UTF8'))

        del environ['INPUT']
    else:
        environ['wsgi.input'] = BytesIO(b'')

    return environ
