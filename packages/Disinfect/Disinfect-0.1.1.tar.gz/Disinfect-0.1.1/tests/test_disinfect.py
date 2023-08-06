# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from disinfect import Field
from disinfect import Mapping
from disinfect import MultiValueError
from disinfect import Test
from disinfect import tests
from disinfect import validate
from pandora.compat import text_type
from pytest import raises


class TestDisinfect(object):
    def test_basics(self):
        test = Test([
            lambda v: text_type(v),
            validate(lambda v: len(v) >= 1, error='Not long enough.'),
            validate(lambda v: len(v) <= 10, error='Too long.'),
        ])

        assert test('Nils') == u'Nils'

        with raises(ValueError) as exc:
            test('')

        assert exc.type is ValueError
        assert str(exc.value) == 'Not long enough.'

    def test_string(self):
        test = tests.string_field()
        test('Nils') == 'Nils'
        test(u'Níls') == u'Níls'

    def test_mapping(self):
        def string_field(min_len=1, max_len=150):
            return Test([
                lambda v: text_type(v),
                validate(lambda v: len(v) >= min_len,
                         error='Not long enough.'),
                validate(lambda v: len(v) <= max_len,
                         error='Too long.'),
            ])

        mapping = Mapping({
            'first': string_field(),
            Field('infix', default=''): string_field(min_len=0, max_len=40),
            'last': string_field(),
        })

        user = mapping({
            'first': 'Nils',
            'last': 'Corver',
        })

        assert user == {
            'first': 'Nils',
            'infix': '',
            'last': 'Corver',
        }

        with raises(MultiValueError) as exc:
            mapping({})

        assert exc.type is MultiValueError
        assert exc.value.errors == {
            'first': 'Field is required.',
            'last': 'Field is required.',
        }

    def test_tests(self):
        test = tests.boolean_field()

        assert test('f') is False
        assert test('true') is True

        with raises(ValueError) as exc:
            test('')

        assert str(exc.value) == 'Not a boolean value.'

    def test_complex(self):
        mapping = Mapping({
            'first': tests.string_field(),
            Field('infix', default=''): tests.string_field(min_len=0,
                                                           max_len=40),
            'last': tests.string_field(),

            'addresses': tests.list_of(Mapping({
                'zipcode': tests.string_field(min_len=6, max_len=6),
                'housenumber': tests.int_field(min_value=1),
            }))
        })

        user = mapping({
            'first': 'Nils',
            'infix': '',
            'last': 'Corver',
            'addresses': [
                {'zipcode': '2024HP', 'housenumber': '118'},
                {'zipcode': '2024VV', 'housenumber': '38'},
            ]
        })

        assert user == {
            'first': 'Nils',
            'infix': '',
            'last': 'Corver',
            'addresses': [
                {'zipcode': '2024HP', 'housenumber': 118},
                {'zipcode': '2024VV', 'housenumber': 38},
            ]
        }

    def test_enum(self):
        test = tests.enum_field(['red', 'green', 'blue'])
        assert test('red') == 'red'

        test = tests.enum_field([1, 2, 3, 4], tests.int_field())
        assert test('3') == 3

    def test_set(self):
        test = tests.set_field(['red', 'green', 'blue'])
        assert test('red,blue') == ['red', 'blue']

        test = tests.set_field([1, 2, 3, 4], tests.int_field())
        assert test('2,3') == [2, 3]
