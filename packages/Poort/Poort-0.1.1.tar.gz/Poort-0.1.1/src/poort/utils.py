# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from copy import deepcopy
from pandora.compat import StringIO
from werkzeug.datastructures import FileStorage as WerkzeugFileStorage
from werkzeug.utils import secure_filename
from werkzeug.wsgi import FileWrapper
import re
import yaml


def flatten_multidict(data, validate=None, wrap=None):
    r"""Flatten a `werkzeug` MultiDict into a simple dict.

    **Parameters**

    :param data: MultiDict to flatten.
    :param validate: Only append values that match this validator.
    :type data: werkzeug.datastructures.MultiDict
    :type validate: mixed for filter
    :rtype: dict

    """
    result = {}
    for key, values in data.lists():
        if validate is not None:
            values = filter(validate, values)
        if wrap is not None:
            values = map(wrap, values)
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


def copy_request_environ(environ):
    copy = deepcopy(environ)

    # copy the input and place it back
    copy['INPUT'] = environ['wsgi.input'].read()
    environ['wsgi.input'] = StringIO(copy['INPUT'])

    del copy['wsgi.errors']
    del copy['wsgi.file_wrapper']
    del copy['wsgi.input']

    if 'gunicorn.socket' in copy:
        del copy['gunicorn.socket']

    return copy


def environ_from_yaml(filename):
    with open(filename) as stream:
        environ = yaml.safe_load(stream)

    environ['wsgi.input'] = StringIO(environ['INPUT'])
    environ['wsgi.file_wrapper'] = FileWrapper
    environ['wsgi.errors'] = StringIO()

    del environ['INPUT']

    return environ
