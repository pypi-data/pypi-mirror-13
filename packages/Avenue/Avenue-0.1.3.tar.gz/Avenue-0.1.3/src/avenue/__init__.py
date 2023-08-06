from __future__ import absolute_import, division, print_function

from .avenue import (
    Avenue,
    PROCESSORS,
)

from .processors import (
    Processor,
    PathProcessor,
    MethodProcessor,
)

__version__ = '0.1.3'

__package__ = 'avenue'
__title__ = 'Avenue'
__description__ = 'Avenue: Highway routing.'
__uri__ = 'https://avenue.readthedocs.org/'

__author__ = 'Nils Corver'
__email__ = 'nils@corverdevelopment.nl'

__license__ = 'MIT'
__copyright__ = 'Copyright (c) 2016 Corver Development B.V.'

__all__ = [
    'Avenue',
    'PROCESSORS',

    'Processor',
    'PathProcessor',
    'MethodProcessor',
]
