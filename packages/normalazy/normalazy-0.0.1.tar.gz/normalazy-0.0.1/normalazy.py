import datetime
from decimal import Decimal
from functools import wraps


#: Defines the version of the `normalazy` library.
__version__ = "0.0.1"


def iffnotnull(func):
    """
    Wraps a function, returns None if the first argument is None, invokes the method otherwise.

    :param func: The function to be wrapped.
    :return: None or the result of the function.

    >>> test1 = iffnotnull(lambda x: x)
    >>> test1(None)
    >>> test1(1)
    1
    """
    @wraps(func)
    def wrapper(value, *args, **kwargs):
        return None if value is None else func(value, *args, **kwargs)
    return wrapper


def identity(x):
    """
    Defines an identity function.

    :param x: value
    :return: value

    >>> identity(None)
    >>> identity(1)
    1
    """
    return x


@iffnotnull
def as_string(x):
    """
    Converts the value to a trimmed string.

    :param x: Value.
    :return: Trimmed string value.

    >>> as_string(None)
    >>> as_string("")
    ''
    >>> as_string("a")
    'a'
    >>> as_string(" a ")
    'a'
    """
    return str(x).strip()


@iffnotnull
def as_factor(x):
    """
    Converts the value to a factor string.

    :param x: Value.
    :return: Trimmer, up-cased string value.

    >>> as_factor(None)
    >>> as_factor("")
    ''
    >>> as_factor("a")
    'A'
    >>> as_factor(" a ")
    'A'
    """
    return as_string(x).upper()


@iffnotnull
def as_number(x):
    """
    Converts the value to a decimal value.

    :param x: The value to be converted to a decimal value.
    :return: A Decimal instance.

    >>> as_number(None)
    >>> as_number(1)
    Decimal('1')
    >>> as_number("1")
    Decimal('1')
    >>> as_number(" 1 ")
    Decimal('1')
    >>> as_number(" a ")
    Traceback (most recent call last):
    ...
    decimal.InvalidOperation: [<class 'decimal.ConversionSyntax'>]
    """
    return Decimal(as_string(x))


@iffnotnull
def as_boolean(x, predicate=None):
    """
    Converts the value to a boolean value.

    :param x: The value to be converted to a boolean value.
    :param predicate: The predicate function if required.
    :return: Boolean

    >>> as_boolean(None)
    >>> as_boolean(1)
    True
    >>> as_boolean(0)
    False
    >>> as_boolean("1")
    True
    >>> as_boolean("0")
    True
    >>> as_boolean("1", predicate=lambda x: int(x) != 0)
    True
    >>> as_boolean("0", predicate=lambda x: int(x) != 0)
    False
    >>> as_boolean("1", predicate=int)
    True
    >>> as_boolean("0", predicate=int)
    False
    >>> as_boolean("1", int)
    True
    >>> as_boolean("0", int)
    False
    """
    return bool(x if predicate is None else predicate(x))


@iffnotnull
def as_datetime(x, fmt=None):
    """
    Converts the value to a datetime value.

    :param x: The value to be converted to a datetime value.
    :param fmt: The format of the date/time string.
    :return: A datetime.date instance.

    >>> as_datetime(None)
    >>> as_datetime("2015-01-01 00:00:00")
    datetime.datetime(2015, 1, 1, 0, 0)
    >>> as_datetime("2015-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S")
    datetime.datetime(2015, 1, 1, 0, 0)
    >>> as_datetime("2015-01-01T00:00:00", fmt="%Y-%m-%dT%H:%M:%S")
    datetime.datetime(2015, 1, 1, 0, 0)
    """
    return datetime.datetime.strptime(x, fmt or "%Y-%m-%d %H:%M:%S")


@iffnotnull
def as_date(x, fmt=None):
    """
    Converts the value to a date value.

    :param x: The value to be converted to a date value.
    :param fmt: The format of the date string.
    :return: A datetime.date instance.

    >>> as_date(None)
    >>> as_date("2015-01-01")
    datetime.date(2015, 1, 1)
    >>> as_date("Date: 2015-01-01", "Date: %Y-%m-%d")
    datetime.date(2015, 1, 1)
    >>> as_date("Date: 2015-01-01", fmt="Date: %Y-%m-%d")
    datetime.date(2015, 1, 1)
    """
    return datetime.datetime.strptime(x, fmt or "%Y-%m-%d").date()


