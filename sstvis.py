import ast
import fileinput
import os
import sys
import math

# prevent pygame from printing their welcome message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame

white = (255, 255, 255)
red = (255, 0, 0)
black = (0, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

window_dimensions = (1200, 800)  # Screen resolution to use

# Current setup uses 0,0 -> window_dimensions as size, so have to 'correct' the coords to be closer to 0
bbox = []

scale = 1  # Enlarging the triangles on the screen

# More granular correction factor, isn't affected by the scale parameter
x_offset = 0
y_offset = 0

# Higher frequency is less updates, lower frequency is more updates (it's a x % frequency == 0)
UPDATE_FREQUENCY = 500

# Only updates every nth triangle, increases clarity in high density datasets
# Can also put this to 1 and make the scaling factor larger
THINNING_FACTOR = 1

screen = pygame.display.set_mode(window_dimensions)
screen.fill(white)

pygame.display.set_caption('sstvis')
pygame.display.flip()

v_count = 1


class Vertex:
    def __init__(self, x, y, z):
        # print(x,y,z)
        # print(x_correction)
        # self.x = (float(x) - bbox[0]) * scale + x_offset
        # self.y = (float(y) - bbox[1]) * scale + y_offset
        self.x, self.y = transform(x, y) 
        self.z = float(z)

        # Easy way to check if the offsets need adjusting; if these are larger than your window_dimensions, it's not going to show up.
        # print(self.x, self.y)

def transform(x, y):
    rex = (float(x) - bbox[0]) * scale + x_offset
    rey = (float(y) - bbox[1]) * scale + y_offset
    return (rex, rey)
        


def process_line(line, count):
    split_line = line.rstrip("\n").split(" ")

    if split_line[0] == "#":
        return

    elif split_line[0] == "b":
        # return
        global bbox
        bbox.append(float(split_line[1]))
        bbox.append(float(split_line[2]))
        bbox.append(float(split_line[3]))
        bbox.append(float(split_line[4]))
        deltax = bbox[2] - bbox[0]
        deltay = bbox[3] - bbox[1]
        delta = deltax
        if (deltay < deltax):
            delta = deltay
        global scale
        scale = math.floor(window_dimensions[1] / delta)
        minx, miny = transform(bbox[0], bbox[1])
        maxx, maxy = transform(bbox[2], bbox[3])
        pygame.draw.lines(screen, red, True, ((minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy)), width=3)


    elif split_line[0] == "v":
        x = split_line[1]
        y = split_line[2]
        z = split_line[3]
        global v_count
        vertices[int(v_count)] = Vertex(x, y, z)
        v_count += 1 

    elif split_line[0] == "f":
        # print (split_line)
        f1 = int(split_line[1])
        f2 = int(split_line[2])
        f3 = int(split_line[3])

        if count % THINNING_FACTOR == 0:
            pygame.draw.lines(screen, black, True, ((vertices[f1].x, vertices[f1].y), (vertices[f2].x, vertices[f2].y), (vertices[f3].x, vertices[f3].y)), width=1)
            # pygame.draw.circle(screen, black, ((vertices[f1].x, vertices[f1].y)), 1)

        if count % UPDATE_FREQUENCY == 0:
            pygame.display.update()

    elif split_line[0] == "x":
        v = int(split_line[1])
        del vertices[v]
        

    else:
        print("Unknown character in stream!")
        return


if __name__ == "__main__":
    vids = {}
    vertices = {}

    faces = []
    running = True

    count = 0

    for stdin_line in fileinput.input():
        if stdin_line == "":
            continue
        process_line(stdin_line, count)
        # Python print already adds new line
        # print(stdin_line.rstrip("\n"))
        count += 1
        sys.stdout.write(stdin_line)

    pygame.display.update()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
