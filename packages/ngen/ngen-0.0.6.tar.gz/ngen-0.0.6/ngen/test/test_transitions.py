from ngen.transitions import transition_factory, TransitionError
from twisted.trial.unittest import TestCase

from mock import patch


class PreTransitionMixin(object):

    def pre_action(self, instance):
        instance.pre = True
        instance.post = False


class PostTransitionMixin(object):

    def post_action(self, instance):
        instance.pre = False
        instance.post = True


class Model(object):

    DEFAULT = 'default'
    NOPE = 'nope'
    YEP = 'yep'
    CHOICES = (DEFAULT, NOPE, YEP)

    LABEL_CHOICES = (
        (DEFAULT, 'd'),
        (NOPE, 'n'),
        (YEP, 'y')
    )

    some_field = None
    transition = transition_factory('some_field', CHOICES)
    pre_transition = transition_factory(
        'some_field', CHOICES, [PreTransitionMixin, ]
    )
    post_transition = transition_factory(
        'some_field', LABEL_CHOICES, [PostTransitionMixin, ]
    )

    def __init__(self, some_field=None):
        self.some_field = some_field or self.DEFAULT

    @transition(DEFAULT, NOPE)
    def reject(self):
        return self.some_field

    @transition(DEFAULT, YEP)
    def accept(self):
        return self.some_field

    @transition(NOPE, YEP)
    def fix(self):
        return self.some_field

    @transition('wont work', YEP)
    def broken(self):
        pass

    @pre_transition(DEFAULT, YEP)
    def pre_action(self):
        pass

    @post_transition(DEFAULT, YEP)
    def post_action(self):
        pass


class TransitionTests(TestCase):

    def setUp(self):
        self.model_instance = Model()
        self.assertEqual(self.model_instance.some_field, Model.DEFAULT)

    def test_pre_action(self):
        transition = self.model_instance.transition
        with patch.object(transition, 'pre_action') as pre_action:
            self.assertFalse(pre_action.called)
            self.model_instance.reject()
            self.assertTrue(pre_action.called)

            pre_action.assert_called_once_with(self.model_instance)

    def test_post_action(self):
        transition = self.model_instance.transition
        with patch.object(transition, 'post_action') as post_action:
            self.assertFalse(post_action.called)
            self.model_instance.reject()
            self.assertTrue(post_action.called)

            post_action.assert_called_once_with(self.model_instance)

    def test_action_reject(self):
        # reject the model and check if the instance is in the right state
        self.model_instance.reject()
        self.assertEqual(self.model_instance.some_field, Model.NOPE)

        # try to reject it again
        self.model_instance.reject()
        self.assertEqual(self.model_instance.some_field, Model.NOPE)

        self.assertRaises(TransitionError, self.model_instance.accept)

    def test_action_accept(self):
        # accept the model and check if the instance is in the right state
        self.model_instance.accept()
        self.assertEqual(self.model_instance.some_field, Model.YEP)

    def test_action_fix(self):
        # reject the instance, check it then try to fix it
        # finally check if the instance is in the right state
        self.model_instance.reject()
        self.assertEqual(self.model_instance.some_field, Model.NOPE)

        self.model_instance.fix()
        self.assertEqual(self.model_instance.some_field, Model.YEP)

    def test_action_broken(self):
        self.assertRaises(TransitionError, self.model_instance.broken)

    def test_action_pre(self):
        self.model_instance.pre_action()
        self.assertTrue(self.model_instance.pre)
        self.assertFalse(self.model_instance.post)

    def test_action_post(self):
        self.model_instance.post_action()
        self.assertTrue(self.model_instance.post)
        self.assertFalse(self.model_instance.pre)

