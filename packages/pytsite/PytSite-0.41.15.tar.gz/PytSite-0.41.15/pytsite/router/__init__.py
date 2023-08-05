"""PytSite Router.
"""
import re as _re
from os import path as _path, makedirs as _makedirs
from traceback import format_exc as _format_exc
from urllib import parse as _urlparse
from importlib import import_module as _import_module
from werkzeug.routing import Map as _Map, Rule as _Rule
from werkzeug.exceptions import HTTPException as _HTTPException
from werkzeug.contrib.sessions import FilesystemSessionStore as _FilesystemSessionStore
from htmlmin import minify as _minify
from pytsite import reg as _reg, logger as _logger, http as _http, util as _util, lang as _lang, metatag as _metatag

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

_routes = _Map()
_map_adapter = _routes.bind(_reg.get('server.name', 'localhost'))
_path_aliases = {}

# Registering module's language package
_lang.register_package(__name__)

# Create directory to store session data
session_storage_path = _reg.get('paths.session')
if not _path.exists(session_storage_path):
    _makedirs(session_storage_path, 0o755, True)

# Initializing session store
_session_store = _FilesystemSessionStore(path=session_storage_path, session_class=_http.session.Session)

# Enable or disable cache
no_cache = False

# Request object
request = None
""":type : pytsite.http._request.Request"""

# Session object
session = None
""":type : pytsite.http._session.Session"""


class Rule(_Rule):
    """Routing Rule.
    """

    def __init__(self, url_path: str, **kwargs):
        self.call = kwargs.pop('call')
        self.filters = kwargs.pop('filters', ())

        endpoint = kwargs.get('endpoint')
        try:
            _routes.iter_rules(endpoint)
            raise Exception("Endpoint name '{}' already used.".format(endpoint))
        except KeyError:
            super().__init__(url_path, **kwargs)

    def get_rules(self, rules_map):
        return super().get_rules(rules_map)


def add_rule(pattern: str, name: str = None, call: str = None, args: dict = None, methods=None, filters=None):
    """Add a rule to the router.
    :param methods: str|tuple|list
    """
    if not name and not call:
        raise Exception("Either 'name' or 'call' must be specified.")

    if filters is None:
        filters = []

    if isinstance(filters, str):
        filters = [filters]

    if isinstance(methods, str):
        methods = (methods,)

    if not isinstance(filters, list) and not isinstance(filters, tuple):
        raise Exception('Filters must be a string, list or tuple. {} given.'.format(repr(filters)))

    if not name:
        name = _util.random_str(32)

    if not call:
        call = name

    if not args:
        args = {}

    args['_name'] = name
    args['_call'] = call

    rule = Rule(
        url_path=pattern,
        endpoint=name,
        call=call,
        defaults=args,
        methods=methods,
        filters=filters
    )

    _routes.add(rule)


def add_path_alias(alias: str, target: str):
    _path_aliases[alias] = target


def is_ep_callable(ep_name: str) -> bool:
    try:
        resolve_ep_callable(ep_name)
        return True
    except ImportError:
        return False


def resolve_ep_callable(ep_name: str) -> callable:
    endpoint = ep_name.split('.')
    if not len(endpoint):
        raise TypeError("Invalid format of endpoint specification: '{}'".format(ep_name))

    module_name = '.'.join(endpoint[0:len(endpoint) - 1])
    callable_name = endpoint[-1]

    module = _import_module(module_name)
    if callable_name not in dir(module):
        raise ImportError("'{}' is not callable".format(ep_name))

    callable_obj = getattr(module, callable_name)
    if not hasattr(callable_obj, '__call__'):
        raise ImportError("'{}' is not callable".format(ep_name))

    return callable_obj


def call_ep(ep_name: str, args: dict = None, inp: dict = None):
    """Call a callable.
    """
    if '_call' in args:
        args['_call_orig'] = args['_call']
    args['_call'] = ep_name

    if '_name' in args:
        args['_name_orig'] = args['_name']
    args['_name'] = ep_name

    return resolve_ep_callable(ep_name)(args, inp)


