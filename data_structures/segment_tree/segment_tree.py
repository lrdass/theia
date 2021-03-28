import math
from math import floor, log2
from queue import Queue
from pprint import pprint
from numbers import Number
from random import randint
from functools import reduce

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


class Segment:
    class Range:
        def __init__(self, min_value, max_value):
            self.min = min_value
            self.max = max_value     
    x = None
    x_interval = Interval()
    y = None
    y_interval = Interval()
    
    def __init__(self, x_range=(-math.inf,math.inf), y_range=(-math.inf,math.inf)):
        self.x = self.Range(min(x_range), max(x_range))
        self.y = self.Range(min(y_range), max(y_range))
        self.x_interval = Interval(self.x.min, self.x.max, 'both')
        self.y_interval = Interval(self.y.min, self.y.max, 'both')
    
    def __repr__(self):
        return 'x : [{},{}], y :[{}, {}]'.format(self.x.min, self.x.max, self.y.min, self.y.max)
    
    def __getitem__(self, name):
        return getattr(self, name)
    def __setitem__(self, name, value):
        return setattr(self, name, value)
    def __delitem__(self, name):
        return delattr(self, name)
    def __contains__(self, name):
        return hasattr(self, name)



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
# one dimensional segment tree
def report_subtree(node=Node, points=[]):
    if node.is_leaf():
        points.append(node.value)
    else:
        report_subtree(node.left, points)
        report_subtree(node.right, points)
    
    return set(points)

def find_split_node(node=Node, range=Segment.Range):
    no = node

    while not no.is_leaf():
        if range.max <= no.value  or range.min > no.value:
            if range.max <= no.value :
                no = no.left
            else:
                no = no.right
        else:
            break

    return no


       
def build_elementary_segments(segments=[Interval]):
    ordered_segment_endpoints = []
    for segment in segments:
        ordered_segment_endpoints.append(segment.left)
        ordered_segment_endpoints.append(segment.right)
    ordered_segment_endpoints = list(dict.fromkeys(ordered_segment_endpoints))
    ordered_segment_endpoints.sort()

    elementary_segments=Queue()
    for index, endpoint in enumerate(ordered_segment_endpoints):
        if index == 0:
           elementary_segments.put(Interval(-math.inf, endpoint, 'neither')) 
           elementary_segments.put(Interval(endpoint, endpoint, 'both'))
        elif index == len(ordered_segment_endpoints) -1:
            previous_endpoint= ordered_segment_endpoints[index-1]
            elementary_segments.put(Interval(previous_endpoint, endpoint, 'neither'))
            elementary_segments.put(Interval(endpoint, endpoint, 'both'))
            elementary_segments.put(Interval(endpoint, math.inf, 'neither'))
        else:
            previous_endpoint = ordered_segment_endpoints[index-1]
            elementary_segments.put(Interval(previous_endpoint, endpoint, 'neither'))
            elementary_segments.put(Interval(endpoint, endpoint, 'both'))
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
    current_index = 0
    while not len(segments_queue.queue) == 2 ** min_fifo_len:
        current = segments_queue.queue[current_index]
        if not current.merged:
            next_element = segments_queue.queue[current_index+1]
            union_node = Node(current.value.union(next_element.value))
            union_node.left = Node(current.value)
            union_node.right = Node(next_element.value)
            union_node.merged = True

            del segments_queue.queue[current_index]
            del segments_queue.queue[current_index]
            
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

def insert_interval_on_segment_tree(node, interval):
    if interval.contains(node.value):
        node.segments = [*node.segments, interval]
    elif not node.is_leaf():
        if node.left.value.intersect(interval):
            insert_interval_on_segment_tree(node.left, interval)
        if node.right.value.intersect(interval):
            insert_interval_on_segment_tree(node.right, interval)
 

def insert_segment_on_segment_tree(node, segment=Segment):
    if segment.x_interval.contains(node.value):
        node.segments = [*node.segments, segment]
    elif not node.is_leaf():
        if node.left.value.intersect(segment.x_interval):
            insert_segment_on_segment_tree(node.left, segment)
        if node.right.value.intersect(segment.x_interval):
            insert_segment_on_segment_tree(node.right, segment)
