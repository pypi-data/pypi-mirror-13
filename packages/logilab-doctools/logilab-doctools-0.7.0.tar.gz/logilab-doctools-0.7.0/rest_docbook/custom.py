# -*- coding: utf-8 -*-

"""
This module defines several customized directives or roles for the
documents written and processed at Logilab.
"""
from docutils import nodes, utils
from docutils.parsers.rst import directives
from docutils.parsers.rst.directives import register_directive
from docutils.parsers.rst.roles import register_canonical_role, set_classes
from docutils.parsers.rst import Directive
from docutils.parsers.rst.directives.admonitions import BaseAdmonition


### New Directive for the manual page / column breaks

class manual_break(nodes.Element):
    """
    New type of node that can be found inside the tree returned by the parser.

    The visitors must implement a enter / depart method for this node.
    """
    pass

class ManualBreak(Directive):
    """
    New directive inserting a manual break (page or column),
    typically for PDF output.
    """
    required_arguments = 0
    optional_arguments = 1
    option_spec = {'type': directives.unchanged # page or column
                  }
    has_content= False

    def run(self):
        # Builds a paragraph node and inserts the content of the node
        break_type = directives.choice(self.options.pop("type", "page"),
                                       ("page", "column") )
        node = manual_break(rawsource=self.content, breaktype=break_type,
                            **self.options)
        return[node]

# Registers the new directive class in the analyzer
register_directive('manual-break', ManualBreak)


### New Directive for the draft notes

class draft(nodes.Admonition, nodes.Element):
    """
    New type of node that can be found inside the tree returned by the parser.

    The visitors must implement a enter / depart method for this node.
    """
    pass

class Draft(BaseAdmonition):
    """
    New directive containing draft information.

    It is basically a new kind of admonition (note).
    """
    node_class = draft

# Registers the new directive class in the analyzer
register_directive('draft', Draft)


### New directives for elements that must be ignored.

class PassDirective(Directive):
    """
    Directive that does nothing.
    """
    required_arguments = 0
    optional_arguments = 0
    has_content= True
    def run(self):
        return []

# Registers the Sphinx-specific directive "toctree" in the analyzer
# As we don't use it, just does nothing when finding it.
register_directive('toctree', PassDirective)


### New text role for the cross references

class crossref(nodes.Inline, nodes.TextElement):
    """
    New type of node that can be found inside the tree returned by the parser.

    The visitors must implement a enter / depart method for this node.
    """
    pass

def build_crossref_role(role, rawtext, text, lineno, inliner,
                  options={}, content=[]):
    set_classes(options)
    return [crossref(rawtext, "", refid=utils.unescape(text),
                     **options)], []

register_canonical_role('crossref', build_crossref_role)


### Additional bibliographic field (inside docinfo node) for document reference

REFERENCE_FIELD_NAMES = (u"ref", u"reference", u"référence")
