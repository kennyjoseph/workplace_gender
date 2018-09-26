from functools import partial
from math import ceil
from random import shuffle

# PROMOTION
def promotion_function_factory(P):
    if P.promotion_model == "top_nonrandom_promotability":
        return get_top_k_by_promotability


def get_top_k_by_promotability(hire_from, n_to_hire):
    hf = sorted(hire_from,
                key=lambda x: x.promotability_perception,
                reverse=True)
    return hf[:n_to_hire], hf[n_to_hire:]

### Leave Functions ####
def leave_function_factory(P):
    if P.leave_function_type == "simple":
        return simple_leave_fn

def simple_leave_fn(P, agents, level):
    # how many agents should leave?
    n_to_leave = int(ceil(P.pct_leave_at_level[level] * len(agents)))

    # select randomly
    shuffle(agents)

    return agents[:n_to_leave], agents[n_to_leave:]
