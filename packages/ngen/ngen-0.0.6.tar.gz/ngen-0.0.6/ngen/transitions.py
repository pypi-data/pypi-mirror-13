from functools import wraps
from .utils import cached_property
from exceptions import Error


class TransitionError(Error):
    pass


class TransitionBase(object):

    field_name = None
    choices = None

    def __init__(self, from_state, to_state):
        self.from_state = from_state
        self.to_state = to_state

    def __call__(self, func):
        @wraps(func)
        def wrapper(instance, *args, **kwargs):
            current_state = getattr(instance, self.field_name)
            if current_state == self.to_state:
                # do nothing if the model is already in the desired state
                return

            self.check_to_state()
            self.check_from_state(current_state)

            self.pre_action(instance)

            ret = func(instance, *args, **kwargs)

            self.post_action(instance)

            self.run_transition(instance)

            self.post_transition(instance)

            return ret
        return wrapper

    def run_transition(self, instance):
        setattr(instance, self.field_name, self.to_state)

    def post_transition(self, instance):
        pass

    @cached_property
    def allowed_states(self):
        allowed_types = (str, unicode, int)
        ret = []
        for choice in self.choices:
            if isinstance(choice, (list, tuple)):
                choice = choice[0]

            if isinstance(choice, allowed_types):
                ret.append(choice)
            else:
                raise TypeError(
                    'State choices must be one of the following types: '
                    '{}'.format(allowed_types)
                )
        return ret

    def check_to_state(self):

        if self.to_state not in self.allowed_states:
            raise TransitionError(
                'Cannot transition to a state that is not '
                'included in the "%s" choices.' % self.allowed_states
            )

    def check_from_state(self, current_state):
        multi = isinstance(self.from_state, (list, tuple))

        # check if the from_states are valid i.e. in the list of choices
        if multi:
            leftovers = set(self.from_state) - set(self.allowed_states)
            if leftovers:
                raise TransitionError(
                    'Invalid from_states: {}'.format(list(leftovers))
                )
            if current_state not in self.from_state:
                raise TransitionError(
                    'Instance is not in a permitted initial state.'
                )
        else:
            if self.from_state not in self.allowed_states:
                raise TransitionError(
                    'Invalid from_states: {}'.format(self.from_state)
                )

            if current_state != self.from_state:
                raise TransitionError(
                    'Instance is not in the permitted initial state.'
                )

    def pre_action(self, instance):
        pass

    def post_action(self, instance):
        pass


def transition_factory(field_name, choices, subclasses=None):
    subclasses = subclasses or []
    bases = list(subclasses) + [TransitionBase, ]
    cls = type(
        'Transition', tuple(bases),
        {'field_name': field_name, 'choices': choices}
    )
    return cls
