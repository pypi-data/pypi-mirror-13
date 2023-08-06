from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyasn1.type import char, constraint, namedtype, univ


MIN_TIPS = 0
""" Minimum number of tips in a CROAK. """
MAX_TIPS = 50
""" Maximum number of tips in a CROAK. """


class FrogTip(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('number', univ.Integer()),
        namedtype.NamedType('tip', char.UTF8String()),
    )


class Croak(univ.SequenceOf):
    componentType = FrogTip()
    sizeSpec = constraint.ValueSizeConstraint(MIN_TIPS, MAX_TIPS)
