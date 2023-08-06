# -*- coding: utf-8 -*-
# :Project:   hurm -- Activities data view
# :Created:   mar 02 feb 2016 17:36:07 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
#

from pyramid.view import view_config

from sqlalchemy import select

from hurm.db.tables import activities

from . import expose


@view_config(route_name='activities', renderer='json')
@expose(select([activities.c.idactivity,
                activities.c.description,
                activities.c.note]),
        metadata=dict(
            description=dict(flex=1),
            note=dict(width=120),
        ))
def _activities(request, results):
    return results