class Value:
    """
    Defines an immutable *[sic.]* boxed value with message, status and extra data as payload if required.

    >>> value = Value(value=42, message=None, status=Value.Status.Success, extras="41 + 1")
    >>> value.value
    42
    >>> value.message
    >>> value.status == Value.Status.Success
    True
    >>> value.extras
    '41 + 1'
    >>> value = Value.success(42, date="2015-01-01")
    >>> value.value
    42
    >>> value.status == Value.Status.Success
    True
    >>> value.date
    '2015-01-01'
    >>> value = Value.warning(value="fortytwo", message="Failed to convert to integer.", date="2015-01-01")
    >>> value.value
    'fortytwo'
    >>> value.status == Value.Status.Warning
    True
    >>> value.date
    '2015-01-01'
    >>> value.message
    'Failed to convert to integer.'
    >>> value = Value.error(message="Failed to compute the value.", date="2015-01-01")
    >>> value.value
    >>> value.status == Value.Status.Error
    True
    >>> value.date
    '2015-01-01'
    >>> value.message
    'Failed to compute the value.'
    """

    class Status:
        """
        Defines an enumeration for value status.
        """

        #: Indicates that value is mapped successfully.
        Success = 1

        #: Indicates that value is mapped successfully with warnings.
        Warning = 2

        #: Indicates that value could not be mapped successfully.
        Error = 3

    def __init__(self, value=None, message=None, status=None, **kwargs):
        """
        Constructs an immutable Value class instance.

        Note that the classmethods `success`, `warning` and `error` should be preferred over this
        constructor.

        :param value: The atomic value.
        :param message: Any messages if required.
        :param status: The value status.
        :param kwargs: Extra payload for the value.
        """
        self.__value = value
        self.__status = status or self.Status.Success
        self.__message = message
        self.__payload = kwargs

    @property
    def value(self):
        return self.__value

    @property
    def status(self):
        return self.__status

    @property
    def message(self):
        return self.__message

    @property
    def payload(self):
        return self.__payload

    def __getattr__(self, item):
        """
        Provides access to payload through attributes.

        :param item: The name of the attribute.
        :return: The value for the attribute if the attribute name is in payload.
        """
        ## Check if the item is in the payload:
        if item in self.payload:
            ## Yes, return it.
            return self.payload.get(item)

        ## Nope, escalate:
        return super().__getattr__(item)

    @classmethod
    def success(cls, value=None, message=None, **kwargs):
        """
        Provides a convenience constructor for successful Value instances.

        :param value: The value of the Value instance to be constructed.
        :param message: The message, if any.
        :param kwargs: Extra payload for the value.
        :return: A successful Value instance.
        """
        return cls(value=value, message=message, status=cls.Status.Success, **kwargs)

    @classmethod
    def warning(cls, value=None, message=None, **kwargs):
        """
        Provides a convenience constructor for Values instances with warnings.

        :param value: The value of the Value instance to be constructed.
        :param message: The message, if any.
        :param kwargs: Extra payload for the value.
        :return: A Value instance with warnings.
        """
        return cls(value=value, message=message, status=cls.Status.Warning, **kwargs)

    @classmethod
    def error(cls, value=None, message=None, **kwargs):
        """
        Provides a convenience constructor for Values instances with errors.

        :param value: The value of the Value instance to be constructed.
        :param message: The message, if any.
        :param kwargs: Extra payload for the value.
        :return: A Value instance with errors.
        """
        return cls(value=value, message=message, status=cls.Status.Error, **kwargs)


