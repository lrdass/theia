import math
import xml.etree.ElementTree as ET
import pprint

SVG_NAMESPACE_CIRCLE = "{http://www.w3.org/2000/svg}circle"
SVG_NAMESPACE_RECT = "{http://www.w3.org/2000/svg}rect"
SVG_NAMESPACE_GROUP = "{http://www.w3.org/2000/svg}g"


def circle_to_point(circle):
    circle_dict = circle.attrib
    return (float(circle_dict["cx"]), float(circle_dict["cy"]))


def get_group_by_id(tree, group_id):
    return [
        circle
        for group in tree.iter(SVG_NAMESPACE_GROUP)
        if "id" in group.attrib
        if group.attrib["id"] == group_id
        for circle in get_all_points_from_tree(group)
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


# svg_tree = read_svg_file("./camera_frustum/kdtree/points/points.svg")
# [pivot] = get_point_by_id(svg_tree, "pivot")
# points = get_group_by_id(svg_tree, "points")


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
def build_kdtree(points, depth=0, parent_split=None):
    n = len(points)
    if n <= 0:
        return None

    axis = depth % k

    sorted_points = sorted(points, key=lambda point: point[axis])
    if n == 1:
        return {
            'point': sorted_points.pop()
        }
    else:
        mid_point = int((n - 1) / 2)
        split_value = sorted_points[mid_point][axis]

        no =  {
            "split": split_value,
            "left": build_kdtree(sorted_points[: mid_point+1], depth + 1),
            "right": build_kdtree(sorted_points[mid_point+1 :], depth + 1),
            # these are bottom-left point and top-right points
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


class Interval:
    class Range:
        def __init__(self, min_value, max_value):
            self.min = min_value
            self.max = max_value     

    x = None
    y = None
    
    def __init__(self, x_range=(0,0), y_range=(0,0)):
        self.x = self.Range(min(x_range), max(x_range))
        self.y = self.Range(min(y_range), max(y_range))
    
    def __str__(self):
        return 'x : {} - {}, y : {} - {}'.format(self.x.min, self.x.max, self.y.min, self.y.max)


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

def report_subtree(node):
    pass

def kdtree_search_in_range(node, query=Interval((-7,3), (-7, 3)), depth=0):
    """ quais pontos estao dentro de rect ? """
    if node['point']:
        if is_point_inside_query(node['point'], query):
            return node['point']
    else:
        if is_area_inside_query(node['left']['area'], query):
            return report_subtree(node['left'])
        elif is_area_intersects_query(node['left']['area'], query):
            kdtree_search_in_range(node['left'], query)
            
        if is_area_inside_query(node['right']['area'], query):
            return report_subtree(node['right'])
        elif is_area_intersects_query(node['right']['area'], query):
            kdtree_search_in_range(node['right'], query)

# kdtree = build_kdtree(points)
kdtree = build_kdtree([
(-13,8),
(-11,-7),
(-8,-1),
(-8,6),
(-5,-5),
(-2,2),
(2,7),
(4,-6),
(6,5),
(8,-3),
])
pprint.pprint(kdtree)

area = Interval( (0, 7), (-1, -7) )
query = Interval((-5, 9), (-4, 6))
print(is_area_intersects_query(area, query))

# print(kdtree_search_in_range({}))
# pprint.pprint(kdtree_search_in_range(kdtree, (0, 0), (130, 130)))