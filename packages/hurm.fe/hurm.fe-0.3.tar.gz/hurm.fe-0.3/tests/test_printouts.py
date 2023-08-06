# -*- coding: utf-8 -*-
# :Project:   hurm -- Test for the PDF generation views
# :Created:   ven 12 feb 2016 10:26:38 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
#

def test_person_duties(app, test_edition, jane_tree):
    response = app.get('/pdf/duties/edition/%d/person/%d' %
                       (test_edition.idedition, jane_tree.idperson))
    assert response.content_type == 'application/pdf'


def test_location_duties(app, test_edition, reception):
    response = app.get('/pdf/duties/edition/%d/location/%d' %
                       (test_edition.idedition, reception.idlocation))
    assert response.content_type == 'application/pdf'


def test_by_location_duties(app, test_edition):
    response = app.get('/pdf/duties/edition/%d/locations' % test_edition.idedition)
    assert response.content_type == 'application/pdf'


def test_by_person_duties(app, test_edition):
    response = app.get('/pdf/duties/edition/%d/persons' % test_edition.idedition)
    assert response.content_type == 'application/pdf'
