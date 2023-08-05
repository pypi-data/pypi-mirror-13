===========
gocept.form
===========

`gocept.form` provides some extended functionality for zope.formlib and
z3c.form. To use the package with formlib support, require it using
``gocept.form[formlib]``. To use the package with z3c.form support, require it
using ``gocept.form[z3cform]``.

Destructive Actions
===================

Destructive actions allow marking actions that can potentially cause harm.
Those actions will be rendered as buttons and - on JavaScript-capable
platforms - be disabled by default. Additionally a checkbox is rendered that
allows enabling the corresponding button.


Grouped Fields
==============

gocept.form.grouped provides a very low-tech way of grouping schema fields
into field sets. The styling is applied only via CSS.


Base Add and Edit forms
=======================
gocept.form.base.Add and gocept.form.base.Edit providing some common code
to make implementing basic forms more convenient.
