import unittest
import numpy as np
from math import sqrt, cos, exp, pi
from ..full import matrix, init, unit, permute

class TestMatrix(unittest.TestCase):

    def test_diag(self):
        ref = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        this = matrix.diag([1,1,1])
        np.testing.assert_equal(this, ref)

    def test_str(self):
        M = matrix((2,2))
        M[0,0] = M[1,1] = 1
        this = str(M)
        ref = """
 (2, 2) 
              Column   1    Column   2
       1      1.00000000    0.00000000
       2      0.00000000    1.00000000
"""
        self.assertEqual(this, ref)

    def test_str2(self):
        M = matrix((6,6))
        for i in range(6):
            M[i, i] = float(i)
        this = str(M)
        ref = """
 (6, 6) 
              Column   1    Column   2    Column   3    Column   4    Column   5
       2      0.00000000    1.00000000    0.00000000    0.00000000    0.00000000
       3      0.00000000    0.00000000    2.00000000    0.00000000    0.00000000
       4      0.00000000    0.00000000    0.00000000    3.00000000    0.00000000
       5      0.00000000    0.00000000    0.00000000    0.00000000    4.00000000

              Column   6
       6      5.00000000
"""
        self.assertEqual(this, ref)

    def test_str3(self):
        M = matrix((2,2,2))
        M[0,0,0] = M[1,1,1] = 1
        this = str(M)
        ref = """
 (2, 2, 2) 
[0]
 (2, 2) 
              Column   1    Column   2
       1      1.00000000    0.00000000
[1]
 (2, 2) 
              Column   1    Column   2
       2      0.00000000    1.00000000
"""
        self.assertEqual(this, ref)

    def test_mul(self):
        M = matrix((2, 2))
        M[0, 0] = M[1, 1] = 2.0
        M[0, 1] = M[1, 0] = 1.0
        np.testing.assert_equal(M*M, [[5, 4], [4, 5]])

    def test_mul_scalar_matrix(self):
        M = matrix((2, 2))
        M[0, 0] = M[1, 1] = 2.0
        M[0, 1] = M[1, 0] = 1.0
        np.testing.assert_equal(2*M, [[4, 2], [2, 4]])

    def test_mul_matrix_scalar(self):
        M = matrix((2, 2))
        M[0, 0] = M[1, 1] = 2.0
        M[0, 1] = M[1, 0] = 1.0
        np.testing.assert_equal(M*2, [[4, 2], [2, 4]])

    def test_outer(self):
        V1 = matrix((2, )); V1[0]=1.0
        V2 = matrix((2, )); V2[1]=1.0
        V12 = V1.x(V2)
        np.testing.assert_equal(V12, [[0, 1], [0, 0]])

    def test_div_scalar(self):
        M = matrix((2, 2))
        M[0, 0] = 1; M[0, 1] = 2; M[1, 0] = 3; M[1, 1] = 4
        np.testing.assert_equal(M/2, [[0.5, 1.0], [1.5, 2.0]])

    def test_div_self(self):
        M = matrix((2, 2))
        M[0, 0] = 1; M[0, 1] = 2; M[1, 0] = 3; M[1, 1] = 4
        np.testing.assert_almost_equal(M/M, [[1.0, 0.0], [0.0, 1.0]])

    def test_neg(self):
        M = matrix((2, 2))
        M[0, 0] = 1; M[0, 1] = 2; M[1, 0] = 3; M[1, 1] = 4
        np.testing.assert_equal(-M, [[-1.0, -2.0], [-3.0, -4.0]])

    def test_and(self):
        M = matrix((2, 2))
        M[0, 0] = 1; M[0, 1] = 2; M[1, 0] = 3; M[1, 1] = 4
        np.testing.assert_equal(M&M, 30)

    def test_scatter(self):
        M = matrix((2, 2))
        M1 = matrix((3, 3))
        M[0, 0] = 1; M[0, 1] = 2; M[1, 0] = 3; M[1, 1] = 4
        M.scatter(M1, [0, 2], [0, 2]) 
        np.testing.assert_equal(M1, [[1, 0, 2], [0, 0, 0], [3, 0, 4]])

    def test_scatter_add(self):
        M = matrix((2, 2))
        M1 = matrix((3, 3)); M1[1, 1] = 5
        M[0, 0] = 1; M[0, 1] = 2; M[1, 0] = 3; M[1, 1] = 4
        M.scatteradd(M1, [0, 2], [0, 2]) 
        np.testing.assert_equal(M1, [[1, 0, 2], [0, 5, 0], [3, 0, 4]])

    def test_pack(self):
        M = matrix((2, 2))
        M1 = matrix((3, 3))
        M1[0, 0] = 1; M1[0, 2] = 2; M1[2, 0] = 3; M1[2, 2] = 4
        M1.packto(M, [0, 2], [0, 2]) 
        np.testing.assert_equal(M, [[1, 2], [3, 4]])

    def test_pack_rows(self):
        M = matrix((2, 3))
        M1 = matrix((3, 3))
        M1[0, 0] = 1; M1[0, 2] = 2; M1[2, 0] = 3; M1[2, 2] = 4
        M1.packto(M, rows=[0, 2])
        np.testing.assert_equal(M, [[1, 0, 2], [3, 0, 4]])

    def test_pack_columns(self):
        M = matrix((3, 2))
        M1 = matrix((3, 3))
        M1[0, 0] = 1; M1[0, 2] = 2; M1[2, 0] = 3; M1[2, 2] = 4
        M1.packto(M, columns=[0, 2])
        np.testing.assert_equal(M, [[1, 2], [0, 0], [3, 4]])

    def test_commute(self):
        z = init([[1, 0], [0, -1]])
        x = init([[0, 1], [1, 0]])
        np.testing.assert_equal(z^x, [[0, 2], [-2, 0]])

    def test_inv_init_none(self):
        M = init([[2, 1], [1, 2]])
        self.assertEqual(M._I, None)

    def test_inv(self):
        M = init([[3, 1], [1, -3]])
        M.inv()
        np.testing.assert_almost_equal(M._I, [[0.3, 0.1], [0.1, -0.3]])

    def test_rdiv(self):
        M = init([[3, 1], [1, -3]])
        np.testing.assert_almost_equal(1/M, [[0.3, 0.1], [0.1, -0.3]])

    def test_det(self):
        M = init([[3, 1], [1, -3]])
        self.assertAlmostEqual(M.det(), -10)

    def test_minor(self):
        M1 = matrix((3, 3))
        M1[0, 0] = 1; M1[0, 2] = 2; M1[2, 0] = 3; M1[2, 2] = 4
        np.testing.assert_equal(M1.minor(1, 1), [[1, 2], [3, 4]])

    def test_cofactor(self):
        M = init([[4, 1], [1, 3]])
        np.testing.assert_almost_equal(M.cofactor(), [[3., -1.], [-1., 4.]])

    def test_eig(self):
        M = init([[0, 1], [1, 0]])
        np.testing.assert_almost_equal(M.eig(), [-1., 1.])

    def test_eigvec(self):
        M = init([[0, 1], [1, 0]])
        np.testing.assert_almost_equal(sqrt(2)*M.eigvec()[1], [[-1., 1.],[1,1]])

    def test_qr_Q(self):
        A = init([[12, 6, -4], [-51, 167, 24], [4, -68, -41]])
        Q, R = A.qr()
        np.testing.assert_almost_equal(Q, 
            -init([[6./7, 3./7, -2./7], [-69./175, 158./175, 6./35], [-58./175, 6./175, -33./35]])
            )
    def test_qr_R(self):
        A = init([[12, 6, -4], [-51, 167, 24], [4, -68, -41]])
        Q, R = A.qr()
        np.testing.assert_almost_equal(R, 
            -init([[14, 0, 0], [21, 175, 0], [-14, -70, 35]])
            )
        np.testing.assert_almost_equal(A, Q*R)

    def test_normalize(self):
        v = init([1.0, 1.0])
        v.normalize()
        np.testing.assert_almost_equal(v, [sqrt(0.5), sqrt(0.5)])

    def test_normalize_with_overlap(self):
        v = init([1.0, 1.0])
        S = init([[1.0, 0.5], [0.5, 1.0]])
        v.normalize(S)
        np.testing.assert_almost_equal(v, [sqrt(1.0/3), sqrt(1.0/3)])

    def test_gram_schmidt(self):
        Delta = 0.1
        S = init([[1.0, Delta], [Delta, 1.0]])
        v = init([[1.0, 0.0], [0.0, 1.0]])
        u = v.GS(S)
        u_ref = init([[1.0, 0.0], [-Delta/sqrt(1-Delta**2), 1.0/sqrt(1-Delta**2)]])
        np.testing.assert_almost_equal(u, u_ref)

    def test_gram_schmidt_as_transformation(self):
        Delta = 0.1
        S = init([[1.0, Delta], [Delta, 1.0]])
        v = init([[1.0, 0.0], [0.0, 1.0]])
        T = v.GST(S)
        u = v*T
        u_ref = init([[1.0, 0.0], [-Delta/sqrt(1-Delta**2), 1.0/sqrt(1-Delta**2)]])
        np.testing.assert_almost_equal(u, u_ref)
        
    def test_sqrt(self):
        Delta = 0.1
        S = init([[1.0, Delta], [Delta, 1.0]])
        Sh = S.sqrt()
        np.testing.assert_almost_equal(Sh*Sh, S)

    def test_sqrtinv(self):
        Delta = 0.1
        S = init([[1.0, Delta], [Delta, 1.0]])
        Sih = S.invsqrt()
        np.testing.assert_almost_equal(Sih*Sih, S.I)

    def test_funcsqrt(self):
        Delta = 0.1
        S = init([[1.0, Delta], [Delta, 1.0]])
        Sh = S.func(sqrt)
        np.testing.assert_almost_equal(Sh*Sh, S)

    def test_exp(self):
        Delta = 0.1
        k = init([[Delta, 0.0], [0.0, -Delta]])
        exp_k = init([[exp(Delta), 0.0], [0.0, exp(-Delta)]])
        np.testing.assert_almost_equal(k.exp(), exp_k)

    def test_sym(self):
        A = init([[1, 2], [3, 4]])
        np.testing.assert_almost_equal(A.sym(), [[1, 2.5], [2.5, 4]])

    def test_asym(self):
        A = init([[1, 2], [3, 4]])
        np.testing.assert_almost_equal(A.antisym(), [[0, 0.5], [-0.5, 0]])

    def test_pack(self):
        from ..full import triangular
        A = init([[1, 2], [3, 4]])
        B = triangular.init([1, 2.5, 4])
        np.testing.assert_almost_equal(A.pack(), B)

    def test_lower(self):
        from ..full import triangular
        A = init([[1, 2], [3, 4]])
        B = triangular.init([1, 2, 4])
        np.testing.assert_almost_equal(A.lower(), B)

    def test_fold(self):
        from ..full import triangular
        A = init([[1, 2], [3, 4]])
        B = triangular.init([1, sqrt(2)*2, 4]) #???
        np.testing.assert_almost_equal(A.fold(), B)

    def test_norm2(self):
        A = init([3, 4])
        self.assertAlmostEqual(A.norm2(), 5.0) 

    def test_block(self):
        A = init([[1, 2], [3, 4]])
        B = A.block([1, 1], [1, 1])
        self.assertEqual(B.subblock[0], [1])
        self.assertEqual(B.subblock[1], [4])

    def test_subblocked(self):
        A = init([[1, 2], [3, 4]])
        B = A.subblocked([1, 1], [1, 1])
        self.assertEqual(B.subblock[0][1], [3])
        self.assertEqual(B.subblock[1][0], [2])

    def test_clear(self):
        A = init([[1, 2], [3, 4]])
        A.clear()
        np.testing.assert_equal(A, [[0, 0], [0, 0]])

    def test_cross(self):
        A = init([1, 2, 3])
        np.testing.assert_equal(A.cross(), [[0, -3, 2], [3, 0, -1], [-2, 1, 0]])

    def test_dist(self):
        A = init([0, 0, 1])
        np.testing.assert_almost_equal(A. dist([0, 1, 0]), sqrt(2))

    def test_angle3(self):
        pass
    
    def test_angle3d(self):
        pass

    def test_angle(self):
        A = init([0, 0, 1])
        B = init([0, 1, 0])
        np.testing.assert_almost_equal(A.angle(B), pi/2)

    def test_dihedral_open(self):
        A = init([1, 1, 0])
        B = init([1, 0, 0])
        C = init([0, 0, 0])
        D = init([0, -1, 0])
        np.testing.assert_equal(A.dihedral(B, C, D), pi)

    def test_dihedral_eclipsed(self):
        A = init([1, 1, 0])
        B = init([1, 0, 0])
        C = init([0, 0, 0])
        D = init([0, 1, 0])
        np.testing.assert_equal(A.dihedral(B, C, D), 0)

    def test_svd(self):
        A = init([[1, 1, sqrt(3)], [-1, -1, 0]])
        u, s, v = A.svd()
        np.testing.assert_almost_equal(A, u*s*v.T)

    def test_unit(self):
        I = init([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        np.testing.assert_almost_equal(unit(3), I)

    def test_unit2(self):
        I = init([[2, 0, 0], [0, 2, 0], [0, 0, 2]])
        np.testing.assert_almost_equal(unit(3, factor=2), I)

    def test_permute(self):
        np.testing.assert_equal(permute([0, 2], 4), 
            [[1, 0, 0, 0],
             [0, 0, 1, 0],
             [0, 1, 0, 0],
             [0, 0, 0, 1],])


if __name__ == "__main__":
    unittest.main()
