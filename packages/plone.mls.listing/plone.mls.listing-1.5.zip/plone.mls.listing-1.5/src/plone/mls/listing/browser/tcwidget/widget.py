# -*- coding: utf-8 -*-
"""Terms & Conditions Widget Implementation"""

# zope imports
from plone import api
from z3c.form import term
from z3c.form.browser.checkbox import CheckBoxWidget
from z3c.form.interfaces import (
    IFieldWidget,
    IFormLayer,
)
from z3c.form.widget import FieldWidget
from zope.interface import (
    implementer,
    implementer_only,
)
from zope.schema import vocabulary
from zope.schema.interfaces import IBool
from zope.component import adapter

# local imports
from plone.mls.listing.browser.tcwidget.interfaces import ITCWidget


@implementer_only(ITCWidget)
class TCWidget(CheckBoxWidget):
    """Single Input type checkbox widget implementation."""

    klass = u'terms-conditions-widget'
    target = None

    def updateTerms(self):
        if self.terms is None:
            self.terms = term.Terms()
            self.terms.terms = vocabulary.SimpleVocabulary((
                vocabulary.SimpleTerm('selected', 'selected',
                                      self.label or self.field.title), ))
        return self.terms

    def tc_link(self):
        if not self.target:
            return

        portal = api.portal.get()
        path = str(self.target)
        if path.startswith('/'):
            path = path[1:]
        item = portal.restrictedTraverse(path, default=False)
        if not item:
            return
        return {
            'label': item.title,
            'url': item.absolute_url(),
        }


@adapter(IBool, IFormLayer)
@implementer(IFieldWidget)
def TCFieldWidget(field, request):
    """IFieldWidget factory for TCWidget."""
    widget = FieldWidget(field, TCWidget(request))
    # widget.label = u''  # don't show the label twice
    return widget
