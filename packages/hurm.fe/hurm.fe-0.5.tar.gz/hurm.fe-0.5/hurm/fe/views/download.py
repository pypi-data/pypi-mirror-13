# -*- coding: utf-8 -*-
# :Project:   hurm -- Download related views
# :Created:   mer 17 feb 2016 09:40:27 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
#

import datetime
import logging

from pyramid.httpexceptions import HTTPBadRequest, HTTPInternalServerError
from pyramid.view import view_config

import yaml

from hurm.db.entities import Edition

from .. import DBSession
from ..i18n import translatable_string as _, translator


logger = logging.getLogger(__name__)


def _dump_edition(edition):
    from hurm.db.utils import dump

    return dump(edition, [{
        'entity': 'hurm.db.entities.edition.Edition',
        'key': 'description',
        'other': 'startdate,enddate,tasks'.split(',')
    }, {
        'entity': 'hurm.db.entities.activity.Activity',
        'key': 'description'
    }, {
        'entity': 'hurm.db.entities.location.Location',
        'key': 'description',
        'other': 'address,city,country,province,zip'.split(',')
    }, {
        'entity': 'hurm.db.entities.task.Task',
        'key': 'edition,activity,location,date,starttime'.split(','),
        'other': 'endtime,npersons,duties'.split(',')
    }, {
        'entity': 'hurm.db.entities.person.Person',
        'key': 'lastname,firstname'.split(','),
        'other': 'birthdate,mobile,phone,email,role,availabilities,preferred_activities'.split(',')
    }, {
        'entity': 'hurm.db.entities.personactivity.PersonActivity',
        'key': 'person,activity'.split(','),
    }, {
        'entity': 'hurm.db.entities.availability.Availability',
        'key': 'edition,person,date,starttime'.split(','),
        'other': 'endtime'
    }, {
        'entity': 'hurm.db.entities.duty.Duty',
        'key': 'person,task,starttime'.split(','),
        'other': 'endtime'
    }])


@view_config(route_name='yaml_dump')
def _yaml_dump(request):
    t = translator(request)

    try:
        idedition = int(request.matchdict['idedition'])
    except KeyError:
        error = t(_('Missing argument: $name', mapping=dict(name='idedition')))
        logger.error("Couldn't dump: %s", error)
        raise HTTPBadRequest(str(error))

    session = DBSession()

    edition = session.query(Edition).get(idedition)
    if edition is None:
        error = t(_('No edition with id $id', mapping=dict(id=str(idedition))))
        logger.error("Couldn't dump: %s", error)
        raise HTTPBadRequest(str(error))

    try:
        data = _dump_edition(edition)

        yaml.add_representer(datetime.time,
                             lambda dumper, data: dumper.represent_scalar('!time', str(data)))

        asyaml = yaml.dump(data, default_flow_style=False)

        response = request.response
        response.content_type = 'application/x-yaml'
        cdisp = 'attachment; filename=edition-%s.yaml' % edition.idedition
        response.content_disposition = cdisp
        response.text = asyaml
        return response
    except Exception as e:
        logger.critical("Couldn't dump: %s", e, exc_info=True)
        raise HTTPInternalServerError(str(e))


