import numpy as np
from util import MALE, tsn, draw_binary
from functools import partial

class Agent:
    # For now, the agent is basically just a container.
    # It should probably be a bit more than that at some point, but the simulation is
    # small ehough right now we can keep all the logic in one place
    def __init__(self,
                 sex_function,
                 competence_function,
                 likeability_function,
                 time_of_creation):
        # set the (for now, binary) sex, and the continuous competence/likeability scores
        self.sex = sex_function()
        if self.sex == MALE:
            self.is_male = True
        else:
            self.is_male = False
        self.competence = competence_function(self)
        self.likeability = likeability_function(self)

        # set others perception of their likeability and competence to the actual values
        self.competence_perception = self.competence
        self.likeability_perception = self.likeability

        # Things we'll use to look at outcome variables
        self.time_of_creation = time_of_creation
        self.num_successful_projects = 0
        self.num_failed_projects = 0
        self.original_competence = self.competence

    def to_string(self):
        return tsn([self.sex,self.competence,self.competence_perception,
                    self.time_of_creation, self.num_successful_projects,
                    self.num_failed_projects,self.original_competence])


#### Sex functions #####
def sex_function_factory(P, level):
    if P.sex_function_type == "simple":
        return partial(draw_binary, p=P.pct_male_at_level[level])
    else:
        raise Exception("sex function not implemented")


### Competence Functions #####

def competence_function_factory(P):
    if P.competence_function_type == "simple":
        return partial(draw_competence,
                          mean_men = P.competence_mean_men,
                          mean_women = P.competence_mean_women,
                          sigma_men = P.competence_sigma_men,
                          sigma_women = P.competence_sigma_women)

def draw_competence(agent, mean_men, mean_women, sigma_men, sigma_women):
    competence_mean = (mean_men if agent.is_male else mean_women)
    competence_sigma = (sigma_men if agent.is_male else sigma_women)
    return np.random.normal(competence_mean, competence_sigma)


def likeability_function_factory(P):
    return draw_likeability

def draw_likeability(agent):
    return -1