import unittest
import numpy as np
from ..full import triangular

class TestTriangular(unittest.TestCase):

    def setUp(self):
        self.twodim = triangular.init([1.,  2.,  3.])

    def test_init_square_shape(self):
        self.assertEqual(self.twodim.sshape, (2, 2))

    def test_init_values(self):
        np.testing.assert_equal(self.twodim, [1., 2., 3.])

    def test_str(self):
        self.assertEqual(str(self.twodim), """
    1.00000000
    2.00000000    3.00000000
"""
        )

    def test_getitem_by_tuple(self):
        self.assertEqual(self.twodim[0, 0], 1.)
        self.assertEqual(self.twodim[1, 0], 2.)
        self.assertEqual(self.twodim[0, 1], 2.)
        self.assertEqual(self.twodim[1, 1], 3.)

    def test_getitem_by_scalar(self):
        self.assertEqual(self.twodim[0], 1.)
        self.assertEqual(self.twodim[1], 2.)
        self.assertEqual(self.twodim[2], 3.)

    def test_setitem(self):
        self.twodim[0, 1] = 4.
        np.testing.assert_equal(self.twodim, [1., 4., 3.])

    def test_unpack(self):
        np.testing.assert_equal(self.twodim.unpack(), [[1., 2.], [2., 3.]])

    def test_mul(self):
        np.testing.assert_equal(self.twodim*self.twodim, [[5., 8.], [8., 13.]])

if __name__ == "__main__":
    unittest.main()
