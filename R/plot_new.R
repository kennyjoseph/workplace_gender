# Just an example of how to plot some results
library(data.table)
library(ggplot2)
library(scales)
library(Hmisc)
theme_set(theme_bw(20))


res_dir <- "minimal"
sim_res <- fread(paste0("../",res_dir,"/turn_output_0.tsv"))


setnames(sim_res, c("fem_prom", "fem_suc", "fem_fail",
                    "male_prom","male_suc","male_fail",
                    "n_men","n_women","turn","level_iter","run_number","replication_number"))
params <- fread(paste0("../",res_dir,"/experiment_details.csv"))
sim_res <- merge(sim_res,params, by="run_number")
sim_res <- sim_res[turn %% 24 == 0]
sim_res$turn <- sim_res$turn / 24 + 1
sim_res$level_iter <- paste("Level",8-sim_res$level_iter)

# Overall
p <- ggplot(sim_res,aes(turn,n_men/(n_men+n_women),color=level_iter))
p <- p  + stat_summary(fun.data="mean_cl_boot") + stat_summary(fun.y="mean",geom="line",size=1.2)  + geom_hline(yintercept = .5)
p <- p + scale_y_continuous("Percent Men at Level", labels=percent) + xlab("Promotion Cycle")
#p <- p + scale_x_continuous(limits=c(1,10),breaks=c(1,2,4,6,8,10))
p


ggplot(melt(sim_res[turn==20 ],id=c("level_iter","turn"),measure=c("fem_suc","male_suc","fem_fail","male_fail"))[value != -1], aes(level_iter, value,color=variable)) + stat_summary(fun.data="mean_cl_boot",position=position_dodge(.5)) 

sim_res[, suc_diff := fem_suc - male_suc]
ggplot(sim_res[fem_suc != -1 & male_suc!=-1], aes(turn,suc_diff)) + stat_summary(fun.data="mean_cl_boot") + facet_wrap(~level_iter) + geom_hline(yintercept = 0,color='red')

sim_res[, prom_diff := fem_prom - male_prom]
ggplot(sim_res[fem_suc != -1 & male_suc!=-1], aes(turn,prom_diff)) + stat_summary(fun.data="mean_cl_boot") + facet_wrap(~level_iter,scales="free_y") + geom_hline(yintercept = 0,color='red')
ggplot(melt(sim_res[fem_fail != -1 & male_fail != -1],id=c("level_iter","turn"),measure=c("fem_prom","male_prom")), aes(level_iter, value,color=variable)) + stat_summary(fun.data="mean_cl_boot") 


sim_res[, male_odds := log((male_suc+1)/(male_fail+1))]
sim_res[, female_odds := log((fem_suc+1)/(fem_fail+1))]
ggplot(melt(sim_res[fem_suc != -1 & male_suc!=-1],id=c("level_iter","turn"),measure=c("male_odds","female_odds"))[value != -1], aes(turn, value,color=variable)) + stat_summary(fun.data="mean_cl_boot",position=position_dodge(.5))  + facet_wrap(~level_iter, scales='free_y',nrow=2)
