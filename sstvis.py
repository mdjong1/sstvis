import fileinput
import sys
import math
import pygame

# Define some basic colors for easy use
white = (255, 255, 255)
red = (255, 0, 0)
black = (0, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

# Screen resolution to use
window_dimensions = (1200, 800)

# Higher frequency is less updates, lower frequency is more updates (it's a x % frequency == 0)
UPDATE_FREQUENCY = 500

# Only updates every nth triangle, increases clarity in high density datasets
# Can also put this to 1 and make the scaling factor larger
THINNING_FACTOR = 1

screen = pygame.display.set_mode(window_dimensions)
screen.fill(white)

pygame.display.set_caption('sstvis')
pygame.display.flip()


class Vertex:
    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)


class Processor:
    def __init__(self):
        self.bbox = []
        self.vertices = {}
        self.count = 0
        self.vertex_count = 1
        self.scale = 1

    def transform(self, x, y):
        rex = (float(x) - self.bbox[0]) * self.scale
        rey = (float(y) - self.bbox[1]) * self.scale
        return rex, rey

    def increment_count(self):
        self.count += 1

    def process_line(self, line):
        split_line = line.rstrip("\n").split(" ")

        if split_line[0] == "#":
            return

        elif split_line[0] == "b":
            self.bbox.append(float(split_line[1]))
            self.bbox.append(float(split_line[2]))
            self.bbox.append(float(split_line[3]))
            self.bbox.append(float(split_line[4]))

            delta_x = self.bbox[2] - self.bbox[0]
            delta_y = self.bbox[3] - self.bbox[1]
            smallest_delta = delta_y if delta_y < delta_x else delta_x

            self.scale = math.floor(window_dimensions[1] / smallest_delta)

            minx, miny = self.transform(self.bbox[0], self.bbox[1])
            maxx, maxy = self.transform(self.bbox[2], self.bbox[3])

            pygame.draw.lines(screen, red, True, ((minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy)), width=3)

        elif split_line[0] == "v":
            x, y = self.transform(split_line[1], split_line[2])
            z = split_line[3]
            self.vertices[self.vertex_count] = Vertex(x, y, z)
            self.vertex_count += 1

        elif split_line[0] == "f":
            f1 = int(split_line[1])
            f2 = int(split_line[2])
            f3 = int(split_line[3])

            if self.count % THINNING_FACTOR == 0:
                pygame.draw.lines(screen, black, True, (
                    (self.vertices[f1].x, self.vertices[f1].y),
                    (self.vertices[f2].x, self.vertices[f2].y),
                    (self.vertices[f3].x, self.vertices[f3].y)
                ), width=1)
                # pygame.draw.circle(screen, black, ((vertices[f1].x, vertices[f1].y)), 1)

            if self.count % UPDATE_FREQUENCY == 0:
                pygame.display.update()

        elif split_line[0] == "x":
            v = int(split_line[1])
            del self.vertices[v]

        else:
            print("Unknown character in stream!")
            return


if __name__ == "__main__":
    processor = Processor()

    for stdin_line in fileinput.input():
        if stdin_line == "":
            continue

        processor.process_line(stdin_line)
        processor.increment_count()

        sys.stdout.write(stdin_line)

    # Do a final update; because of update frequency a final update in processing loop is not guaranteed
    pygame.display.update()

    # Keep the pygame window running so you can view the final result
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
