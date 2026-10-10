import unittest
import numpy as np
from fea_audit import wrench
class WrenchTests(unittest.TestCase):
 def test_force_and_moment_for_offset_grip(self):
  X=np.array([[0,0,0],[1,0,0],[0,1,0],[0,0,1],[1,1,1]],float);F=np.array([0,0,-50.]);P=np.array([150,70,50.]);f,M,c=wrench(X,F,P)
  np.testing.assert_allclose(f.sum(0),F,atol=1e-10)
  np.testing.assert_allclose(np.cross(X-c,f).sum(0),np.cross(P-c,F),atol=1e-8)
 def test_centre_force_has_no_couple(self):
  X=np.array([[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]],float);f,M,c=wrench(X,[30,0,0],X.mean(0));np.testing.assert_allclose(f,np.tile([5,0,0],(6,1)));np.testing.assert_allclose(M,0)
if __name__=='__main__':unittest.main()
