# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from disinfect import tests as t
from pytest import raises


class TestTests(object):
    def test_string(self):
        test = t.String()
        assert test('Nils') == 'Nils'
        assert test(u'Níls') == u'Níls'
        assert test('<script>test') == 'test'

        test = t.String(min_len=None, max_len=None, strip_html=False)
        assert test('') == ''
        assert test('<script>test') == '<script>test'

    def test_int(self):
        test = t.Int(1, 40)
        assert test('4') == 4

        with raises(ValueError) as exc:
            test('abc')
        assert str(exc.value) == 'Not an integer.'

        with raises(ValueError) as exc:
            test('99')
        assert str(exc.value) == 'Too high.'

        with raises(ValueError) as exc:
            test('-4')
        assert str(exc.value) == 'Too low.'

    def test_float(self):
        test = t.Float(1, 40)
        assert test('4') == 4.0

        with raises(ValueError) as exc:
            test('abc')
        assert str(exc.value) == 'Not a float.'

        with raises(ValueError) as exc:
            test('99.0')
        assert str(exc.value) == 'Too high.'

        with raises(ValueError) as exc:
            test('-4.0')
        assert str(exc.value) == 'Too low.'

        test = t.Float()
        assert test('4') == 4.0

    def test_boolean(self):
        test = t.Boolean()

        assert test('f') is False
        assert test('true') is True

        with raises(ValueError) as exc:
            test('')
        assert str(exc.value) == 'Not a boolean value.'

        test = t.Boolean(true_unless_false=True)

        assert test('f') is False
        assert test('true') is True
        assert test('') is True

        test = t.Boolean(none_values=t.BOOL_FIELD_NONE_VALUES)

        assert test('f') is False
        assert test('true') is True
        assert test('null') is None

        test = t.Boolean(true_values=['ja', 'j'],
                         false_values=['nee', 'n'])

        assert test('ja') is True
        assert test('nee') is False

        with raises(ValueError) as exc:
            test('yes')
        assert str(exc.value) == 'Not a boolean value.'

    def test_enum(self):
        test = t.Enum(['red', 'green', 'blue'])
        assert test('red') == 'red'

        test = t.Enum([1, 2, 3, 4], t.Int())
        assert test('3') == 3

    def test_set(self):
        test = t.Set(['red', 'green', 'blue'])
        assert test('red,blue') == ['red', 'blue']

        test = t.Set([1, 2, 3, 4], t.Int())
        assert test('2,3') == [2, 3]

    def test_list_of(self):
        test = t.ListOf(t.Boolean())
        assert test('yes,yes,no') == [True, True, False]

        with raises(ValueError) as exc:
            test('bluh,blah,no')
        assert exc.value.to_dict() == [
            'Not a boolean value.',
            'Not a boolean value.',
            None,
        ]

        test = t.Set([1, 2, 3, 4], t.Int())
        assert test('2,3') == [2, 3]
