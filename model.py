from util import *
import yaml
import gzip
from multiprocessing import Pool
from functools import partial

def model_runner(chunk_data,default_param_file,n_replications):

    chunk_num, chunk = chunk_data

    default_params_dict = yaml.load(open(default_param_file))

    turn_output_file = gzip.open("output/turn_output_{i}.tsv.gz".format(i=chunk_num),"w")
    agent_output_file = gzip.open("output/agent_output_{i}.tsv.gz".format(i=chunk_num),"w")
    for i,row in enumerate(chunk):
        if i % 1000 == 0:
            print chunk_num, i
        for replication in range(n_replications):
            #print replication
            params_dict = default_params_dict.copy()
            params_dict.update(row)
            params_dict['replication_number'] = replication
            params_dict['run_number'] = int(params_dict['run_number'])
            params_dict['turn_output_file'] = turn_output_file
            params_dict['agent_output_file'] = agent_output_file
            run_single_model(params_dict)

    turn_output_file.close()
    agent_output_file.close()


def run_single_model(params_dict):

    P = ParameterHolder(params_dict)

    # the list of currently active agents at the base of the company
    agents = []

    # Okay, start the simulation
    for proj_iter in range(P.n_projects):

        # If agents have left the company, or been promoted (or at the start of the simulation)
        # we need to "replenish" the set of agents
        # note: this is super slow b/c we're drawing each agent individually. Who cares for now.
        while len(agents) < P.agent_size:
            # determine the agent's sex
            new_agent_sex = draw_binary(p=P.percent_male)

            # determine their competence and likeability (again, pretty verbose here, but whatever)
            competence_mean = (P.competence_mean_men if new_agent_sex == MALE else P.competence_mean_women)
            competence_sigma = (P.competence_sigma_men if new_agent_sex == MALE else P.competence_sigma_women)
            competence = np.random.normal(competence_mean,competence_sigma)
            agents.append(Agent(new_agent_sex, competence, -1, proj_iter, len(agents)))

        # Okay, now we start on the project

        # Pick the project members = for now, totally randomly
        num_project_members = np.random.poisson(P.rate_of_project_member_distribution, 1)[0] + 1
        if num_project_members > P.agent_size:
            num_project_members = P.agent_size

        project_members = np.random.choice(agents, num_project_members, replace=False)
        num_men = len([x for x in project_members if x.sex == MALE])
        num_women = num_project_members - num_men

        # Is the project successful? 1 for yes, 0 for no
        project_success = draw_binary(p=P.project_success_rate)

        # determine how much credit (i.e. increased competence perception) agents get
        # Credit is positive if the project was successful and negative otherwise
        # And there is a standard amount of credit to be given out per agent
        project_competence_credit = num_project_members * project_success * P.competence_credit_factor

        # (Potentially) update competence, likeability and their perceptions
        for group_member in project_members:
            # increase number of projects for agent
            if project_success:
                group_member.num_successful_projects += 1
            else:
                group_member.num_failed_projects += 1

            # as you do more projects, your competence increases, but perceptions of it do not
            group_member.competence += P.project_performed_competence_increase_factor

            solo_project_attribute_to_luck_rate = (P.solo_project_attribute_to_luck_rate_men
                                                   if group_member.sex == MALE else
                                                   P.solo_project_attribute_to_luck_rate_women)

            # Distribute credit for the project success/failure
            if num_project_members == 1:

                # Are we just going to attribute a success to luck and not increase perceived competence?
                attribute_to_luck_rate = project_success * solo_project_attribute_to_luck_rate
                will_attribute_to_luck = draw_binary(p=attribute_to_luck_rate)

                # if not attibuting to luck, then we increase perception of the agent's competence
                group_member.competence_perception += (1-will_attribute_to_luck) * project_competence_credit

            else:

                # how many people of the same sex are there?
                project_sex_size = num_men if group_member.sex == MALE else num_women

                # set amount of credit for man vs woman
                if group_member.sex == MALE:
                    percent_credit = (P.percent_credit_success_to_men if project_success
                                      else P.percent_credit_failure_to_men)
                else:
                    percent_credit = ((1 - P.percent_credit_success_to_men) if project_success
                                      else (1-P.percent_credit_failure_to_men))

                # you get 1/Num.M/F * competence credit * M/F percent of total credit
                credit_magnitude = (1. / project_sex_size *
                                    project_competence_credit *
                                    percent_credit)
                if not project_success:
                    # if its a failure, competence perceptions decrease
                    credit_magnitude *= -1.

                group_member.competence_perception += credit_magnitude

        # Write out 1 out of every 25 projects
        if proj_iter % 25 == 0:
            # compute statistics to write out for analysis
            mean_female_comp_perc = np.mean([a.competence_perception for a in agents if a.sex == FEMALE])
            mean_male_comp_perc = np.mean([a.competence_perception for a in agents if a.sex == MALE])
            mean_female_competence = np.mean([a.competence for a in agents if a.sex == FEMALE])
            mean_male_competence = np.mean([a.competence for a in agents if a.sex == MALE])
            n_male = len([a for a in agents if a.sex == MALE])
            n_female = len([a for a in agents if a.sex == FEMALE])

            P.turn_output_file.write(tsn([mean_female_comp_perc,
                                        mean_male_comp_perc,
                                        mean_female_competence,
                                        mean_male_competence,
                                        n_male,n_female,proj_iter,
                                        P.run_number,
                                        P.replication_number]))

        if proj_iter > 0 and proj_iter % P.projects_per_decision_period == 0:
            #print proj_iter

            # We'll promote K agents, probabilistically, based on their perceived competence
            perceived_competences = scale_to_probability(np.array([a.competence_perception for a in agents]))
            agents_to_promote = np.random.choice(agents,
                                                 size=int(P.num_agents_to_promote),
                                                 p=perceived_competences,
                                                 replace=False)

            for agent in agents_to_promote:
                P.agent_output_file.write("PROMOTED\t{itr}\t{repl}\t".format(itr=proj_iter,repl=P.run_number)
                                        + agent.to_string())

            promoted_indices = {a.index for a in agents_to_promote}

            # K agents will leave the company, based on the difference between their actual and percieved competence
            not_promoted_agents = [a for a in agents if a.index not in promoted_indices]
            actual_perceived_comp_diff = np.array([a.competence_perception - a.competence for a in not_promoted_agents])
            actual_perceived_diff_prob = scale_to_probability(actual_perceived_comp_diff)

            agents_that_leave = np.random.choice(not_promoted_agents,
                                                 size=int(P.num_agents_to_leave),
                                                 p=actual_perceived_diff_prob,
                                                 replace=False)

            for agent in agents_that_leave:
                P.agent_output_file.write("LEFT\t{itr}\t{repl}\t".format(itr=proj_iter,repl=P.run_number)
                                        + agent.to_string())

            removed_indices = {a.index for a in agents_to_promote.tolist() + agents_that_leave.tolist()}
            agents = [a for a in agents if a.index not in removed_indices]





n_chunks = 16

experiment_details = yaml.load(open("experiment.yaml"))

experimental_runs = expand_grid(experiment_details)
experimental_runs = experimental_runs.reset_index().rename(index=str,columns={"index":"run_number"})


experimental_runs.to_csv("output/experiment_details.csv",index=False)
experimental_runs = [x[1].to_dict() for x in experimental_runs.iterrows()]
chunked = list(chunks(experimental_runs, int(len(experimental_runs) / n_chunks) + 1))
chunked = list(enumerate(chunked))

runner_partial = partial(model_runner,
                         default_param_file="default_params.yaml",
                         n_replications=5)

runner_partial(chunked[0])

#
# p = Pool(n_chunks)
#
# print "N experimental conditions per chunk: ", len(chunked[0][1])
# print "N total experiments: ", len(chunked[0][1])*5
#

# res = p.map(runner_partial, chunked)
# p.close()
# p.terminate()