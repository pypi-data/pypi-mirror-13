# -*- coding: utf-8 -*-
'''
    trytonacs_party_access_control.py

    :copyright: The file COPYRIGHT at the top level of this
    :repository contains the full copyright notices.
    :license: , see LICENSE for more details.

'''
import random
import time

from sql.aggregate import Count

from trytond.pool import PoolMeta, Pool
from trytond.model import ModelView, ModelSQL, fields
from trytond.config import config
from trytond.transaction import Transaction

__all__ = ['Party', 'Badge']

__metaclass__ = PoolMeta

code_size = config.getint('party-access-control', 'size', 5)
timeout = config.getint('party-access-control', 'timeout', 120)


class Party:
    __name__ = 'party.party'

    badges = fields.One2Many('access.control.badge', 'party', 'Badge')


class Badge(ModelSQL, ModelView):
    "Badge"
    __name__ = 'access.control.badge'
    _rec_name = 'code'

    code = fields.Char('Code', select=True, required=True, readonly=True)
    disabled = fields.Boolean('Disabled')
    description = fields.Char('Description')
    party = fields.Many2One(
        'party.party', 'Party', ondelete='CASCADE', select=True, required=True
    )
    enable_from = fields.Date('Enable From', select=True)

    @classmethod
    def __setup__(cls):
        super(Badge, cls).__setup__()
        cls._order.insert(0, ('code', 'ASC'))
        cls._error_messages.update({
            'duplicate_code': 'Duplicate badge code "%(code)s"',
            'timeout': 'Could not find available code',
            })

    @classmethod
    def default_disabled(cls):
        return False

    @classmethod
    def generate_code(cls):
        return ''.join(str(random.randint(1, 9)) for i in xrange(code_size))

    @classmethod
    def create(cls, vlist):
        cursor = Transaction().cursor
        cursor.lock(cls._table)
        vlist = [v.copy() for v in vlist]
        for values in vlist:
            if not values.get('code'):
                start = time.time()
                while True:
                    code = cls.generate_code()
                    same = cls.search([
                        ('code', '=', code),
                        ('disabled', '=', False),
                        ])
                    if not same:
                        break
                    now = time.time()
                    if now - start > timeout:
                        cls.raise_user_error('timeout')
                values['code'] = code
        return super(Badge, cls).create(vlist)

    @classmethod
    def validate(cls, badges):
        cursor = Transaction().cursor
        table = cls.__table__()

        super(Badge, cls).validate(badges)

        cursor.execute(*table.select(
            table.code,
            where=table.disabled == False,
            group_by=table.code,
            having=Count(table.id) > 1))
        code = cursor.fetchone()
        if code:
            cls.raise_user_error('duplicate_code', {
                'code': code,
                })

    @classmethod
    def enablebadges(cls):
        """
        Simple Cron method to set disabled field to false.
        """
        pool = Pool()
        Date = pool.get('ir.date')
        today = Date.today()
        print '### enable badges'
        print '## today %s' % today
        badges = cls.search([
                 ('disabled', '=', True),
                 ('enable_from', '<=', today)
             ])
        for badge in badges:
            badge.disabled = False
            badge.enable_from = None
            badge.save()
