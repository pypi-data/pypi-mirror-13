from .exceptions import TransitionError
from .signals import pre_transition_event, post_transition_event
from .utils import parse_receiver_resps
from functools import wraps

import logging
import uuid

logger = logging.getLogger(__name__)


def property_transition(state, from_state, **kwargs):
    return transition(
        state, from_state, to_state=None, is_mutable=False, **kwargs
    )


###############################################################################
#                                                                             #
# TRANSITION DECORATOR                                                        #
#                                                                             #
###############################################################################
def transition(
    state=None, from_state=None, to_state=None, is_mutable=True,
    **decorator_kwargs
):
    """
    transition is model method decorator that flattens the the logic around
    transitioning the state of model. A model attribute is given as the first
    argument and the following two args are the states to transition from and
    to respectively. This is an implementation of a Finite State Machine
    design pattern.
        state => field_name e.g. 'status'
        from_state => state_name or state_number e.g. 'new' or 0
        to_state => state_name or state_number e.g. 'read' or 1
    Usage:
    @transition('read_status', 'new', 'read')
    def read(self):
        # stuff relating to the instance being read
    """
    def decorator(func):
        "First stage of the decorator. It accepts the function to be wraped"
        _function_name = func.__name__
        @wraps(func)
        def _transition(self, *args, **kwargs):
            "wraps the function"
            current_state = getattr(self, state)

            side_effects_enabled = not kwargs.pop('transmission_disable_side_effects', False)

            if current_state == to_state and from_state != to_state:
                # do nothing if the model is already in the desired state
                # but if you want the state to remain the same then continue
                return

            if is_mutable:
                choices = self._meta.get_field(state).choices
                if choices:
                    states = [status for status, _ in choices]
                    if to_state not in states:
                        raise TransitionError(
                            'Cannot transition to a state that is not '
                            'included in the "%s" choices.' % state
                        )
            is_iter = isinstance(from_state, (list, tuple))
            states_align = current_state == from_state
            if (is_iter and current_state in from_state) or states_align:

                thisuuid = str(uuid.uuid4())

                # PRE TRANSITION EVENT
                if side_effects_enabled:
                    receiver_resps = pre_transition_event.send_robust(
                        sender=self.__class__, instance=self, state=state,
                        from_state=current_state, to_state=to_state,
                        transition_name=func.__name__,
                        uuid=thisuuid, **decorator_kwargs
                    )
                    parse_receiver_resps(receiver_resps, log=logger)

                try:
                    # TRANSITION: Run the transition method
                    ret = func(self, *args, **kwargs)
                except:
                    raise
                if side_effects_enabled:
                    if is_mutable:
                        setattr(self, state, to_state)
                    self.save()

                if side_effects_enabled:
                # POST TRANSITION EVENT
                    receiver_resps = post_transition_event.send_robust(
                        sender=self.__class__, instance=self, state=state,
                        from_state=current_state, to_state=to_state,
                        transition_name=func.__name__,
                        uuid=thisuuid, **decorator_kwargs
                    )
                    parse_receiver_resps(receiver_resps, log=logger)

            else:
                raise TransitionError(
                    'Cannot transition from "{current_state!r}"" to '
                    '"{final_state!r}"'.format(
                        current_state=current_state,
                        final_state=to_state or _function_name
                    )
                )
            return ret
        return _transition
    return decorator
