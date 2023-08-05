# -*- coding: latin-1 -*-
# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: pagelet.py 5531 2008-01-24 13:37:55Z zagy $

"""Pagelet support for z3c.form forms."""

import z3c.form.form
import z3c.pagelet.browser
import z3c.pagelet.interfaces
import zope.interface
import z3c.template.interfaces
import zope.component

class Form(z3c.pagelet.browser.BrowserPagelet, z3c.form.form.Form):
        """Pagelet support for z3c.form.form.Form"""
        zope.interface.implements(z3c.pagelet.interfaces.IPageletForm)

        update = z3c.form.form.Form.update

class AddForm(z3c.pagelet.browser.BrowserPagelet, z3c.form.form.AddForm):
        """Pagelet support for z3c.form.form.AddForm"""
        zope.interface.implements(z3c.pagelet.interfaces.IPageletAddForm)

        update = z3c.form.form.AddForm.update

class EditForm(z3c.pagelet.browser.BrowserPagelet, z3c.form.form.EditForm):
        """Pagelet support for z3c.form.form.EditForm"""
        zope.interface.implements(z3c.pagelet.interfaces.IPageletEditForm)

        update = z3c.form.form.EditForm.update
