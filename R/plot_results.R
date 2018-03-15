# Just an example of how to plot some results
library(data.table)
library(ggplot2)
sim_res <- rbind(fread("../output/turn_output_0.tsv"),
                 fread("../output/turn_output_1.tsv"))
setnames(sim_res, c("n_men","n_women","turn","level_iter","run_number","replication_number"))

params <- fread("../output/experiment_details.csv")
sim_res <- merge(sim_res,params, by="run_number")
sim_res <- sim_res[turn %% 13 == 0]
sim_res$turn <- sim_res$turn / 13
ggplot(sim_res[run_number==0],aes(turn,n_men/(n_men+n_women),color=factor(replication_number))) + geom_line() + facet_wrap(~level_iter) + geom_hline(yintercept = .5)
