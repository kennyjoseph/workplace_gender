import numpy as np
from util import MALE, tsn, draw_binary
from functools import partial

class Agent:
    # For now, the agent is basically just a container.
    # It should probably be a bit more than that at some point, but the simulation is
    # small ehough right now we can keep all the logic in one place
    def __init__(self,
                 sex_function,
                 promotability_function,
                 time_of_creation):
        # set the (for now, binary) sex, and the continuous promotability score
        self.sex = sex_function()
        if self.sex == MALE:
            self.is_male = True
        else:
            self.is_male = False
        self.promotability = promotability_function(self)

        # set others perception of their promotability to the actual values
        self.promotability_perception = self.promotability

        # Things we'll use to look at outcome variables
        self.time_of_creation = time_of_creation
        self.num_successful_projects = 0
        self.num_failed_projects = 0
        self.original_promotability = self.promotability

    def to_string(self):
        return tsn([self.sex,self.promotability,self.promotability,
                    self.time_of_creation, self.num_successful_projects,
                    self.num_failed_projects,self.original_promotability])


#### Sex functions #####
def sex_function_factory(P, level):
    if P.sex_function_type == "simple":
        return partial(draw_binary, p=P.pct_male_at_level[level])
    else:
        raise Exception("sex function not implemented")


### Promotability Functions #####

def promotability_function_factory(P):
    if P.promotability_function_type == "simple":
        return partial(draw_promotability,
                          mean_men = P.promotability_mean_men,
                          mean_women = P.promotability_mean_women,
                          sigma_men = P.promotability_sigma_men,
                          sigma_women = P.promotability_sigma_women)

def draw_promotability(agent, mean_men, mean_women, sigma_men, sigma_women):
    promotability_mean = (mean_men if agent.is_male else mean_women)
    promotability_sigma = (sigma_men if agent.is_male else sigma_women)
    return np.random.normal(promotability_mean, promotability_sigma)
