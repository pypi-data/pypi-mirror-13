from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from RIBBIT.client import RIBBITClient


def cli():
    client = RIBBITClient()
    print(client.frog_tip())
