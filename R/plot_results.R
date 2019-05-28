# Just an example of how to plot some results
library(data.table)
library(ggplot2)
library(scales)
library(Hmisc)
theme_set(theme_bw(20))
sim_res <- rbind(fread("../out2/turn_output_0.tsv"),
                 fread("../out2/turn_output_1.tsv"),
                 fread("../out2/turn_output_2.tsv"),
                 fread("../out2/turn_output_3.tsv"),
                 fread("../out2/turn_output_4.tsv"),
                 fread("../out2/turn_output_5.tsv"))

#sim_res <- fread("../out/turn_output_0.tsv")


setnames(sim_res, c("fem_prom", "fem_suc", "fem_fail",
                    "male_prom","male_suc","male_fail",
                    "n_men","n_women","turn","level_iter","run_number","replication_number"))
params <- fread("../out2/experiment_details.csv")
sim_res <- merge(sim_res,params, by="run_number")
sim_res <- sim_res[turn %% 24 == 0]
sim_res$turn <- sim_res$turn / 24 + 1
sim_res$level_iter <- paste("Level",8-sim_res$level_iter)



# Boost/drop
p <- ggplot(sim_res,aes(turn,n_men/(n_men+n_women),
                                            color=level_iter))
p <- p  + stat_summary(fun.data="mean_cl_boot") + stat_summary(fun.y="mean",geom="line",size=1.2)  + geom_hline(yintercept = .5)
p <- p + facet_grid(project_promotability_boost_women_percent_of_men~project_promotability_drop_women_percent_of_men)+ scale_color_discrete("")
p <- p + scale_y_continuous("Percent Men at Level", labels=percent) + xlab("Promotion Cycle")
p <- p + scale_x_continuous(limits=c(1,10),breaks=c(1,2,4,6,8,10))
ggsave("boost_diff.jpeg",p,h=10,w=12)


# mixed group effects
p <- ggplot(sim_res,aes(turn,n_men/(n_men+n_women),color=level_iter))
p <- p  + stat_summary(fun.data="mean_cl_boot") + stat_summary(fun.y="mean",geom="line",size=1.2)  + geom_hline(yintercept = .5)
p <- p + facet_grid(project_women_mixed_group_percent_drop_success~project_women_mixed_group_percent_increase_failure)+ scale_color_discrete("")
p <- p + scale_y_continuous("Percent Men at Level", labels=percent) + xlab("Promotion Cycle")
p <- p + scale_x_continuous(limits=c(1,10),breaks=c(1,2,4,6,8,10))
ggsave("mixed_group_diff.jpeg",p,h=10,w=12)

# complain effects
p <- ggplot(sim_res,aes(turn,n_men/(n_men+n_women),color=level_iter))
p <- p  + stat_summary(fun.data="mean_cl_boot") + stat_summary(fun.y="mean",geom="line",size=1.2)  + geom_hline(yintercept = .5)
p <- p + facet_grid(project_women_additional_promotability_percent_drop_on_complain~project_women_percent_complain_on_mixed_success)+ scale_color_discrete("")
p <- p + scale_y_continuous("Percent Men at Level", labels=percent) + xlab("Promotion Cycle")
p <- p + scale_x_continuous(limits=c(1,10),breaks=c(1,2,4,6,8,10))
ggsave("complain.jpeg",p,h=10,w=12)


# stretch effects
p <- ggplot(sim_res,aes(turn,n_men/(n_men+n_women),color=level_iter))
p <- p  + stat_summary(fun.data="mean_cl_boot") + stat_summary(fun.y="mean",geom="line",size=1.2)  + geom_hline(yintercept = .5)
p <- p + facet_grid( project_promotability_stretch_multiplier~ project_min_men_stretch_project +project_min_women_stretch_project)+ scale_color_discrete("")
p <- p + scale_y_continuous("Percent Men at Level", labels=percent) + xlab("Promotion Cycle")
p <- p + scale_x_continuous(limits=c(1,10),breaks=c(1,2,4,6,8,10))
ggsave("stretch.jpeg",p,h=10,w=12)


# bias effects
p <- ggplot(sim_res,aes(turn,n_men/(n_men+n_women),color=level_iter))
p <- p  + stat_summary(fun.data="mean_cl_boot") + stat_summary(fun.y="mean",geom="line",size=1.2)  + geom_hline(yintercept = .5)
p <- p + facet_grid(project_prototype_boost_bias_multiplier+project_prototype_drop_bias_multiplier~project_prototype_percentage_threshold)+ scale_color_discrete("")
p <- p + scale_y_continuous("Percent Men at Level", labels=percent) + xlab("Promotion Cycle")
p <- p + scale_x_continuous(limits=c(1,10),breaks=c(1,2,4,6,8,10))
ggsave("threshold2.jpeg",p,h=18,w=8)


# bias effects
d <- sim_res[turn==20, as.list(smean.cl.boot(n_men/(n_men+n_women))),by=.(project_prototype_boost_bias_multiplier,project_prototype_drop_bias_multiplier,project_prototype_percentage_threshold,level_iter)]
ggplot(d, aes(level_iter, Mean,ymin=Lower,ymax=Upper,color=factor(project_prototype_percentage_threshold))) + geom_pointrange(position=position_dodge(width=.4)) + facet_wrap(project_prototype_boost_bias_multiplier~project_prototype_drop_bias_multiplier) + scale_color_discrete("")



# Overall
p <- ggplot(sim_res,aes(turn,n_men/(n_men+n_women),color=level_iter))
p <- p  + stat_summary(fun.data="mean_cl_boot") + stat_summary(fun.y="mean",geom="line",size=1.2)  + geom_hline(yintercept = .5)
p <- p + scale_y_continuous("Percent Men at Level", labels=percent) + xlab("Promotion Cycle")
p <- p + scale_x_continuous(limits=c(1,10),breaks=c(1,2,4,6,8,10))
ggsave("threshold2.jpeg",p,h=18,w=8)

