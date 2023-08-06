"""
Fake Nova client

This exists to allow people to install our client without novaclient.
Supernova requires the novaclient to be importable but doesn't actually use
it.
"""


def client():
    """Don't do anything."""
    pass
