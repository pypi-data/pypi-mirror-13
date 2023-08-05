# coding=utf-8
from __future__ import unicode_literals, absolute_import

import celery
# used to avoid strange import bug with Python 3.2/3.3
# noinspection PyStatementEffect
celery.__file__
from celery import shared_task
from django.utils.module_loading import import_string
from django.conf import settings
from django.http import HttpRequest
from djangofloor.utils import import_module
from django.utils.lru_cache import lru_cache

from djangofloor.decorators import REGISTERED_SIGNALS, RedisCallWrapper, SignalRequest

__author__ = 'Matthieu Gallet'


USER = 'users'
SESSION = 'sessions'
BROADCAST = 'broadcast'
WINDOW = 'window'
# special value used for plain HTTP requests
RETURN = 'return'


@shared_task(serializer='json')
def signal_task(signal_name, request, from_client, kwargs):
    """Unique Celery tasks, transparently called for delayed signal calls.

    You should not have to use it.

    :type signal_name: :class:`str`
    :param request: a :class:`djangofloor.decorators.SignalRequest` serialized as a :class:`dict` object
    :type request: :class:`dict`
    :type from_client: :class:`bool`
    :type kwargs: :class:`dict`
    """
    import_signals()
    request = SignalRequest(**request)
    if signal_name not in REGISTERED_SIGNALS:
        return
    for wrapper in REGISTERED_SIGNALS[signal_name]:
        if not isinstance(wrapper, RedisCallWrapper) or not wrapper.delayed:
            continue
        if (from_client and not wrapper.allow_from_client) or (wrapper.auth_required and not request.session_key):
            continue
        prepared_kwargs = wrapper.prepare_kwargs(kwargs)
        wrapper.function(request, **prepared_kwargs)


@lru_cache()
def import_signals():
    """Import all `signals.py` files to register signals.
    """
    for app in settings.INSTALLED_APPS:
        try:
            import_module('%s.signals' % app)
        except ImportError:
            pass


@lru_cache()
def get_signal_encoder():
    """ return the class for encoding signal data to JSON. The result is cached.

    Only import `settings.FLOOR_SIGNAL_ENCODER` and cache the results.
    """
    return import_string(settings.FLOOR_SIGNAL_ENCODER)


@lru_cache()
def get_signal_decoder():
    """ return the class for decoding signal data to JSON. The result is cached.

    Only import `settings.FLOOR_SIGNAL_DECODER` and cache the results.
    """
    return import_string(settings.FLOOR_SIGNAL_DECODER)


def call(signal_name, request, sharing=None, **kwargs):
    """ Call a signal and all the three kinds of receivers can receive it:
        * standard Python receiverrs
        * Python receivers through Celery (thanks to the `delayed` argument)
        * JavaScript receivers (through websockets)

    Example:

    .. code-block:: python

        from djangofloor.tasks import call, SESSION
        from djangofloor.decorators import connect

        def any_function(request):
            call('myproject.signal_name', request, sharing=SESSION, arg1="arg1", arg2=42)

        @connect('myproject.signal_name')
        def signal_name(request, arg1, arg2):
            print(arg1, arg2)


    :param signal_name:
    :type signal_name: :class:`str`
    :param request: initial request, giving informations about HTTP sessions and its user
    :type request: :class:`djangofloor.decorators.SignalRequest` or :class:`django.http.HttpRequest`
    :param sharing:
        * `None`: does not propagate to the JavaScript (client) side
        * `WINDOW`: only to the browser window that initiated the original request
        * `USER`, `SESSION`, `BROADCAST`: propagate to the request user, only to its current session,
            or to all currently logged-in users
        * {'users': ['username1', 'username2'], 'groups': ['group1', 'group2'], 'broadcast': True}
         (or any subset of these keys)
        * `RETURN` return result values of signal calls to the caller
    :param kwargs: arguments for the receiver
    """
    return df_call(signal_name, request, sharing=sharing, from_client=False, kwargs=kwargs)


def df_call(signal_name, request, sharing, from_client, kwargs):
    """ Call a signal and all the three kinds of receivers can receive it:
        * standard Python receiverrs
        * Python receivers through Celery (thanks to the `delayed` argument)
        * JavaScript receivers (through websockets)

    Do not use it directly, you should prefer use the `call` function.

    :param signal_name:
    :type signal_name: :class:`str`
    :param request: initial request, giving informations about HTTP sessions and its user
    :type request: :class:`djangofloor.decorators.SignalRequest` or :class:`django.http.HttpRequest`
    :param sharing:
        * `None`: does not propagate to the JavaScript (client) side
        * `WINDOW`: only to the browser window that initiated the original request
        * `USER`, `SESSION`, `BROADCAST`: propagate to the request user, only to its current session,
            or to all currently logged-in users
        * {'users': ['username1', 'username2'], 'groups': ['group1', 'group2'], 'broadcast': True}
            (or any subset of these keys)
        * `RETURN` return result values of signal calls to the caller
    :param from_client: True if this call comes a JS client
    :param kwargs: arguments for the receiver
    :return:
        if sharing != `RETURN`: return `None`
        else: call `djangofloor.tasks.df_call` on each element of the call result
    """
    import_signals()
    result = []
    if isinstance(request, HttpRequest):
        request = SignalRequest.from_request(request)
    if sharing is not None and sharing != RETURN:
        if settings.FLOOR_USE_WS4REDIS:
            from djangofloor.df_ws4redis import ws_call
            ws_call(signal_name, request, sharing, kwargs)
        else:
            from djangofloor.df_redis import push_signal_call
            push_signal_call(request, signal_name, kwargs=kwargs, sharing=sharing)

    must_delay = False
    for wrapper in REGISTERED_SIGNALS.get(signal_name, []):
        if (not wrapper.allow_from_client and from_client) or (wrapper.auth_required and not request.session_key):
            continue
        if wrapper.delayed:
            must_delay = True
        else:
            prepared_kwargs = wrapper.prepare_kwargs(kwargs)
            wrapper_result = wrapper.function(request, **prepared_kwargs)
            if wrapper_result:
                result += list(wrapper_result)
    if must_delay and settings.USE_CELERY:
        signal_task.delay(signal_name, request.to_dict(), from_client, kwargs)
    if sharing == RETURN:
        return result
    for data in result:
        df_call(data['signal'], request, sharing=data.get('sharing', SESSION), from_client=False,
                kwargs=data['options'])
