from . import Test
from . import validate
from pandora.compat import string_types
from pandora.compat import text_type
from . import test_and_return
import bleach

BOOL_FIELD_TRUE_VALUES = ['t', '1', 1, True, 'true', 'yes', 'True']
BOOL_FIELD_FALSE_VALUES = ['f', '-1', '0', -1, 0, False, 'false', 'no',
                           'False']
BOOL_FIELD_NONE_VALUES = ['null', 'none', None, 'None', 'undefined',
                          'Undefined']


def string_field(min_len=1, max_len=150,
                 min_error='Too short.', max_error='Too long.',
                 strip_html=True):
    commands = list()
    commands.append(lambda v: text_type(v))

    if min_len is not None:
        commands.append(validate(lambda v: len(v) >= min_len, min_error))
    if max_len is not None:
        commands.append(validate(lambda v: len(v) <= max_len, max_error))

    if strip_html:
        commands.append(lambda v: bleach.clean(v, tags=list(), strip=True))

    return Test(commands)


def int_field(min_value=None, max_value=None,
              min_error='Too low.', max_error='Too high.'):
    commands = list()
    commands.append(lambda v: int(v))

    if min_value is not None:
        commands.append(validate(lambda v: v >= min_value, min_error))
    if max_value is not None:
        commands.append(validate(lambda v: v <= max_value, max_error))

    return Test(commands)


def float_field(min_value=None, max_value=None,
                min_error='Too low.', max_error='Too high.'):
    commands = list()
    commands.append(lambda v: float(v))

    if min_value is not None:
        commands.append(validate(lambda v: v >= min_value, min_error))
    if max_value is not None:
        commands.append(validate(lambda v: v <= max_value, max_error))

    return Test(commands)


def boolean_field(false_values=None, true_values=None, true_unless_false=True,
                  none_values=None, error='Not a boolean value.'):
    if false_values is None:
        false_values = BOOL_FIELD_FALSE_VALUES
    if true_values is None:
        true_values = BOOL_FIELD_TRUE_VALUES

    commands = list()

    if none_values is not None:
        commands.append(test_and_return(lambda v: v in none_values, None))

    if true_values is None and true_unless_false:
        commands.append(lambda v: v not in false_values)
    else:
        commands.append(test_and_return(lambda v: v in false_values, False))
        commands.append(test_and_return(lambda v: v in true_values, True))

    return Test(commands, mode=Test.OR, error_or=error)


def list_field(sanitize=None, split_character=','):
    test = Test([
        Test([
            validate(lambda v: isinstance(v, string_types)),
            validate(lambda v: len(v) > 0),
            lambda v: v.split(split_character),
        ]),
        Test([
            validate(lambda v: isinstance(v, (list, set,))),
        ]),
    ], mode=Test.OR)

    if sanitize:
        return Test([
            test,
            lambda v: [sanitize(x) for x in v],
        ])

    return test


def enum_field(allowed_values, sanitize=None):
    if sanitize is None:
        sanitize = string_field()

    return Test([
        sanitize,
        validate(lambda v: v in allowed_values),
    ])


def set_field(allowed_values, sanitize=None, split_character=','):
    return Test([
        list_field(sanitize, split_character),
        validate(lambda v: [x in allowed_values for x in v]),
    ])


def list_of(test, sanitize=None, split_character=','):
    return Test([
        list_field(sanitize, split_character),
        lambda v: [test(x) for x in v],
    ])
