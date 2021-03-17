import math
from random import randint
import pprint

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

    def intersect(self, range):
        return False
    
    def inside(self, range):
        return False 


segments = [Interval(-6, -5, 'both'), Interval(-2, 1, 'both'), Interval(0, 2, 'both'), Interval(3, 6, 'both'), ]
## one dimensional segment tree
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


sorted_ele_segments= sorted(elementary_segments, key=lambda seg: seg.left)


sorted_ele_segments= sorted(elementary_segments, key=lambda seg: seg.left)
print(sorted_ele_segments)
print(len(sorted_ele_segments))