# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: base.py 5639 2008-03-27 09:59:57Z nilo $

import zope.app.container.interfaces

def apply_data_with_setattr(context, form_fields, data, adapters=None):
    """Applies data of a form to an object using setattr. Allows to adapt
    form fields to given interfaces."""

    if adapters is None:
        adapters = {}

    changed = False

    for form_field in form_fields:
        field = form_field.field

        name = form_field.__name__
        newvalue = data.get(name, form_field)  # using form_field as marker
        if newvalue is form_field:
            continue

        # Adapt context, if necessary
        interface = form_field.interface
        adapter = adapters.get(interface)
        if adapter is None:
            if interface is None:
                adapter = context
            else:
                adapter = interface(context)
            adapters[interface] = adapter

        setattr(adapter, name, newvalue)

    return changed


class Add(object):

    factory = None
    redirect_to_context_after_add = False

    def applyChanges(self, object, data):
        return apply_data_with_setattr(
            object, self.form_fields, data)

    def create(self, data):
        obj = self.factory()
        self.applyChanges(obj, data)
        return obj

    def add(self, object):
        chooser = zope.app.container.interfaces.INameChooser(self.context)
        name = chooser.chooseName(self.get_name(object), object)
        self.context[name] = object
        self._added_object = self.context[name]
        self._finished_add = True

    def nextURL(self):
        if self.redirect_to_context_after_add:
            target = self.context
        else:
            target = self._added_object

        return zope.component.getMultiAdapter(
            (target, self.request), name='absolute_url')()

    def get_name(self, object):
        return object.__class__.__name__



class Edit(object):

    redirect_to_parent_after_edit = True
    redirect_to_view = None
    new_context_interface = None

    def render(self):
        next_url = self.nextURL()
        if not self.errors and self.status and next_url is not None:
            self.notify(self.status)
            self.request.response.redirect(next_url)
            return ''
        return super(Edit, self).render()

    def notify(self, message):
        """hook to notify the user"""
        pass

    def nextURL(self):
        if (not self.redirect_to_parent_after_edit
            and not self.redirect_to_view
            and not self.new_context_interface):
            return None

        new_context = self.new_context()
        if self.redirect_to_parent_after_edit:
            new_context = new_context.__parent__

        view = ''
        if self.redirect_to_view:
            view = '/@@%s' % self.redirect_to_view

        return '%s%s' % (
            zope.component.getMultiAdapter(
                (new_context, self.request), name='absolute_url')(),
            view)

    def new_context(self):
        if self.new_context_interface:
            return self.new_context_interface(self.context)
        return self.context