def dispatch(env: dict, start_response: callable):
    """Dispatch the request.
    """
    from pytsite import tpl, events
    global _map_adapter, request, session, no_cache

    # Check maintenance mode status
    if _path.exists(_reg.get('paths.maintenance.lock')):
        wsgi_response = _http.response.Response(response=_lang.t('pytsite.router@we_are_in_maintenance'),
                                                status=503, content_type='text/html')
        return wsgi_response(env, start_response)

    # Remove trailing slash
    _map_adapter = _routes.bind_to_environ(env)
    path_info = _map_adapter.path_info
    if len(path_info) > 1 and path_info.endswith('/'):
        redirect_url = _re.sub('/$', '', path_info)
        if _map_adapter.query_args:
            redirect_url += '?' + _map_adapter.query_args
        return _http.response.Redirect(redirect_url, 301)(env, start_response)

    # All requests are cached by default
    no_cache = False

    # Detect language from path
    languages = _lang.langs()
    if len(languages) > 1:
        if _re.search('^/[a-z]{2}(/|$)', env['PATH_INFO']):
            # Extract language code as first two-letters of the path
            lang_code = env['PATH_INFO'][1:3]
            try:
                _lang.set_current(lang_code)
                env['PATH_INFO'] = env['PATH_INFO'][3:]
                if not env['PATH_INFO']:
                    env['PATH_INFO'] = '/'
                # If requested language is default, redirect to path without language prefix
                if lang_code == languages[0]:
                    return _http.response.Redirect(env['PATH_INFO'], 301)(env, start_response)
            except _lang.error.LanguageNotSupported:
                # If language is not defined, do nothing. 404 will fired in the code below.
                pass
        else:
            # No language code found in the path. Set first defined language as current.
            _lang.set_current(languages[0])

    # Notify listeners
    events.fire('pytsite.router.pre_dispatch', path_info=env['PATH_INFO'])

    # Loading path alias
    env['PATH_INFO'] = _path_aliases.get(env['PATH_INFO'], env['PATH_INFO'])

    # Replace url adapter with modified environment
    _map_adapter = _routes.bind_to_environ(env)

    # Creating request
    request = _http.request.Request(env)

    # Session setup
    sid = request.cookies.get('PYTSITE_SESSION')
    if sid:
        session = _session_store.get(sid)
    else:
        session = _session_store.new()

    # Processing
    try:
        # Notify listeners
        events.fire('pytsite.router.dispatch')

        # Search for rule
        rule, rule_args = _map_adapter.match(return_rule=True)

        # Processing rule filters
        for flt in rule.filters:
            flt_args = rule_args.copy()
            flt_split = flt.split(':')
            flt_endpoint = flt_split[0]
            if len(flt_split) > 1:
                for flt_arg_str in flt_split[1:]:
                    flt_arg_str_split = flt_arg_str.split('=')
                    if len(flt_arg_str_split) == 2:
                        flt_args[flt_arg_str_split[0]] = flt_arg_str_split[1]

            flt_response = call_ep(flt_endpoint, flt_args, request.inp)
            if isinstance(flt_response, _http.response.Redirect):
                return flt_response(env, start_response)

        # Preparing response object
        wsgi_response = _http.response.Response(response='', status=200, content_type='text/html', headers=[])

        # Processing response from handler
        response_from_callable = call_ep(rule.call, rule_args, request.inp)
        if isinstance(response_from_callable, str):
            if _reg.get('output.minify'):
                response_from_callable = _minify(response_from_callable, True, True)
            wsgi_response.data = response_from_callable
        elif isinstance(response_from_callable, _http.response.Response):
            wsgi_response = response_from_callable
        else:
            wsgi_response.data = ''

        # Cache control
        if no_cache or request.method != 'GET':
            wsgi_response.headers.set('Cache-Control', 'private, max-age=0, no-cache, no-store')
            wsgi_response.headers.set('Pragma', 'no-cache')
        else:
            wsgi_response.headers.set('Cache-Control', 'public')

        # Updating session data
        if session.should_save:
            _session_store.save(session)
            wsgi_response.set_cookie('PYTSITE_SESSION', session.sid)

        return wsgi_response(env, start_response)

    except Exception as e:
        if isinstance(e, _HTTPException):
            code = e.code
            title = _lang.t('pytsite.router@http_error_' + str(e.code))
        else:
            code = 500
            title = _lang.t('pytsite.router@error', {'code': '500'})
            _logger.error(str(e), __name__)

        _metatag.t_set('title', title)

        args = {
            'title': title,
            'exception': e,
            'traceback': _format_exc()
        }

        events.fire('pytsite.router.exception', args=args)

        if is_ep_callable('app.ep.exception'):
            wsgi_response = call_ep('app.ep.exception', args)
        else:
            wsgi_response = tpl.render('exceptions/common', args)

        return _http.response.Response(wsgi_response, code, content_type='text/html')(env, start_response)


