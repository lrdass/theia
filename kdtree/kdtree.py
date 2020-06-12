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


svg_tree = read_svg_file("./camera_frustum/kdtree/points/points.svg")
[pivot] = get_point_by_id(svg_tree, "pivot")
points = get_group_by_id(svg_tree, "points")


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


def build_kdtree(points, depth=0):
    n = len(points)
    if n <= 0:
        return None

    axis = depth % k

    sorted_points = sorted(points, key=lambda point: point[axis])
    return {
        "point": sorted_points[int(n / 2)],
        "left": build_kdtree(sorted_points[: int(n / 2)], depth + 1),
        "right": build_kdtree(sorted_points[int(n / 2) + 1 :], depth + 1),
    }


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


def kdtree_search_in_range(root, point1, point2, depth=0, points_inside=[]):
    """ quais pontos estao dentro de rect ? """
    if root is None:
        return None
    axis = depth % k

    splitin_point = root["point"][axis]

    if point1[axis] < splitin_point and point2[axis] < splitin_point:
        points_inside += report_subtree(root["left"])
    elif point1[axis] < splitin_point:
        kdtree_search_in_range(root["left"], point1, point2, depth + 1, points_inside)

    if point1[axis] > splitin_point and point2[axis] > splitin_point:
        points_inside += report_subtree(root["right"])
    elif point2[axis] > splitin_point:
        kdtree_search_in_range(root["right"], point1, point2, depth + 1, points_inside)

    return points_inside


def node_region(node, point1, point2):
    
    pass


def report_subtree(tree, points=[]):
    if tree is None:
        return None

    points.append(tree["point"])

    if tree["left"] is not None:
        report_subtree(tree["left"], points)
    elif tree["right"] is not None:
        report_subtree(tree["right"], points)

    return points


kdtree = build_kdtree(points)
pprint.pprint(kdtree_search_in_range(kdtree, (0, 0), (130, 130)))
