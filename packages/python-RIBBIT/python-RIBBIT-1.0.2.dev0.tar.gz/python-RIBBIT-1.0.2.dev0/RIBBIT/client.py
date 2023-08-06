from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import random

import requests

from .decoder import decode_CROAK


class RIBBITClientError(Exception):
    pass


class RIBBITClient(object):
    """
    RIBBITClient is a frog.tips API client

    RIBBITClient is a client for making requests against the frog.tips API and
    parsing the responses returned via the RIBBIT messaging protocol:

    http://frog.tips/api/1/
    """

    DEFAULT_ENDPOINT = 'http://frog.tips/api/1/tips'
    DEFAULT_HEADERS = {'Accept': 'application/der-stream'}

    def __init__(self, endpoint=DEFAULT_ENDPOINT, headers=None):
        """
        Initialize a new RIBBITClient

        Parameters
        ----------
        endpoint : str
            The URL to make requests against.
        headers : dict
            An optional dict of extra headers to pass to the API.
        """
        self.endpoint = endpoint
        self.headers = self.DEFAULT_HEADERS.copy()
        if headers is not None:
            self.headers.update(headers)

        self._croak_cache = None

    def croak(self):
        """
        Retrieve a CROAK of FROG tips.

        Returns
        -------
        dict[int]str
            A CROAK of FROG tips represented as a dict, indexed by tip
            number.
        """
        try:
            croak_resp = requests.get(self.endpoint, headers=self.headers)
            croak_resp.raise_for_status()
        except requests.HTTPError as exc:
            raise RIBBITClientError(
                'Error during CROAK request: %s' % exc.message)

        return decode_CROAK(croak_resp.content)

    def frog_tip(self, refresh_cache=False):
        """
        Retrieve a single FROG tip.

        Returns
        -------
        str
            A single FROG tip, without its number.
        """
        if self._croak_cache is None or refresh_cache:
            self._croak_cache = self.croak()

        return self._croak_cache[random.choice(self._croak_cache.keys())]
