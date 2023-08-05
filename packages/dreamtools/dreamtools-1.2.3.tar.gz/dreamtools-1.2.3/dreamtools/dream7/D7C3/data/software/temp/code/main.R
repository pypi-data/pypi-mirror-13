####1. Load packages and data processing function
t0=proc.time();
working_dir="Origent Model Document//Slope Model//Slope Model Code"; ## change the directory for where your model sits here!!!
setwd(working_dir); 
install.packages("randomForest");
library(randomForest);

full_data=read.csv("data/PROACT-ALL_FORMS.csv",sep="|", header=F);
full_data_slope=read.table("data/slopes_full.txt", header=F);
names(full_data_slope)=c("Pid","slope");
full_data=full_data[full_data$V1%in%full_data_slope$Pid,];


####2.Model Training and Validation
##2.1 Random split data as training and validation data set (80/20)
pid_all=unique(full_data$V1);
trainInd=sample((1:length(pid_all)),2*round(length(pid_all)/3));
trainPool=rep(F,length(pid_all));
trainPool[trainInd]=T;
pid_t=pid_all[trainPool];
pid_v=pid_all[!trainPool];
tdat=full_data[full_data$V1%in%pid_t,];
vdat=full_data[full_data$V1%in%pid_v,];
tdat_slope=full_data_slope[full_data_slope$Pid%in%pid_t,];
vdat_slope=full_data_slope[full_data_slope$Pid%in%pid_v,];
    
##2.2 Train and Validation
source("code/data_process_fun.R");  
source("code/training.R");
source("code/validation.R");  
    
    
##3 Remove the object generate in the validation and clean memory
#rm(list=ls());
#gc();
    

