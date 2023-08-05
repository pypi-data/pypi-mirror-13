####1. Data Processing
face=face_process_fun(vdat);
hand=hand_process_fun(vdat);
body=body_process_fun(vdat);
leg=leg_process_fun(vdat);
chest=chest_process_fun(vdat);
ALSFRS=ALSFRS_process_fun(vdat,face,hand,body,leg,chest);
three_m_slope=cal_three_month_slope_fun(ALSFRS);
onset=onset_process_fun(vdat);
family_hist=family_hist_process_fun(vdat);
group=treatment_group_process_fun(vdat);
fvc=fvc_process_fun(vdat);
svc=svc_process_fun(vdat);
fvc_slope=cal_slope_fvc_fun(fvc);
svc_slope=cal_slope_svc_fun(svc);
vc_slope=comb_vc_slope_fun(vdat,fvc_slope,svc_slope);
demo=demographic_process_fun(vdat);
weight=weight_process_fun(vdat);
weight_slope=cal_weight_slope_fun(weight);
uric_acid=uric_acid_process_fun(vdat);
RR=RR_process_fun(vdat);
pulse=pulse_process_fun(vdat);
RR_slope=cal_RR_slope_fun(RR);
pulse_slope=cal_pulse_slope_fun(pulse);
sodium=sodium_process_fun(vdat);

####2. combine all the predictors
vdat_comb=dat_comb_fun(three_m_slope,onset,family_hist,vc_slope,demo,weight_slope,uric_acid,group,RR_slope,pulse_slope,sodium)

####3. impute the missing data with average value
vdat_comb=impute_avg_fun(vdat_comb);

####4. load model
#load("rm_fit");
#load("rm_fit1");
#load("rm_fit2");
#load("rm_fit3");

####5. Make prediction and write out results
vdat_comb1=vdat_comb[vdat_comb$fvc_ind==1,];
vdat_comb2=vdat_comb[vdat_comb$uric_acid_value_missing_ind==0 &  !vdat_comb$Pid %in% vdat_comb1$Pid,];
vdat_comb3=vdat_comb[vdat_comb$onset_diag_missing_ind==0 & !vdat_comb$Pid %in% vdat_comb1$Pid & !vdat_comb$Pid %in% vdat_comb2$Pid,];
vdat_comb_base=vdat_comb[!vdat_comb$Pid %in% vdat_comb1$Pid & !vdat_comb$Pid %in% vdat_comb2$Pid & !vdat_comb$Pid %in% vdat_comb3$Pid ,];

dim(vdat_comb)[1];
dim(vdat_comb1)[1]+dim(vdat_comb2)[1]+dim(vdat_comb3)[1]+dim(vdat_comb_base)[1];

slope1=cbind(vdat_comb1$Pid,predict(rm_fit1, newdata=vdat_comb1));
slope2=cbind(vdat_comb2$Pid,predict(rm_fit2, newdata=vdat_comb2));
slope3=cbind(vdat_comb3$Pid,predict(rm_fit3, newdata=vdat_comb3));
slope_base=cbind(vdat_comb_base$Pid,predict(rm_fit, newdata=vdat_comb_base));

slope_comb=as.data.frame(rbind(slope1,slope2,slope3,slope_base));
names(slope_comb)=c("Pid","predicted_slope");

unique_pid=as.data.frame(unique(vdat_comb$Pid));
names(unique_pid)=c("Pid");

predicted=merge(merge(unique_pid, slope_comb, by="Pid", all.x=T), vdat_slope,by="Pid", all.y=T);
predicted=predicted[!duplicated(predicted),]   ##kick out the duplicated predictions if there is any
predicted$predicted_slope[is.na(predicted$predicted_slope)]=rnorm(length(predicted$predicted_slope[is.na(predicted$predicted_slope)]), -0.75, 0.25);  ##in case there is no patients not be predicted
predicted=predicted[order(predicted$Pid),];

write.csv(predicted, file=paste("predicted.csv"));

rslt=cal_score_fun(predicted,2,3);
cat(paste("Model Validation RMSD is: ", rslt[[1]], "\n", sep=""));