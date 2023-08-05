import logging
import sys
import warnings


logger = logging.getLogger(__name__)


def parse_receiver_resps(receiver_resps, log=logger):
    for _, resp in receiver_resps:
        try:
            if isinstance(resp, Exception):
                raise resp
        except Exception, e:
            log.error(unicode(e), exc_info=True)


class RemovedInTransmission2Warning(DeprecationWarning):
    pass


# Deprecated aliases for functions were exposed in this module.

def make_alias(func_name):
    # Close func_name.
    def alias(*args, **kwargs):
        warnings.warn(
            "transmission.utils.%s is deprecated." % func_name,
            RemovedInTransmission2Warning, stacklevel=2
        )
        # This raises a second warning.
        from . import transitions
        return getattr(transitions, func_name)(*args, **kwargs)
    alias.__name__ = func_name
    return alias

this_module = sys.modules['transmission.utils']

for function_name in ('transition', 'property_transition'):
    setattr(this_module, function_name, make_alias(function_name))

del this_module, make_alias, function_name
