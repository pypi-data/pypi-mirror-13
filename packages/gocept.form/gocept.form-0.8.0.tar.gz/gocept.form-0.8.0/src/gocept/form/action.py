# -*- coding: latin-1 -*-
# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: action.py 5829 2008-05-23 09:54:52Z zagy $
"""Additional actions."""

import sys
import xml.sax.saxutils

import zope.i18n
import zope.i18nmessageid
import zope.formlib.form
import zope.formlib.namedtemplate

class DestructiveAction(zope.formlib.form.Action):
    pass


@zope.formlib.namedtemplate.implementation(DestructiveAction)
def render_destructive_action(self):
    button = zope.formlib.form.render_submit_button(self)()
    if button == '':
        return ''

    # Extend the button with a check box that is synchronized with the
    # 'active' status of the button.

    additional = """
        <script type="text/javascript">
        document.getElementById('%s').disabled = true;
        </script>

        <label>
            <input
            type="checkbox" 
            id="%s" 
            onChange="document.getElementById('%s').disabled = !this.checked"/> Unlock &quot;%s&quot; button</label>

    """ % (self.__name__, self.__name__ + '.unlock', self.__name__, self.label)
    # XXX: the label should be translated.

    return button + additional


class destructive_action(zope.formlib.form.action):
    """Decorator to create destructive actions in form views."""

    def __call__(self, success):
        action = DestructiveAction(self.label, success=success, **self.options)
        self.actions.append(action)
        return action


class ConfirmAction(zope.formlib.form.Action):

    def __init__(self, label, confirm_message, **options):
        super(self.__class__, self).__init__(label, **options)
        self.confirm_message = confirm_message


@zope.formlib.namedtemplate.implementation(ConfirmAction)
def render_confirm_action(self):
    button = zope.formlib.form.render_submit_button(self)()
    if button == '':
        return ''

    # Extend the button with the confirmation.

    message = self.confirm_message
    if isinstance(message, zope.i18nmessageid.Message):
        message = zope.i18n.translate(message, context=self.form.request)

    additional = """
        <script type="text/javascript">
            function confirm_%(func_name)s(){
                var confirmed = confirm(%(message)s);
                if (confirmed)
                    return true;
                return false;
            }
            document.getElementById("%(name)s").onclick = confirm_%(func_name)s;
        </script>

    """ % dict(
        name=self.__name__,
        func_name=self.__name__.encode('base64')[:-3],
        message=xml.sax.saxutils.quoteattr(message))

    return button + additional


class confirm(object):
    """Decorator to create confirm actions in form views."""

    def __init__(self, label, actions=None, confirm_message=None, **options):
        if confirm_message is None:
            raise ValueError("No confirm message given.")
        caller_locals = sys._getframe(1).f_locals
        if actions is None:
            actions = caller_locals.get('actions')
        if actions is None:
            actions = caller_locals['actions'] = zope.formlib.form.Actions()
        self.actions = actions

        self.label = label
        self.options = options
        self.confirm_message = confirm_message

    def __call__(self, success):
        action = ConfirmAction(self.label, self.confirm_message,
                               success=success, **self.options)
        self.actions.append(action)
        return action

