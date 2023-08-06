# -*- coding: utf-8 -*-
# :Project:   hurm -- Pyramid entry point
# :Created:   lun 01 feb 2016 20:21:56 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
#

import logging

from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory

from sqlalchemy import engine_from_config

import zope.sqlalchemy

from hurm.db.entities import DBSession

logger = logging.getLogger(__name__)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    from metapensiero.extjs.desktop.pyramid import configure

    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    zope.sqlalchemy.register(DBSession)

    timeout = settings.get('session.timeout', 24*60*60)
    if timeout == 'None':
        timeout = None
    else:
        timeout = int(timeout)

    reissue_time = settings.get('session.reissue_time', 24*60*60)
    if reissue_time == 'None':
        reissue_time = None
    else:
        reissue_time = int(reissue_time)

    session_factory = SignedCookieSessionFactory(settings['session.secret'],
                                                 timeout=timeout,
                                                 reissue_time=reissue_time)
    config = Configurator(settings=settings, session_factory=session_factory)

    configure(config)

    config.add_translation_dirs('hurm.db:locale/')
    config.add_translation_dirs('hurm.fe:locale/')

    config.add_static_view('static', 'static', cache_max_age=60*60)

    config.add_route('login', '/auth/login')
    config.add_route('logout', '/auth/logout')

    config.add_route('activities', '/data/activities')
    config.add_route('availabilities', '/data/availabilities')
    config.add_route('available_persons', '/data/available_persons')
    config.add_route('countries', '/data/countries')
    config.add_route('duties', '/data/duties')
    config.add_route('editions', '/data/editions')
    config.add_route('location_duties', '/data/location_duties')
    config.add_route('locations', '/data/locations')
    config.add_route('person_duties', '/data/person_duties')
    config.add_route('persons', '/data/persons')
    config.add_route('subcountries', '/data/subcountries')
    config.add_route('tasks', '/data/tasks')

    config.add_route('pdf_by_location_duties',
                     '/pdf/duties/edition/{idedition}/locations')
    config.add_route('pdf_by_person_duties',
                     '/pdf/duties/edition/{idedition}/persons')
    config.add_route('pdf_location_duties',
                     '/pdf/duties/edition/{idedition}/location/{idlocation}')
    config.add_route('pdf_person_duties',
                     '/pdf/duties/edition/{idedition}/person/{idperson}')

    config.add_route('yaml_dump', '/yaml/edition/{idedition}')
    config.add_route('excel_dump', '/xls/edition/{idedition}')

    config.scan()

    return config.make_wsgi_app()
