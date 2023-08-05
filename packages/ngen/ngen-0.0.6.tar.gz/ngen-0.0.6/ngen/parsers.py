from .exceptions import (
    ParserError, FieldError, ValidationError, ImproperlyConfigured
)
from .utils import cached_property
from .validators import is_int, is_char

import inspect
import six


class Field(object):
    """
        A parser field is the mechanism by which data is accessed from the
        original object, whereas the Parser class is the
        container and logical interface that utilizes these fields.
    """

    name = None
    base_validators = None

    def __init__(self, ref, delimiter='.', default=None, _validators=None):
        if inspect.isclass(ref) and issubclass(ref, Parser):
            self.is_parser = True
            self.ref = ref()
        elif isinstance(ref, six.string_types):
            self.is_parser = False
            self.ref = ref
        else:
            raise ImproperlyConfigured(
                'The first arg to a field must either be a string or a '
                'subclass of Parser.'
            )

        self.delimiter = delimiter
        self.default = default
        self.validators = _validators or []

    @cached_property
    def path(self):
        try:
            return self.ref.split(self.delimiter)
        except TypeError as exception:
            raise ImproperlyConfigured(
                'Field attribute {}.delimiter '.format(
                    self.name
                ) + str(exception)
            )

    def get_value(self, obj):
        """
            parses the object as specified but the string reference or the
            Parser subclass.
        """
        # if the reference is a parser then execute it and return the result
        if self.is_parser:
            return self.ref(obj)

        # else try to access the data from he object using the dot string path
        try:
            for name in self.path:
                obj = obj.get(name, {})
        except AttributeError:
            raise FieldError(
                'The field "{}" expected a dict at the reference "{}", '
                'instead got a value of {}.\n'
                'This indicates that the reference "{}" is incorrect.'. format(
                    self.name, name, type(obj), self.ref
                )
            )

        obj = self.run_validators(obj)

        if obj == {} and self.default is not None:
            obj = self.default
        elif obj == {}:
            obj = None

        return obj

    def run_validators(self, value):
        for validator in self.all_validators:
            value = validator(self, value)
        return value

    @cached_property
    def all_validators(self):
        _validators = self.base_validators or []
        _validators = list(_validators)
        _validators += list(self.validators)
        return _validators


class IntField(Field):
    base_validators = (is_int, )


class CharField(Field):
    base_validators = (is_char, )


class ParserBase(type):

    def __new__(mcs, classname, bases, attrs):

        super_new = super(ParserBase, mcs).__new__
        parents = [base for base in bases if isinstance(base, ParserBase)]
        if not parents:
            return super_new(mcs, classname, bases, attrs)

        new_cls = super_new(
            mcs, classname, bases, {'__module__': attrs['__module__']}
        )
        new_cls._parser_fields = []
        for parent in parents:
            new_cls._parser_fields += getattr(parent, '_parser_fields', [])

        for name, value in attrs.items():
            if isinstance(value, Field):
                value.name = name
                new_cls._parser_fields.append(value)
            else:
                setattr(new_cls, name, value)
        return new_cls


class Parser(six.with_metaclass(ParserBase)):
    """
        Parser is a utility class that facilitates the acquistion of data from
        a nested dicts into a flattened key-value dictionary.
        Usage:
        from ngen.utils import Parser, Field

        class YoutubeDataParser(Parser):
            title = Field('snippet.title')

        mapper = YoutubeDataParser()

        # obj = youtube response item
        data = mapper(obj)
        print data
            => {'title': 'Some Title'}
    """

    def __init__(self, reraise=True):
        if not isinstance(reraise, bool):
            raise TypeError('reraise must be a boolean.')
        self.reraise = reraise

    def __call__(self, obj):
        ret = {}
        errors = {}
        for field in self.get_fields():
            fieldname = field.name

            try:
                value = field.get_value(obj)
            except (FieldError, ValidationError) as exception:
                errors[fieldname] = str(exception)
                continue

            # get the clean method for a particular field, then clean the value
            # if a cleaner was found
            cleaner = getattr(self, 'clean_{}'.format(fieldname), None)
            if cleaner is not None and callable(cleaner):
                value = cleaner(value)

            # store the cleaned value
            ret[fieldname] = value

        # clean the entire object
        ret = self.clean(ret)

        if errors and self.reraise:
            raise ParserError(errors)
        return ret

    def get_fields(self):
        return getattr(self.__class__, '_parser_fields')

    def clean(self, obj):
        """
            An interface to be overidden by the user.
        """
        return obj
