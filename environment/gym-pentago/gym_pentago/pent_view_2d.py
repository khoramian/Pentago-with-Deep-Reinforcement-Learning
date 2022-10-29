import pygame
import numpy as np
import random
import os
import time


class PentagoView2D:

    def __init__(self, maze_name="Pentago", maze_size=(6, 6), screen_size=(640, 640), enable_render=True):

        # PyGame configurations
        pygame.init()
        pygame.display.set_caption(maze_name)
        self.__game_over = False
        self.__enable_render = enable_render

        self.maze_size = maze_size
        if self.__enable_render is True:
            # to show the right and bottom border
            self.screen = pygame.display.set_mode(screen_size)
            self.__screen_size = tuple(map(sum, zip(screen_size, (-1, -1))))

        # Set the environment buttons
        self.__env = []

        # Set the agent buttons
        self.__agent = []

        # pentago board view elements
        self.background = None
        self.maze_layer = None

    def update(self, mode="human"):
        if self.background is None and self.maze_layer is None:
            if self.__enable_render is True:
                # Create a background
                self.background = pygame.Surface(self.screen.get_size()).convert()
                self.background.fill((255, 255, 255))

                # Create a layer for the maze
                self.maze_layer = pygame.Surface(self.screen.get_size()).convert_alpha()
                self.maze_layer.fill((0, 0, 0, 0,))

                self.__draw_maze()

        try:
            img_output = self.__view_update(mode)
            self.__controller_update()
        except Exception as e:
            self.__game_over = True
            self.quit_game()
            raise e
        else:
            return img_output

    def quit_game(self):
        try:
            self.__game_over = True
            if self.__enable_render is True:
                pygame.display.quit()
            pygame.quit()
        except Exception:
            pass

    def play_agent(self, action):

        # clear the drawing
        self.__draw_env(transparency=0)
        self.__draw_agent(transparency=0)

        # add new button for agent
        self.__agent.append(action[0:2])

        # rotate a board quarter
        self.rotate_maze(action[2])

        # draw buttons
        self.__draw_env(transparency=255)
        self.__draw_agent(transparency=255)
        pygame.display.set_caption('Agent:  ' + str(action))

    def play_env(self, action):

        # clear the drawing
        self.__draw_env(transparency=0)
        self.__draw_agent(transparency=0)

        # add new button for agent
        self.__env.append(action[0:2])

        # rotate a board quarter
        self.rotate_maze(action[2])

        # draw buttons
        self.__draw_env(transparency=255)
        self.__draw_agent(transparency=255)
        pygame.display.set_caption('Environment:  ' + str(action))

    def reset_pent(self):

        self.__draw_env(transparency=0)
        self.__draw_agent(transparency=0)

        self.__env.clear()
        self.__agent.clear()

    def __controller_update(self):
        if not self.__game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.__game_over = True
                    self.quit_game()

    def __view_update(self, mode="human"):
        if not self.__game_over:
            # update the positions
            self.__draw_env()
            self.__draw_agent()

            # update the screen
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.maze_layer, (0, 0))

            if mode == "human":
                pygame.display.flip()

            return np.flipud(np.rot90(pygame.surfarray.array3d(pygame.display.get_surface())))

    def __draw_maze(self):

        if self.__enable_render is False:
            return

        line_colour = (0, 0, 0, 255)

        # drawing walls lines
        for x in range(self.maze_size[0] + 1):
            for y in range(self.maze_size[1] + 1):
                if x == 3:
                    pygame.draw.line(self.maze_layer, line_colour, (x * self.CELL_W, 0),
                                     (x * self.CELL_W, self.SCREEN_H))
                if y == 3:
                    pygame.draw.line(self.maze_layer, line_colour, (0, y * self.CELL_H),
                                     (self.SCREEN_W, y * self.CELL_H))

                self.__cover_walls(x, y, "NE")

    def __cover_walls(self, x, y, dirs, colour=(0, 0, 255, 15)):

        if self.__enable_render is False:
            return

        dx = x * self.CELL_W
        dy = y * self.CELL_H

        if not isinstance(dirs, str):
            raise TypeError("dirs must be a str.")

        for dir in dirs:
            if dir == "S":
                line_head = (dx + 1, dy + self.CELL_H)
                line_tail = (dx + self.CELL_W - 1, dy + self.CELL_H)
            elif dir == "N":
                line_head = (dx + 1, dy)
                line_tail = (dx + self.CELL_W - 1, dy)
            elif dir == "W":
                line_head = (dx, dy + 1)
                line_tail = (dx, dy + self.CELL_H - 1)
            elif dir == "E":
                line_head = (dx + self.CELL_W, dy + 1)
                line_tail = (dx + self.CELL_W, dy + self.CELL_H - 1)
            else:
                raise ValueError("The only valid directions are (N, S, E, W).")

            pygame.draw.line(self.maze_layer, colour, line_head, line_tail)

    def __draw_env(self, colour=(0, 0, 150), transparency=255):

        if self.__enable_render is False:
            return

        r = int(min(self.CELL_W, self.CELL_H) / 5 + 0.5)
        for k in range(len(self.__env)):
            x = int(self.__env[k][0] * self.CELL_W + self.CELL_W * 0.5 + 0.5)
            y = int(self.__env[k][1] * self.CELL_H + self.CELL_H * 0.5 + 0.5)
            pygame.draw.circle(self.maze_layer, colour + (transparency,), (y, x), r)

    def __draw_agent(self, colour=(150, 0, 0), transparency=255):

        if self.__enable_render is False:
            return

        r = int(min(self.CELL_W, self.CELL_H) / 5 + 0.5)
        for k in range(len(self.__agent)):
            x = int(self.__agent[k][0] * self.CELL_W + self.CELL_W * 0.5 + 0.5)
            y = int(self.__agent[k][1] * self.CELL_H + self.CELL_H * 0.5 + 0.5)
            pygame.draw.circle(self.maze_layer, colour + (transparency,), (y, x), r)

    def is_taken(self, position) -> bool:
        for i in self.__env:
            if i[0] == position[0] and i[1] == position[1]:
                return True

        for j in self.__agent:
            if j[0] == position[0] and j[1] == position[1]:
                return True
        return False

    def rotate_maze(self, quarter):

        h = int(self.maze_size[1] / 2)
        w = int(self.maze_size[0] / 2)
        temp = np.zeros((h, w), dtype=int)

        env_to_remove = []
        agent_to_remove = []

        if quarter == 0:
            for i in self.__env:
                if i[0] < 3 and i[1] < 3:
                    temp[i[0], i[1]] = 1
                    env_to_remove.append(i)
            for i in self.__agent:
                if i[0] < 3 and i[1] < 3:
                    temp[i[0], i[1]] = 2
                    agent_to_remove.append(i)

        if quarter == 1:
            for i in self.__env:
                if i[0] < 3 and i[1] > 2:
                    temp[i[0], i[1] - 3] = 1
                    env_to_remove.append(i)
            for i in self.__agent:
                if i[0] < 3 and i[1] > 2:
                    temp[i[0], i[1] - 3] = 2
                    agent_to_remove.append(i)

        if quarter == 2:
            for i in self.__env:
                if i[0] > 2 and i[1] < 3:
                    temp[i[0] - 3, i[1]] = 1
                    env_to_remove.append(i)
            for i in self.__agent:
                if i[0] > 2 and i[1] < 3:
                    temp[i[0] - 3, i[1]] = 2
                    agent_to_remove.append(i)

        if quarter == 3:
            for i in self.__env:
                if i[0] > 2 and i[1] > 2:
                    temp[i[0] - 3, i[1] - 3] = 1
                    env_to_remove.append(i)
            for i in self.__agent:
                if i[0] > 2 and i[1] > 2:
                    temp[i[0] - 3, i[1] - 3] = 2
                    agent_to_remove.append(i)

        self.remove_env(env_to_remove)
        self.remove_agent(agent_to_remove)

        # rotate temp matrix
        rot_temp = np.rot90(temp, k=1, axes=(1, 0))

        for i in range(h):
            for j in range(w):
                if rot_temp[i][j] == 1:  # env rotated buttons
                    if quarter < 2:
                        self.__env.append(np.array((i, j + (quarter % 2) * 3), dtype=int))
                    else:
                        self.__env.append(np.array((i + 3, j + (quarter % 2) * 3), dtype=int))

                elif rot_temp[i][j] == 2:  # agent rotated buttons
                    if quarter < 2:
                        self.__agent.append(np.array((i, j + (quarter % 2) * 3), dtype=int))
                    else:
                        self.__agent.append(np.array((i + 3, j + (quarter % 2) * 3), dtype=int))

    def env_vertical_line(self) -> bool:

        # sort the list by second element of each tuple (y)
        self.__env.sort(key=lambda x: x[1])

        # find maximum number of buttons with the same (y)
        max_num = 0
        max_index = 0
        cnt = 0
        j = 0
        for i in self.__env:
            if i[1] == j:
                cnt = cnt + 1
            else:
                if cnt > max_num:
                    max_num = cnt
                    max_index = j
                j = i[1]
                cnt = 1

        # in case of one occurrence for each y
        if cnt > max_num:
            max_num = cnt
            max_index = j

        # if there are 5 or more buttons with the same (y)
        if max_num == 6:
            return True
        elif max_num < 5:
            return False

        arr = []
        for i in self.__env:
            if i[1] == max_index:
                arr.append(i[0])

        if self.check_sequence(arr):
            return True
        return False

    def agent_vertical_line(self) -> bool:

        # sort the list by second element of each tuple (y)
        self.__agent.sort(key=lambda x: x[1])

        # find maximum number of buttons with the same (y)
        max_num = 0
        max_index = 0
        cnt = 0
        j = 0
        for i in self.__agent:
            if i[1] == j:
                cnt = cnt + 1
            else:
                if cnt > max_num:
                    max_num = cnt
                    max_index = j
                j = i[1]
                cnt = 1

        # in case of one occurrence for each y
        if cnt > max_num:
            max_num = cnt
            max_index = j

        # if there are 5 or more buttons with the same (y)
        if max_num == 6:
            return True
        elif max_num < 5:
            return False

        arr = []
        for i in self.__agent:
            if i[1] == max_index:
                arr.append(i[0])

        if self.check_sequence(arr):
            return True
        return False

    def env_horizontal_line(self) -> bool:

        # sort the list by first element of each tuple (x)
        self.__env.sort(key=lambda x: x[0])

        # find maximum number of buttons with the same (x)
        max_num = 0
        max_index = 0
        cnt = 0
        j = 0
        for i in self.__env:
            if i[0] == j:
                cnt = cnt + 1
            else:
                if cnt > max_num:
                    max_num = cnt
                    max_index = j
                j = i[0]
                cnt = 1

        # in case of one occurrence for each x
        if cnt > max_num:
            max_num = cnt
            max_index = j

        # if there are 5 or more buttons with the same (x)
        if max_num == 6:
            return True
        elif max_num < 5:
            return False

        arr = []
        for i in self.__env:
            if i[0] == max_index:
                arr.append(i[1])

        if self.check_sequence(arr):
            return True
        return False

    def agent_horizontal_line(self) -> bool:

        # sort the list by first element of each tuple (x)
        self.__agent.sort(key=lambda x: x[0])

        # find maximum number of buttons with the same (x)
        max_num = 0
        max_index = 0
        cnt = 0
        j = 0
        for i in self.__agent:
            if i[0] == j:
                cnt = cnt + 1
            else:
                if cnt > max_num:
                    max_num = cnt
                    max_index = j
                j = i[0]
                cnt = 1

        # in case of one occurrence for each x
        if cnt > max_num:
            max_num = cnt
            max_index = j

        # if there are 5 or more buttons with the same (x)
        if max_num == 6:
            return True
        elif max_num < 5:
            return False

        arr = []
        for i in self.__agent:
            if i[0] == max_index:
                arr.append(i[1])

        if self.check_sequence(arr):
            return True
        return False

    def env_diagonal_line(self) -> bool:

        temp_sum = 0
        temp_dif = 0

        # check for button left to top right line
        sum_4 = 0
        sum_5 = 0
        sum_6 = 0

        # check for top left to button right line
        dif__1 = 0
        dif_0 = 0
        dif_1 = 0

        for i in self.__env:
            temp_sum = i[0] + i[1]
            temp_dif = i[1] - i[0]

            if temp_sum == 4:
                sum_4 = sum_4 + 1
            elif temp_sum == 5:
                sum_5 = sum_5 + 1
            elif temp_sum == 6:
                sum_6 = sum_6 + 1

            if temp_dif == 1:
                dif_1 = dif_1 + 1
            elif temp_dif == 0:
                dif_0 = dif_0 + 1
            elif temp_dif == -1:
                dif__1 = dif__1 + 1

        if sum_4 == 5 or sum_6 == 5 or sum_5 == 6:
            return True

        if dif__1 == 5 or dif_1 == 5 or dif_0 == 6:
            return True

        if sum_5 == 5:
            arr = []
            for i in self.__env:
                if i[0] + i[1] == 5:
                    arr.append(i[0])
            if self.check_sequence(arr):
                return True

        if dif_0 == 5:
            arr = []
            for i in self.__env:
                if i[0] - i[1] == 0:
                    arr.append(i[0])
            if self.check_sequence(arr):
                return True

        return False

    def agent_diagonal_line(self) -> bool:

        temp_sum = 0
        temp_dif = 0

        # check for button left to top right line
        sum_4 = 0
        sum_5 = 0
        sum_6 = 0

        # check for top left to button right line
        dif__1 = 0
        dif_0 = 0
        dif_1 = 0

        for i in self.__agent:
            temp_sum = i[0] + i[1]
            temp_dif = i[1] - i[0]

            if temp_sum == 4:
                sum_4 = sum_4 + 1
            elif temp_sum == 5:
                sum_5 = sum_5 + 1
            elif temp_sum == 6:
                sum_6 = sum_6 + 1

            if temp_dif == 1:
                dif_1 = dif_1 + 1
            elif temp_dif == 0:
                dif_0 = dif_0 + 1
            elif temp_dif == -1:
                dif__1 = dif__1 + 1

        if sum_4 == 5 or sum_6 == 5 or sum_5 == 6:
            return True

        if dif__1 == 5 or dif_1 == 5 or dif_0 == 6:
            return True

        if sum_5 == 5:
            arr = []
            for i in self.__agent:
                if i[0] + i[1] == 5:
                    arr.append(i[0])
            if self.check_sequence(arr):
                return True

        if dif_0 == 5:
            arr = []
            for i in self.__agent:
                if i[0] - i[1] == 0:
                    arr.append(i[0])
            if self.check_sequence(arr):
                return True

        return False

    def check_sequence(self, arr):
        arr.sort()
        if np.array_equal(arr, [0, 1, 2, 3, 4]) or np.array_equal(arr, [1, 2, 3, 4, 5]):
            return True
        return False

    def remove_agent(self, positions):
        for i in positions:
            index = 0
            size = len(self.__agent)
            while index != size and not np.array_equal(self.__agent[index], i):
                index += 1
            if index != size:
                self.__agent.pop(index)
            else:
                raise ValueError('array not found in agent list.')

    def remove_env(self, positions):
        for i in positions:
            index = 0
            size = len(self.__env)
            while index != size and not np.array_equal(self.__env[index], i):
                index += 1
            if index != size:
                self.__env.pop(index)
            else:
                raise ValueError('array not found in env list.')

    def show_result(self, status):
        back = pygame.Surface(self.screen.get_size()).convert()

        if status == 0:
            pygame.display.set_caption('Draw!')
            back.fill((255, 0, 255))

        if status == 1:
            pygame.display.set_caption('Environment Won!')
            back.fill((0, 0, 255))

        if status == 2:
            pygame.display.set_caption('Agent Won!')
            back.fill((255, 0, 0))

        # update the screen
        self.screen.blit(back, (0, 0))
        pygame.display.flip()

    def get_state(self):

        state = [-1 for i in range(36)]

        for i in self.__env:
            state[i[0] * 6 + i[1]] = 1

        for i in self.__agent:
            state[i[0] * 6 + i[1]] = 0

        return np.array(state, dtype=int)

    @property
    def env(self):
        return self.__env

    @property
    def agent(self):
        return self.__agent

    @property
    def game_over(self):
        return self.__game_over

    @property
    def SCREEN_SIZE(self):
        return tuple(self.__screen_size)

    @property
    def SCREEN_W(self):
        return int(self.SCREEN_SIZE[0])

    @property
    def SCREEN_H(self):
        return int(self.SCREEN_SIZE[1])

    @property
    def CELL_W(self):
        return float(self.SCREEN_W) / float(self.maze_size[0])

    @property
    def CELL_H(self):
        return float(self.SCREEN_H) / float(self.maze_size[1])
