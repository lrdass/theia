import sys
from segment_tree import build_2d_segment_tree, query_2d_segment_tree, Segment
from range_tree import build_2d_segment_range_tree, search_in_range_2d_segments
import pygame
from itertools import chain
import datetime

"""
algoritmo:
    devemos construir um mapa com todos os segmentos do brasil
    devemos consultar com um janela neste mundo quais segmentos estão dentro desta janela
    retornamos estes segmentos
    a viewport irá traduzí-los em retas e segmentos no canvas

"""


def window_to_viewport(x_w, y_w, x_wmax, y_wmax,
                       x_wmin, y_wmin, x_vmax,
                       y_vmax, x_vmin, y_vmin):

    # point on viewport
    # calculatng Sx and Sy
    sx = (x_vmax - x_vmin) / (x_wmax - x_wmin)
    sy = (y_vmax - y_vmin) / (y_wmax - y_wmin)

    # calculating the point on viewport
    x_v = x_vmin + ((x_w - x_wmin) * sx)
    y_v = y_vmin + ((y_w - y_wmin) * sy)

    return (x_v, y_v)


window = [
    [-148125.0-9000, -133125.0-9000],
    [-23437.5, -12187.5]
]
print(window[0][0])
print(window[0][1])
viewports_size = (640, 480)

is_building = True
segments = []
with open(sys.path[0] + "/../data_structures/utils/points/brasil.in", "r") as points_file:
    for line in points_file:
        line_values = line.split(' ')
        segments.append(Segment(
            o_p1=(int(line_values[0]), int(line_values[1])),
            o_p2=(int(line_values[2]), int(line_values[3])),
        ))


print('GOING TO BUILD')

# segment_tree = build_2d_segment_tree(segments)
# segments_extreme_points = list(
#     chain.from_iterable(
#         [[segment.p1, segment.p2] for segment in segments]
#     )
# )
range_tree = build_2d_segment_range_tree(segments)

print('FINISHED BUILDING')


pygame.init()
screen = pygame.display.set_mode(viewports_size)

canvas = pygame.Surface(screen.get_size())

clock = pygame.time.Clock()
running = True


# move right:
# x.min+= 1000
# x.max+= -1000
# move left:
# x.min+= -1000
# x. max+= 1000
w_dow = Segment(
    x_range=(window[0][0] + 3000, window[0][1] - 3000),
    y_range=(window[1][0] + 3000, window[1][1] - 3000)
)  # main loop

canvas.blit(pygame.Surface(screen.get_size()), (0, 0))
# event handling, gets all event from the event queue
# a = datetime.datetime.now()

a = datetime.datetime.now()

# b = datetime.datetime.now()
# print(window)
# delta = b - a
# print(int(delta.total_seconds() * 1000), " ms")
# segments_inside.extend(query_2d_segment_tree(segment_tree, Segment((window[0][0], window[0][0]), window[1])))
# segments_inside.extend(query_2d_segment_tree(segment_tree, Segment((window[0][1], window[0][1]), window[1])))


def render():
    segments_inside = search_in_range_2d_segments(range_tree,
                                                  Segment(
                                                      x_range=(
                                                          window[0][0] + 3000, window[0][1] - 3000),
                                                      y_range=(
                                                          window[1][0] + 3000, window[1][1] - 3000)
                                                  )
                                                  )
    print(len(segments_inside))
    for segment in segments_inside:
        # for segment in segments:
        line_xpos = window_to_viewport(segment.o_p1[0], segment.o_p1[1], window[0][1], window[1][1],
                                       window[0][0], window[1][0], viewports_size[0], viewports_size[1], 0, 0)

        line_ypos = window_to_viewport(segment.o_p2[0], segment.o_p2[1], window[0][1], window[1][1],
                                       window[0][0], window[1][0], viewports_size[0], viewports_size[1], 0, 0)

        pygame.draw.line(canvas, (255, 255, 255), line_xpos, line_ypos)

    b = datetime.datetime.now()
    delta = b - a
    print(int(delta.total_seconds() * 1000), " ms")

    del segments_inside

    screen.blit(canvas, (0, 0))
    pygame.display.flip()


while True:
    pygame.draw.rect(canvas, (0, 0, 0), screen.get_rect())
    for event in pygame.event.get():
        # only do something if the event is of type QUIT
        if event.type == pygame.QUIT:
            # change the value to False, to exit the main loop
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
            pass
            # window[1][0] = window[1][0] + 1000
            # window[1][1] = window[1][1] + 1000
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
            pass
            # window[1][0] = window[1][0] - 1000
            # window[1][1] = window[1][1] - 1000
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_a:
            window[0][0] -= 1000
            window[0][1] -= 1000
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_d:
            window[0][0] += 1000
            window[0][1] += 1000

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            screen.fill((0, 0, 0))
            render()
            break

clock.tick(30)
