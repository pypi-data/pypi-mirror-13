from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyasn1.codec.der import encoder
from pyasn1.error import PyAsn1Error

from .definition import Croak, FrogTip


def encode_CROAK(croak):
    """
    Encode a CROAK represented as a dict to DER.

    Parameters
    ----------
    croak : dict[int]str
        A dict keyed by integer FROG tip id.

    Returns
    -------
    bytes
        The DER encoded CROAK.
    """

    asn1_croak = Croak()

    try:
        for idx, frog_tip in enumerate(croak.items()):
            tip_id, tip = frog_tip

            asn1_frog_tip = FrogTip()
            asn1_frog_tip.setComponentByName('number', tip_id)
            asn1_frog_tip.setComponentByName('tip', tip)

            asn1_croak.setComponentByPosition(idx, asn1_frog_tip)

        return encoder.encode(asn1_croak)

    except PyAsn1Error as exc:
        raise ValueError('Error during FROG tip encoding: %s' % exc.message)
