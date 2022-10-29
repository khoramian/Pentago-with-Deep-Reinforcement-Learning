from gym.envs.registration import register

register(
    id='pentago-v0',
    entry_point='gym_pentago.envs:PentagoEnv',
)
