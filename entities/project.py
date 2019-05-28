
from util import draw_binary
from random import shuffle
from functools import partial
class Project():

    def __init__(self,
                 agent=None,
                 agent_list=None,
                 is_stretch_project=False,
                 determine_success_fn = None):
        if agent:
            self.agents = [agent]
            self.is_solo_project = True
            self.is_group_project = False
        elif agent_list:
            self.agents = agent_list
            self.is_solo_project = False
            self.is_group_project = True
        else:
            raise Exception("No agents provided to project!")

        if not determine_success_fn:
            self.is_successful = draw_binary(p=.5)
        else:
            self.is_successful = determine_success_fn(self)

        self.is_stretch = is_stretch_project

def project_function_factory(P,percent_women_at_above_level, type):

    # TODO: I have to clean this up at some point
    # Add in stereotype fit variables
    woman_boost_multiplier = P.project_promotability_boost_women_percent_of_men
    woman_drop_multiplier = P.project_promotability_drop_women_percent_of_men
    if percent_women_at_above_level < P.project_prototype_percentage_threshold:
        woman_boost_multiplier = 1 - ((1- woman_boost_multiplier) * P.project_prototype_boost_bias_multiplier)
        woman_drop_multiplier =  ((woman_drop_multiplier - 1) * P.project_prototype_drop_bias_multiplier) + 1

        if woman_boost_multiplier < 0:
            woman_boost_multiplier = 0
        if woman_drop_multiplier > 10:
            woman_drop_multiplier = 10

    if type == 'success':
        return partial(simple_project_promotability,
                       man_boost=(P.project_promotability_boost),
                       woman_boost=(P.project_promotability_boost*woman_boost_multiplier),
                       stretch_boost = P.project_promotability_stretch_multiplier,
                       woman_mixed_group_diff=P.project_women_mixed_group_percent_drop_success,
                       complaint_percentage=P.project_women_percent_complain_on_mixed_success,
                       complaint_boost_impact=P.project_women_additional_promotability_percent_drop_on_complain
                       )
    elif type == 'fail':
        return partial(simple_project_promotability,
                       man_boost=-(P.project_promotability_drop),
                       woman_boost=-(P.project_promotability_drop*woman_drop_multiplier),
                       stretch_boost=P.project_promotability_stretch_multiplier,
                       woman_mixed_group_diff=P.project_women_mixed_group_percent_increase_failure,
                       complaint_percentage=0.,
                       complaint_boost_impact=0.
                       )
    raise Exception("Not implemented project function")


def simple_project_promotability(proj,
                                 man_boost,
                                 woman_boost,
                                 stretch_boost,
                                 woman_mixed_group_diff,
                                 complaint_percentage,
                                 complaint_boost_impact):

    if proj.is_stretch:
        man_boost *= stretch_boost
        woman_boost *= stretch_boost

    if proj.is_solo_project:
        if proj.agents[0].is_male:
            proj.agents[0].promotability_perception += man_boost
        else:
            proj.agents[0].promotability_perception += woman_boost
    else:
        n_men = sum([a.is_male for a in proj.agents ])
        n_women = sum([not a.is_male for a in proj.agents])
        if n_men == 0:
            for a in proj.agents:
                a.promotability_perception += woman_boost
        elif n_women == 0:
            for a in proj.agents:
                a.promotability_perception += man_boost
        else:
            for a in proj.agents:
                if a.is_male:
                    a.promotability_perception += man_boost
                else:
                    indiv_woman_boost = woman_boost
                    if complaint_percentage > 0 and draw_binary(p=complaint_percentage):
                        indiv_woman_boost = woman_boost*(complaint_boost_impact)
                    a.promotability_perception += woman_mixed_group_diff*indiv_woman_boost



def assign_projects(param_holder, company_level, turn, level_index):
    if param_holder.project_assignment_method == "equal_solo_group_within_level":
        # Shuffle around the hierarchy
        shuffle(company_level)

        # Assign projects

        agent_start_index = 0
        projects = []

        # Assign stretch project, if its time to do so

        if turn % param_holder.project_turns_per_stretch == 0:
            for index, agent in enumerate(company_level):
                min_proj = (param_holder.project_min_men_stretch_project if agent.is_male else
                            param_holder.project_min_women_stretch_project)
                min_proj += param_holder.project_stretch_min_level_multiplier*level_index
                if agent.num_successful_projects > min_proj:
                    projects.append(Project(agent=agent, is_stretch_project=True))
                    # put the agent at the front of the company level
                    # and then start assigning projects at index 1
                    # to make sure we don't assign 2 projects to this person
                    company_level = [agent] + company_level[0:index] + company_level[(index+1):]
                    agent_start_index = 1
                    break

        n_agents_to_assign_to = len(company_level) - agent_start_index
        # First half are solo projects
        solo_proj_len = n_agents_to_assign_to / 2
        solo_proj_len = solo_proj_len - 1 if not n_agents_to_assign_to % 2 else solo_proj_len
        projects = [Project(agent=company_level[i]) for i in range(agent_start_index,solo_proj_len)]

        # Second half are group projects
        projects += [Project(agent_list=company_level[i:i + 2])
                     for i in range(solo_proj_len, len(company_level), 2)]

        return projects

