# -*- coding: utf-8 -*-
"""
    urly
    ~~~~
    ``urly`` is really just a thin wrapper for the werkzeug, with some extra
    sugar added to maximize enjoyment and minimize effort.
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .urls import URL, new_netloc
__all__ = ['URL', 'new_netloc']
