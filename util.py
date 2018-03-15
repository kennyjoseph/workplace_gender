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


def print_stats(P, turn, company_hierarchy):

    # Write out number of men and women at each level
    for level_iter, level in enumerate(company_hierarchy):
        n_men = sum([agent.is_male for agent in level])
        n_women = len(level) - n_men
        P.turn_output_file.write(tsn([n_men,n_women,turn,level_iter,
                                     P.run_number,P.replication_number]))


    # mean_female_comp_perc = np.mean([a.competence_perception for a in agents if a.sex == FEMALE])
    # mean_male_comp_perc = np.mean([a.competence_perception for a in agents if a.sex == MALE])
    # mean_female_competence = np.mean([a.competence for a in agents if a.sex == FEMALE])
    # mean_male_competence = np.mean([a.competence for a in agents if a.sex == MALE])
    # n_male = len([a for a in agents if a.sex == MALE])
    # n_female = len([a for a in agents if a.sex == FEMALE])
    #
    # P.turn_output_file.write(tsn([mean_female_comp_perc,
    #                               mean_male_comp_perc,
    #                               mean_female_competence,
    #                               mean_male_competence,
    #                               n_male, n_female, proj_iter,
    #                               P.run_number,
    #                               P.replication_number]))




