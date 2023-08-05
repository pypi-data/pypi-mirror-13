"""Fields module."""

import datetime

import six

from . import errors


class Field(property):
    """Base field."""

    _converter = lambda _, value: value
    """Convert raw input value of the field."""

    def __init__(self, default=None):
        """Initializer."""
        super(Field, self).__init__(self.get_value, self.set_value)
        self.name = None
        self.storage_name = None

        self.model_cls = None

        self.default = default

    def bind_name(self, name):
        """Bind field to its name in model class."""
        if self.name:
            raise errors.Error('Already bound "{0}" with name "{1}" could not '
                               'be rebound'.format(self, self.name))
        self.name = name
        self.storage_name = ''.join(('_', self.name))
        return self

    def bind_model_cls(self, model_cls):
        """Bind field to model class."""
        if self.model_cls:
            raise errors.Error('"{0}" has been already bound to "{1}" and '
                               'could not be rebound to "{2}"'.format(
                                   self, self.model_cls, model_cls))
        self.model_cls = model_cls
        return self

    def init_model(self, model, value):
        """Init model with field."""
        if not value:
            value = self.default() if callable(self.default) else self.default
        setattr(model, self.storage_name, value)

    def get_value(self, model):
        """Return field's value."""
        return getattr(model, self.storage_name)

    def set_value(self, model, value):
        """Set field's value."""
        if value is not None:
            value = self._converter(value)
        setattr(model, self.storage_name, value)


class Bool(Field):
    """Bool field."""

    _converter = lambda _, value: bool(value)
    """Convert raw input value of the field."""


class Int(Field):
    """Int field."""

    _converter = lambda _, value: int(value)
    """Convert raw input value of the field."""


class Float(Field):
    """Float field."""

    _converter = lambda _, value: float(value)
    """Convert raw input value of the field."""


class String(Field):
    """String field."""

    _converter = lambda _, value: str(value)
    """Convert raw input value of the field."""


class Binary(Field):
    """Binary field."""

    _converter = lambda _, value: six.binary_type(value)
    """Convert raw input value of the field."""


class Date(Field):
    """Date field."""

    def _converter(self, value):
        """Convert raw input value of the field."""
        if not isinstance(value, datetime.date):
            raise TypeError('{0} is not valid date'.format(value))
        return value


class DateTime(Field):
    """Date and time field."""

    def _converter(self, value):
        """Convert raw input value of the field."""
        if not isinstance(value, datetime.datetime):
            raise TypeError('{0} is not valid date and time')
        return value


class Model(Field):
    """Model relation field."""

    def __init__(self, related_model_cls, default=None):
        """Initializer."""
        super(Model, self).__init__(default=default)

        self.related_model_cls = related_model_cls

    def _converter(self, value):
        """Convert raw input value of the field."""
        if not isinstance(value, self.related_model_cls):
            raise TypeError('{0} is not valid model instance, instance of '
                            '{1} required'.format(value,
                                                  self.related_model_cls))
        return value


class Collection(Field):
    """Models collection relation field."""

    def __init__(self, related_model_cls, default=None):
        """Initializer."""
        super(Collection, self).__init__(default=default)
        self.related_model_cls = related_model_cls

    def _converter(self, value):
        """Convert raw input value of the field."""
        if type(value) is not self.related_model_cls.Collection:
            value = self.related_model_cls.Collection(value)
        return value
