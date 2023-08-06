from logilab.common.testlib import TestCase,unittest_main

from logilab.doctools.rest_docbook import rest_dbk_transform
from lxml.etree import tostring


class SourceCodeTransformerTest(TestCase):

    def generic_test(self, rst, dbk):
        result = rest_dbk_transform(rst)
        res_string = ""
        for elt in result:
            res_string += tostring(elt)
        self.assertMultiLineEqual(res_string, dbk)

    def test_colorized_code(self):
        rst = u"""
Colorized code test.

.. code:: python

   class Number(object):
       def __init__(self, value):
           self.value = value

   obj = Number(12)

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Colorized code test.</para><programlisting xmlns:ldg="http://www.logilab.org/2005/DocGenerator" role="python"><phrase ldg:bold="true" ldg:color="#008800">class</phrase> <phrase ldg:bold="true" ldg:color="#BB0066">Number</phrase><phrase>(</phrase><phrase ldg:color="#007020">object</phrase><phrase>):</phrase>
    <phrase ldg:bold="true" ldg:color="#008800">def</phrase> <phrase ldg:bold="true" ldg:color="#0066BB">__init__</phrase><phrase>(</phrase><phrase ldg:color="#007020">self</phrase><phrase>,</phrase> <phrase>value</phrase><phrase>):</phrase>
        <phrase ldg:color="#007020">self</phrase><phrase ldg:color="#333333">.</phrase><phrase>value</phrase> <phrase ldg:color="#333333">=</phrase> <phrase>value</phrase>

<phrase>obj</phrase> <phrase ldg:color="#333333">=</phrase> <phrase>Number</phrase><phrase>(</phrase><phrase ldg:bold="true" ldg:color="#0000DD">12</phrase><phrase>)</phrase></programlisting><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_colorized_code_with_line_numbering(self):
        rst = u"""
Colorized code with line numbers test.

.. code:: python
   :number-lines:

   a = 2 * 3
   b = a + a

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Colorized code with line numbers test.</para><programlisting xmlns:ldg="http://www.logilab.org/2005/DocGenerator" role="python"><phrase>1 </phrase><phrase>a</phrase> <phrase ldg:color="#333333">=</phrase> <phrase ldg:bold="true" ldg:color="#0000DD">2</phrase> <phrase ldg:color="#333333">*</phrase> <phrase ldg:bold="true" ldg:color="#0000DD">3</phrase>
<phrase>2 </phrase><phrase>b</phrase> <phrase ldg:color="#333333">=</phrase> <phrase>a</phrase> <phrase ldg:color="#333333">+</phrase> <phrase>a</phrase></programlisting><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)


if __name__ == '__main__':
    unittest_main()
