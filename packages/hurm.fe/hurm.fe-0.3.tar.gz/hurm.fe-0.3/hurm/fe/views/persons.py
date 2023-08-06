# -*- coding: utf-8 -*-
# :Project:   hurm -- Persons data view
# :Created:   mar 02 feb 2016 09:58:18 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
#

from pyramid.view import view_config

from sqlalchemy import exists, select, text
from sqlalchemy.sql.expression import literal_column
from sqlalchemy.types import String

from hurm.db.tables import availabilities, persons, tasks

from ..i18n import translatable_string as _
from . import expose


_a = availabilities.alias('a')
_p = persons.alias('p')
_t = tasks.alias('t')

@view_config(route_name='persons', renderer='json')
@expose(select([_p.c.idperson,
                _p.c.lastname,
                _p.c.firstname,
                # text() is needed here, to workaround default normalization
                # performed by the Name type decorator, sigh...
                (_p.c.lastname + text("' '") + _p.c.firstname).label('FullName'),
                _p.c.phone,
                _p.c.mobile,
                _p.c.email,
                _p.c.birthdate,
                _p.c.role,
                _p.c.note,
                literal_column("'*'", String).label('password')]),
        metadata=dict(
            FullName=dict(
                flex=1,
                hint=_('Full name of the person'),
                label=_('Full name'),
            ),
            birthdate=dict(hidden=True),
            email=dict(width=140, vtype='email'),
            firstname=dict(hidden=True),
            lastname=dict(hidden=True),
            mobile=dict(hidden=True, vtype='phone'),
            note=dict(width=120),
            password=dict(
                hidden=True,
                hint=_('Login password of the user'),
                label=_('Password'),
                nullable=True,
                password=True,
                width=70,
            ),
            phone=dict(hidden=True, vtype='phone'),
            role=dict(width=140),
        ))
def _persons(request, results):
    return results


@view_config(route_name='available_persons', renderer='json')
@expose(select([_p.c.idperson,
                # text() is needed here, to workaround default normalization
                # performed by the Name type decorator, sigh...
                (_p.c.lastname + text("' '") + _p.c.firstname).label('fullname')])
        .order_by('lastname', 'firstname'))
def _available_persons():
    request, params = (yield)
    if 'idtask' in params:
        idtask = params.pop('idtask')
        conditions = (exists()
                      .where(_t.c.idtask == idtask)
                      .where(_a.c.date == _t.c.date)
                      .where(_a.c.idperson == _p.c.idperson)
                      .where(text("(COALESCE(a.starttime, '00:00'),"
                                  " COALESCE(a.endtime, '24:00'))"
                                  " OVERLAPS "
                                  "(t.starttime,"
                                  " COALESCE(t.endtime, '24:00'))")),)
        result = yield params, conditions
    else:
        result = yield params
    yield result
