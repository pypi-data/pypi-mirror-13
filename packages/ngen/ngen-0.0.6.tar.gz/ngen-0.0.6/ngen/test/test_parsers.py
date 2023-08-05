from mock import patch, MagicMock
from ngen.parsers import (
    Parser, Field, ParserError, FieldError, ImproperlyConfigured,
    ValidationError, IntField, CharField
)

from twisted.trial.unittest import TestCase

import copy


class MyParser(Parser):

    first = Field('rando_name')
    second = Field('nested.info')
    third = Field('nested__delim', delimiter='__')
    fourth = Field('missing', default=[])
    fifth = Field('nodefault')


class MyChildParser(MyParser):

    sixth = Field('nested.three.deep')


TEST_OBJECT = {
    'rando_name': 1,
    'nested': {
        'info': 2,
        'delim': 3,
        'three': {
            'deep': 6
        }
    },
    'text': 'foo'
}


class ParserTests(TestCase):

    def setUp(self):
        self.test_obj = copy.deepcopy(TEST_OBJECT)

    def test_parser_can_map(self):

        obj = self.test_obj
        parser = MyParser()
        parsed_obj = parser(obj)
        self.assertIsInstance(parsed_obj, dict)
        self.assertItemsEqual(
            parsed_obj, ['first', 'second', 'third', 'fourth', 'fifth']
        )
        self.assertEqual(parsed_obj['first'], 1)
        self.assertEqual(parsed_obj['second'], 2)
        self.assertEqual(parsed_obj['third'], 3)

        self.assertEqual(parsed_obj['fourth'], [])
        self.assertEqual(parsed_obj['fifth'], None)

        child_parser = MyChildParser()

        child_parsed_obj = child_parser(obj)
        self.assertItemsEqual(
            child_parsed_obj,
            ['first', 'second', 'third', 'fourth', 'fifth', 'sixth']
        )
        self.assertEqual(child_parsed_obj['sixth'], 6)

    def test_parser_assign_attrs(self):
        parser = MyParser()

        cls_attrs = {
            name: value
            for name, value in parser.__class__.__dict__.items()
            if not name.startswith('_')
        }
        self.assertEqual(cls_attrs, {})

        class AttrParser(MyParser):
            test1 = 10
            test2 = 'asdf'

        attr_parser = AttrParser()
        cls_attrs = {
            name: value
            for name, value in attr_parser.__class__.__dict__.items()
            if not name.startswith('_')
        }
        self.assertEqual(cls_attrs, {'test1': 10, 'test2': 'asdf'})

    def test_parser_module_info(self):
        self.assertEqual(Parser.__dict__['__module__'], 'ngen.parsers')

    def test_parser_access_on_value(self):
        obj = {'value': 1}

        class UselessParser(Parser):
            broken = Field('value.nope')

        parser = UselessParser()

        with self.assertRaises(ParserError) as ctxt_manager:
            parser(obj)

        exception = ctxt_manager.exception

        msg = (
            'The field "broken" expected a dict at the reference "nope", '
            'instead got a value of <type \'int\'>.\n'
            'This indicates that the reference "value.nope" is incorrect.'
        )
        self.assertEqual(dict(exception.message), {'broken': msg})

        # tests the reraise functionality
        parser = UselessParser(reraise=False)
        ret = parser(obj)
        self.assertEqual(ret, {})

        class SlightlyUselessParser(UselessParser):
            diff_name = Field('value')

        parser = SlightlyUselessParser(reraise=False)
        ret = parser(obj)
        self.assertEqual(ret, {'diff_name': 1})

    def test_field_raises_fielderror(self):
        field = Field('ha.nope')
        field.name = 'nope'

        obj = {'ha': 1}

        self.assertRaises(FieldError, field.get_value, obj)
        self.assertRaises(ParserError, field.get_value, obj)
        self.assertRaises(TypeError, field.get_value, obj)

    def test_field_run_validators(self):
        field = Field('easy')
        obj = {'easy': 'test'}

        with patch.object(field, 'run_validators') as mock:
            field.get_value(obj)
            mock.assert_called_once_with(obj['easy'])

    def test_parser_hits_clean(self):

        def mocked_clean(obj):
            return obj

        value = 2
        data = {'asdf': {'lkj': value}}

        class McParser(Parser):
            multiplier = 1000
            haha = Field('asdf.lkj')

            def clean_haha(self, value):
                return value * self.multiplier

        parser = McParser()

        with patch.object(parser, 'clean', side_effect=mocked_clean) as mclean:
            parser(data)
            # the value of 2000 also indicates that the method clean_haha was
            # executed
            mclean.assert_called_once_with(
                {'haha': value * McParser.multiplier}
            )

    def test_reraise_not_bool(self):
        self.assertRaisesRegexp(
            TypeError, 'reraise must be a boolean.',
            MyParser, reraise='asdf'
        )

    def test_raise_on_bad_ref(self):
        self.assertRaisesRegexp(
            ImproperlyConfigured, (
                'The first arg to a field must either be a string or a '
                'subclass of Parser.'
            ), Field, 1
        )

    def test_raise_on_bad_delim(self):
        field = Field('test', delimiter=1)
        field.name = 'hello'
        self.assertRaisesRegexp(
            ImproperlyConfigured, (
                'Field attribute hello.delimiter expected a character '
                'buffer object'
            ), field.get_value, {}
        )

    def test_parser_in_field_ref(self):

        class NestedParser(Parser):
            nested = Field('rando_name')

        class MainParser(Parser):

            first = Field('nested.info')
            second = Field(NestedParser)

        parser = MainParser()

        data = parser(self.test_obj)
        self.assertItemsEqual(data, ['first', 'second'])
        self.assertIsInstance(data['second'], dict)
        self.assertEqual(
            data['second']['nested'],
            self.test_obj['rando_name']
        )

    def test_int_field(self):
        field = IntField('rando_name')
        ret = field.get_value(self.test_obj)
        self.assertEqual(ret, self.test_obj['rando_name'])

        field = IntField('text')
        self.assertRaises(ValidationError, field.get_value, self.test_obj)

    def test_char_field(self):
        field = CharField('text')
        ret = field.get_value(self.test_obj)
        self.assertEqual(ret, self.test_obj['text'])

        field = CharField('rando_name')
        self.assertRaises(ValidationError, field.get_value, self.test_obj)
