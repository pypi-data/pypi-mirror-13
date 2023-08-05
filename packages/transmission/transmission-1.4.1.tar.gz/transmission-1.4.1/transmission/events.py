from .exceptions import ServerError
from .signals import pre_event_signal, post_event_signal
from django.db import transaction
from functools import wraps

import logging
import sys


logger = logging.getLogger(__name__)


def send_event_signals(func):
    """
        `send_event_signals` is an instance method decorator that is designed
        to generate pre and post signals for the method that it is
        decoratoring.
        E.g.
        class SomeModel(models.Model):
            @send_event_signals
            def say_hello(self):
                ...

        will send a pre_event_signal and a post_event_signal signal that will
        have the event_name="say_hello"
    """
    @wraps(func)
    def _wrap(self, *args, **kwargs):
        try:
            with transaction.atomic():
                # PRE EVENT SIGNAL
                pre_event_signal.send(
                    sender=self.__class__, instance=self,
                    event_name=func.__name__, arg_data=args, kwarg_data=kwargs
                )

                # EXECUTE ORIGINAL FUNCTION
                output = func(self, *args, **kwargs)

                # POST EVENT SIGNAL
                post_event_signal.send(
                    sender=self.__class__, instance=self,
                    event_name=func.__name__, event_output=output,
                    arg_data=args, kwarg_data=kwargs
                )

                return output
        except Exception, e:
            logger.error(unicode(e), exc_info=True)
            exc = type('EventError', (ServerError, e.__class__), {})
            raise exc(
                detail=(
                    'Sorry there was an error in processing '
                    'your request, please try again later.'
                )
            ), None, sys.exc_info()[2]
    return _wrap
