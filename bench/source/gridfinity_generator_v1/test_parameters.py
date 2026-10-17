"""Parameter and mount-layout invariants without FreeCAD."""
import unittest
from parameters import validate

class Parameters(unittest.TestCase):
    def test_layouts(self):
        for columns in range(1,13):
            p=validate(dict(columns=columns))
            self.assertGreaterEqual(p['mount_width'],42*columns+4)
            self.assertGreaterEqual(len(p['mount_columns']),2)
            for x in p['mount_columns']:self.assertLessEqual(abs(x)+5,p['frame_width']/2+1e-8)
            for a,b in zip(p['mount_columns'],p['mount_columns'][1:]):
                self.assertLessEqual(b-a,76.200001)
                self.assertAlmostEqual((b-a)/25.4,round((b-a)/25.4))
            self.assertAlmostEqual(p['mount_columns'][0],-p['mount_columns'][-1])
    def test_bounds(self):
        for bad in [dict(columns=1.2),dict(rows=0),dict(columns=True),dict(columns=12,rows=12),dict(web=1),dict(angle=-31),dict(angle=6),dict(clearance=float('nan')),dict(typo=1)]:
            with self.assertRaises(ValueError):validate(bad)
        for angle in [-30,0,5]:self.assertEqual(validate(dict(angle=angle))['angle'],angle)

if __name__=='__main__':unittest.main()
