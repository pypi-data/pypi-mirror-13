# coding: utf-8

from functools import partial, wraps
from logging import getLogger

from django.conf import settings
from django.conf.urls import url as django_url
from django.http import HttpResponse
from typeddict import ValidationError
import ujson


logger = getLogger('dj_tiny_api')


Response = HttpResponse
JsonResponse = partial(Response, content_type='application/json')


class WebError(Exception):
    status_code = 500
    _default_code = 'UnexpectedError'

    def __init__(self, code=None, message=None, status_code=None, **kwargs):

        self.code = code or self._default_code
        self.message = message or self.code
        self.status_code = status_code or self.status_code
        self.__dict__.update(kwargs)

    def __repr__(self):
        return '<{} [{}]>'.format(self.__class__.__name__, self.__dict__)

    def __str__(self):
        return repr(self)


class BadRequest(WebError):
    status_code = 400
    _default_code = 'BadRequest'


class Unauthorized(WebError):
    status_code = 401
    _default_code = 'Unauthorized'


class NotFound(WebError):
    status_code = 404
    default_code = 'NotFound'


class MethodNotAllowed(WebError):
    status_code = 405
    _default_code = 'MethodNotAllowed'


class Forbidden(WebError):
    status_code = 403
    _default_code = 'Forbidden'


class Conflict(WebError):
    status_code = 409
    _default_code = 'Conflict'


class FailedDependency(WebError):
    status_code = 424
    _default_code = 'FailedDependency'


class UnexpectedResult(WebError):
    _default_code = 'UnexpectedResult'


class Endpoint(object):

    def __init__(
        self,
        data_spec=None,
        result_spec=None,
        opt=False,
        auth_checks=None,
        slug=None,
        url=None,
        methods=None,
    ):
        self.data_spec = data_spec
        self.result_spec = result_spec
        self.opt = opt
        self.auth_checks = auth_checks or []
        self.slug = slug
        self.url = url
        self.methods = methods

    def __call__(self, f):

        self.slug = self.slug or f.__name__

        @wraps(f)
        def wrapped_f(request, *args, **kwargs):
            self.request = request
            try:
                self.after_request_set()
                for auth_func in self.auth_checks:
                    response = auth_func(request)
                    if response:
                        return response

                after_auth_result = self.after_auth()
                if isinstance(after_auth_result, Response):
                    return after_auth_result

                self.get_data()

                try:
                    self.validate_data()
                except ValidationError as e:
                    return self.error(BadRequest(message=str(e), extra=e.errors))

                kwargs['request'] = request

                self.before_view()
                result = f(self.data, *args, **kwargs)
            except WebError as e:
                return self.error(e)
            except Exception as e:
                message = 'Unexpected API error'
                logger.error(message, exc_info=True)
                return self.error(WebError(message=message))

            if result is None:
                if self.opt:
                    return self.response('null')
                else:
                    return self.error(UnexpectedResult())

            if isinstance(result, Response):
                return result
            elif not self.result_spec:
                return self.response(ujson.dumps(result))
            elif not isinstance(result, self.result_spec):
                return self.error(UnexpectedResult())
            else:
                return self.response(self.result_spec.dumps(result))

        if self.url:
            urlconf = __import__(settings.ROOT_URLCONF, {}, {}, [''])
            urlconf.urlpatterns.append(django_url(self.url, wrapped_f, name=self.slug))

        return wrapped_f

    def after_auth(self):
        pass

    def before_view(self):
        pass

    def after_request_set(self):
        pass

    def get_data(self):
        if self.request.method == 'POST':
            content_type = self.request.META.get('CONTENT_TYPE')
            if content_type and 'application/json' in content_type:
                try:
                    data = ujson.loads(self.request.body or 'null')
                except ValueError as e:
                    raise BadRequest(message='Invalid JSON: ' + str(e))
            else:
                data = self.request.POST.dict()

        elif self.request.method == 'GET':
            data = self.request.GET.dict()
        else:
            raise MethodNotAllowed(extra={'method': self.request.method})
        self.data = data

    def validate_data(self):
        if self.data_spec is not None:
            if self.data is None:
                raise BadRequest(message='Expecting non-empty data')
            if not isinstance(self.data, dict):
                raise BadRequest(message='data is not dict')
            self.data = self.data_spec(**self.data)

    def response(self, data=None, error=None, status_code=200):
        response_data = '{{"data": {data}, "error": {error}}}'.format(
            data=data or 'null',
            error=error or 'null',
        )

        return JsonResponse(
            response_data,
            status=status_code,
        )

    def error(self, e):
        error = ujson.encode(e, ensure_ascii=False)
        return self.response(error=error, status_code=e.status_code)
