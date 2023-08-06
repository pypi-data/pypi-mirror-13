from __future__ import absolute_import, division, print_function

from .disinfect import (
    Field,
    MappedValueError,
    Mapping,
    MultiValueError,
    Test,
    test_and_return,
    validate,
    sanitize,
)

__version__ = '0.1.2'

__package__ = 'disinfect'
__title__ = 'Disinfect'
__description__ = 'Disinfect: Destroy bad input.'
__uri__ = 'https://github.com/corverdevelopment/Disinfect/'

__author__ = 'Nils Corver'
__email__ = 'nils@corverdevelopment.nl'

__license__ = 'MIT'
__copyright__ = 'Copyright (c) 2016 Corver Development B.V.'

__all__ = [
    'Field',
    'MappedValueError',
    'Mapping',
    'MultiValueError',
    'Test',
    'test_and_return',
    'validate',
    'sanitize',
]
