import sys
from segment_tree import build_2d_segment_tree, query_2d_segment_tree, Segment
from range_tree import build_2d_segment_range_tree, search_in_range_2d_segments
import pygame
from itertools import chain

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



window = [[-148125.0, -133125.0], [-23437.5, -12187.5]]
viewports_size = (480,360)

is_building= True
segments=[]
with  open(sys.path[0] + "/../data_structures/utils/points/brasil.in", "r") as points_file:
    for line in points_file:
        line_values = line.split(' ')
        segments.append(Segment(
            (int(line_values[0]), int(line_values[2])),
            (int(line_values[1]), int(line_values[3]))
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



running = True
    # main loop
while running:
    # event handling, gets all event from the event queue
    canvas.blit(pygame.Surface(screen.get_size()), (0,0))

    segments_inside = search_in_range_2d_segments(range_tree, Segment(window[0], window[1]))
    # segments_inside = query_2d_segment_tree(segment_tree, Segment((window[0][0], window[0][0]), window[1]))
    # segments_inside.union(query_2d_segment_tree(segment_tree, Segment((window[0][1], window[0][1]), window[1])))


    for event in pygame.event.get():
        # only do something if the event is of type QUIT
        if event.type == pygame.QUIT:
            # change the value to False, to exit the main loop
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                window[0][1]*=2
                window[0][0]*=2
                window[1][1]*=2
                window[1][0]*=2
            if event.button == 5:
                window[0][1]/=2
                window[0][0]/=2
                window[1][1]/=2
                window[1][0]/=2

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w ]:
        window[1][0] += 10000
        window[1][1] += 10000
    if keys[pygame.K_s]:
        window[1][0] -= 10000
        window[1][1] -= 10000
    if keys[pygame.K_a ]:
        window[0][0] += 10000
        window[0][1] += 10000
    if keys[pygame.K_d]:
        window[0][0] -= 10000
        window[0][1] -= 10000


    for segment in segments_inside:
        line_xpos = window_to_viewport(segment.x.min, segment.y.min, window[0][1], window[1][1],
                        window[0][0], window[1][0], viewports_size[0], viewports_size[1], 0,0)


        line_ypos = window_to_viewport(segment.x.max, segment.y.max, window[0][1], window[1][1], 
                        window[0][0], window[1][0], viewports_size[0], viewports_size[1], 0,0)

        pygame.draw.line(canvas, (255,255,255), line_xpos, line_ypos)
        
    screen.blit(canvas, (0,0))
    pygame.display.flip()
                            