import ast
import fileinput
import os
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
x_correction = 0 #bbox-minx
y_correction = 0 #bbox-miny

scale = 1  # Enlarging the triangles on the screen

# More granular correction factor, isn't affected by the scale parameter
x_offset = 10
y_offset = 10

# Higher frequency is less updates, lower frequency is more updates (it's a x % frequency == 0)
UPDATE_FREQUENCY = 1000

# Only updates every nth triangle, increases clarity in high density datasets
# Can also put this to 1 and make the scaling factor larger
THINNING_FACTOR = 1

screen = pygame.display.set_mode(window_dimensions)
screen.fill(white)

pygame.display.set_caption('SSTVis')
pygame.display.flip()

v_count = 1


class Vertex:
    def __init__(self, x, y, z):
        # print(x,y,z)
        # print(x_correction)
        self.x = (float(x) - x_correction) * scale + x_offset
        self.y = (float(y) - y_correction) * scale + y_offset
        self.z = float(z)

        # Easy way to check if the offsets need adjusting; if these are larger than your window_dimensions, it's not going to show up.
        # print(self.x, self.y)


def process_line(line, count):
    split_line = line.rstrip("\n").split(" ")

    if split_line[0] == "#":
        return

    elif split_line[0] == "b":
        # return
        global x_correction 
        x_correction = float(split_line[1])
        global y_correction 
        y_correction = float(split_line[2])

        deltax = float(split_line[3]) - x_correction
        deltay = float(split_line[4]) - y_correction
        delta = deltax
        if (deltay < deltax):
            delta = deltay

        global scale
        scale = math.floor(window_dimensions[1] / delta)


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
            pygame.draw.lines(screen, black, True, ((vertices[f1].x, vertices[f1].y), (vertices[f2].x, vertices[f2].y), (vertices[f3].x, vertices[f3].y)))

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

    pygame.display.update()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
