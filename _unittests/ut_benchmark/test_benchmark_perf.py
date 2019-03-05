# -*- coding: utf-8 -*-
"""
@brief      test log(time=2s)
"""
import io
import contextlib
import sys
import os
import unittest
import numpy
from pyquickhelper.pycode import ExtTestCase


try:
    import src
except ImportError:
    path = os.path.normpath(
        os.path.abspath(
            os.path.join(
                os.path.split(__file__)[0],
                "..",
                "..")))
    if path not in sys.path:
        sys.path.append(path)
    import src


from src.pymlbenchmark.benchmark import BenchPerf, BenchPerfTest
from src.pymlbenchmark.datasets import random_binary_classification


class TestBenchPerf(ExtTestCase):

    def test_filter_conf(self):
        pbefore = dict(a=[0, 1], b=['a', 'b', 'c'])
        bp = BenchPerf(pbefore, None, None)
        opts = list(bp.enumerate_tests(pbefore))
        self.assertEqual(len(opts), 6)
        self.assertEqual(opts, [{'a': 0, 'b': 'a'}, {'a': 0, 'b': 'b'},
                                {'a': 0, 'b': 'c'}, {'a': 1, 'b': 'a'},
                                {'a': 1, 'b': 'b'}, {'a': 1, 'b': 'c'}])

    def test_perf_benchmark_vfalse(self):
        self.do_test_perf_benchmark(False)

    def test_perf_benchmark_vtrue(self):
        st = io.StringIO()
        with contextlib.redirect_stdout(st):
            with contextlib.redirect_stderr(st):
                self.do_test_perf_benchmark(True)
        self.assertIn("/24", st.getvalue())

    def do_test_perf_benchmark(self, verbose):

        class dummycl:
            def __init__(self, alpha):
                self.alpha = alpha

            def fit(self, X, y):
                self.mean_ = X.mean(axis=0)  # pylint: disable=W0201
                return self

            def predict(self, X):
                return self.predict_proba(X) > 0

            def predict_proba(self, X):
                return numpy.sum(X - self.mean_[numpy.newaxis, :], axis=1) * self.alpha

        class dummycl2(dummycl):
            def predict_proba(self, X):
                r = dummycl.predict_proba(self, X)
                return dummycl.predict_proba(self, X) + r

        class myBenchPerfTest(BenchPerfTest):
            def __init__(self, N=10, dim=4, alpha=3):
                BenchPerfTest.__init__(self)
                X, y = random_binary_classification(N, dim)
                self.skl = dummycl(alpha).fit(X, y)
                self.ort = dummycl2(alpha).fit(X, y)

            def fcts(self, **kwargs):

                def predict_skl_predict(X, model=self.skl):
                    return model.predict(X)

                def predict_skl_predict_proba(X, model=self.skl):
                    return model.predict_proba(X)

                def predict_ort_predict(X, model=self.ort):
                    return model.predict(X)

                def predict_ort_predict_proba(X, model=self.ort):
                    return model.predict_proba(X)

                return [{'lib': 'skl', 'method': 'predict', 'fct': predict_skl_predict},
                        {'lib': 'skl', 'method': 'predict_proba',
                            'fct': predict_skl_predict_proba},
                        {'lib': 'ort', 'method': 'predict',
                            'fct': predict_ort_predict},
                        {'lib': 'ort', 'method': 'predict_proba', 'fct': predict_ort_predict_proba}]

            def data(self, N=10, dim=4, **kwargs):  # pylint: disable=W0221
                return random_binary_classification(N, dim)[:1]

        pbefore = dict(alpha=[0, 1, 2], dim=[1, 10])
        pafter = dict(method=["predict", "predict_proba"],
                      N=[1, 10])
        bp = BenchPerf(pbefore, pafter, myBenchPerfTest)
        res = list(bp.enumerate_run_benchs(verbose=verbose))
        self.assertEqual(len(res), 96)
        self.assertLesser(res[0]['min'], res[0]['max'])
        self.assertEqual(set(_['N'] for _ in res), {1, 10})


if __name__ == "__main__":
    unittest.main()
