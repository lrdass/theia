import svgwrite
import random
import xml.etree.ElementTree as ET
import math


class Node:
    left = None
    right = None
    value = None
    associated = None

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


def create_svg_points(file_name, number_points, size=(200, 200)):
    dwg = svgwrite.Drawing(file_name, size=size)
    dwg.viewbox(-size[0]/2, -size[1]/2, size[0], size[1])
    for n in range(number_points):
        x_rnd = random.randint(-size[0]/2, size[0]/2)
        y_rnd = random.randint(-size[1]/2, size[1]/2)
        dwg.add(dwg.circle(center=(x_rnd, y_rnd), r=2))
    
    x_rnd = random.randint(-size[0]/2, size[0]/2)
    y_rnd = random.randint(-size[1]/2, size[1]/2)
    
    y_size = random.randint(1, (size[1]/2)) 
    x_size = random.randint(1, (size[0]/2))

    x_size = x_size if x_rnd+x_size<= (size[0] / 2) else size[0]/2
    y_size = y_size if y_rnd+y_size<= size[1] / 2 else size[1]/2

    dwg.add(dwg.rect(insert=(-50, -60), size=(40, 40), rx=None, ry=None, fill='none', stroke='red'))

    dwg.save()



def circle_to_point(circle):
    circle_dict = circle.attrib
    return (float(circle_dict["cx"]), float(circle_dict["cy"]))

def read_svg_file(svg_file):
    return ET.parse(svg_file)

def colorize_points_inside(points_inside, svg_tree):
    for circle in svg_tree.iter('circle'):
        point_circle = circle_to_point(circle)
        if point_circle in points_inside:
            circle.attrib['style'] = 'fill:#00ff00' 
    svg_tree.write('teste.svg')


create_svg_points('new_points.svg', 200)
