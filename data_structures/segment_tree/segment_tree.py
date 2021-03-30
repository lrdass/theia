from math import floor, log2
from queue import Queue
import math
from pprint import pprint
from numbers import Number
from random import randint
from functools import reduce
from itertools import chain
from collections import defaultdict, OrderedDict
# import svgwrite
import xml.etree.ElementTree as ET


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

        if self.closed_left and self.closed_right:
            return self.left <= value <= self.right
        elif self.closed_left and not self.closed_right:
            return self.left <= value < self.right
        elif self.closed_right and not self.closed_left:
            return self.left < value <= self.right
        else:
            return self.left < value < self.right

    def union(self, target):
        # segment1 = Interval(-math.inf, -6, 'right')
        # segment2 = Interval(-math.inf, -5, 'neither')
        # fix union, left bounded values are wrong!
        # fix union !! is too damn wrong!!!  ]-inf, -6] U ]-6, -5[
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
            else 'left' if closed_info['right'] in ['left', 'neither'] and closed_info['left'] in ['left', 'both']      \
            else 'both'

        return Interval(left, right, closed)

    # ]-inf, -6] interset [-6, -5]
    def intersect(self, target):
        if self.closed_left and self.closed_right:
            return target.left in self or target.right in self or \
                self.left in target or self.right in target
        elif self.closed_left:
            return target.left in self or \
                self.left in target or \
                self.left < target.right < self.right or \
                target.left < self.right < target.right
        elif self.closed_right:
            return target.right in self or \
                self.right in target or \
                self.left < target.left < self.right or \
                target.left < self.left < target.right
        else:
            return target.left < self.left < target.right or \
                target.left < self.right < target.right or \
                self.left < target.left < self.right or \
                self.left < target.right < self.right

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

    def __init__(self, x_range=(-math.inf, math.inf), y_range=(-math.inf, math.inf)):
        self.x = self.Range(min(x_range), max(x_range))
        self.y = self.Range(min(y_range), max(y_range))
        self.x_interval = Interval(self.x.min, self.x.max, 'both')
        self.y_interval = Interval(self.y.min, self.y.max, 'both')

    def __repr__(self):
        return 'x : [{},{}], y :[{}, {}]'.format(self.x.min, self.x.max, self.y.min, self.y.max)

    def __hash__(self):
        return hash(str(self))

    # def __getitem__(self, name):
    #     if name == 0:
    #         return self.x
    #     elif name == 1:
    #         return self.y

    def __eq__(self, o):
        return self.x_interval == o.x_interval and self.y_interval == o.y_interval

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
    segments = None

    def __init__(self, value=None):
        self.value = value
        self.left = None
        self.right = None
        self.segments = set()

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


def line_to_segment(line):
    line_dict = line.attrib
    if line_dict['stroke'] == 'black':
        p1 = (int(line_dict['x1']), int(line_dict['x2']))
        p2 = (int(line_dict['y1']), int(line_dict['y2']))
        return Segment(p1, p2)
    return


def read_svg_file(svg_file):
    return ET.parse(svg_file)


def colorize_segments_inside(segments_inside, svg_tree):
    for line in svg_tree.iter('{http://www.w3.org/2000/svg}line'):
        line_segment = line_to_segment(line)
        if line_segment in segments_inside:
            line.attrib['stroke'] = 'green'
    svg_tree.write('inside_segments.svg')


def create_svg_segments(file_name, size=(200, 200), segments=[], number_segments=30, window=Interval, inside_segments=[]):
    dwg = svgwrite.Drawing(file_name, size=size)

    dwg.viewbox(-size[0]/2, -size[1]/2, size[0], size[1])
    g = svgwrite.container.Group()
    g.scale(1, -1)

    # window min-x, min-y
    # x_rand = random.randint(-size[0]/2, size[0]/2)
    # y_rand = random.randint(-size[0]/2, size[0]/2)

    # g.add(dwg.line(
    #     insert=(x_rand, y_rand),
    #     size=(40, 40),
    #     rx=None, ry=None, fill='none', stroke='red')
    # )

    # g.add(dwg.rect(
    #                 insert=(window.x.min, window.y.min),
    #                 size=(abs(window.x.min-window.x.max), abs(window.y.min-window.y.max)),
    #                 rx=None, ry=None, fill='none', stroke='red', stroke_width=0.5)
    # )
    # # for segment in segments:
    #     if segment in inside_segments:
    #         g.add(
    #             dwg.line(start=segment.p1, end=segment.p2, stroke='green',  stroke_width=0.5)
    #         )
    #     else:
    #         g.add(
    #             dwg.line(start=segment.p1, end=segment.p2, stroke='black',  stroke_width=0.5)
    #         )
    for i in range(number_segments):
        x_rand1 = randint(-size[0]/2, size[0]/2)
        x_rand2 = randint(-size[0]/2, size[0]/2)
        y_rand1 = randint(-size[0]/2, size[0]/2)
        y_rand2 = randint(-size[0]/2, size[0]/2)
        g.add(
            dwg.line(start=(x_rand1, y_rand1), end=(
                x_rand2, y_rand2), stroke='black')
        )

    dwg.add(g)
    dwg.save()


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
        if range.max <= no.value or range.min > no.value:
            if range.max <= no.value:
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

    elementary_segments = Queue()
    for index, endpoint in enumerate(ordered_segment_endpoints):
        if index == 0:
            elementary_segments.put(Interval(-math.inf, endpoint, 'neither'))
            elementary_segments.put(Interval(endpoint, endpoint, 'both'))
        elif index == len(ordered_segment_endpoints) - 1:
            previous_endpoint = ordered_segment_endpoints[index-1]
            elementary_segments.put(
                Interval(previous_endpoint, endpoint, 'neither'))
            elementary_segments.put(Interval(endpoint, endpoint, 'both'))
            elementary_segments.put(Interval(endpoint, math.inf, 'neither'))
        else:
            previous_endpoint = ordered_segment_endpoints[index-1]
            elementary_segments.put(
                Interval(previous_endpoint, endpoint, 'neither'))
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

    element = None
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
        node.segments.add(segment)
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


