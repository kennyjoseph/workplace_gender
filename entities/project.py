
from util import draw_binary
from random import shuffle
from functools import partial
class Project():

    def __init__(self,agent=None,agent_list=None, determine_success_fn = None):
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



def project_function_factory(P,type):
    if type == 'success':
        return partial(simple_project_competence,
                       man_boost=(P.competence_sigma_men*
                                  P.project_competence_percent_variance_boost_men),
                       woman_boost=(P.competence_sigma_men*
                                    P.project_competence_percent_variance_boost_women),
                       woman_mixed_group_diff=P.project_women_mixed_group_percent_drop_success
                       )
    elif type == 'fail':
        return partial(simple_project_competence,
                       man_boost=-(P.competence_sigma_men*
                                  P.project_competence_percent_variance_drop_men),
                       woman_boost=-(P.competence_sigma_men*
                                    P.project_competence_percent_variance_drop_women),
                       woman_mixed_group_diff=P.project_women_mixed_group_percent_increase_failure
                       )
    raise Exception("Not implemented project function")


def simple_project_competence(proj, man_boost,woman_boost, woman_mixed_group_diff):
    if proj.is_solo_project:
        if proj.agents[0].is_male:
            proj.agents[0].competence_perception += man_boost
        else:
            proj.agents[0].competence_perception += woman_boost
    else:
        n_men = sum([a.is_male for a in proj.agents ])
        n_women = sum([not a.is_male for a in proj.agents])
        if n_men == 0:
            for a in proj.agents:
                a.competence_perception += man_boost
        elif n_women == 0:
            for a in proj.agents:
                a.competence_perception += woman_boost
        else:
            for a in proj.agents:
                if a.is_male:
                    a.competence_perception += man_boost
                else:
                    a.competence_perception += woman_mixed_group_diff*woman_boost



def assign_projects(param_holder, company_level):
    if param_holder.project_assignment_method == "equal_solo_group_within_level":
        # Shuffle around the hierarchy
        shuffle(company_level)

        # Assign projects

        # First half are solo projects
        solo_proj_len = len(company_level) / 2
        solo_proj_len = solo_proj_len + 1 if not len(company_level) % 2 else solo_proj_len
        projects = [Project(agent=company_level[i]) for i in range(solo_proj_len)]

        # Second half are group projects
        projects += [Project(agent_list=company_level[i:i + 2])
                     for i in range(solo_proj_len, len(company_level), 2)]

        return projects

