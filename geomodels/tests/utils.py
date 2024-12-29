"""Utility functions."""


def dms_to_dec(d, m, s):
    """Convert angles from degres, minutes and seconds to decimal degrees."""
    return ((d * 60 + m) * 60 + s) / 60**2
