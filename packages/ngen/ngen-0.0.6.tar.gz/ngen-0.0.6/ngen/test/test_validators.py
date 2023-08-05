from ngen import validators
from twisted.trial.unittest import TestCase

from datetime import datetime, date


NOW = datetime.utcnow()
TODAY = date.today()


class Field(object):
    pass


class ValidatorTests(TestCase):

    def setUp(self):
        self.field = Field()
        self.field.name = 'foo'
        self.field.min_length = 3
        self.field.max_length = 5

    def _tester(self, func, success, failure):
        for value in success:
            ret = func(self.field, value)
            self.assertEqual(ret, value)

        for value in failure:
            self.assertRaises(
                validators.ValidationError, func, self.field, value
            )

    def test_is_int(self):
        self._tester(
            validators.is_int,
            (-1, 0, 1),
            (1., 'bar', [], None, {}, set(), True, (), NOW, TODAY)
        )

    def test_is_float(self):
        self._tester(
            validators.is_float,
            (0., 1.),
            (1, 'bar', [], None, {}, set(), True, (), NOW, TODAY)
        )

    def test_is_number(self):
        self._tester(
            validators.is_number,
            (-1., 0, 1),
            ('bar', [], None, {}, set(), True, (), NOW, TODAY)
        )

    def test_is_char(self):
        self._tester(
            validators.is_char,
            ('bar', ),
            (1., 1, [], None, {}, set(), True, (), NOW, TODAY)
        )

    def test_is_bool(self):
        self._tester(
            validators.is_bool,
            (True, False),
            (1., 'bar', 1, [], None, {}, set(), (), NOW, TODAY)
        )

    def test_is_set(self):
        self._tester(
            validators.is_set,
            (set(), ),
            (1., 'bar', [], None, {}, True, (), NOW, TODAY)
        )

    def test_is_dict(self):
        self._tester(
            validators.is_dict,
            ({}, ),
            (1., 'bar', [], None, set(), True, (), NOW, TODAY)
        )

    def test_is_list(self):
        self._tester(
            validators.is_list,
            ([], ()),
            (1., 'bar', set(), None, {}, True, NOW, TODAY)
        )

    def test_is_datetime(self):
        self._tester(
            validators.is_datetime,
            (NOW, ),
            (1., 'bar', set(), None, {}, True, [], (), TODAY)
        )

    def test_is_date(self):
        self._tester(
            validators.is_date,
            (TODAY, ),
            (1., 'bar', set(), None, {}, True, NOW, [], ())
        )

    def test_check_length(self):

        self.assertRaises(
            validators.ValidationError,
            validators.check_length, self.field, 'a'
        )

        self.assertRaises(
            validators.ValidationError,
            validators.check_length, self.field, 'ab'
        )

        expected = 'foo'
        ret = validators.check_length(self.field, expected)
        self.assertEqual(ret, expected)

        expected += 'b'
        ret = validators.check_length(self.field, expected)
        self.assertEqual(ret, expected)

        expected += 'a'
        ret = validators.check_length(self.field, expected)
        self.assertEqual(ret, expected)

        self.assertRaises(
            validators.ValidationError,
            validators.check_length, self.field, 'foobar'
        )
