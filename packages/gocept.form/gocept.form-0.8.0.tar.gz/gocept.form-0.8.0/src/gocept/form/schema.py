# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: schema.py 5720 2008-05-06 13:31:02Z zagy $

import zope.schema.interfaces


def applySchemaData(context, schema, data, omit=(), set_defaults=True):
    _marker = object()
    omit = set(omit)
    for name in schema.names(all=True):
        if name in omit:
            continue
        field = schema[name]
        if not zope.schema.interfaces.IField.providedBy(field):
            continue
        value = data.get(name, _marker)
        if value is _marker and set_defaults:
            value = field.default
        if value is not _marker:
            setattr(context, name, value)
