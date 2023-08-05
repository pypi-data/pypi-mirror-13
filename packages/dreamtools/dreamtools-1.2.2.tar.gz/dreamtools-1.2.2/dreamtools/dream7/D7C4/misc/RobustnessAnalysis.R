\# submissions is a list with all submitted prediction matrices
# observed is the matrix of measured values


# submissions for me is a list with all prediction matrices
N <- 10000
subResults <-list()

# I will save, for each submission, the score and the ranking computed for N resamplings
subResults$score <- matrix(0, nrow=length(submissions), ncol=N)
subResults$ranking <- matrix(0, nrow=length(submissions), ncol=N)


CompoundsID <- colnames(observed)

# this is my scoring function
source("RMSELeaderboard.R")

for (i in 1:N){
  # sample 90% of the compounds (=82 for me)
  SampledCompounds <- CompoundsID[sample(1:length(CompoundsID), 82, replace=FALSE)]
  
  # compute score and ranking
  SampledLeaderboard <- SampledRMSELeaderboard(submissions, observed, SampledCompounds)
  # save the score
  subResults$score[,i] <- SampledLeaderboard$MeanRanking_RMSE
  # save the ranking
  subResults$ranking[,i] <- SampledLeaderboard$TeamsRanking_RMSE
}



### tests: based on ranking
# Team1 in the index of the Team ranked first 
Comp1 <- subResults$ranking[Team1,]

# compare the distribution of the best performin team with the distribution of all other teams using Wilcoxon signed-rank test
tmp<-subResults$ranking[-Team1,]
pVal <- rep(NA, dim(tmp)[1])
for (i in 1:dim(tmp)[1]) {
  Comp2 <- tmp[i,]
  pVal[i] <- wilcox.test(Comp1, Comp2, paired=TRUE)$p.value
}

# False discovery rates (FDR) is calculated using the Benjamini-Hochberg correction
cPVal <- p.adjust(pVal, method="BH")



### tests: based on score
# Team1 in the index of the Team ranked first 
Comp1 <- subResults$score[Team1,]

# compare the distribution of the best performin team with the distribution of all other teams using Wilcoxon signed-rank test
tmp<-subResults$score[-Team1,]
pVal <- rep(NA, dim(tmp)[1])
for (i in 1:dim(tmp)[1]) {
  Comp2 <- tmp[i,]
  pVal[i] <- wilcox.test(Comp1, Comp2, paired=TRUE)$p.value
}

# False discovery rates (FDR) is calculated using the Benjamini-Hochberg correction
cPVal <- p.adjust(pVal, method="BH")
