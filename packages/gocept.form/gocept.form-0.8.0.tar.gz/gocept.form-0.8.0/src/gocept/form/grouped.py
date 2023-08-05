import gocept.form.interfaces
import zope.formlib.form
import zope.formlib.interfaces
import zope.formlib.namedtemplate


grouped_form_template = zope.formlib.namedtemplate.NamedTemplateImplementation(
    zope.browserpage.ViewPageTemplateFile('grouped-form.pt'),
    zope.formlib.interfaces.IPageForm)


class Fields(object):

    zope.interface.implements(gocept.form.interfaces.IFieldGroup)

    # Use slots to make sure that nothing sets anything else on the group.
    __slots__ = ('title', 'fields', 'css_class')

    def __init__(self, title, fields, css_class=None):
        self.title = title
        self.fields = fields
        self.css_class = css_class

    def get_field_names(self):
        return self.fields


class RemainingFields(object):

    zope.interface.implements(gocept.form.interfaces.IRemainingFields)

    __slots__ = ('title', 'css_class')

    def __init__(self, title, css_class=None):
        self.title = title
        self.css_class = css_class

    def get_field_names(self):
        return None


class FormBase(object):
    """Baseclass for forms."""

    template = zope.formlib.namedtemplate.NamedTemplate('gocept.form.grouped')
    field_groups = None
    title = u''

    def setUpWidgets(self, ignore_request=False):
        self.adapters = {}
        self.widgets = None
        self.widget_groups = []
        remainder_group = None
        fields = []
        if self.field_groups is None:
            self.field_groups = []

        remainder_id = None
        for id, group in enumerate(self.field_groups):

            if gocept.form.interfaces.IRemainingFields.providedBy(group):
                widgets = None
                remainder_id = id
            else:
                field_names = group.get_field_names()
                # Select only form fields that actually exist
                form_field_names = [x.__name__ for x in self.form_fields]
                field_names = [x for x in field_names if x in
                               form_field_names]
                widgets = self._get_widgets(self.form_fields.select(
                    *field_names), ignore_request)
                if self.widgets is None:
                    self.widgets = widgets
                else:
                    self.widgets += widgets
                fields.extend(field_names)

                self.widget_groups.append(dict(
                    meta=group,
                    widgets=widgets))

        # we create a default widget_group which puts all the rest of the
        # fields in one group
        remaining_fields = self.form_fields.omit(*fields)
        if remaining_fields:
            widgets = self._get_widgets(remaining_fields, ignore_request)
            if remainder_id is None:
                remainder_group = RemainingFields(u'')
                self.field_groups = tuple(self.field_groups) + (
                    remainder_group,)
            else:
                remainder_group = self.field_groups[remainder_id]

            remainders = dict(
                meta=remainder_group,
                widgets=widgets)

            if remainder_id is None:
                self.widget_groups.append(remainders)
            else:
                self.widget_groups[remainder_id:remainder_id] = [remainders]

            if self.widgets is None:
                self.widgets = widgets
            else:
                self.widgets += widgets


class Form(FormBase, zope.formlib.form.Form):
    """Edit form base."""

    def _get_widgets(self, form_fields, ignore_request):
        return zope.formlib.form.setUpWidgets(
            form_fields, self.prefix, self.context, self.request,
            adapters=self.adapters, ignore_request=ignore_request)


class AddForm(FormBase, zope.formlib.form.AddForm):
    """Add form base."""

    def _get_widgets(self, form_fields, ignore_request):
        return zope.formlib.form.setUpInputWidgets(
            form_fields, self.prefix, self.context, self.request,
            ignore_request=ignore_request)

class EditForm(FormBase, zope.formlib.form.EditForm):
    """Edit form base."""

    def _get_widgets(self, form_fields, ignore_request):
        return zope.formlib.form.setUpEditWidgets(
            form_fields, self.prefix, self.context, self.request,
            adapters=self.adapters, ignore_request=ignore_request)


class DisplayForm(FormBase, zope.formlib.form.PageDisplayForm):
    """Display form base."""

    def _get_widgets(self, form_fields, ignore_request):
        return zope.formlib.form.setUpEditWidgets(
            form_fields, self.prefix, self.context, self.request,
            adapters=self.adapters, for_display=True,
            ignore_request=ignore_request)
