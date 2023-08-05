# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: interfaces.py 5531 2008-01-24 13:37:55Z zagy $

import zope.interface
import zope.publisher.interfaces.browser
import zope.schema


class IFieldGroup(zope.interface.Interface):

    title = zope.schema.TextLine(title=u"Widget Group Title")

    css_class = zope.schema.TextLine(
        title=u"CSS class to apply to the group")

    widgets = zope.schema.List(
        title=u"Widges of this group",
        description=u"Will be filled by form")

    def get_field_names():
        "Return list of field names."


class IRemainingFields(IFieldGroup):
    """Marker interface for a fieldgroup which contains all remaining fields.

    Remaining fields are fields which are not noted in any other field group.

    """

    def get_field_names():
        """Returns None."""


class IGroupedForm(zope.interface.Interface):

    field_groups = zope.schema.List(
        title=u"Field groups to display",
        value_type=zope.schema.Object(IFieldGroup))


class IJSValidationLayer(zope.publisher.interfaces.browser.IBrowserRequest):
    """Layer for default javascript validation functions."""


class IJSValidator(zope.interface.Interface):
    """A javascript validation adapter.

    XXX

    """