class Field:
    """
    Provides a concrete mapper field.

    >>> field = Field()
    >>> field.map(None, dict()).value
    >>> field.map(None, dict()).status == Value.Status.Success
    True
    >>> field = Field(null=False)
    >>> field.map(None, dict()).value
    >>> field.map(None, dict()).status == Value.Status.Error
    True
    >>> field = Field(func=lambda i, r: r.get("a", None))
    >>> field.map(None, dict(a="")).value
    ''
    >>> field.map(None, dict(a="")).status == Value.Status.Success
    True
    >>> field = Field(func=lambda i, r: r.get("a", None), blank=False)
    >>> field.map(None, dict(a="")).value
    ''
    >>> field.map(None, dict(a="")).status == Value.Status.Error
    True
    >>> field = Field(func=lambda i, r: r.get("a", None))
    >>> field.map(None, dict()).value
    >>> field.map(None, dict(a=1)).value
    1
    >>> field.map(None, dict(a=1)).status == Value.Status.Success
    True
    """

    def __init__(self, name=None, func=None, blank=True, null=True):
        """
        Constructs a mapper field with the given argument.

        :param name: The name of the field.
        :param func: The function which is to be used to map the value.
        :param blank: Boolean indicating if blank values are allowed.
        :param null: Boolean indicating if null values are allowed.
        """
        self.__name = name
        self.__func = func
        self.__blank = blank
        self.__null = null

    @property
    def name(self):
        """
        Returns the name of the field.

        :return: The name of the field.
        """
        return self.__name

    @property
    def func(self):
        """
        Returns the mapping function of the field.

        :return: The mapping function of the field.
        """
        return self.__func

    @property
    def blank(self):
        """
        Indicates if the value is allowed to be blank.

        :return: Boolean indicating if the value is allowed to be blank.
        """
        return self.__blank

    @property
    def null(self):
        """
        Indicates if the value is allowed to be null.

        :return: Boolean indicating if the value is allowed to be null.
        """
        return self.__null

    def rename(self, name):
        """
        Renames the field.

        :param name: The new name of the field.
        """
        self.__name = name

    def treat_value(self, value):
        """
        Treats the value and return.

        :param value: The value to be treated.
        :return: A Value instance.
        """
        ## By now we have a value. If it is an instance of Value
        ## class, return it as is:
        if isinstance(value, Value):
            return value

        ## If the value is string and empty, but is not allowed to be so, return
        ## with error:
        if not self.blank and isinstance(value, str) and value == "":
            return Value.error(value="", message="Value is not allowed to be blank.")

        ## If the value is None but is not allowed to be so, return
        ## with error:
        if not self.null and value is None:
            return Value.error(message="Value is not allowed to be None.")

        ## OK, we have a value to be boxed and returned successfully:
        return Value.success(value=value)

    def map(self, instance, record):
        """
        Returns the value of for field as a Value instance.

        :param instance: The instance for which the value will be retrieved.
        :param record: The raw record.
        :return: A Value instance.
        """
        ## Check if we have a function:
        if self.func is None:
            ## OK, value shall be None:
            value = None
        ## Check if the function is a callable or the name of an attribute of the instance:
        elif hasattr(self.func, "__call__"):
            ## The function is a callable. Call it directly on the
            ## instance and the record and get the raw value:
            value = self.func(instance, record)
        else:
            ## The function is not a callable. We assume that it is
            ## the name of a method of the instance. Apply the
            ## instance method on the record and get the raw value:
            value = getattr(instance, self.func)(record)

        ## Treat the value and return:
        return self.treat_value(value)


class KeyField(Field):
    """
    Provides a mapper field for a given key which belongs to the
    record. The record can be an object which has `__getitem__` method
    or a simple object just with attribute access.

    The method starts reading the source value using the key provided
    checking `__getitem__` method (for iterables such as `dict` or
    `list`), then checks the attribute for simple object attribute
    access.

    >>> field = KeyField(key="a")
    >>> field.map(None, dict(a="")).value
    ''
    >>> field.map(None, dict(a="")).status == Value.Status.Success
    True
    >>> field = KeyField(key="a", blank=False)
    >>> field.map(None, dict(a="")).value
    ''
    >>> field.map(None, dict(a="")).status == Value.Status.Error
    True
    >>> field = KeyField(key="a", func=lambda i, r, v: as_number(v))
    >>> field.map(None, dict(a="12")).value
    Decimal('12')
    >>> field.map(None, dict(a="12")).status == Value.Status.Success
    True
    """

    def __init__(self, key=None, **kwargs):
        """
        Constructs a mapper field with the given argument.

        :param key: The key of the property of the record to be mapped.
        :param **kwargs: Keyword arguments to `Field`.
        """
        super().__init__(**kwargs)
        self.__key = key

    @property
    def key(self):
        """
        Returns the key of for the field mapping.
        """
        return self.__key

    def rename(self, name):
        """
        Renames the field.

        :param name: The new name of the field.
        """
        ## Call the super:
        super().rename(name)

        ## If the key is None, set it with joy:
        if self.__key is None:
            self.__key = name

    def map(self, instance, record):
        """
        Returns the value of for field as a Value instance.

        :param instance: The instance for which the value will be retrieved.
        :param record: The raw record.
        :return: A Value instance.
        """
        ## Does the record have __getitem__ method (Indexable) and key exist?
        if hasattr(record, "__getitem__") and self.key in record:
            ## Yes, get the value:
            value = record.get(self.key)
        ## Nope, let's check if the record has such an attribute:
        elif hasattr(record, self.key):
            ## Yes, get the value using attribute access:
            value = getattr(record, self.key)
        ## We can't access such a value in the record.
        else:
            ## OK, Value shall be None:
            value = None

        ## Do we have a function:
        if self.func is None:
            ## Nope, skip:
            pass
        ## Check if the function is a callable or the name of an attribute of the instance:
        elif hasattr(self.func, "__call__"):
            ## The function is a callable. Call it directly on the
            ## instance, the record and the raw value:
            value = self.func(instance, record, value)
        else:
            ## The function is not a callable. We assume that it is
            ## the name of a method of the instance. Apply the
            ## instance method on the record and the raw value:
            value = getattr(instance, self.func)(record, value)

        ## Done, treat the value and return:
        return self.treat_value(value)


