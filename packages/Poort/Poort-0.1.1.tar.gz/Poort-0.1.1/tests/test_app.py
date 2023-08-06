from __future__ import absolute_import, division, print_function

from avenue import Avenue
from pandora import Laborer
from poort import JsonResponse
from poort import Request
from poort import template_or_json_response
# from poort.utils import copy_request_environ
from threading import local
# import datetime as dt
# import yaml


class TestApp(object):
    def setup_application(self):
        router = Avenue()
        laborer = Laborer()
        threadlocal = local()

        @laborer.provider('request')
        def provide_request(kwargs):
            return threadlocal.request

        @router.attach(path='/')
        def get_index(request):
            data = {
                'message': 'Hello world!',
                'request': request.as_dict(),
            }

            return template_or_json_response(request, 'index.html', data)

        def application(environ, start_response):
            # -- store the request for testing purposes
            # now = dt.datetime.now()
            # filename = './{:s}.yaml'.format(now.strftime('%Y%m%d-%H%M%S'))
            # with open(filename, 'w') as stream:
            #     yaml.safe_dump(copy_request_environ(environ), stream,
            #                    allow_unicode=True, default_flow_style=False,
            #                    indent=2)

            request = Request(environ)
            setattr(threadlocal, 'request', request)

            path, match = router.match(**request.as_dict())

            if path:
                partial = laborer.provide(path.func)
                response = partial(**match.kwargs)
            else:
                response = JsonResponse({
                    'message': 'Page does not exist.'
                }, status_code=404)

            delattr(threadlocal, 'request')
            return response(start_response)

        return application

    def test_basics(self):
        application = self.setup_application()
        assert application


application = TestApp().setup_application()
