from operator import is_
from reportlab.lib.textsplit import is_multi_byte
try:
    import numpy as np
    has_np = True
    from numpy import cos, pi
except:
    has_np = False
    from math import cos, pi


def interp_cosine(y1, y2, t):
    '''Smooth interpolation weighted by t from 0 to 1.'''
    t2 = (1. - cos(t*pi)) / 2.
    return y1*(1.-t2) + y2 * t2

def interp_cosine_many(y1, y2, t):
    '''For two python lists.'''
    t2 = (1. - cos(t*pi)) / 2.
    return [a*(1.-t2) + b * t2 for a,b in zip(y1,y2)]

def interp_linear(y1, y2, t):
    '''Return linear interpolation weighted by t from 0 to 1.'''
    return y1*(1.-t) + y2*t

def interp_linear_many(y1, y2, t):
    '''For two python lists.'''
    return [a*(1.-t) + b*t for a,b in zip(y1,y2)]

def interp_none(y1, *args):
    '''No interpolation defaults to lower bound.'''
    return y1

def interp_none_many(y1, *args):
    return y1

def load(data):
    '''Return new lut from JSON filename or dict.'''
    if type(data) == str:
        return Lut.loadf(data)

    return Lut.load(data)

class Lut(object):
    '''
    Lut is a multi-component interpolating lookup table.
    If a table is not built, then each lookup will interpolate.
    Numpy is used if available.
    '''
    
    def __init__(self, method='linear', size=0):
        '''
        Parameters
        ----------
        method : str
            None, 'cosine', or 'linear'
            No interpolation uses the lower bracketing bound.
        size : int
            Build table of this size for speed, otherwise compute
            interpolation for each lookup.
        '''
        self.range = (0., 1.)
        self.size = size
        self.method = method
        self.pts = [] # [[x, y, ...], ...]
        self.table = []

    def add(self, x, *ys):
        '''Add control point x, y1, ..., yn '''
        p = [x] + list(ys)
        if has_np:
            p = np.array(p)
            
        # First.
        if not self.pts:
            self.pts = [p]
            return
        
        # In the middle.
        npts = len(self.pts)
        for i in range(npts):
            if x <= self.pts[i][0]:
                self.pts.insert(i, p)
                return
            
        # Last.
        self.pts.append(p)
        
    def build(self):
        '''Build the lookup table entries.'''
        if not self.size or not self.pts:
            return

        npts = len(self.pts)
        ncol = len(self.pts[0]) - 1
        
        # Create new clear table.
        if has_np:
            self.table = np.zeros((self.size+1, ncol))
        else:
            self.table = [[0]*ncol for _ in range(self.size+1)]
        
        self.table[-1] = self.pts[-1][1:]
        
        # Iterate control points.    
        interp = self.get_interp_function()
        for pUpper in range(1, npts):
            pLower = pUpper - 1
            tLower = int(self.pts[pLower][0] * self.size)
            tUpper = int(self.pts[pUpper][0] * self.size)
            
            # Interp between control point neighbors.
            for t in range(tLower, tUpper):
                w = 1. * (t - tLower) / (tUpper - tLower)
                self.table[t] = interp(self.pts[pLower][1:],
                                       self.pts[pUpper][1:],
                                       w)
            
    def get(self, x):
        '''Return interpolated value(s) at x.'''
        if self.size:
            return self.lookup(x)
        else:
            return self.interp(x)
    
    def get_interp_function(self):
        '''Return interpolation function: f(y1, y2, weight).'''
        if 'linear' == self.method:
            interp = 'interp_linear'
        elif 'cosine' == self.method:
            interp = 'interp_cosine'
        elif self.method is None:
            interp = 'interp_none'
        else:
            msg = 'Uknown interpolation method={0}'
            raise Exception(msg.format(self.method))
        
        if not has_np and len(self.pts[0]) > 2:
            interp += '_many'
        
        return eval(interp)
    
    def interp(self, x):
        '''Interpolate control points at x.'''
        is_multi_comp = len(self.pts[0]) > 2
        
        # Outside bounds?
        if x <= self.range[0]:
            if is_multi_comp:
                return self.pts[0][1:]
            else:
                return self.pts[0][1]
        elif x >= self.range[1]:
            if is_multi_comp:
                return self.pts[-1][1:]
            else:
                return self.pts[-1][1]
        
        xi = (1. * x - self.range[0]) / (self.range[1] - self.range[0])
        npts = len(self.pts)
        
        # Find lower bound.
        for i in range(1, npts):
            if xi <= self.pts[i][0]:
                break

        # No interp?
        if not self.method:
            if is_multi_comp:
                return self.pts[i-1][1:]
            else:
                return self.pts[i-1][1]
            
        w = (xi - self.pts[i-1][0]) / (self.pts[i][0] - self.pts[i-1][0])
          
        if is_multi_comp: 
            lower = self.pts[i-1][1:]
            upper = self.pts[i][1:]
        else:
            lower = self.pts[i-1][1]
            upper = self.pts[i][1]

        interp = self.get_interp_function()            
        return interp(lower, upper, w)
        
    @staticmethod
    def load(js):
        '''Build new lut from dict.'''
        r = Lut()
        r.interp = js.get('method', 'linear')
        r.range = js.get('range', (0., 1.))
        r.size = js.get('size', 0)
        
        table = js.get('table', [])
        for row in table:
            r.add(*row)
            
        r.build()
        
        return r
    
    @staticmethod
    def loadf(filename):
        '''Build new lut from JSON filename.'''
        import json
        with open(filename) as f:
            js = json.load(f)
        
        return Lut.load(js)

    def lookup(self, x):
        '''Lookup x value or array in built table.'''
        if hasattr(x, '__len__'):
            return self.lookup_many(x)
        else:
            return self.lookup_single(x)
        
    def lookup_single(self, x):
        '''Lookup one value in built table.'''
        is_multi_comp = len(self.pts[0]) > 2
        
        # Outside bounds?
        if x <= self.range[0]:
            if is_multi_comp:
                return self.pts[0][1:]
            else:
                return self.pts[0][1]
        elif x >= self.range[1]:
            if is_multi_comp:
                return self.pts[-1][1:]
            else:
                return self.pts[-1][1]
        
        numer = x - self.range[0]
        rng = self.range[1] - self.range[0]
        idx = int(1. * self.size * numer / rng)
        res = self.table[idx]
        
        if is_multi_comp:
            return res
        else:
            return res[0]

    def lookup_many(self, x):
        '''Lookup array x in built table.'''
        if has_np:
            if type(x) != np.ndarray:
                x = np.array(x)

            numer = x - self.range[0]
            rng = self.range[1] - self.range[0]
            idx = 1. * self.size * numer / rng
            clipped = np.clip(idx, 0, self.size).astype(np.int)
            results = self.table[clipped]
            
            if len(self.pts[0]) > 2:
                return results
            else:
                return results[:,0]
        else:
            return [self.lookup_single(xi) for xi in x]


#     LICENSE BEGIN
# 
#     lut - A Python interpolating lookup table.
#     Copyright (C) 2016  Remik Ziemlinski
# 
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
#     LICENSE END
