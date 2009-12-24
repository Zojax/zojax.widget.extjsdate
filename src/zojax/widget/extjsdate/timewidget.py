##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id$
"""
import time
from pytz import utc
import datetime

from zope import interface, component
from zope.schema.interfaces import ITime
from zope.security.management import queryInteraction
from zope.interface.common.idatetime import ITZInfo

from z3c.form import interfaces
from z3c.form.widget import FieldWidget
from z3c.form.browser.text import TextWidget
from z3c.form.converter import BaseDataConverter
from z3c.form.converter import FormatterValidationError
from zojax.resourcepackage.library import includeInplaceSource

from interfaces import ITimeWidget, IDateWidgetsLayer


jssource = """<script type="text/javascript">
Ext.EventManager.onDocumentReady(function() {
   var timeField = new Ext.form.TimeField({
      applyTo: '%(id)s', name: '%(name)s', format: '%(format)s'});
   timeField.setValue('%(value)s');
})</script>"""


class TimeWidget(TextWidget):
    interface.implements(ITimeWidget)

    klass = 'widget-extjs-time'

    def render(self):
        if self.mode == interfaces.DISPLAY_MODE:
            self.value = datetime.time(*(time.strptime(self.value, '%H:%M:%S'))[0:3])
            return super(TimeWidget, self).render()

        if not self.value and self.field.required:
            tz = ITZInfo(self.request, utc)
            dt = datetime.datetime.now(tz)
            value = dt.strftime('%H:%M:%S')
        else:
            value = self.value

        includeInplaceSource(jssource%{
                'id': self.id,
                'name': self.name,
                'value': value,
                'klass': self.klass,
                'format': 'H:i:s',
                }, ('extjs-widgets',))

        return super(TimeWidget, self).render()


@component.adapter(ITime, IDateWidgetsLayer)
@interface.implementer(interfaces.IFieldWidget)
def TimeFieldWidget(field, request):
    """IFieldWidget factory for TimeWidget."""
    return FieldWidget(field, TimeWidget(request))


class TimeDataConverter(BaseDataConverter):
    component.adapts(ITime, ITimeWidget)

    def toWidgetValue(self, value):
        if value is self.field.missing_value:
            return u''
        return value.strftime('%H:%M:%S')

    def toFieldValue(self, value):
        if value == u'':
            return self.field.missing_value

        tz = ITZInfo(getRequest(), utc)
        try:
            return datetime.time(tzinfo=tz, *time.strptime(value, '%H:%M:%S')[3:6]
                                 )
        except Exception, err:
            raise FormatterValidationError(err.args[0], value)

def getRequest():
    interaction = queryInteraction()

    if interaction is not None:
        for request in interaction.participations:
            return request
