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
from datetime import date, datetime

from zope import interface, component
from zope.schema.interfaces import IDate

from z3c.form import interfaces
from z3c.form.widget import FieldWidget
from z3c.form.browser.text import TextWidget
from z3c.form.converter import BaseDataConverter
from z3c.form.converter import FormatterValidationError
from zojax.resourcepackage.library import includeInplaceSource

from interfaces import IDateWidget, IDateWidgetsLayer


jssource = """<script type="text/javascript">
Ext.EventManager.onDocumentReady(function() {
   var dateField = new Ext.form.DateField({
      applyTo: '%(id)s', name: '%(name)s', format: '%(format)s'});
   dateField.setValue('%(value)s');
})</script>"""


class DateWidget(TextWidget):
    interface.implements(IDateWidget)

    klass = 'widget-extjs-date'

    def render(self):
        if self.mode == interfaces.DISPLAY_MODE:
            self.value = date(*(time.strptime(self.value, '%m/%d/%y'))[0:3])
            return super(DateWidget, self).render()

        if not self.value and self.field.required:
            value = date.today().strftime('%m/%d/%y')
        else:
            value = self.value

        includeInplaceSource(jssource%{
                'id': self.id,
                'name': self.name,
                'value': value,
                'klass': self.klass,
                'format': 'm/d/y',
                }, ('extjs-widgets',))

        return super(DateWidget, self).render()


@component.adapter(IDate, IDateWidgetsLayer)
@interface.implementer(interfaces.IFieldWidget)
def DateFieldWidget(field, request):
    """IFieldWidget factory for DateWidget."""
    return FieldWidget(field, DateWidget(request))


class DateDataConverter(BaseDataConverter):
    component.adapts(IDate, IDateWidget)

    def toWidgetValue(self, value):
        if value is self.field.missing_value:
            return u''
        return value.strftime('%m/%d/%y')

    def toFieldValue(self, value):
        if value == u'':
            return self.field.missing_value

        try:
            return date(*(time.strptime(value, '%m/%d/%y'))[0:3])
        except Exception, err:
            raise FormatterValidationError(err.args[0], value)
