from django.conf import settings
from django.conf.urls import url
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.utils.html import escape
from django.utils.importlib import import_module
from django.utils.six import iteritems, wraps, iterkeys, itervalues
from django.views.decorators.cache import never_cache

__author__ = 'snake'


def response_wrap(response):
    """
    Convert ``response`` from any object types to http response
    Will try to prettify lists dans dicts
    """
    if hasattr(response, 'status_code'):
        # Is a valid http response
        return response
    if isinstance(response, (list, tuple, dict)):
        try:
            response = iteritems(response)
        except AttributeError:
            pass
        output = '<br>'.join(escape(obj) for obj in response)
    else:
        output = escape(response)
    return HttpResponse(output)


def protect_access(view):
    """
    Make sure ``view`` is used only by superusers when in prod
    """
    if not settings.DEBUG:
        view = user_passes_test(lambda u: u.is_superuser)(view)
    return view


def hotfix_wrap(func):
    """
    Decorator that turns any function into a view.
    """

    @never_cache
    @protect_access
    @wraps(func)
    def _wrapper(*args, **kwargs):
        return response_wrap(func(*args, **kwargs))

    return _wrapper


def hotfix_callables():
    """
    Generate a list of callables from installed apps with hotfix.py
    """
    for app in settings.INSTALLED_APPS:
        hotfix_module_name = '%s.hotfix' % app
        try:
            hotfix_module = import_module(hotfix_module_name)
        except ImportError as e:
            if 'hotfix' not in str(e):
                raise
            continue
        for attr in dir(hotfix_module):
            obj = getattr(hotfix_module, attr)
            if callable(obj) and obj.__module__ == hotfix_module.__name__:
                yield obj


class HotfixDuplicateKeyException(Exception):
    """
    Hotfix function names are unique because they would give the same url
    """

    def __init__(self, key):
        super(HotfixDuplicateKeyException, self).__init__('Function "%s" is already registered in hotfix' % key)


class HotfixRegister(object):
    """
    Url pattern generator and registry
    """

    def __init__(self):
        self._registry = {'index': url(r'^$', hotfix_wrap(self.index_view), name='index')}

    def index_view(self, request):
        return list(iterkeys(self._registry))

    def _register(self, f):
        if f.__name__ in self._registry:
            raise HotfixDuplicateKeyException(f.__name__)
        self._registry[f.__name__] = url(r'^%s/?$' % f.__name__, hotfix_wrap(f))
        return f

    def autodiscover(self):
        for callable_ in hotfix_callables():
            self._register(callable_)

    @property
    def urlpatterns(self):
        return list(itervalues(self._registry))