"""
* construir segment tree com os x intervalos
    * preciso trocar a expressao de segmentos para intervalos
* metodo: insert_segment_tree:
    - se intervalo_x do segmento contem o valor do nó
    - insere o segmento na lista de segmentos
    - por fim, vamos ter a árvore de segmentos(x_interalos dos segmentos) com a lista de Segmentos nos nós
    - passa por cada nó e constrói uma árvore associada com os y_intervalos dos segmentos em cada um dos nós que tiver
- consulta:
    -  consulta em uma e consulta a arvore associada
"""

def query_segment_tree(node, query,segment_to_report=set()):
    for segment in node.segments:
        segment_to_report.add(segment)
    if not node.is_leaf():
        if query in node.left.value:
            query_segment_tree(node.left, query, segment_to_report)
        else:
            query_segment_tree(node.right, query, segment_to_report)
    return segment_to_report

def query_2d_segment_tree(node, query=Segment,segment_to_report=set()):
    # optimization for tree search
    for segment in node.segments:
        if segment.y_interval.left in query.y_interval or segment.y_interval.right in query.y_interval:
            segment_to_report.add(segment)
    if not node.is_leaf():
        if query.x_interval.left in node.left.value:
            query_2d_segment_tree(node.left, query, segment_to_report)
        else:
            query_2d_segment_tree(node.right, query, segment_to_report)
    return segment_to_report

def build_associated_tree(points=[], axis=1): 
    sorted_points = sorted(points, key=lambda point: point[axis])
    n = len(points)
    
    mid_point = int((n-1) / 2)
    split_value = sorted_points[mid_point][axis]
    if n == 1:
        no = Node(points.pop()) 
        return no
    else:
        no = Node(split_value)
        no.left = build_associated_tree(sorted_points[:mid_point+1])
        no.right = build_associated_tree(sorted_points[mid_point+1:])
        return no

def search_in_range_1d(tree, range=Segment.Range, axis=1):
    split = find_split_node(tree, range)
    inside = [] 

    if split.is_leaf():
        if range.min <= split.value[axis] <= range.max:
            inside.append(split.value)
    else:
        no = split.left
        while not no.is_leaf():
            if range.min <= no.value:
                inside.extend(report_subtree(node=no.right))
                no = no.left
            else:
                no = no.right 
        # aqui ta chegando uma tupla
        if range.min < no.value[axis] <= range.max:
            inside.append(no.value)

        no = split.right
        while not no.is_leaf():
            if range.max > no.value:
                inside.extend(report_subtree(node=no.left))
                no = no.right
            else:
                no = no.left 
        if range.min < no.value[axis] <= range.max:
            inside.append(no.value)
        
    return set(inside)

def build_2d_segment_tree(segments=[]):

    x_intervals_of_segments= list(map(lambda segment: segment.x_interval, segments))
    elementary_segments = build_elementary_segments(x_intervals_of_segments)

    segment_tree = build_1d_segment_tree(elementary_segments)

    point_segment_map = dict([(segment.x_interval, segment) for segment in segments])
    point_segment_map.update(dict([(segment.y_interval, segment) for segment in segments]))

    for segment in segments :
        insert_segment_on_segment_tree(segment_tree, segment)
    


    #construct_associated_tree(segment_tree)
    return segment_tree


def build_range_tree(points, point_segment_map={}):
    y_tree = build_associated_tree(copy(points))

    n = len(points)
    sorted_points = sorted(points, key=lambda point: point[0])
    mid_point = int( (n-1)/2 )

    if n == 1:
        no = Node(points.pop()) 
        no.associated = y_tree
        return no
    else:
        no = Node(sorted_points[mid_point][0])
        no.left = build_range_tree(sorted_points[:mid_point+1])
        no.right = build_range_tree(sorted_points[mid_point+1:])
        no.associated = y_tree
        return no

segments = [Segment((-3,-1), (0, 1)), Segment((-2,1),(0,-8)), Segment((1,5),(1,-2)), Segment((6,7),(-4, 2))]
# generating a list of x_intervals of the list of segments
#x_intervals_of_segments = list(map(lambda segment: Interval(segment.x.min, segment.x.max, 'both'), segments))
#print(x_intervals_of_segments)

#elementary_segments = build_elementary_segments(x_intervals_of_segments)

## checa se algum segmento cruza alguam extremidade da janela
segment_tree = build_2d_segment_tree(segments)
print(segment_tree.value)

inside = query_2d_segment_tree(segment_tree, query=Segment(x_range=(1,1), y_range=(-8, 8)))
print(inside)