import copy
import math
import xml.etree.ElementTree as ET
import pprint

SVG_NAMESPACE_CIRCLE = "{http://www.w3.org/2000/svg}circle"
SVG_NAMESPACE_RECT = "{http://www.w3.org/2000/svg}rect"
SVG_NAMESPACE_GROUP = "{http://www.w3.org/2000/svg}g"



class Interval:
    class Range:
        def __init__(self, min_value, max_value):
            self.min = min_value
            self.max = max_value     
    x = None
    y = None
    
    def __init__(self, x_range=(-math.inf,math.inf), y_range=(-math.inf,math.inf)):
        self.x = self.Range(min(x_range), max(x_range))
        self.y = self.Range(min(y_range), max(y_range))
    
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



def circle_to_point(circle):
    circle_dict = circle.attrib
    return (float(circle_dict["cx"]), float(circle_dict["cy"]))


def get_group_by_id(tree, group_id):
    return [
        circle
        for circle in get_all_points_from_tree(tree)
    ]


def read_svg_file(svg_file):
    return ET.parse(svg_file)


def get_all_points_from_tree(tree):
    return [circle_to_point(circle) for circle in tree.iter(SVG_NAMESPACE_CIRCLE)]


def get_point_by_id(tree, point_id):
    return [
        circle_to_point(circle)
        for circle in tree.iter(SVG_NAMESPACE_CIRCLE)
        if "id" in circle.attrib
        if circle.attrib["id"] == point_id
    ]


def distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2

    dx = x1 - x2
    dy = y1 - y2

    return math.sqrt(dx * dx + dy * dy)


def closest_point(all_points, new_point):
    best_point = None
    best_distance = None

    for current_point in all_points:
        current_distance = distance(current_point, new_point)

        if best_distance is None or current_distance < best_distance:
            best_point = current_point
            best_distance = current_distance

    return best_point


k = 2
def build_kdtree(points, depth=0, area=Interval(), last_split=None, side=''):
    n = len(points)
    if n <= 0:
        return None

    axis = depth % k
    axis_name = 'x' if axis == 1 else 'y' 

    sorted_points = sorted(points, key=lambda point: point[axis])
    if n == 1:
        return {
            'point': sorted_points.pop()
        }
    else:
        mid_point = int((n - 1) / 2)
        split_value = sorted_points[mid_point][axis]
        
        update_area = copy.deepcopy(area) 

        if last_split is not None:
            ## right last_split > eixo.min 
            if side == 'right':
                update_area[axis_name].min = last_split if last_split > update_area[axis_name].min else update_area[axis_name].min
            ## left  last_split < eixo.min
            if side == 'left':
                update_area[axis_name].max = last_split if last_split < update_area[axis_name].max else update_area[axis_name].max

        no =  {
            "split": split_value,
            "left": build_kdtree(sorted_points[: mid_point+1], depth + 1, update_area, split_value, side='left'),
            "right": build_kdtree(sorted_points[mid_point+1 :], depth + 1, update_area, split_value, side='right'),
            "area": update_area,
        }
        return no



def kdtree_naive_closest_point(root, point, depth=0, best=None):
    if root is None:
        return best

    axis = depth % k

    next_branch = None
    next_best = None

    if best is None or distance(point, best) > distance(point, root["point"]):
        next_best = root["point"]
    else:
        next_best = best

    if point[axis] < root["point"][axis]:
        next_branch = root["left"]
    else:
        next_branch = root["right"]

    return kdtree_naive_closest_point(next_branch, point, depth + 1, next_best)


def kdtree_closest_point(root, point, depth=0):
    if root is None:
        return None

    axis = depth % k

    next_branch = None
    opposite_branch = None

    if point[axis] < root["point"][axis]:
        next_branch = root["left"]
        opposite_branch = root["right"]
    else:
        next_branch = root["right"]
        opposite_branch = root["left"]

    best = closer_distante(
        point, kdtree_closest_point(next_branch, point, depth + 1), root["point"]
    )

    if distance(point, best) > abs(point[axis] - root["point"][axis]):
        best = closer_distante(
            point, kdtree_closest_point(opposite_branch, point, depth + 1), best
        )

    return best


def closer_distante(point, p1, p2):
    if p1 is None:
        return p2

    if p2 is None:
        return p1

    d1 = distance(point, p1)
    d2 = distance(point, p2)

    if d1 < d2:
        return p1
    else:
        return p2

def is_point_inside_query(point, interval=Interval):
    return point[0] <= interval.x.max and point[0] >= interval.x.min \
        and point[1] <= interval.y.max and point[1] >= interval.y.min
    
def is_area_inside_query(area=Interval, query=Interval):
    return area.y.min >= query.y.min and area.y.max <= query.y.max  \
        and area.x.max <= query.x.max and area.x.min >= area.x.min

def is_area_intersects_query(area=Interval, query=Interval):
    return area.x.max == math.inf and area.x.min == -math.inf \
         and  area.y.max == math.inf and area.y.min == -math.inf \
        or query.x.min <= area.x.max <= query.x.max \
        or query.y.min <= area.y.max <= query.y.max \
        or query.y.min <= area.y.min <= query.y.max \
        or query.x.min <= area.x.min <= query.x.max \

def report_subtree(node={}, points=[]):
    try:
        point = node['point']
        points.append(point)
        return points
    except KeyError:
        report_subtree(node['left'], points)
        report_subtree(node['right'], points)
    
    return set(points)


def kdtree_search_in_range(node, query=Interval, depth=0, points=[]):
    """ quais pontos estao dentro de rect ? """
    try:
        point = node['point']
        if is_point_inside_query(point, query):
            return  points.append(point)
    except KeyError as not_a_point:
            try:
                left_branch = node['left']
                if is_area_inside_query(left_branch['area'], query):
                    return points.append(report_subtree(left_branch))
                elif is_area_intersects_query(left_branch['area'], query):
                    kdtree_search_in_range(left_branch, query=query, points=points)
            except KeyError as left_is_point:
                kdtree_search_in_range(left_branch, query=query, points=points)

            try:
                right_branch = node['right']
                if is_area_inside_query(right_branch['area'], query):
                    return points.append( report_subtree(right_branch))
                elif is_area_intersects_query(right_branch['area'], query):
                    kdtree_search_in_range(right_branch, query=query, points=points)
            except KeyError as right_is_point:
                kdtree_search_in_range(right_branch, query=query, points=points)

    return set(points)

# kdtree = build_kdtree(points)

svg_tree = read_svg_file("./kdtree/points/points3.svg")
points = get_group_by_id(svg_tree, "points")
rect_query = next(svg_tree.iter(SVG_NAMESPACE_RECT)).attrib

min_x = float(rect_query['x'])
max_x = float(rect_query['x']) + float(rect_query['width'])
min_y = float(rect_query['y'])
max_y = float(rect_query['y']) - float(rect_query['height'])

rect_query = Interval((min_x, max_x), (min_y, max_y))
print(rect_query)

kdtree = build_kdtree(points)

pprint.pprint(kdtree)
pprint.pprint(kdtree_search_in_range(kdtree, query=rect_query))

# print(kdtree_search_in_range({}))