class ChoiceKeyField(KeyField):
    """
    Defines a choice mapper for the index of the record provided.

    >>> field = ChoiceKeyField(key="a", choices=dict(a=1, b=2))
    >>> field.map(None, dict(a="a")).value
    1
    >>> field = ChoiceKeyField(key="a", choices=dict(a=1, b=2), func=lambda i, r, v: Decimal(str(v)))
    >>> field.map(None, dict(a="a")).value
    Decimal('1')
    """

    def __init__(self, *args, choices=None, **kwargs):
        ## Choices?
        choices = choices or {}

        ## Get the function:
        functmp = kwargs.pop("func", None)

        ## Compute the func
        if functmp is not None:
            func = lambda i, r, v: functmp(i, r, choices.get(v, None))
        else:
            func = lambda i, r, v: choices.get(v, None)

        ## Add the func back:
        kwargs["func"] = func

        ## OK, proceed as usual:
        super().__init__(*args, **kwargs)


class RecordMetaclass(type):
    """
    Provides a record metaclass.
    """

    def __new__(mcs, name, bases, attrs, **kwargs):
        ## Pop all fields:
        fields = dict([(key, attrs.pop(key)) for key in list(attrs.keys()) if isinstance(attrs.get(key), Field)])

        ## Check fields and make sure that names are added:
        for name, field in fields.items():
            if field.name is None:
                field.rename(name)

        ## Get the record class as usual:
        record_cls = super().__new__(mcs, name, bases, attrs, **kwargs)

        ## Now, process the fields:
        record_cls._fields.update(fields)

        ## Done, return the record class:
        return record_cls


class Record(metaclass=RecordMetaclass):
    """
    Provides a record normalizer base class.

    >>> class Test1Record(Record):
    ...     a = KeyField()
    >>> record1 = Test1Record(dict(a=1))
    >>> record1.a
    1
    >>> class Test2Record(Record):
    ...     a = KeyField()
    ...     b = ChoiceKeyField(choices={1: "Bir", 2: "Iki"})
    >>> record2 = Test2Record(dict(a=1, b=2))
    >>> record2.a
    1
    >>> record2.b
    'Iki'
    """
    #: Defines the fields of the record normalizer.
    _fields = {}

    def __init__(self, record):
        ## Save the record slot:
        self.__record = record

        ## Declare the values map:
        self._values = {}

    def __getattr__(self, item):
        """
        Returns the value of the attribute named `item`, particularly from within the fields set or pre-calculated
        field values set.

        :param item: The name of the attribute, in particular the field name.
        :return: The value (value attribute of the Value).
        """
        ## Do we have such a value yet?
        if item in self._values:
            ## Yes, return the value slot of the value:
            return self._values.get(item).value

        ## Do we have such a field?
        if item not in self._fields:
            ## Nope. raise error:
            raise AttributeError("Item {} is not in fields".format(item))

        ## Compute the value:
        self._values[item] = self._fields.get(item).map(self, self.__record)

        ## Done, return the value slot of the Value instance:
        return self._values[item].value
