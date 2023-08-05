# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: jsvalidation.py 5532 2008-01-24 13:39:39Z zagy $

import xml.sax.saxutils

import zope.contentprovider.interfaces
import zope.component
import zope.formlib.interfaces
import zope.interface
import zope.schema.interfaces
import zope.i18n

import zc.resourcelibrary

import gocept.mochikit.interfaces

import gocept.form.interfaces
from gocept.form.i18n import MessageFactory as _


class ValidationViewlet(zope.viewlet.viewlet.ViewletBase):

    def __init__(self, context, request, view, manager):
        super(ValidationViewlet, self).__init__(
            context, request, view, manager)
        self.validators = []

    def update(self):
        for form_field in self.__parent__.form_fields:
            field = form_field.field
            validators = zope.component.getAdapters(
                (field, self.request),
                gocept.form.interfaces.IJSValidator)
            self.validators.extend(validators)

    def render(self):
        result = ['<script language="javascript">']
        for name, validator in self.validators:
            result.append('// %s' % name)
            result.append(
                'connect(window, "onload", function(event) {%s});' % validator)
        result.append('</script>')
        return '\n'.join(result)


@zope.component.adapter(
    zope.schema.interfaces.IMinMaxLen,
    gocept.form.interfaces.IJSValidationLayer)
@zope.interface.implementer(gocept.form.interfaces.IJSValidator)
def max_length_validator(field, request):
    """validate the maximum length is not overridden"""
    if not field.max_length:
        return
    zc.resourcelibrary.need('gocept.form.jsvalidation')
    message = _("Too long (max ${max_length})",
               mapping=dict(max_length=field.max_length))
    return '''new gocept.validation.MaxLength('form.%s', %d, %s)'''  % (
        field.__name__, field.max_length,
        xml.sax.saxutils.quoteattr(
            zope.i18n.translate(message, context=request)))