def search_in_range_1d(tree, range=Segment.Range):
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
        if range.min < no.value <= range.max:
            inside.append(no.value)

        no = split.right
        while not no.is_leaf():
            if range.max > no.value:
                inside.extend(report_subtree(node=no.left))
                no = no.right
            else:
                no = no.left
        if range.min < no.value <= range.max:
            inside.append(no.value)

    segments_to_return = set()
    for point in inside:
        segments_to_return.update(tree.y_intervals_segment_map[point])

    return segments_to_return


def query_segment_tree(node, query, segment_to_report=set()):
    for segment in node.segments:
        segment_to_report.add(segment)
    if not node.is_leaf():
        if query in node.left.value:
            query_segment_tree(node.left, query, segment_to_report)
        else:
            query_segment_tree(node.right, query, segment_to_report)
    return segment_to_report


def query_2d_segment_tree(node, query=Segment, segment_to_report=set()):
    # optimization for tree search
    # linear search
    for segment in node.segments:
        if segment.y_interval.left in query.y_interval or segment.y_interval.right in query.y_interval:
            segment_to_report.add(segment)

    # if node.segments:
    #     segment_to_report.update(
    #         search_in_range_1d(node.segments, range=query.y)
    #     )

    if not node.is_leaf():
        if query.x_interval.left in node.left.value:
            query_2d_segment_tree(node.left, query, segment_to_report)
        else:
            query_2d_segment_tree(node.right, query, segment_to_report)

    return segment_to_report


def build_associated_tree(points=[], y_intervals_segment_map=dict()):
    sorted_points = sorted(points)
    n = len(points)

    mid_point = int((n-1) / 2)
    split_value = sorted_points[mid_point]
    if n == 1:
        no = Node(points.pop())
        return no
    else:
        no = Node(split_value)
        no.left = build_associated_tree(
            sorted_points[:mid_point+1], y_intervals_segment_map)
        no.right = build_associated_tree(
            sorted_points[mid_point+1:], y_intervals_segment_map)
        no.y_intervals_segment_map = y_intervals_segment_map
        return no


def build_2d_segment_tree(segments=[]):
    def _build_associated_range_y_tree(node=Node):
        if node.segments:
            all_y_endpoints = list(
                chain.from_iterable(
                    [
                        [seg.y_interval.left, seg.y_interval.right]
                        for seg in node.segments
                    ]
                )
            )
            list_y_intervals_tuple_segment = list(
                chain.from_iterable(
                    map(
                        lambda segment: [
                            (segment.y_interval.left, segment),
                            (segment.y_interval.right, segment)
                        ],
                        node.segments
                    )
                )
            )
            y_intervals_segment_map = defaultdict(set)
            for point, segment in list_y_intervals_tuple_segment:
                y_intervals_segment_map[point].add(segment)

            node.segments = build_associated_tree(
                all_y_endpoints, y_intervals_segment_map)

        if node.left:
            _build_associated_range_y_tree(node.left)
        if node.right:
            _build_associated_range_y_tree(node.right)

    x_intervals_of_segments = list(
        map(lambda segment: segment.x_interval, segments))
    elementary_segments = build_elementary_segments(x_intervals_of_segments)

    segment_tree = build_1d_segment_tree(elementary_segments)

    point_segment_map = dict([(segment.x_interval, segment)
                             for segment in segments])
    point_segment_map.update(
        dict([(segment.y_interval, segment) for segment in segments]))

    for segment in segments:
        insert_segment_on_segment_tree(segment_tree, segment)
    # insert_segment_on_segment_tree(segment_tree, segments[0])

    # tree search
    # _build_associated_range_y_tree(segment_tree)

    # build a range tree on flatten points of y_intervals
    # then, map every segment to those points ..not optmal, but ok

    # construct_associated_tree(segment_tree)
    return segment_tree


segments = [Segment((-3, -1), (0, 1)), Segment((-2, 1), (0, -8)),
            Segment((1, 5), (1, -2)), Segment((6, 7), (-4, 2))]
# generating a list of x_intervals of the list of segments
#x_intervals_of_segments = list(map(lambda segment: Interval(segment.x.min, segment.x.max, 'both'), segments))
# print(x_intervals_of_segments)

#elementary_segments = build_elementary_segments(x_intervals_of_segments)

# checa se algum segmento cruza alguam extremidade da janela
# segment_tree = build_2d_segment_tree(segments)

# inside = query_2d_segment_tree(
#     segment_tree, query=Segment(x_range=(1, 1), y_range=(-8, 8)))
# print(inside)


# create_svg_segments("segments_random.svg")

svg_tree = read_svg_file("segments_to_study.svg")
segments = [line_to_segment(line) for line in svg_tree.iter(
    '{http://www.w3.org/2000/svg}line')
]
segments = [segment for segment in segments
            if segment]

line_query = None
for line in svg_tree.iter('{http://www.w3.org/2000/svg}line'):
    try:
        if line.attrib['id'] == 'query-line':
            p1 = (int(line.attrib['x1']), int(line.attrib['x2']))
            p2 = (int(line.attrib['y1']), int(line.attrib['y2']))
            line_query = Segment(p1, p2)
    except:
        continue


pprint(segments)
print('line query', line_query)


# print('build segment tree')
segment_tree = build_2d_segment_tree(segments)
# print(segment_tree)

inside = query_2d_segment_tree(segment_tree, line_query)
for seg in inside:
    print(seg)
