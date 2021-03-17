import fileinput
import sys
import math
import random
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

pygame.init()

screen = pygame.display.set_mode(window_dimensions)
screen.fill(white)

font = pygame.font.SysFont("Arial", 24)

# TODO: Split label and value for each statistics field

time_taken = font.render("Time taken:                                  0s", True, black, white)
tt_rect = time_taken.get_rect(bottomleft=(50, window_dimensions[1] - 95))
screen.blit(time_taken, tt_rect)

points_per_second = font.render("Average points per second:      0.0", True, black, white)
pps_rect = points_per_second.get_rect(bottomleft=(50, window_dimensions[1] - 60))
screen.blit(points_per_second, pps_rect)

points_last_minute = font.render("Points processed past minute:  0", True, black, white)
plm_rect = points_last_minute.get_rect(bottomleft=(50, window_dimensions[1] - 25))
screen.blit(points_last_minute, plm_rect)

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

        self.start_time = time.time()
        self.points_per_time = {}

    def transform(self, x, y):
        rex = (float(x) - self.bbox[0]) * self.scale
        rey = (float(y) - self.bbox[1]) * self.scale
        return rex, rey

    def increment_count(self):
        self.count += 1

    def update_statistics(self):
        current_epoch = int(time.time())

        time_taken = font.render("Time taken:                                 " + str(round(current_epoch - self.start_time)) + "s         ", True, black, white)
        screen.blit(time_taken, tt_rect)

        points_in_past_minute = 0
        for i in range(current_epoch - 60, current_epoch):
            if i in self.points_per_time:
                points_in_past_minute += self.points_per_time[i]

        points_per_second = font.render("Average points per second:     " + str(round(points_in_past_minute / 60 * 100) / 100) + "    ", True, black, white)
        screen.blit(points_per_second, pps_rect)

        points_last_minute = font.render("Points processed past minute: " + str(points_in_past_minute) + "     ", True, black, white)
        screen.blit(points_last_minute, plm_rect)


    def process_line(self, line):
        pygame.event.get()

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

            pygame.draw.lines(surface=screen, color=red, closed=True, points=((minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy)), width=3)

        elif split_line[0] == "v":
            # Add vertex count per unit
            current_epoch = int(time.time())
            if current_epoch not in self.points_per_time.keys():
                self.points_per_time[current_epoch] = 1
            else:
                self.points_per_time[current_epoch] += 1

            # Transform x and y into current scale for visualization, then store that version in the Vertex
            x, y = self.transform(split_line[1], split_line[2])
            z = split_line[3]
            self.vertices[self.vertex_count] = Vertex(x, y, z)
            self.vertex_count += 1

        elif split_line[0] == "f":
            f1 = int(split_line[1])
            f2 = int(split_line[2])
            f3 = int(split_line[3])

            if self.count % THINNING_FACTOR == 0:
                pygame.draw.lines(
                    surface=screen,
                    color=black,
                    closed=True,
                    points=(
                        (self.vertices[f1].x, self.vertices[f1].y),
                        (self.vertices[f2].x, self.vertices[f2].y),
                        (self.vertices[f3].x, self.vertices[f3].y)
                    ),
                    width=1)
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
