# -*- coding: utf-8 -*-
# :Project:   hurm -- Edition related printouts
# :Created:   dom 14 feb 2016 19:27:54 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
#

from operator import attrgetter

from pyramid.view import view_config

from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import KeepTogether, Paragraph, Spacer

from .. import DBSession
from ..i18n import translatable_string as _
from . import BasicEditionPrintout, create_pdf, subtitle_style


class ByLocationDuties(BasicEditionPrintout):
    pagesize = landscape(A4)

    def __init__(self, output, translate, pluralize, edition):
        super().__init__(output, translate, pluralize, edition)
        locations = set(task.location for task in edition.tasks)
        self.locations = sorted(locations, key=attrgetter('description'))

    def getCenterHeader(self):
        return self.getTitle()

    def getTitle(self):
        return self.translate(_('Duties calendar by location'))

    def getSubTitle(self):
        ngettext = self.pluralize
        count = len(self.locations)
        return ngettext('$count location', '$count locations', count,
                        mapping=dict(count=count))

    def getElements(self):
        from .location import duties_table

        yield from super().getElements()

        for location in self.locations:
            yield Spacer(0, 10)
            yield KeepTogether([Paragraph(location.description, subtitle_style),
                                Spacer(0, 5),
                                duties_table(self.translate, self.doc, location)])


@view_config(route_name='pdf_by_location_duties')
def _by_location_duties(request):
    return create_pdf(DBSession(), request, ByLocationDuties)


class ByPersonDuties(BasicEditionPrintout):
    pagesize = landscape(A4)

    def __init__(self, output, translate, pluralize, edition):
        super().__init__(output, translate, pluralize, edition)
        persons = set(duty.person for task in edition.tasks for duty in task.duties)
        self.persons = sorted(persons, key=lambda p: self.translate(p.fullname))

    def getCenterHeader(self):
        return self.getTitle()

    def getTitle(self):
        return self.translate(_('Duties calendar by person'))

    def getSubTitle(self):
        ngettext = self.pluralize
        count = len(self.persons)
        return ngettext('$count person', '$count persons', count,
                        mapping=dict(count=count))

    def getElements(self):
        from .person import duties_table

        yield from super().getElements()

        for person in self.persons:
            yield Spacer(0, 10)
            yield KeepTogether([Paragraph(self.translate(person.fullname), subtitle_style),
                                Spacer(0, 5),
                                duties_table(self.translate, self.doc, person)])


@view_config(route_name='pdf_by_person_duties')
def _by_person_duties(request):
    return create_pdf(DBSession(), request, ByPersonDuties)
