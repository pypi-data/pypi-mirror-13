from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyasn1.codec.der import decoder
from pyasn1.error import PyAsn1Error
from pyasn1.type.error import ValueConstraintError

from .definition import Croak


def decode_CROAK(der):
    """
    Decode a sequence of DER encoded RIBBIT protocol FROG tips.

    Parameters
    ----------
    der : bytes
        Raw DER encoded FROG tips.

    Returns
    -------
    dict
        A dict of FROG tips, keyed by their number.
    """
    try:
        decoded = decoder.decode(der, asn1Spec=Croak())
        return {int(frog_tip[0]): str(frog_tip[1]) for frog_tip in decoded[0]}
    except ValueConstraintError:
        raise ValueError('Too many or too few FROG tips')
    except PyAsn1Error as exc:
        raise ValueError('Error during FROG tip parsing: %s' % exc.message)