def base_path(lang: str = None) -> str:
    """Get base path of application.
    """
    available_langs = _lang.langs()

    if len(available_langs) == 1:
        return '/'

    if not lang:
        lang = _lang.get_current()
    if lang not in available_langs:
        raise Exception("Language '{}' is not supported.".format(lang))

    r = '/'
    if lang != available_langs[0]:
        r += lang + '/'

    return r


def server_name():
    """Get server's name.
    """
    from pytsite import reg
    name = reg.get('server.name', 'localhost')
    if _map_adapter:
        name = _map_adapter.server_name

    return name


def scheme():
    """Get current URL scheme.
    """
    r = 'http'
    if _map_adapter:
        r = _map_adapter.url_scheme

    return r


def base_url(lang: str = None, query: dict = None):
    """Get base URL of the application.
    """
    r = scheme() + '://' + server_name() + base_path(lang)
    if query:
        r = url(r, query=query)

    return r


def is_base_url(compare: str = None) -> bool:
    """Check if the given URL is base.
    """
    if not compare:
        compare = current_url(True)

    return base_url() == compare


def url(url_str: str, lang: str = None, strip_lang=False, query: dict = None, relative: bool = False,
        strip_query=False) -> str:
    """Generate an URL.
    """
    if not url_str:
        raise ValueError('url_str cannot be empty.')

    # https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlparse
    parsed_url = _urlparse.urlparse(url_str)
    r = [
        parsed_url[0] if parsed_url[0] else scheme(),  # 0, Scheme
        parsed_url[1] if parsed_url[1] else server_name(),  # 1, Netloc
        parsed_url[2] if parsed_url[2] else '',  # 2, Path
        parsed_url[3] if parsed_url[3] else '',  # 3, Params
        parsed_url[4] if parsed_url[4] else '',  # 4, Query
        parsed_url[5] if parsed_url[5] else '',  # 5, Fragment
    ]

    if relative:
        r[0] = ''
        r[1] = ''

    if strip_query:
        # Stripping query
        r[4] = ''
    elif query:
        # Attaching additional query arguments
        parsed_qs = _urlparse.parse_qs(parsed_url[4])
        parsed_qs.update(query)
        r[4] = _urlparse.urlencode(parsed_qs, doseq=True)

    # Adding language suffix
    if not strip_lang:
        lang_re = '^/({})/'.format('|'.join(_lang.langs()))
        if not _re.search(lang_re, parsed_url[2]):
            r[2] = str(base_path(lang) + parsed_url[2]).replace('//', '/')

    return _urlparse.urlunparse(r)


def current_path(strip_query=False, resolve_alias=True, strip_lang=True, lang: str = None) -> str:
    """Get current path.
    """
    if not request:
        return '/'

    r = _urlparse.urlparse(request.url)
    path = _urlparse.urlunparse(('', '', r[2], r[3], '', ''))
    query = _urlparse.urlunparse(('', '', '', '', r[4], r[5]))

    if resolve_alias:
        for k, v in _path_aliases.items():
            if path == v:
                path = k
                break

    if not strip_lang:
        path = str(base_path(lang) + path).replace('//', '/')

    r = str(path)
    if not strip_query:
        r += str(query)

    return r


def current_url(strip_query: bool = False, resolve_alias: bool = True, lang: str = None) -> str:
    """Get current URL.
    """
    return scheme() + '://' + server_name() + current_path(strip_query, resolve_alias, False, lang)


def ep_path(endpoint: str, args: dict = None, strip_lang=False) -> str:
    return url(_map_adapter.build(endpoint, args), relative=True, strip_lang=strip_lang)


def ep_url(ep_name: str, args: dict = None, strip_lang=False) -> str:
    """Get URL for endpoint.
    """
    r = _map_adapter.build(ep_name, args)
    return url(r, strip_lang=strip_lang, relative=False)
