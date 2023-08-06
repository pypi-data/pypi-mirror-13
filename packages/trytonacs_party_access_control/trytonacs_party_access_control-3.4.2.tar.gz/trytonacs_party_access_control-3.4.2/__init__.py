# -*- coding: utf-8 -*-
"""
    trytonacs_party_access_control

    :copyright: (c) The file COPYRIGHT at the top level of this
    :repository contains the full copyright notices.
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import Pool

from .party import Party, Badge


def register():
    Pool.register(
        Party,
        Badge,
        module='party_access_control', type_='model'
    )
