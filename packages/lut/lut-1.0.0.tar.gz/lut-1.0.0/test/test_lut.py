import lut
import unittest

try: 
    import numpy as np
    has_np = True
except:
    has_np = False
    

class TestLut(unittest.TestCase):
    def test_add(self):
        t = lut.Lut()
        t.add(.5, .05, 3)
        t.add(0,  0,   1)
        t.add(.2, .02, 2)
        t.add(1,  1,   4)

        expect = [[0,0,1], [.2,.02,2], [.5,.05,3], [1,1,4]] 
        if has_np:
            r = np.all(np.array(expect) == t.pts)
            self.assertTrue(r)
        else:       
            self.assertEqual(expect, t.pts)
 
    def test_build(self):
        size = 100
        t = lut.Lut(size=size)
        t.add(.5, .05, 3)
        t.add(0,  0,   1)
        t.add(.2, .02, 2)
        t.add(1,  1,   4)
        t.build()
        
        self.assertTrue(len(t.table) >= size)
        
        for i in range(1, size):
            self.assertEqual(2, len(t.table[i]))
            self.assertTrue(t.table[i-1][0] <= t.table[i][0])
 
    def test_interp_cosine(self):        
        t = lut.Lut(method='cosine')
        t.add(0, 0)
        t.add(1, 1)
        
        self.assertEqual(0, t.interp(0))
        self.assertAlmostEqual(.146, t.interp(.25), places=3)
        self.assertEqual(1, t.interp(1))
 
    def test_interp_cosine_many(self):        
        t = lut.Lut(method='cosine')
        t.add(0, 0, 0)
        t.add(1, 1, 10)
        
        if has_np:
            self.assertTrue(np.all([0, 0] == t.interp(0)))
            self.assertTrue(np.all([1, 10] == t.interp(1)))
        else:
            self.assertEqual([0, 0], t.interp(0))
            self.assertEqual([1, 10], t.interp(1))
 
    def test_interp_linear(self):        
        t = lut.Lut(method='linear')
        t.add(0, 0)
        t.add(1, 1)
        
        self.assertEqual(0, t.interp(0))
        self.assertEqual(.5, t.interp(.5))
        self.assertEqual(1, t.interp(1))
 
    def test_interp_linear_many(self):        
        t = lut.Lut(method='linear')
        t.add(0, 0, 0)
        t.add(1, 1, 10)
        
        if has_np:
            self.assertTrue(np.all([0, 0] == t.interp(0)))
            self.assertTrue(np.all([.5, 5] == t.interp(.5)))
            self.assertTrue(np.all([1, 10] == t.interp(1)))
        else:
            self.assertEqual([0, 0], t.interp(0))
            self.assertEqual([.5, 5], t.interp(.5))
            self.assertEqual([1, 10], t.interp(1))
 
    def test_interp_none(self):        
        t = lut.Lut(method=None)
        t.add(0, 0)
        t.add(1, 1)
        
        self.assertEqual(0, t.interp(0))
        self.assertEqual(0, t.interp(.5))
        self.assertEqual(1, t.interp(1))
 
    def test_interp_none_many(self):        
        t = lut.Lut(method=None)
        t.add(0, 0, 0)
        t.add(1, 1, 1)
        
        if has_np:
            self.assertTrue(np.all([0,0] == t.interp(0)))
            self.assertTrue(np.all([0,0] == t.interp(.5)))
            self.assertTrue(np.all([1,1] == t.interp(1)))
        else:
            self.assertEqual([0,0], t.interp(0))
            self.assertEqual([0,0], t.interp(.5))
            self.assertEqual([1,1], t.interp(1))
 
    def test_lookup_single(self):
        t = lut.Lut(size=100)
        t.add(0, 0)
        t.add(1, 1)
        t.build()
        
        self.assertEqual(0,  t.lookup(0))
        self.assertEqual(.5, t.lookup(.5))
        self.assertEqual(1,  t.lookup(1))
 
    def test_lookup_many(self):
        t = lut.Lut(size=100)
        t.add(0, 0)
        t.add(1, 1)
        t.build()

        if has_np:
            values = t.lookup([0, .5, 1])
            res = np.all([0, .5, 1] == values) 
            self.assertTrue(res)
        else:
            self.assertEqual([0, .5, 1],  t.lookup([0, .5, 1]))
 
    def test_load(self):
        d = {
            "range": [10, 20],
            "size": 100,
            "table": [
                [0,   150],
                [0.5, 200],
                [1,   234]
            ]
        }
        
        t = lut.load(d)
        
        self.assertTrue(100 <= t.size)
        self.assertEqual([10, 20], t.range)
        self.assertEqual(234, t.get(20))
 
    def test_loadf(self):
        s = '''{
            "range": [10, 20],
            "size": 100,
            "table": [
                [0,   150],
                [0.5, 200],
                [1,   234]
            ]
        }'''
        
        fn = 'tmp.json'
        with open(fn, 'w') as f:
            f.write(s)
        
        t = lut.load(fn)
        
        self.assertTrue(100 <= t.size)
        self.assertEqual([10, 20], t.range)
        self.assertEqual(234, t.get(20))
 
        import os
        if os.path.exists(fn):
            os.remove(fn)

 
if '__main__' == __name__:
    unittest.main(verbosity=2)