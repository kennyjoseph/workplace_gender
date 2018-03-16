# Just an example of how to plot some results
library(data.table)
library(ggplot2)
library(scales)
sim_res <- rbind(fread("../output/turn_output_0.tsv"),
                 fread("../output/turn_output_1.tsv"))
setnames(sim_res, c("n_men","n_women","turn","level_iter","run_number","replication_number"))

params <- fread("../output/experiment_details.csv")
sim_res <- merge(sim_res,params, by="run_number")
sim_res <- sim_res[turn %% 24 == 0]
sim_res$turn <- sim_res$turn / 24 + 1
theme_set(theme_bw(20))
sim_res$level_iter <- paste("Level",8-sim_res$level_iter)
p <- ggplot(sim_res[competence_mean_women == 50],aes(turn,n_men/(n_men+n_women),
                                            color=factor(project_competence_percent_variance_boost_women)))
p <- p + geom_smooth()  + geom_hline(yintercept = .5)
p <- p + facet_wrap(~level_iter,ncol=2) + scale_color_manual("Competence Boost\nFor Women\n(Men constant @ .05)",values=c("blue","red"))
p <- p + scale_y_continuous("Percent Men at Level", labels=percent) + xlab("Promotion Cycle")
p <- p + scale_x_continuous(limits=c(1,10),breaks=c(1,2,4,6,8,10))
ggsave("boost_diff.pdf",p,h=8,w=8)
