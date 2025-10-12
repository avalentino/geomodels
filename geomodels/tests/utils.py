"""Utility functions."""


def dms_to_dec(deg, min_, sec):
    """Convert angles from degrees, minutes and seconds to decimal degrees."""
    return ((deg * 60 + min_) * 60 + sec) / 60**2
