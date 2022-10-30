import random


class Trainer(object):
    """Runs games for given agents. Optionally will visualise and save the results"""
    def __init__(self, config, agents):
        self.config = config
        self.agents = agents
        self.results = None
        self.colors = ["red", "blue", "green", "orange", "yellow", "purple"]
        self.colour_ix = 0

    def run_games_for_agents(self):
        """Run a set of games for each agent. Optionally visualising and/or saving the results"""
        self.results = {}
        for agent_number, agent_class in enumerate(self.agents):
            agent_name = agent_class.agent_name
            self.run_games_for_agent(agent_number + 1, agent_class)
        # plt.show()
        return self.results

    def run_games_for_agent(self, agent_number, agent_class):
        """Runs a set of games for a given agent, saving the results in self.results"""
        agent_results = []
        agent_name = agent_class.agent_name
        agent_group = "DQN_Agents"
        agent_round = 1
        for run in range(self.config.runs_per_agent):
            agent_config = self.config

            if self.config.randomise_random_seed: agent_config.seed = random.randint(0, 2**32 - 2)
            agent_config.hyperparameters = agent_config.hyperparameters[agent_group]
            print("AGENT NAME: {}".format(agent_name))
            print("\033[1m" + "{}.{}: {}".format(agent_number, agent_round, agent_name) + "\033[0m", flush=True)
            agent = agent_class(agent_config)
            self.environment_name = agent.environment_title
            print(agent.hyperparameters)
            print("RANDOM SEED ", agent_config.seed)
            game_scores, rolling_scores, time_taken = agent.run_n_episodes()
            print("Time taken: {}".format(time_taken), flush=True)
            self.print_two_empty_lines()
            agent_results.append([game_scores, rolling_scores, len(rolling_scores), -1 * max(rolling_scores), time_taken])
            agent_round += 1
        self.results[agent_name] = agent_results

    def print_two_empty_lines(self):
        print("-----------------------------------------------------------------------------------")
        print("-----------------------------------------------------------------------------------")
        print(" ")
