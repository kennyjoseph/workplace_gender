from util import *
from entities import *
import yaml
from multiprocessing import Pool
from functools import partial
from random import seed
import sys
import os

def model_runner(chunk_data,default_param_file,n_replications, output_folder):

    chunk_num, chunk = chunk_data

    default_params_dict = yaml.load(open(default_param_file))

    #turn_output_file = gzip.open("output/turn_output_{i}.tsv.gz".format(i=chunk_num),"w")
    turn_output_file = open(os.path.join(output_folder,"turn_output_{i}.tsv".format(i=chunk_num)),"w")
    #agent_output_file = gzip.open("output/agent_output_{i}.tsv.gz".format(i=chunk_num),"w")
    for i,row in enumerate(chunk):
        if i % 1000 == 0:
            print chunk_num, i
        for replication in range(n_replications):
            print "\t", replication
            #print replication
            params_dict = default_params_dict.copy()
            params_dict.update(row)
            params_dict['replication_number'] = replication
            params_dict['run_number'] = int(params_dict['run_number'])
            params_dict['turn_output_file'] = turn_output_file
            #params_dict['agent_output_file'] = agent_output_file
            run_single_model(params_dict)

    turn_output_file.close()
    #agent_output_file.close()




def run_single_model(params_dict):

    P = ParameterHolder(params_dict)

    # How is agent competence/likeability determined?
    agent_competence_fn = competence_function_factory(P)
    agent_likeability_fn = likeability_function_factory(P)

    # What happens on project success and failure?
    proj_success_fn = project_function_factory(P,'success')
    proj_failure_fn = project_function_factory(P,'fail')

    # Functions for new agents
    initial_level_sex_fn = sex_function_factory(P, len(P.hierarchy_sizes)-1)

    # How agents are promoted
    promotion_function = promotion_function_factory(P)

    # How agents decide to leave
    leave_function = leave_function_factory(P)

    # Initialize the company
    company_hierarchy = []
    for level, level_size in enumerate(P.hierarchy_sizes):
        sex_fn = sex_function_factory(P, level)
        company_hierarchy.append([Agent(sex_function = sex_fn,
                                        competence_function=agent_competence_fn,
                                        likeability_function=agent_likeability_fn,
                                        time_of_creation=0)
                                  for _ in range(level_size)])

    # Okay, start the simulation

    # For each project cycle
    for turn in range(P.n_project_cycles):
        #### Print stats about the company
        print_stats(P, turn, company_hierarchy)

        # For each hierarchy level
        for company_level in company_hierarchy:

            ##### Assign Projects
            projects = assign_projects(P, company_level)

            #### Carry out the projects
            for project in projects:
                # Is the project successful? 1 for yes, 0 for no
                if project.is_successful:
                    proj_success_fn(project)
                else:
                    proj_failure_fn(project)

        # If its a promotion period
        if turn % P.projects_per_promotion_cycle == 0:

            ### Compute the turnover at the company
            for level_iter, company_level in enumerate(company_hierarchy):
                # See who leaves
                leaving_agents, staying_agents = leave_function(P,company_level,level)
                # Remove them
                company_hierarchy[level_iter] = staying_agents

            ### Now, promote up, starting at the bottom
            for level_iter, company_level in enumerate(company_hierarchy[:-1]):
                # find the top K at the level below me
                hire_from = company_hierarchy[level_iter + 1]
                agents_to_hire, agents_remaining = promotion_function(hire_from,
                                                                      P.hierarchy_sizes[level_iter]-len(company_level))
                # promote them
                company_hierarchy[level_iter] = company_level + agents_to_hire
                # leave the remaining agents
                company_hierarchy[level_iter + 1] = agents_remaining


            ### Add new agents to the bottom
            new_agents = [Agent(sex_function = initial_level_sex_fn,
                                competence_function=agent_competence_fn,
                                likeability_function=agent_likeability_fn,
                                time_of_creation=turn)
                          for _ in range(P.hierarchy_sizes[-1] - len(company_hierarchy[-1]))]

            company_hierarchy[-1] = company_hierarchy[-1] + new_agents



sys.argv = ['','experiment.yaml','default_params.yaml','output','5','2','0']
if __name__ == "__main__":

    if len(sys.argv) != 6:
        print 'Usage: python model.py [path to experiment file] ',
        print '[path to default params file] [path to desired output folder] ',
        print ' [n_replications_per_condition] [n_cores] [random seed]'


    experiment_file, default_params_file, output_folder, n_replications, n_cores, rseed = sys.argv[1:]

    seed(int(rseed))

    n_replications = int(n_replications)
    n_cores = int(n_cores)

    experiment_details = yaml.load(open(experiment_file))

    print experiment_details
    experimental_runs = expand_grid(experiment_details)
    experimental_runs = experimental_runs.reset_index().rename(index=str,columns={"index":"run_number"})

    experimental_runs.to_csv(os.path.join(output_folder, "experiment_details.csv"),index=False)
    experimental_runs = [x[1].to_dict() for x in experimental_runs.iterrows()]
    chunked = list(chunks(experimental_runs, int(len(experimental_runs) / n_cores) + 1))
    chunked = list(enumerate(chunked))

    runner_partial = partial(model_runner,
                             default_param_file=default_params_file,
                             n_replications=n_replications,
                             output_folder=output_folder)

    print "N experimental conditions per chunk: ", len(chunked[0][1])
    print "N total experiments: ", len(chunked[0][1])*n_replications

    if n_cores > 1:
        p = Pool(n_cores)
        res = p.map(runner_partial, chunked)
        p.close()
        p.terminate()
    else:
        # run on single process
        for c in chunked:
            runner_partial(c)