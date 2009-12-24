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
from datetime import datetime
from zope import interface, component
from zope.schema.interfaces import IDatetime
from zope.interface.common.idatetime import ITZInfo
from zope.security.management import queryInteraction
from z3c.form import interfaces
from z3c.form.widget import FieldWidget
from z3c.form.browser.text import TextWidget
from z3c.form.converter import BaseDataConverter
from z3c.form.converter import FormatterValidationError
from zojax.resourcepackage.library import includeInplaceSource

from interfaces import IDatetimeWidget, IDateWidgetsLayer

jssource = """<script type="text/javascript">
Ext.EventManager.onDocumentReady(function(){
 var dateField = new Ext.ux.form.DateTime({
      applyTo:'%(id)s', name:'%(name)s', timeFormat:'%(tformat)s'});
 dateField.setValue('%(value)s');
});</script>"""


class DatetimeWidget(TextWidget):
    interface.implements(IDatetimeWidget)

    klass = 'widget-extjs-datetime'
    style = 'display: none'

    def render(self):
        if self.mode == interfaces.DISPLAY_MODE:
            tz = ITZInfo(getRequest(), utc)
            self.value = datetime(
                tzinfo=tz, *(time.strptime(self.value, '%Y-%m-%d %H:%M'))[0:6])
            return super(DatetimeWidget, self).render()

        dates = self.request.locale.dates
        formatter = dates.getFormatter('dateTime', 'short')

        tformat = dates.getFormatter('time', 'short').getPattern()
        if tformat[-1] == 'a':
            tformat = 'g:i A'
        else:
            tformat = 'H:i'

        if len(self.value) > 16:
            self.value = self.value[:16]

        if self.value:
            value = self.value
        else:
            tz = ITZInfo(self.request, utc)
            dt = datetime.now(tz)
            dt = dt.replace(minute=0, second=0, microsecond=0)
            value = dt.strftime('%Y-%m-%d %H:%M')

        includeInplaceSource(jssource%{
                'id': self.id,
                'name': self.name,
                'value': value,
                'klass': self.klass,
                'tformat': tformat,
                }, ('extjs-widgets',))

        return super(DatetimeWidget, self).render()


@component.adapter(IDatetime, IDateWidgetsLayer)
@interface.implementer(interfaces.IFieldWidget)
def DatetimeFieldWidget(field, request):
    """IFieldWidget factory for DatetimeWidget."""
    return FieldWidget(field, DatetimeWidget(request))


class DatetimeDataConverter(BaseDataConverter):
    component.adapts(IDatetime, IDatetimeWidget)

    def toWidgetValue(self, value):
        if value is self.field.missing_value:
            return u''
        return value.strftime('%Y-%m-%d %H:%M')

    def toFieldValue(self, value):
        if value == u'':
            return self.field.missing_value

        tz = ITZInfo(getRequest(), utc)
        try:
            return tz.localize(datetime(*(time.strptime(value, '%Y-%m-%d %H:%M:%S'))[0:6]))
        except Exception, err:
            raise FormatterValidationError(err.args[0], value)


def getRequest():
    interaction = queryInteraction()

    if interaction is not None:
        for request in interaction.participations:
            return request
