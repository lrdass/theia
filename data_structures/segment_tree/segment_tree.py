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
    segments = []

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
        self.closed_left = closed in ['left', 'both']
        self.closed_right = closed in ['right', 'both']


    def __eq__(self, target):
        return self.left == target.left and self.right == target.right and self.closed == target.closed

    def __hash__(self):
        return hash(str(self))
    
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
    # segment1 = Interval(-math.inf, -6, 'right')
    # segment2 = Interval(-math.inf, -5, 'neither')
    ## fix union, left bounded values are wrong!
        ## fix union !! is too damn wrong!!!  ]-inf, -6] U ]-6, -5[
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

        closed = 'neither' if closed_info['left'] in ['neither', 'right'] and closed_info['right'] in ['neither', 'left']                    \
            else 'right' if closed_info['left'] in ['right', 'neither'] and closed_info['right'] in ['right', 'both']   \
            else 'left' if closed_info['right'] in ['left', 'neither'] and closed_info['left'] in ['left','both']      \
            else 'both'

        return Interval(left, right, closed)

    # ]-inf, -6] interset [-6, -5]
    def intersect(self, target):
        if target.closed_left and target.closed_right:
            return target.left in self or target.right in self
        elif target.closed_left:
            return target.left in self or \
                self.left < target.right< self.right
        elif target.closed_right:
            return target.right in self or \
                self.left < target.left < self.right
        else:
            return target.left < self.left < target.right or \
                target.left < self.right < target.right

    def contains(self, target):
        if self.closed_left and self.closed_right:
            return target.left in self and target.right in self
        elif self.closed_left:
            return target.left in self and \
                self.left < target.right < self.right
        elif self.closed_right:
            return target.right in self and \
                self.left < target.left < self.right
        else:
            return target.left < self.left < target.right and \
                target.left < self.right < target.right

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
    while not elementary_segments_queue.empty():
        seg = elementary_segments_queue.get()
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
            union_node.left = Node(current.value)
            union_node.right = Node(next_element.value)
            union_node.merged = True
            
            segments_queue.queue.insert(current_index, union_node)
            current_index += 1

    element =  None
    while not segments_queue.empty():
        element = segments_queue.get()
        if segments_queue.empty():
            break
        else:
            next_element = segments_queue.get()
            next_node = Node(element.value.union(next_element.value))
            next_node.left = element
            next_node.right = next_element
            segments_queue.put(next_node)
            
    return element

def insert_segment_tree(node, segment):
    if segment.contains(node.value):
        node.segments = [*node.segments, segment]
    elif not node.is_leaf():
        if node.left.value.intersect(segment):
            insert_segment_tree(node.left, segment)
        if node.right.value.intersect(segment):
            insert_segment_tree(node.right, segment)
    return node


segments = [Interval(-3,-1,'both'), Interval(-2,1,'both'), Interval(1,5,'both'), Interval(6,7,'both')]
elementary_segments = build_elementary_segments(segments)
#]-inf, -6] U ]-6, -5[ = ]-inf, -5[ 
#segment1 = Interval(-math.inf, -2, 'neither')
#segment2 = Interval(-2, 1, 'both')
#print(segment1.union(segment2))

tree = build_1d_segment_tree(elementary_segments)
print(tree.value)
#  ]-inf, -6] interset [-6, -5]
#i1 = Interval(-math.inf, -6, 'right')
#i2 = Interval(-6, -5, 'both')
#print(i1.intersect(i2))

tree2 = insert_segment_tree(tree, segments[0])

print(tree2)
print(tree2.segments)
# TODO - Intervals operations that going to be used: in, union, intersect
# TODO - build tree
