# -*- coding: utf-8 -*-
# :Project:   hurm -- Editions data view
# :Created:   mar 02 feb 2016 16:54:48 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
#

from pyramid.view import view_config

from sqlalchemy import select

from hurm.db.tables import editions

from . import expose


@view_config(route_name='editions', renderer='json')
@expose(select([editions.c.idedition,
                editions.c.description,
                editions.c.startdate,
                editions.c.enddate,
                editions.c.note]),
        metadata=dict(
            description=dict(flex=1),
            note=dict(width=120),
        ))
def _editions(request, results):
    return results
