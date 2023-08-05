from django.dispatch import Signal


pre_transition_event = Signal(
    providing_args=[
        "instance", "state", "from_state", "to_state", "transition_name"
    ]
)

post_transition_event = Signal(
    providing_args=[
        "instance", "state", "from_state", "to_state", "transition_name"
    ]
)

pre_event_signal = Signal(
    providing_args=[
        "instance", "event_name", "arg_data", "kwarg_data"
    ]
)

post_event_signal = Signal(
    providing_args=[
        "instance", "event_name", "event_output", "arg_data", "kwarg_data"
    ]
)
