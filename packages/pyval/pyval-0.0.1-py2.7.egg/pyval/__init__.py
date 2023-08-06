import inspect
import collections
import re
from dateutil import parser


def keys(obj):
    """Provide a normalized way to iterate through the keys or indexes of an obj.

    @param obj: The object to iterate.
    @type obj:  C{list} or C{tuple} or C{dict}
    @return: a generator for the keys or indexes of the object.
    """
    if isinstance(obj, list) or isinstance(obj, tuple):
        for idx, item in enumerate(obj):
            yield idx
    elif isinstance(obj, dict):
        for key in obj:
            yield key
    else:
        raise TypeError('Object provided must be a list, tuple or dictionary.')


class ValidatedResult(object):

    def __init__(self, obj):
        self.has_completed = False
        self.messages = None
        self.obj = obj

    @property
    def is_bound(self):
        return self.obj is not None

    @property
    def is_valid(self):
        assert self.is_bound
        return self.has_completed and self.messages is None

    @property
    def is_invalid(self):
        return not self.is_valid

    def finish(self):
        """Mark to finish the validation, and clean up messages."""
        self.has_completed = True


class SchemaValidatedResult(ValidatedResult):

    def __init__(self, obj):
        """A result after a schema has validated a form.

        @type schema: L(Schema)
        """
        super(SchemaValidatedResult, self).__init__(obj)
        self.messages = {key: [] for key in self.obj.keys}

    def finish(self):
        if len(reduce(lambda x, y: x + y, self.messages.values(), [])) == 0:
            self.messages = None
        else:
            for key in self.messages.keys():
                if len(self.messages[key]) == 0:
                    del self.messages[key]
        self.has_completed = True

    def add_error_message(self, key, error_msg):
        assert key in self.obj.keys
        assert self.is_bound
        self.messages[key].append(error_msg)


class ArrayValidatedResult(ValidatedResult):

    def __init__(self, obj):
        """A result after an obj is validated.

        @type obj: L(Array)
        """
        super(ArrayValidatedResult, self).__init__(obj)
        self.current_message = None
        self.messages = []

    def finish(self):
        if len(reduce(lambda x, y: x + y, self.messages, [])) == 0:
            self.messages = None
        else:
            for idx, item in enumerate(self.messages):
                if len(item) == 0:
                    self.messages[idx] = None
        self.has_completed = True

    def next(self):
        self.current_message = []
        self.messages.append(self.current_message)

    def add_error_message(self, error_msg):
        assert self.is_bound
        self.current_message.append(error_msg)


class ValidationError(Exception):
    pass


class Validator(object):
    """Base class for validating simple forms."""
    error_msg = 'Validation error.'
    require = []
    allow_empty = True

    def __init__(self):
        self.parent = None

    def preprocess(self, value):
        """Normalize and mutate a value."""
        return value

    def validate(self, value):
        """Raise ValidationError if something is wrong."""
        pass

    @classmethod
    def get_instance(cls, obj):
        """Get an instance of validator, whether it is a class, instance or function."""
        validator_class = None
        validator = None
        if inspect.isclass(obj):
            # initiate a new one
            validator_class = obj
            validator = obj()
        elif inspect.isfunction(obj) or inspect.ismethod(obj):
            # custom validator
            validator_class = Custom
            validator = Custom(obj)
        else:
            # already an instance
            validator_class = obj.__class__
            validator = obj
        if not issubclass(validator_class, Validator):
            raise ValidationError('Validation rule must be a subclass of Validator.')
        return validator

    def run(self, form, form_key):
        if self.parent is None:
            for required_validator in self.require:
                Validator.get_instance(required_validator).run(form, form_key)
        if form_key in keys(form):
            form[form_key] = self.preprocess(form[form_key])
            if not (self.allow_empty and form[form_key] is None):
                self.validate(form[form_key])

    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)


class ChainedValidator(Validator):
    """Derive require resolve tree."""

    def __init__(self, validators):
        super(ChainedValidator, self).__init__()
        if not (isinstance(validators, list) or isinstance(validators, tuple)):
            validators = (validators, )
        self.resolve(validators)

    def resolve(self, validators):
        self.require = []
        def recursive_resolve(validator, require):
            for v in require:
                if isinstance(v, Validator) or inspect.isclass(v) and issubclass(v, Validator):
                    v.parent = validator
                    recursive_resolve(v, v.require)
                if v not in self.require:
                    self.require.append(v)
        recursive_resolve(self, validators)


class Schema(Validator):
    error_msg = 'This is not a valid dictionary.'

    def __init__(self, schema):
        super(Schema, self).__init__()
        self.schema = {key: [] for key in schema}
        for key in schema:
            self.schema[key] = ChainedValidator(schema[key])

    @property
    def keys(self):
        return self.schema.keys()

    def validate(self, value):
        if not isinstance(value, dict):
            raise ValidationError(self.error_msg)

    def run(self, form, form_key=None):
        """Preprocess the form entry in place, and return the validated result."""
        current_form = form if form_key is None else form[form_key]
        self.validate(current_form)
        validated_result = SchemaValidatedResult(self)
        for key in self.schema:
            try:
                self.schema[key].run(current_form, key)
            except ValidationError as exc:
                validated_result.add_error_message(key, exc.message)
        validated_result.finish()
        if form_key is None:
            return validated_result
        elif validated_result.is_invalid:
            raise ValidationError(validated_result.messages)


