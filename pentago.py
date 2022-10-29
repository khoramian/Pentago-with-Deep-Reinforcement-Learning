import numpy as np
import gym
from gym import error, spaces, utils
from gym.utils import seeding
from gym_pentago.pent_view_2d import PentagoView2D
import time


class PentagoEnv(gym.Env):
    """
        Description:
            A Pentago board game simulator.

        Observation:
            Type: Box(36)  (-1 empty position, 0 agent position, 1 env position)
            Num     Observation               Min                     Max
            0       Button 0,0                -1                      1
            1       Button 0,1                -1                      1
            .
            .
            .
            35       Button 5,5               -1                      1

        Actions:
            Type: Box(3)
            Num     Action                     Min                     Max
            0       Button x coordinate        0                       5
            1       Button y coordinate        0                       5
            2       Board quarter to turn      0                       3
    """
    metadata = {
        "render.modes": ["human", "rgb_array"],
    }

    def __init__(self, maze_size=(6, 6), enable_render=True):
        self.enable_render = enable_render

        if maze_size:
            self.maze_view = PentagoView2D(maze_size=maze_size, screen_size=(640, 640), enable_render=enable_render)
        else:
            raise AttributeError("One must supply the maze_size (2D)")

        self.maze_size = self.maze_view.maze_size

        # Action space
        low = np.zeros((3,), dtype=int)
        high = np.array([5, 5, 3], dtype=int)
        self.action_space = spaces.Box(low, high, dtype=int)

        # Observation space
        low = np.zeros((36,), dtype=int) - np.ones((36,), dtype=int)
        high = np.ones((36,), dtype=int)
        self.observation_space = spaces.Box(low, high, dtype=int)

        # initial condition
        self.state = None
        self.done = False
        self.status = 0

        # Simulation related variables
        self.seed()
        self.reset()

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def close(self):
        if self.enable_render is True:
            self.maze_view.quit_game()

    def step(self, agent_action):
        taken = False
        reward = 0.0
        self.done = False
        self.status = 0

        if self.action_space.contains(agent_action) is False:
            raise AttributeError("Must supply an action from Action Box")

        if self.maze_view.is_taken(agent_action[0:2]):
            taken = True
            reward = -1
            self.state = self.maze_view.get_state()
            return self.state, reward, self.done, {taken}

        self.maze_view.play_agent(agent_action)

        env_win = self.maze_view.env_horizontal_line() or self.maze_view.env_vertical_line() or self.maze_view.env_diagonal_line()
        agent_win = self.maze_view.agent_horizontal_line() or self.maze_view.agent_vertical_line() or self.maze_view.agent_diagonal_line()

        if env_win and agent_win:
            self.done = True
        elif env_win:
            self.done = True
            reward = -30.0
            self.status = 1
        elif agent_win:
            self.done = True
            reward = 30.0
            self.status = 2
        elif len(self.maze_view.env) + len(self.maze_view.agent) == self.maze_size[0] * self.maze_size[0]:
            self.done = True

        if self.done is False:
            if self.enable_render is True:
                self.render()
        else:
            self.state = self.maze_view.get_state()
            return self.state, reward, self.done, {taken}

        self.done = False
        self.status = 0
        reward = 0.0
        taken = False

        env_action = self.action_space.sample()

        while self.maze_view.is_taken(env_action[0:2]):
            env_action = self.action_space.sample()

        self.maze_view.play_env(env_action)

        env_win = self.maze_view.env_horizontal_line() or self.maze_view.env_vertical_line() or self.maze_view.env_diagonal_line()
        agent_win = self.maze_view.agent_horizontal_line() or self.maze_view.agent_vertical_line() or self.maze_view.agent_diagonal_line()

        if env_win and agent_win:
            self.done = True
        elif env_win:
            self.done = True
            reward = -30.0
            self.status = 1
        elif agent_win:
            self.done = True
            reward = 30.0
            self.status = 2
        elif len(self.maze_view.env) + len(self.maze_view.agent) == self.maze_size[0] * self.maze_size[0]:
            self.done = True

        self.state = self.maze_view.get_state()
        return self.state, reward, self.done, {taken}

    def reset(self):
        self.maze_view.reset_pent()
        self.state = self.maze_view.get_state()
        self.done = False
        self.status = 0
        return self.state

    def render(self, mode="human", close=False):
        if self.state is None:
            return None
        if close:
            self.maze_view.quit_game()

        x = self.maze_view.update(mode)
        time.sleep(0.1)
        return x

    def show_result(self):
        self.maze_view.show_result(self.status)
        time.sleep(1)
