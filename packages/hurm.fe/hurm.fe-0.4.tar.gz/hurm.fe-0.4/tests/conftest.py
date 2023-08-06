# -*- coding: utf-8 -*-
# :Project:   hurm -- Functional tests configuration
# :Created:   dom 07 feb 2016 18:23:13 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
#

from pyramid.paster import get_appsettings
from webtest import TestApp
import pytest

from hurm.db import entities
from hurm.fe import main


@pytest.fixture(scope="module")
def app():
    settings = get_appsettings('test.ini')
    app = TestApp(main({}, **settings))
    app.post('/auth/login', {'email': 'bob@example.com', 'password': 'test'})
    return app


@pytest.fixture(scope="module")
def session():
    return entities.DBSession()


@pytest.fixture
def test_edition(session):
    return session.query(entities.Edition).filter_by(description='Test edition').one()


@pytest.fixture
def jane_tree(session):
    return session.query(entities.Person).filter_by(lastname='Tree').one()


@pytest.fixture
def reception(session):
    return session.query(entities.Location).filter_by(description='Reception').one()
