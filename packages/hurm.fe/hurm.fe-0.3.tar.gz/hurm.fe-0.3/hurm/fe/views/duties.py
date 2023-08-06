# -*- coding: utf-8 -*-
# :Project:   hurm -- Duties data view
# :Created:   mer 03 feb 2016 21:19:58 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
#

from pyramid.view import view_config

from sqlalchemy import select, text

from hurm.db.tables import activities, duties, locations, persons, tasks

from ..i18n import translatable_string as _
from . import expose

_a = activities.alias('a')
_d = duties.alias('d')
_l = locations.alias('l')
_p = persons.alias('p')
_t = tasks.alias('t')

@view_config(route_name='duties', renderer='json')
@expose(select([_d.c.idduty,
                _d.c.idtask,
                _d.c.idperson,
                # text() is needed here, to workaround default normalization
                # performed by the Name type decorator, sigh...
                (_p.c.lastname + text("' '") + _p.c.firstname).label('Person'),
                _d.c.starttime,
                _d.c.endtime,
                _d.c.note],
               from_obj=_d.join(_p)),
        metadata=dict(
            Person=dict(
                flex=1,
                hint=_('Full name of the person'),
                label=_('Person'),
                lookup=dict(
                    displayField='fullname',
                    idField='idperson',
                    url='/data/available_persons',
                ),
            ),
            note=dict(width=120),
        ))
def _duties(request, results):
    return results


@view_config(route_name='location_duties', renderer='json')
@expose(select([_d.c.idduty,
                _d.c.idtask,
                _d.c.idperson,
                _t.c.date.label('Task_date'),
                # text() is needed here, to workaround default normalization
                # performed by the Name type decorator, sigh...
                (_p.c.lastname + text("' '") + _p.c.firstname).label('Person'),
                _a.c.description.label('Activity'),
                _t.c.starttime.label('Task_starttime'),
                _t.c.endtime.label('Task_endtime'),
                _d.c.starttime,
                _d.c.endtime,
                _d.c.note],
               from_obj=_d.join(_p).join(_t).join(_a).join(_l)),
        metadata=dict(
            Activity=dict(width=140),
            Person=dict(
                flex=1,
                hint=_('Full name of the person'),
                label=_('Person'),
                lookup=dict(
                    displayField='fullname',
                    idField='idperson',
                    url='/data/available_persons',
                ),
            ),
            Task_endtime=dict(
                hidden=True,
                label=_('Task end'),
            ),
            Task_starttime=dict(
                hidden=True,
                label=_('Task start'),
            ),
            note=dict(width=120),
        ))
def _location_duties(request, results):
    return results


@view_config(route_name='person_duties', renderer='json')
@expose(select([_d.c.idduty,
                _d.c.idtask,
                _d.c.idperson,
                _t.c.date.label('Task_date'),
                # text() is needed here, to workaround default normalization
                # performed by the Name type decorator, sigh...
                (_p.c.lastname + text("' '") + _p.c.firstname).label('Person'),
                _l.c.description.label('Location'),
                _a.c.description.label('Activity'),
                _t.c.starttime.label('Task_starttime'),
                _t.c.endtime.label('Task_endtime'),
                _d.c.starttime,
                _d.c.endtime,
                _d.c.note],
               from_obj=_d.join(_p).join(_t).join(_a).join(_l)),
        metadata=dict(
            Activity=dict(width=140),
            Location=dict(flex=1),
            Person=dict(
                flex=1,
                hidden=True,
                hint=_('Full name of the person'),
                label=_('Person'),
                lookup=dict(
                    displayField='fullname',
                    idField='idperson',
                    url='/data/available_persons',
                ),
            ),
            Task_endtime=dict(
                hidden=True,
                label=_('Task end'),
            ),
            Task_starttime=dict(
                hidden=True,
                label=_('Task start'),
            ),
            note=dict(width=120),
        ))
def _person_duties(request, results):
    return results
