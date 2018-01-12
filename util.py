import functools
import numpy as np
import pandas as pd
from itertools import product

###### Constants
MALE = 0
FEMALE = 1

# make it more obvious and succinct to draw a single binary variable
draw_binary = functools.partial(np.random.binomial, n=1)

np.set_printoptions(suppress=True)


def tsn(x):
    return "\t".join([str(y) if type(y) is int else '{:.5f}'.format(y) for y in x]) + "\n"

class Agent:
    # For now, the agent is basically just a container.
    # It should probably be a bit more than that at some point, but the simulation is
    # small ehough right now we can keep all the logic in one place
    def __init__(self,
                 sex,
                 competence,
                 likeability,
                 time_of_creation,
                 agent_index):
        # set the (for now, binary) sex, and the continuous competence/likeability scores
        self.sex = sex
        self.competence = competence
        self.likeability = likeability

        # set others perception of their likeability and competence to the actual values
        self.competence_perception = self.competence
        self.likeability_perception = self.likeability

        # Things we'll use to look at outcome variables
        self.time_of_creation = time_of_creation
        self.num_successful_projects = 0
        self.num_failed_projects = 0
        self.original_competence = competence

        self.index = agent_index


    def to_string(self):
        return tsn([self.sex,self.competence,self.competence_perception,
                    self.time_of_creation, self.num_successful_projects,
                    self.num_failed_projects,self.original_competence])



class ParameterHolder(object):
  def __init__(self, adict):
    self.__dict__.update(adict)



def scale_to_probability(x):
    exp_x = np.exp(x)
    exp_x = exp_x / (1 + np.sum(exp_x))
    return exp_x/np.sum(exp_x)


def expand_grid(dictionary):
    return pd.DataFrame([row for row in product(*dictionary.values())],
                        columns=dictionary.keys())


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i + n]

