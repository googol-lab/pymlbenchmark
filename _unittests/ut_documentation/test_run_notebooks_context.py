# -*- coding: utf-8 -*-
"""
@brief      test log(time=8s)
"""
import os
import unittest
from pyquickhelper.loghelper import fLOG
from pyquickhelper.ipythonhelper import test_notebook_execution_coverage
from pyquickhelper.pycode import add_missing_development_version
import pymlbenchmark


class TestNotebookContext(unittest.TestCase):

    def setUp(self):
        add_missing_development_version(["jyquickhelper"], __file__, hide=True)

    def test_notebook_example_pyquickhelper(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        self.assertTrue(pymlbenchmark is not None)
        folder = os.path.join(os.path.dirname(__file__),
                              "..", "..", "_doc", "notebooks")
        test_notebook_execution_coverage(__file__, "context", folder,
                                         this_module_name="pymlbenchmark", fLOG=fLOG,
                                         copy_files=["README.txt"])


if __name__ == "__main__":
    unittest.main()