def _create_workbook(translate, data):
    from io import BytesIO
    import xlwt

    byclass = {e['entity'].split('.')[-1]: e for e in data}

    output = BytesIO()

    workbook = xlwt.Workbook()
    heading_xf = xlwt.easyxf('font: bold on; align: wrap on, vert centre, horiz center')
    date_xf = xlwt.easyxf(num_format_str='D-MMM-YY')
    time_xf = xlwt.easyxf(num_format_str='HH:MM')

    editions_sn = translate(_('Editions'))
    sheet = workbook.add_sheet(editions_sn)
    headings = (
        translate(_('Edition')),
        translate(_('Start date')),
        translate(_('End date')),
    )
    sheet.set_panes_frozen(True)
    sheet.set_horz_split_pos(1)
    sheet.set_remove_splits(True)

    for col, value in enumerate(headings):
        sheet.write(0, col, value, heading_xf)

    for row, edata in enumerate(byclass['Edition']['data'], 1):
        edata[':row'] = row+1
        sheet.write(row, 0, edata['description'])
        sheet.write(row, 1, edata['startdate'], date_xf)
        sheet.write(row, 2, edata['enddate'], date_xf)

    activities_sn = translate(_('Activities'))
    sheet = workbook.add_sheet(activities_sn)
    headings = (translate(_('Activity')),)
    sheet.set_panes_frozen(True)
    sheet.set_horz_split_pos(1)
    sheet.set_remove_splits(True)

    for col, value in enumerate(headings):
        sheet.write(0, col, value, heading_xf)

    for row, edata in enumerate(byclass['Activity']['data'], 1):
        edata[':row'] = row+1
        sheet.write(row, 0, edata['description'])

    locations_sn = translate(_('Locations'))
    sheet = workbook.add_sheet(locations_sn)
    headings = (
        translate(_('Location')),
        translate(_('Address')),
        translate(_('Zip')),
        translate(_('City')),
    )
    sheet.set_panes_frozen(True)
    sheet.set_horz_split_pos(1)
    sheet.set_remove_splits(True)

    for col, value in enumerate(headings):
        sheet.write(0, col, value, heading_xf)

    for row, edata in enumerate(byclass['Location']['data'], 1):
        edata[':row'] = row+1
        sheet.write(row, 0, edata['description'])
        sheet.write(row, 1, edata['address'])
        sheet.write(row, 2, edata['zip'])
        sheet.write(row, 3, edata['city'])

    persons_sn = translate(_('Persons'))
    sheet = workbook.add_sheet(persons_sn)
    headings = (
        translate(_('Full name')),
        translate(_('Email')),
        translate(_('Phone')),
        translate(_('Mobile')),
        translate(_('Birthdate')),
        translate(_('Role')),
        translate(_('Preferred activities')),
    )
    sheet.set_panes_frozen(True)
    sheet.set_horz_split_pos(1)
    sheet.set_remove_splits(True)

    for col, value in enumerate(headings):
        sheet.write(0, col, value, heading_xf)

    pref_acts = {}
    for pa in byclass['PersonActivity']['data']:
        p = pa['person']
        name = p['lastname']+p['firstname']
        a = pa['activity']
        pref_acts.setdefault(name, []).append(a['description'])

    for row, edata in enumerate(byclass['Person']['data'], 1):
        edata[':row'] = row+1
        sheet.write(row, 0, edata['lastname'] + ' ' + edata['firstname'])
        if 'email' in edata: sheet.write(row, 1, edata['email'])
        if 'phone' in edata: sheet.write(row, 2, edata['phone'])
        if 'mobile' in edata: sheet.write(row, 3, edata['mobile'])
        if 'birthdate' in edata: sheet.write(row, 4, edata['birthdate'], date_xf)
        if 'role' in edata: sheet.write(row, 5, edata['role'])
        sheet.write(row, 6, ', '.join(sorted(pref_acts.get(edata['lastname']+edata['firstname'], []))))

    availabilities_sn = translate(_('Availabilities'))
    sheet = workbook.add_sheet(availabilities_sn)
    headings = (
        translate(_('Person')),
        translate(_('Date')),
        translate(_('Start time')),
        translate(_('End time')),
    )
    sheet.set_panes_frozen(True)
    sheet.set_horz_split_pos(1)
    sheet.set_remove_splits(True)

    for col, value in enumerate(headings):
        sheet.write(0, col, value, heading_xf)

    for row, edata in enumerate(byclass['Availability']['data'], 1):
        edata[':row'] = row+1
        formula = "'%(sheet)s'!$A$%(row)d" % dict( sheet=persons_sn,
                                                   row=edata['person'][':row'])
        sheet.write(row, 0, xlwt.Formula(formula))
        sheet.write(row, 1, edata['date'], date_xf)
        if 'starttime' in edata: sheet.write(row, 2, edata['starttime'], time_xf)
        if 'endtime' in edata: sheet.write(row, 3, edata['endtime'], time_xf)

    tasks_sn = translate(_('Tasks'))
    sheet = workbook.add_sheet(tasks_sn)
    headings = (
        translate(_('Activity')),
        translate(_('Location')),
        translate(_('Date')),
        translate(_('Start time')),
        translate(_('End time')),
    )
    sheet.set_panes_frozen(True)
    sheet.set_horz_split_pos(1)
    sheet.set_remove_splits(True)

    for col, value in enumerate(headings):
        sheet.write(0, col, value, heading_xf)

    for row, edata in enumerate(byclass['Task']['data'], 1):
        edata[':row'] = row+1
        formula = "'%(sheet)s'!$A$%(row)d" % dict(sheet=activities_sn,
                                                  row=edata['activity'][':row'])
        sheet.write(row, 0, xlwt.Formula(formula))
        formula = "'%(sheet)s'!$A$%(row)d" % dict(sheet=locations_sn,
                                                  row=edata['location'][':row'])
        sheet.write(row, 1, xlwt.Formula(formula))
        sheet.write(row, 2, edata['date'], date_xf)
        if 'starttime' in edata: sheet.write(row, 3, edata['starttime'], time_xf)
        if 'endtime' in edata: sheet.write(row, 4, edata['endtime'], time_xf)

    duties_sn = translate(_('Duties'))
    sheet = workbook.add_sheet(duties_sn)
    headings = (
        translate(_('Person')),
        translate(_('Activity')),
        translate(_('Location')),
        translate(_('Date')),
        translate(_('Start time')),
        translate(_('End time')),
    )
    sheet.set_panes_frozen(True)
    sheet.set_horz_split_pos(1)
    sheet.set_remove_splits(True)

    for col, value in enumerate(headings):
        sheet.write(0, col, value, heading_xf)

    for row, edata in enumerate(byclass['Duty']['data'], 1):
        edata[':row'] = row+1
        formula = "'%(sheet)s'!$A$%(row)d" % dict(sheet=persons_sn,
                                                  row=edata['person'][':row'])
        sheet.write(row, 0, xlwt.Formula(formula))
        formula = "'%(sheet)s'!$A$%(row)d" % dict(sheet=activities_sn,
                                                  row=edata['task']['activity'][':row'])
        sheet.write(row, 1, xlwt.Formula(formula))
        formula = "'%(sheet)s'!$A$%(row)d" % dict(sheet=locations_sn,
                                                  row=edata['task']['location'][':row'])
        sheet.write(row, 2, xlwt.Formula(formula))
        sheet.write(row, 3, edata['task']['date'], date_xf)
        if 'starttime' in edata: sheet.write(row, 4, edata['starttime'], time_xf)
        if 'endtime' in edata: sheet.write(row, 5, edata['endtime'], time_xf)

    workbook.save(output)

    return output.getvalue()


@view_config(route_name='excel_dump')
def _excel_dump(request):
    t = translator(request)

    try:
        idedition = int(request.matchdict['idedition'])
    except KeyError:
        error = t(_('Missing argument: $name', mapping=dict(name='idedition')))
        logger.error("Couldn't dump: %s", error)
        raise HTTPBadRequest(str(error))

    session = DBSession()

    edition = session.query(Edition).get(idedition)
    if edition is None:
        error = t(_('No edition with id $id', mapping=dict(id=str(idedition))))
        logger.error("Couldn't dump: %s", error)
        raise HTTPBadRequest(str(error))

    try:
        data = _dump_edition(edition)
        response = request.response
        response.content_type = 'application/vnd.ms-excel'
        cdisp = 'attachment; filename=edition-%s.xls' % edition.idedition
        response.content_disposition = cdisp
        response.body = _create_workbook(t, data)
        return response
    except Exception as e:
        logger.critical("Couldn't dump: %s", e, exc_info=True)
        raise HTTPInternalServerError(str(e))