class Array(Validator):
    error_msg = 'This is not a valid list of items.'

    def __init__(self, *args, **kwargs):
        super(Array, self).__init__()
        self.inner_validator = ChainedValidator(args)
        self.min_length = kwargs.get('min_length')
        self.max_length = kwargs.get('max_length')

    def validate(self, value):
        if not (isinstance(value, list) or isinstance(value, tuple)):
            raise ValidationError(self.error_msg)
        if self.min_length is not None:
            if len(value) < self.min_length:
                raise ValidationError('You must select at least {} item(s).'.format(self.min_length))
        if self.max_length is not None:
            if len(value) > self.max_length:
                raise ValidationError('You can only select at most {} item(s).'.format(self.max_length))

    def run(self, form, form_key):
        super(Array, self).run(form, form_key)
        self.validate(form[form_key])
        validated_result = ArrayValidatedResult(self)
        for idx, item in enumerate(form[form_key]):
            validated_result.next()
            try:
                self.inner_validator.run(form[form_key], idx)
            except ValidationError as exc:
                validated_result.add_error_message(exc.message)
        validated_result.finish()
        if validated_result.is_invalid:
            raise ValidationError(validated_result.messages)


class Custom(Validator):
    """Custom validator wrapper.

    @param func: Function to validate things passing in. The function should returns
    true when the validation passes, and return the error message if it fails.
    @rtype func: func
    """

    def __init__(self, func):
        super(Custom, self).__init__()
        self.func = func

    def validate(self, value):
        result = self.func(value)
        if not (result == True):
            raise ValidationError(result)


class Required(Validator):
    error_msg = 'This is a required field.'
    allow_empty = False

    def validate(self, value):
        if (value is None or
            isinstance(value, collections.Iterable) and len(value) == 0 or
            isinstance(value, basestring) and value.strip() == ''):
            raise ValidationError(self.error_msg)

    def run(self, form, form_key):
        if form_key not in form:
            raise ValidationError(self.error_msg)
        super(Required, self).run(form, form_key)


class Number(Validator):
    error_msg = 'This is not a valid number.'

    def validate(self, value):
        if not isinstance(value, int):
            raise ValidationError(self.error_msg)

class Float(Validator):
    error_msg = 'This is not a valid float.'

    def validate(self, value):
        if not isinstance(value, float):
            raise ValidationError(self.error_msg)


class Min(Validator):
    error_msg = 'The minimum value is {}.'
    require = [Number]

    def __init__(self, min=None):
        super(Min, self).__init__()
        self.min = min

    def validate(self, value):
        if self.min is not None:
            if value < self.min:
                raise ValidationError(self.error_msg.format(self.min))


class Max(Validator):
    error_msg = 'The maximum value is {}.'
    require = [Number]

    def __init__(self, max=None):
        super(Max, self).__init__()
        self.max = max

    def validate(self, value):
        if self.max is not None:
            if value > self.max:
                raise ValidationError(self.error_msg.format(self.max))


class String(Validator):
    error_msg = 'This is not a valid string input.'

    def validate(self, value):
        if not isinstance(value, basestring):
            raise ValidationError(self.error_msg)


class LengthMin(Validator):
    error_msg = 'The minimum length is {} character long.'
    require = [String]

    def __init__(self, min_):
        super(LengthMin, self).__init__()
        self.min = min_

    def validate(self, value):
        if len(value) < self.min:
            raise ValidationError(self.error_msg.format(self.min))


class LengthMax(Validator):
    error_msg = 'The maximum length is {} character long.'
    require = [String]

    def __init__(self, max_):
        super(LengthMax, self).__init__()
        self.max = max_

    def validate(self, value):
        if len(value) > self.max:
            raise ValidationError(self.error_msg.format(self.max))


class Length(Validator):

    def __init__(self, min=None, max=None):
        super(Length, self).__init__()
        self._validators = []
        if min is not None:
            self._validators.append(LengthMin(min))
        if max is not None:
            self._validators.append(LengthMax(max))

    def run(self, form, form_key):
        super(Length, self).run(form, form_key)
        for validator in self._validators:
            validator.run(form, form_key)


class OneOf(Validator):
    error_msg = 'Value must be one within {}.'

    def __init__(self, elements):
        super(OneOf, self).__init__()
        self.elements = elements

    def validate(self, value):
        if value not in self.elements:
            raise ValidationError(self.error_msg.format(self.elements))


class Regex(Validator):
    error_msg = 'Not initialized regex error.'
    pattern = None
    require = [String]

    def __init__(self, pattern=None, error_msg=None):
        super(Regex, self).__init__()
        pattern = pattern or self.pattern
        self.error_msg = error_msg or self.error_msg
        if pattern is None:
            raise TypeError('Pattern must be provided to Regex validator.')
        self.regex = re.compile(pattern)

    def validate(self, value):
        if self.regex.match(value) is None:
            raise ValidationError(self.error_msg)


class Lower(Validator):
    require = [String]

    def preprocess(self, value):
        return value.lower()


class Upper(Validator):
    require = [String]

    def preprocess(self, value):
        return value.upper()


class Stripped(Validator):
    require = [String]

    def preprocess(self, value):
        return value.strip()


class Split(Validator):
    require = [String]

    def __init__(self, sep=' '):
        super(Split, self).__init__()
        self.sep = sep

    def preprocess(self, value):
        return value.split(self.sep)


class Email(Regex):
    error_msg = 'This is not a valid email address.'
    pattern = r'^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$'
    require = [Stripped, Lower]


class UrlFriendlyText(Regex):
    error_msg = 'This field can only contain alphabets, numbers, hyphen or dot. Spaces are not allowed.'
    require = [Stripped, Lower]
    pattern = r'^[a-z0-9\-\.]+$'


class BlankToNone(Validator):
    require = [Stripped]

    def preprocess(self, value):
        if value == "":
            return None
        return value


class UTCDateTime(Validator):
    require = [String]

    def preprocess(self, value):
        if value is None:
            return None
        try:
            return parser.parse(value)
        except (ValueError, TypeError):
            raise ValidationError('Not a valid datetime string.')

