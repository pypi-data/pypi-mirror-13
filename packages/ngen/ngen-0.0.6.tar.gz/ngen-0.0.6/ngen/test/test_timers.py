from twisted.trial.unittest import TestCase

from ngen.utils import TimerContext, timer, simple_timer, DEFAULT_PATH

import __builtin__

import mock
import time


def _error():
    raise RuntimeError('Bang!')


def error():
    with TimerContext():
        time.sleep(0.1)
        _error()


def context_success(path=None, name=None):
    with TimerContext(path=path, name=name):
        time.sleep(0.1)


class DummyClass(object):

    cls_callable = mock.MagicMock()

    def __init__(self):
        self.callable = mock.MagicMock()

    @timer()
    def method(self, *args, **kwargs):
        self.callable(*args, **kwargs)

    @timer('asdf.log')
    def custom_path(self, *args, **kwargs):
        self.callable(*args, **kwargs)

    @staticmethod
    @timer()
    def static(*args, **kwargs):
        if args:
            _callable = args[0]
            _args = args[1:]
            _callable(*_args, **kwargs)
            return _callable

    @classmethod
    @timer()
    def classy(cls, *args, **kwargs):
        cls.cls_callable(*args, **kwargs)


@simple_timer
def simple(*args, **kwargs):
    if args:
        _callable = args[0]
        _args = args[1:]
        _callable(*_args, **kwargs)
        return _callable


class TimerTests(TestCase):

    def setUp(self):
        mocked_open = mock.mock_open()
        self._file = mocked_open.return_value

        self.patcher = mock.patch.object(
            __builtin__, 'open', mocked_open
        )
        self._open = self.patcher.start()
        self.dummy = DummyClass()

    def tearDown(self):
        self.patcher.stop()

    def _test_file_actions(self, path, name):
        self.assertTrue(self._open.called)
        self._open.assert_called_once_with(path, 'a')
        self.assertEqual(len(self._file.method_calls), 1)
        call = self._file.method_calls[0]
        call_name = call[0]
        self.assertEqual(call_name, 'write')
        call_args = call[1]
        self.assertTrue(name in call_args[0])

    def test_TimerContext_reraises(self):
        self.assertRaises(RuntimeError, error)
        self._test_file_actions(DEFAULT_PATH, 'None')

    def test_TimerContext_success_with_defaults(self):
        context_success()
        self._test_file_actions(DEFAULT_PATH, 'None')

    def test_TimerContext_success_with_default_and_custom_name(self):
        context_success(name='asdf')
        self._test_file_actions(DEFAULT_PATH, 'asdf')

    def test_TimerContext_success_with_custom_path(self):
        context_success('asdf.log')
        self._test_file_actions('asdf.log', 'None')

    def test_TimerContext_success_with_custom_path_and_custom_name(self):
        context_success('asdf.log', name='asdf')
        self._test_file_actions('asdf.log', 'asdf')

    def test_timer_on_method(self):
        self.dummy.method()
        self._test_file_actions(DEFAULT_PATH, 'method')

    def test_timer_on_custom_path(self):
        self.dummy.custom_path()
        self._test_file_actions('asdf.log', 'custom_path')

    def test_timer_on_static(self):
        self.dummy.static()
        self._test_file_actions(DEFAULT_PATH, 'static')

    def test_timer_on_classy(self):
        self.dummy.classy()
        self._test_file_actions(DEFAULT_PATH, 'classy')

    def test_timer_static_arg_integrity(self):
        _mock = self.dummy.static(mock.MagicMock(), 1, 'test', x=3)
        _mock.assert_called_once_with(1, 'test', x=3)

    def test_timer_classy_arg_integrity(self):
        self.dummy.classy(1, 'test', x=3)
        self.dummy.cls_callable.assert_called_once_with(1, 'test', x=3)

    def test_timer_method_arg_integrity(self):
        self.dummy.method(1, 'test', x=3)
        self.dummy.callable.assert_called_once_with(1, 'test', x=3)

    def test_timer_error_behaviour(self):
        self.dummy.callable.side_effect = RuntimeError('haha!')
        self.assertRaises(RuntimeError, self.dummy.method, 1, 'test', x=3)
        self.dummy.callable.assert_called_once_with(1, 'test', x=3)
        self.assertFalse(self._open.called)

    def test_simple_timer(self):
        simple()
        self._test_file_actions(DEFAULT_PATH, 'simple')

    def test_simple_timer_arg_integrity(self):
        _mock = simple(mock.MagicMock(), 1, 'test', x=3)
        _mock.assert_called_once_with(1, 'test', x=3)

    def test_simple_timer_error_behaviour(self):
        __mock = mock.MagicMock()
        __mock.side_effect = RuntimeError('haha!')
        self.assertRaises(RuntimeError, simple, __mock, 1, 'test', x=3)
        __mock.assert_called_once_with(1, 'test', x=3)
        self.assertFalse(self._open.called)
