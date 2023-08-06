from logilab.common.testlib import TestCase,unittest_main

from logilab.doctools.rest_docbook import rest_dbk_transform
from lxml.etree import tostring


class CustomTransformerTest(TestCase):

    def generic_test(self, rst, dbk):
        result = rest_dbk_transform(rst)
        res_string = ""
        for elt in result:
            res_string += tostring(elt)
        self.assertMultiLineEqual(res_string, dbk)

    def test_draft(self):
        rst = u"""
Draft test.

.. draft::

   This is a paragraph in the draft section.

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Draft test.</para><ldg:draft xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><para>This is a paragraph in the draft section.</para></ldg:draft><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_crossref(self):
        rst = u"""
Crossref test.

This is a paragraph containing a crossref towards an external
identifier: :crossref:`identifier`.

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Crossref test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a paragraph containing a crossref towards an external identifier: <xref linkend="identifier"/>.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_manual_break(self):
        rst = u"""
Manual break test.

.. manual-break::

This is a paragraph after a page break.

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Manual break test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator" ldg:break="page">This is a paragraph after a page break.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_manual_page_break(self):
        rst = u"""
Manual page break test.

.. manual-break::
   :type: page

This is a paragraph after a page break.

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Manual page break test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator" ldg:break="page">This is a paragraph after a page break.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_manual_column_break(self):
        rst = u"""
Manual column break test.

.. manual-break::
   :type: column

This is a paragraph after a column break.

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Manual column break test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator" ldg:break="column">This is a paragraph after a column break.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

if __name__ == '__main__':
    unittest_main()
