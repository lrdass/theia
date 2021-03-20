import math
from math import floor, log2
from queue import Queue
from pprint import pprint
from numbers import Number
from random import randint

NEITHER = 'neither'
BOTH = 'both'
LEFT = 'left'
RIGHT = 'right'


class Node:
    merged = False
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
        return 'Node {}'.format(self.value)


# rework on interval class to represent mathematical intervals
class Interval:
    left = None
    right = None

    def __init__(self, left=0, right=0, closed='neither'):
        _closed_types = {'right', 'left', 'both', 'neither'}
        if closed not in _closed_types:
            raise ValueError('invalid type')

        if left > right or right < left:
            swp = left
            left = right 
            right = swp

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
            # TODO - check if an interval is cotained by another
            return True

        return self.closed == 'both' and self.left <= value <= self.right or        \
            self.closed == 'neither' and self.left < value < self.right or          \
            self.closed == 'left' and self.left <= value < self.right or            \
            self.closed == 'right' and self.left < value <= self.right

    def union(self, target):
        ## fix union, left bounded values are wrong!
        ## fix union !! is too damn wrong!!! 
        self.merged = True
        left, right, = None, None
        closed_info = {'left': None, 'right': None}
        if self.left < target.left:
            left = self.left
            closed_info['left'] = self.closed
        elif self.left == target.left:
            left = self.left
            closed_info['left'] = 'left' if self.closed in ['left', 'both'] or target.closed in ['left', 'both'] \
                else 'neither'
        else:
            left = target.left
            closed_info['left'] = target.closed

        if self.right > target.right:
            right = self.right
            closed_info['right'] = self.closed
        elif self.right == target.right:
            right = self.right
            closed_info['right'] = 'right' if self.closed in ['right', 'both'] or target.closed in ['right', 'both'] \
                else 'neither'
        else:
            right = target.right
            closed_info['right'] = target.closed

        closed = 'neither' if closed_info['left'] == 'neither' and closed_info['right'] == 'neither'                    \
            else 'right' if closed_info['left'] in ['right', 'neither'] and closed_info['right'] in ['right', 'both']   \
            else 'left' if closed_info['right'] in ['left', 'neither'] and closed_info['left'] in ['left', 'both']      \
            else 'both'

        return Interval(left, right, closed)

    def intersect(self, range):
        return False

    def inside(self, range):
        return False


# one dimensional segment tree
def build_elementary_segments(segments=[Interval]):
    ## there is a bug here : generating segment ]1,0[ 
    ordered_segments = sorted(segments, key=lambda seg: seg.left)
    elementary_segments = Queue()
    
    for index, segment in enumerate(ordered_segments):
        if index == 0:
            elementary_segments.put(Interval(-math.inf, segment.left, 'neither'))
            elementary_segments.put(Interval(segment.left, segment.left, 'both'))
            elementary_segments.put(Interval(segment.left, segment.right, 'neither'))
            elementary_segments.put(Interval(segment.right, segment.right, 'both'))
        elif index == len(ordered_segments) -1:
            previous_segment=ordered_segments[index-1] 
            elementary_segments.put(Interval(previous_segment.right, segment.left, 'neither'))
            elementary_segments.put(Interval(segment.left, segment.left, 'both'))
            elementary_segments.put(Interval(segment.left, segment.right, 'neither'))
            elementary_segments.put(Interval(segment.right, segment.right, 'both'))
            elementary_segments.put(Interval(segment.right, math.inf, 'neither'))
            break
        else:
            previous_segment = ordered_segments[index-1]
            elementary_segments.put(Interval(previous_segment.right, segment.left, 'neither'))
            elementary_segments.put(Interval(segment.left, segment.left, 'both'))
            elementary_segments.put(Interval(segment.left, segment.right, 'neither'))
            elementary_segments.put(Interval(segment.right, segment.right, 'both'))

    return elementary_segments
        
        

def build_segments_queue_nodes(elementary_segments_queue=()):
    queue = Queue()
    while not elementary_segments.empty():
        seg = elementary_segments.get()
        node = Node(seg)
        queue.put(node)
    return queue

     
    # build a fifo with all the segments
    # unite elementary intervals until len(fifo) is 2**k
    # until fifo is empty
 
def build_1d_segment_tree(segments_queue=Queue()):
    segments_queue = build_segments_queue_nodes(segments_queue)
    min_fifo_len = floor(log2(len(segments_queue.queue))) 
    # is it safe to assume that this will only happen before going through all the leafs?
    while not len(segments_queue.queue) == 2 ** min_fifo_len:
        current_index = 0
        current = segments_queue.get()
        if not current.merged:
            next_element = segments_queue.get()
            union_node = Node(current.value.union(next_element.value))
            segments_queue.queue.insert(current_index, union_node)
            current_index += 1
            
    
    element =  None
    while not segments_queue.empty():
        element = segments_queue.get()
        next_element = segments_queue.get()
        if not next_element:
            break
        else:
            next_node = Node(element.value.union(next_element.value))
            next_node.left = element
            next_node.right = next_node
            segments_queue.put(next_node)
    return element


            


segments = [Interval(-6, -5, 'both'), Interval(-2, 1, 'both'),
            Interval(0, 2, 'both'), Interval(3, 6, 'both'), ]
elementary_segments = build_elementary_segments(segments)

pprint(build_1d_segment_tree(elementary_segments))


# TODO - Intervals operations that going to be used: in, union, intersect
# TODO - build tree
