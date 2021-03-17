from numbers import Number
import math
from random import randint
import pprint

class Node:
    left = None
    right = None
    value = None

    def __init__(self, value=None):
        self.value = value
        self.left = None
        self.right = None
    
    def is_leaf(self):
        return self.left is None and self.right is None

    def __str__(self, level=0):
        ret = '\t'*level+repr(self.value)+'\n'
        if not self.is_leaf():
            ret += '{}'.format(self.right.__str__(level+1))
            ret += '{}'.format(self.left.__str__(level+1))
            return ret
        return ret
    
    def __repr__(self):
        return '{}'.format(self.value)


# rework on interval class to represent mathematical intervals
class Interval:
    left = None
    right = None

    def __init__(self, left=0, right=0, closed='neither' ):
        _closed_types = {'right', 'left', 'both', 'neither'}
        if closed not in _closed_types:
            raise ValueError('invalid type')

        self.left = left
        self.right = right
        self.closed = closed
    def __repr__(self):
        interval = F"{self.left},{self.right}"
        if self.closed == 'both':
            return F"[{interval}]"
        if self.closed == 'neither':
            return F"]{interval}[ " 
        if self.closed == 'left':
            return F"[{interval}[ " 
        if self.closed == 'right':
            return F"]{interval}]" 
        return interval 
    
    def __contains__(self, value=0):
        if not isinstance(value, Interval) and not isinstance(value, Number):
            raise ValueError('comparing between two distinct types')
        if isinstance(value, Interval):
            return True 

        return self.closed == 'both' and self.left <= value <= self.right or \
                self.closed == 'neither' and self.left < value < self.right or \
                self.closed == 'left' and self.left <= value < self.right or \
                self.closed == 'right' and self.left < value <= self.right

    def intersect(self, range):
        return False
    
    def inside(self, range):
        return False 


## one dimensional segment tree
def build_elementary_segments(segments=[Interval]):
    ordered_segments = sorted(segments, key=lambda seg: seg.left)
    elementary_segments = set() 
    for index, segment in enumerate(ordered_segments):
        # return a list of elementary segments    
        # ] -inf, first[ ; [first, first] ... so on
        if index == 0:
            elementary_segments.add(Interval(-math.inf, segment.left, 'neither'))
        elif index == len(ordered_segments) - 1:
            previous_segment = ordered_segments[index-1]
            elementary_segments.add(Interval(previous_segment.right, segment.left,  'neither'))
            elementary_segments.add(Interval(segment.right,math.inf, 'neither'))
        else:
            previous_segment = ordered_segments[index-1]
            elementary_segments.add(Interval(previous_segment.right, segment.left,  'neither'))
            
        elementary_segments.add(Interval(segment.left, segment.left, 'both'))
        elementary_segments.add(Interval(segment.left, segment.right, 'neither'))
        elementary_segments.add(Interval(segment.right, segment.right, 'both'))
    return elementary_segments

segments = [Interval(-6, -5, 'both'), Interval(-2, 1, 'both'), Interval(0, 2, 'both'), Interval(3, 6, 'both'), ]
elementary_segments = build_elementary_segments(segments)
sorted_ele_segments= sorted(elementary_segments, key=lambda seg: seg.left)

#TODO - Intervals operations that going to be used: in, union, intersect
#TODO - build tree

sorted_ele_segments= sorted(elementary_segments, key=lambda seg: seg.left)
print(sorted_ele_segments)
print(len(sorted_ele_segments))