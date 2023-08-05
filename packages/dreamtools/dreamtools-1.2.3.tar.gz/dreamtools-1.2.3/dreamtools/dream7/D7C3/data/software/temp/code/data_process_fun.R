####################1. Arithmetic Function
##1.1 Function to combine data with missing values. 
na_plus_fun=function(x,y){
    z=x
    for (i in (1:length(x))){if (is.na(x[i])){z[i]=y[i]} }
    for (i in (1:length(y))){if (is.na(y[i])){z[i]=x[i]} }  
    for (i in (1:length(x))){if (!is.na(x[i]) & !is.na(y[i])){z[i]=(x[i]+y[i])/2} }
return(z)
}

##1.2 Function to impute average for the numeric variable and most common value to impute for factor variable
impute_avg_fun=function(dat){
    for (i in (1:dim(dat)[2])){
        ##numeric variable
        if(is.numeric(dat[,i])){dat[is.na(dat[,i]),i]=mean(dat[,i],na.rm=T)}
        ##factor variable
        if(is.factor(dat[,i])){
            ux=unique(dat[!is.na(dat[,i]),i])
            dat[is.na(dat[,i]),i]=ux[which.max(tabulate(match(dat[!is.na(dat[,i]),i], ux)))]
            #dat[is.na(dat[,i]),i]='UNKOWN'
        }
    }
    return(dat)
}

####################2. Data Process Function Definition
##2.1 Function to process demographic data
demographic_process_fun=function(dat){
    unique_id=as.data.frame(unique(dat$V1))
    names(unique_id)=c("Pid")
    age=dat[dat$V5==1257,c(1,7)]
    names(age)=c("Pid","age")
    age$age=as.numeric(as.character(age$age))
    race=dat[dat$V5%in%c(1207,1208,1210,1211) & dat$V7!='',][,c(1,6)]
    names(race)=c("Pid","race")
    race$race=as.character(race$race)
    race$race[race$race=='Race - Black/African American']='African_American'
    race$race[race$race=='Race - Asian']='Asian'
    race$race[race$race=='Race - Caucasian']='Caucasian'
    gender=dat[dat$V5==1205,c(1,7)]
    names(gender)=c("Pid","gender")
    gender$gender=as.character(gender$gender)
    gender$gender[as.character(gender$gender)=='1']='Female'
    gender$gender[as.character(gender$gender)=='2']='Male'
    height=unique(merge(dat[dat$V5==1171,c(1,4,7)], dat[dat$V5==1181,c(4,7)], by="V4")[,2:4])
    names(height)=c("Pid","height","height_unit")
    height$height=as.numeric(as.character(height$height))
    height$height[height$height_unit=="Inches" & !is.na(height$height)]=2.54*height$height[height$height_unit=="Inches" & !is.na(height$height)]
    height$height_unit="CM"
    height=unique(height[!is.na(height$height),])
    height=aggregate(height~Pid+height_unit,data=height,mean)              ###some of the patients has two height values, here use the average one
    demo=merge(merge(merge(merge(unique_id, age, by="Pid", all.x=T),race, by="Pid",all.x=T),gender, by="Pid",all.x=T),height, by="Pid",all.x=T)
    demo$age[is.na(demo$age)]=mean(demo$age,na.rm=T)
    demo$race[is.na(demo$race)]='Caucasian'
    demo$gender[is.na(demo$gender)]='UNKOWN'
    demo$race=as.factor(demo$race)
    demo$gender=as.factor(demo$gender)
    return(demo)
}

##2.2 Function to process treatment group data
treatment_group_process_fun=function(dat){
    unique_id=as.data.frame(unique(dat$V1))
    names(unique_id)=c('V1')
    group=dat[dat$V5==1454,c(1,7)]
    group_delta=dat[dat$V5==1456,c(1,7)]
    group=merge(unique_id,merge(group,group_delta,by="V1"),by='V1',all.x=T)
    names(group)=c("Pid","treatment","group_delta")
    group$group=rep("UNKONW", dim(group)[1])
    group$treatment=as.factor(toupper(as.character(group$treatment)))
    group$group_delta=as.numeric(as.character(group$group_delta))
    group$group[group$treatment=='ACTIVE' & group$group_delta<92]="ACTIVE"
    group$group[group$treatment=='PLACEBO' & group$group_delta<92]="PLACEBO"
    group$group=as.factor(group$group)
    return(group)
}

##2.3 Function to derive the ALS score related with face part muscle
face_process_fun=function(dat){
    Speech_1=dat[dat$V5==1213,c(4,7)]
    Salivation_2=dat[dat$V5==1215,c(4,7)]
    Swallowing_3=dat[dat$V5==1216,c(4,7)]
    face=merge(merge(Speech_1,Salivation_2, by="V4", all.x=T),Swallowing_3, by="V4", all.x=T)
    names(face)=c("id","Speech_1","Salivation_2","Swallowing_3")
    face$Speech_1=as.numeric(as.character(face$Speech_1))
    face$Salivation_2=as.numeric(as.character(face$Salivation_2))
    face$Swallowing_3=as.numeric(as.character(face$Swallowing_3))
    face$face=face$Speech_1+face$Salivation_2+face$Swallowing_3
    return(face)
}

##2.4 Function to derive the ALS score realted with the hand part muscle
hand_process_fun=function(dat){
    Handwriting_4=dat[dat$V5==1217,c(4,7)]
    Cutting_wo_Gastrostomy_5a=dat[dat$V5==1218,c(4,7)]
    Cutting_wo_Gastrostomy_5b=dat[dat$V5==1219,c(4,7)]
    hand=merge(merge(Handwriting_4, Cutting_wo_Gastrostomy_5a, by='V4', all.x=T),Cutting_wo_Gastrostomy_5b, by='V4',all.x=T)
    names(hand)=c("id","Handwriting_4","Cutting_wo_Gastrostomy_5a","Cutting_wo_Gastrostomy_5b")
    hand$Handwriting_4=as.numeric(as.character(hand$Handwriting_4))
    hand$Cutting_wo_Gastrostomy_5a=as.numeric(as.character(hand$Cutting_wo_Gastrostomy_5a))
    hand$Cutting_wo_Gastrostomy_5b=as.numeric(as.character(hand$Cutting_wo_Gastrostomy_5b))
    hand$Cutting_5=na_plus_fun(hand$Cutting_wo_Gastrostomy_5a,hand$Cutting_wo_Gastrostomy_5b)
    hand$hand=hand$Handwriting_4+hand$Cutting_5
    return(hand)
}

##2.5 Function to derive the ALS score related with body part muscle
body_process_fun=function(dat){
    Dressing_Hygiene_6=dat[dat$V5==1220,c(4,7)]
    Turning_in_Bed_7=dat[dat$V5==1221,c(4,7)]
    body=merge(Dressing_Hygiene_6,Turning_in_Bed_7, by='V4', all.x=T)
    names(body)=c("id","Dressing_Hygiene_6","Turning_in_Bed_7")
    body$Dressing_Hygiene_6=as.numeric(as.character(body$Dressing_Hygiene_6))
    body$Turning_in_Bed_7=as.numeric(as.character(body$Turning_in_Bed_7))
    body$body=body$Dressing_Hygiene_6+body$Turning_in_Bed_7
    return(body)
}

##2.6 Function to derive the ALS score related with leg part muscle
leg_process_fun=function(dat){
    Walking_8=dat[dat$V5==1222,c(4,7)]
    Climbing_Stairs_9=dat[dat$V5==1223,c(4,7)]
    leg=merge(Walking_8, Climbing_Stairs_9, by='V4', all.x=T)
    names(leg)=c("id","Walking_8","Climbing_Stairs_9")
    leg$Walking_8=as.numeric(as.character(leg$Walking_8))
    leg$Climbing_Stairs_9=as.numeric(as.character(leg$Climbing_Stairs_9))
    leg$leg=leg$Walking_8+leg$Climbing_Stairs_9
    return(leg)
}

##2.7 Function to derive the ALS score related with chest part muscle
chest_process_fun=function(dat){
    Respiratory=dat[dat$V5==1214,c(4,7)]
    R_1_Dyspnea=dat[dat$V5==1230,c(4,7)]
    R_2_Orthopnea=dat[dat$V5==1231,c(4,7)]
    R_3_Respiratory_Insufficiency=dat[dat$V5==1232,c(4,7)]
    chest=merge(Respiratory,R_3_Respiratory_Insufficiency, by='V4',all=T)
    names(chest)=c("id","Respiratory","R_3_Respiratory_Insufficiency")
    chest$Respiratory=as.numeric(as.character(chest$Respiratory))
    chest$R_3_Respiratory_Insufficiency=as.numeric(as.character(chest$R_3_Respiratory_Insufficiency))
    chest$Respiratory_10=na_plus_fun(chest$Respiratory,chest$R_3_Respiratory_Insufficiency)
    chest$chest=chest$Respiratory_10
    return(chest)
}

##2.8 Function to derive the ALSFRS total score 
ALSFRS_process_fun=function(dat,a,b,c,d,e){
    clinical_id=unique(dat[dat$V2==145, c(1,4)])
    ALSFRS_Delta=dat[dat$V5==1225,c(4,7)]
    ALSFRS_Total=dat[dat$V5==1228,c(4,7)]
    ALSFRS_R_Total=dat[dat$V5==1229,c(4,7)]
    R_1_Dyspnea=dat[dat$V5==1230,c(4,7)]
    R_2_Orthopnea=dat[dat$V5==1231,c(4,7)]
    R_3_Respiratory_Insufficiency=dat[dat$V5==1232,c(4,7)]
    R_score_adjusted=merge(merge(ALSFRS_R_Total,R_2_Orthopnea,by='V4'),R_3_Respiratory_Insufficiency,by='V4')
    R_score_adjusted$R_Adjusted=as.numeric(as.character(R_score_adjusted[,2]))-as.numeric(as.character(R_score_adjusted[,3]))-as.numeric(as.character(R_score_adjusted[,4]))
    ALSFRS=merge(merge(merge(clinical_id, ALSFRS_Delta, by='V4', all.x=T), ALSFRS_Total, by='V4', all.x=T),R_score_adjusted[,c(1,5)], by='V4',all.x=T)
    names(ALSFRS)=c("id","Pid", "ALSFRS_Delta", "ALSFRS", "ALSFRS_R")
    ALSFRS$ALSFRS_Delta=as.numeric(as.character(ALSFRS$ALSFRS_Delta))
    ALSFRS$ALSFRS=as.numeric(as.character(ALSFRS$ALSFRS))
    ALSFRS$ALSFRS_R=as.numeric(as.character(ALSFRS$ALSFRS_R))
  

    ALSFRS$ALSFRS[is.na(ALSFRS$ALSFRS)]=0
    ALSFRS$ALSFRS_R[is.na(ALSFRS$ALSFRS_R)]=0
    ALSFRS=transform(ALSFRS,ALSFRS_comb=ALSFRS+ALSFRS_R)

    ALSFRS=ALSFRS[ALSFRS$ALSFRS_Delta<92,]
    ALSFRS=ALSFRS[!is.na(ALSFRS$Pid),]
    ALSFRS=merge(merge(merge(merge(merge(ALSFRS,a,by="id"),b,by="id"),c,by="id"),d,by="id"),e,by="id")
    
    return(ALSFRS)
}

##2.9 Function to caculate the slope based on the three month score. 
##    (1) Slope is defined as the coefficients of a fitted line. 
##    (2) Use MSE (mean square error to measure the fitness and consistency of the score before three month. 
##    (3) For the patients with just one score, the slope is set to be missing (will be imputed by the average of the three month slope for all the 
##        patients at the final step of data processing.)

cal_three_month_slope_fun=function(dat){
   dat=dat[!is.na(dat$ALSFRS_comb),]
   dat=dat[!is.na(dat$ALSFRS_Delta),]
   a=rep(NA, length(unique(dat$Pid)))
   b=rep(NA, length(unique(dat$Pid)))
   c=rep(NA, length(unique(dat$Pid)))
   d=rep(NA, length(unique(dat$Pid)))
   face=rep(NA, length(unique(dat$Pid)))
   hand=rep(NA, length(unique(dat$Pid)))
   body=rep(NA, length(unique(dat$Pid)))
   leg=rep(NA, length(unique(dat$Pid)))
   chest=rep(NA, length(unique(dat$Pid)))
   Speech_1=rep(NA, length(unique(dat$Pid)))
   Salivation_2=rep(NA, length(unique(dat$Pid)))
   Swallowing_3=rep(NA, length(unique(dat$Pid)))
   Handwriting_4=rep(NA, length(unique(dat$Pid)))
   Cutting_5=rep(NA, length(unique(dat$Pid)))
   Dressing_Hygiene_6=rep(NA, length(unique(dat$Pid)))
   Turning_in_Bed_7=rep(NA, length(unique(dat$Pid)))
   Walking_8=rep(NA, length(unique(dat$Pid)))
   Climbing_Stairs_9=rep(NA, length(unique(dat$Pid)))
   Respiratory_10=rep(NA, length(unique(dat$Pid)))
   face_slope=rep(NA, length(unique(dat$Pid)))
   hand_slope=rep(NA, length(unique(dat$Pid)))
   body_slope=rep(NA, length(unique(dat$Pid)))
   leg_slope=rep(NA, length(unique(dat$Pid)))
   chest_slope=rep(NA, length(unique(dat$Pid)))

   for (i in (1:length(unique(dat$Pid)))){
    min_delta=min(dat$ALSFRS_Delta[dat$Pid==unique(dat$Pid)[i]],na.rm=T)
       max_delta=max(dat$ALSFRS_Delta[dat$Pid==unique(dat$Pid)[i]],na.rm=T)
       min_score=dat$ALSFRS_comb[dat$Pid==unique(dat$Pid)[i] & dat$ALSFRS_Delta==min_delta]
       max_score=dat$ALSFRS_comb[dat$Pid==unique(dat$Pid)[i] & dat$ALSFRS_Delta==max_delta]
       face[i]=dat$face[dat$Pid==unique(dat$Pid)[i] & dat$ALSFRS_Delta==max_delta]
       face_min=dat$face[dat$Pid==unique(dat$Pid)[i] & dat$ALSFRS_Delta==min_delta]
       hand[i]=dat$hand[dat$Pid==unique(dat$Pid)[i] & dat$ALSFRS_Delta==max_delta]
       hand_min=dat$hand[dat$Pid==unique(dat$Pid)[i] & dat$ALSFRS_Delta==min_delta]
       body[i]=dat$body[dat$Pid==unique(dat$Pid)[i] & dat$ALSFRS_Delta==max_delta]
       body_min=dat$body[dat$Pid==unique(dat$Pid)[i] & dat$ALSFRS_Delta==min_delta]
       leg[i]=dat$leg[dat$Pid==unique(dat$Pid)[i] & dat$ALSFRS_Delta==max_delta]
       leg_min=dat$leg[dat$Pid==unique(dat$Pid)[i] & dat$ALSFRS_Delta==min_delta]
       chest[i]=dat$chest[dat$Pid==unique(dat$Pid)[i] & dat$ALSFRS_Delta==max_delta]
       chest_min=dat$chest[dat$Pid==unique(dat$Pid)[i] & dat$ALSFRS_Delta==min_delta]
       Speech_1[i]=dat$Speech_1[dat$Pid==unique(dat$Pid)[i] & dat$ALSFRS_Delta==max_delta]
       Salivation_2[i]=dat$Salivation_2[dat$Pid==unique(dat$Pid)[i] & dat$ALSFRS_Delta==max_delta]
       Swallowing_3[i]=dat$Swallowing_3[dat$Pid==unique(dat$Pid)[i] & dat$ALSFRS_Delta==max_delta]
       Handwriting_4[i]=dat$Handwriting_4[dat$Pid==unique(dat$Pid)[i] & dat$ALSFRS_Delta==max_delta]
       Cutting_5[i]=dat$Cutting_5[dat$Pid==unique(dat$Pid)[i] & dat$ALSFRS_Delta==max_delta]
       Dressing_Hygiene_6[i]=dat$Dressing_Hygiene_6[dat$Pid==unique(dat$Pid)[i] & dat$ALSFRS_Delta==max_delta]
       Turning_in_Bed_7[i]=dat$Turning_in_Bed_7[dat$Pid==unique(dat$Pid)[i] & dat$ALSFRS_Delta==max_delta]
       Walking_8[i]=dat$Walking_8[dat$Pid==unique(dat$Pid)[i] & dat$ALSFRS_Delta==max_delta]
       Climbing_Stairs_9[i]=dat$Climbing_Stairs_9[dat$Pid==unique(dat$Pid)[i] & dat$ALSFRS_Delta==max_delta]
       Respiratory_10[i]=dat$Respiratory_10[dat$Pid==unique(dat$Pid)[i] & dat$ALSFRS_Delta==max_delta]  
       b[i]=max_score
       c[i]=min_score
       face_slope[i]=(face[i]-face_min)/((max_delta-min_delta+1)/365.24*12)
       hand_slope[i]=(hand[i]-hand_min)/((max_delta-min_delta+1)/365.24*12)
       body_slope[i]=(body[i]-body_min)/((max_delta-min_delta+1)/365.24*12)
       leg_slope[i]=(leg[i]-leg_min)/((max_delta-min_delta+1)/365.24*12)
       chest_slope[i]=(chest[i]-chest_min)/((max_delta-min_delta+1)/365.24*12)


       if (dim(dat[dat$Pid==unique(dat$Pid)[i],])[1]==1) {
           next
          }
      else{  
           lm_fit=lm(ALSFRS_comb~ALSFRS_Delta,data=dat[dat$Pid==unique(dat$Pid)[i],])
           a[i]=lm_fit$coefficients[2]*365.24/12
           d[i]=sqrt(deviance(lm_fit)/df.residual(lm_fit))
          
          }

   }

   rslt=as.data.frame(cbind(unique(dat$Pid), a,b,c,d,face,hand,body,leg,chest,face_slope,hand_slope,body_slope,leg_slope,chest_slope
                                        ,Speech_1,Salivation_2,Swallowing_3,Handwriting_4,Cutting_5,Dressing_Hygiene_6,Turning_in_Bed_7,Walking_8,Climbing_Stairs_9,Respiratory_10))
   names(rslt)=c("Pid","three_m_slope","score_three_month","first_score", "MSE_three_m_slope", "face","body","hand","leg","chest","face_three_m_slope","hand_three_m_slope"
              ,"body_three_m_slope","leg_three_m_slope","chest_three_m_slope","Speech_1","Salivation_2","Swallowing_3","Handwriting_4","Cutting_5","Dressing_Hygiene_6"
              ,"Turning_in_Bed_7","Walking_8","Climbing_Stairs_9","Respiratory_10")
   rslt$score_three_month_26_abs=abs(rslt$score_three_month-26)
   return(rslt) 
}

## 2.10 Function to get the data for the onset information of the patients: onset delta, onset_site. 
##      For the patients whose onset site is missing, use the mode of this categorical variable ("Limb") to impute. 
onset_process_fun=function(dat){
    onset_delta=unique(dat[dat$V5==1417,c(1,7)])
    names(onset_delta)=c("Pid","onset_delta")
    onset_delta$onset_delta=as.numeric(as.character(onset_delta$onset_delta))
    onset_delta$onset_delta_log=log(-onset_delta$onset_delta)

    onset_site=dat[dat$V5==1416,c(1,7)]
    names(onset_site)=c("Pid","onset_site")
    onset_site$onset_site=as.character(onset_site$onset_site)
    onset_site$onset_site[onset_site$onset_site=='Onset: Bulbar']='Bulbar'
    onset_site$onset_site[onset_site$onset_site=='Onset: Limb']='Limb'
    onset_site$onset_site[onset_site$onset_site=='Onset: Limb and Bulbar']='Both'
    onset_site$onset_site[onset_site$onset_site=='1']='Bulbar'
    onset_site$onset_site[onset_site$onset_site=='3']='Limb'
    onset_site$onset_site[is.na(onset_site$onset_site)]='Limb'

    diag_delta=dat[dat$V5==1418,c(1,7)]
    names(diag_delta)=c("Pid", "diag_delta")
    diag_delta$diag_delta=as.numeric(as.character(diag_delta$diag_delta))

    onset=merge(merge(onset_delta,onset_site, by="Pid"),diag_delta, by="Pid",all.x=T)
    onset$onset_site=as.factor(onset$onset_site)
    onset$onset_diag_delta_diff=onset$diag_delta-onset$onset_delta
    onset$onset_diag_missing_ind=0
    onset$onset_diag_missing_ind[is.na(onset$onset_diag_delta_diff)]=1
    return(onset)
}

## 2.11 Function to get the data for the family disease information of the patients, two variables are defined here. 
##      (1) ALS_ind: 1 if any family member has got ALS before, 0 otherwise;
##      (2) neuro_ind: 1 if any family member has got neurological disease before, 0 otherwise;
family_hist_process_fun=function(dat){
    unique_pid=as.data.frame(unique(dat$V1))
    names(unique_pid)=c("Pid")
    als_pid=as.data.frame(unique(dat$V1[dat$V5==1419 & dat$V7=='ALS']))
    als_pid$als_ind=1
    names(als_pid)=c("Pid","als_ind")
    neuro_disease_pid=as.data.frame(unique(dat$V1[dat$V5==1419]))
    neuro_disease_pid$neuro_disease_ind=1
    names(neuro_disease_pid)=c("Pid","neuro_disease_ind")
    family_hist=merge(merge(unique_pid, als_pid, by="Pid", all.x=T), neuro_disease_pid, by="Pid", all.x=T)
    family_hist$als_ind[is.na(family_hist$als_ind)]=0
    family_hist$neuro_disease_ind[is.na(family_hist$neuro_disease_ind)]=0
    return(family_hist)
}


## 2.12 Function to get the data for the vital RR (Respiratory Rate) information of the patients. 
RR_process_fun=function(dat){
    RR=dat[dat$V5==1176,c(4,7)]
    RR_delta=dat[dat$V5==1174,c(1,4,7)]
    RR=merge(RR_delta,RR,by="V4")
    names(RR)=c("id","Pid","RR_delta","RR")
    RR$RR_delta=as.numeric(as.character(RR$RR_delta))
    RR$RR=as.numeric(as.character(RR$RR))
    RR=RR[!is.na(RR$RR) & !is.na(RR$RR_delta) & RR$RR_delta<92,]
    return(RR)
}

## 2.13 Function to caculate the slope of RR (Respiratory Rate) of the patients, two variables are defined here. 
##    (1) Slope is defined as the coefficients of a fitted line. 
##    (2) Use MSE (mean square error to measure the fitness and consistency of the score before three month. 
##    (3) For the patients with just one score, the slope is set to be missing (will be imputed by the average of the three month slope for all the 
##        patients at the final step of data processing.)
cal_RR_slope_fun=function(dat){
 a=rep(NA, length(unique(dat$Pid)))
 b=rep(NA, length(unique(dat$Pid)))
 d=rep(NA, length(unique(dat$Pid)))
  for (i in (1:length(unique(dat$Pid)))){
      b[i]=mean(dat$RR[dat$Pid==unique(dat$Pid)[i]],na.rm=T)
      if (dim(dat[dat$Pid==unique(dat$Pid)[i],])[1]==1) {
           ##a[i]=0
           next
          }
      else{  
           lm_fit=lm(RR~RR_delta,data=dat[dat$Pid==unique(dat$Pid)[i],])
           a[i]=lm_fit$coefficients[2]*365.24/12
           d[i]=sqrt(deviance(lm_fit)/df.residual(lm_fit))     
          }
  }
  c=as.data.frame(cbind(unique(dat$Pid), a,b,d))
  names(c)=c("Pid","RR_slope", "avg_RR", "MSE_RR_slope")
  c$RR_slope[is.na(c$RR_slope)]=0
  return(c)
}

## 2.14 Function to get the data for the pulse rate information of the patients 
pulse_process_fun=function(dat){
    pulse=dat[dat$V5==1175,c(4,7)]
    pulse_delta=dat[dat$V5==1174,c(1,4,7)]
    pulse=merge(pulse_delta,pulse,by="V4")
    names(pulse)=c("id","Pid","pulse_delta","pulse")
    pulse$pulse_delta=as.numeric(as.character(pulse$pulse_delta))
    pulse$pulse=as.numeric(as.character(pulse$pulse))
    pulse=pulse[!is.na(pulse$pulse) & !is.na(pulse$pulse_delta) & pulse$pulse_delta<92,]
    return(pulse)
}

## 2.15 Function to caculate the slope of pulse rate of the patients. 
##    (1) Slope is defined as the coefficients of a fitted line. 
##    (2) Use MSE (mean square error to measure the fitness and consistency of the score before three month. 
##    (3) For the patients with just one score, the slope is set to be missing (will be imputed by the average of the three month slope for all the 
##        patients at the final step of data processing.)
cal_pulse_slope_fun=function(dat){
  a=rep(NA, length(unique(dat$Pid)))
  b=rep(NA, length(unique(dat$Pid)))
  d=rep(NA, length(unique(dat$Pid)))
  for (i in (1:length(unique(dat$Pid)))){
      b[i]=mean(dat$pulse[dat$Pid==unique(dat$Pid)[i]],na.rm=T)
      if (dim(dat[dat$Pid==unique(dat$Pid)[i],])[1]==1) {
           ##a[i]=0
           next
          }
      else{  
            lm_fit=lm(pulse~pulse_delta,data=dat[dat$Pid==unique(dat$Pid)[i],])
            a[i]=lm_fit$coefficients[2]*365.24/12
            d[i]=sqrt(deviance(lm_fit)/df.residual(lm_fit))             
          }
  }
  c=as.data.frame(cbind(unique(dat$Pid), a,b,d))
  names(c)=c("Pid","pulse_slope", "avg_pulse","MSE_pulse_slope")
  c$pulse_slope[is.na(c$pulse_slope)]=0
  return(c)
}



## 2.16 Function to derive the data for the fvc(forced vital capacity) from the original data. 
fvc_process_fun=function(dat){
    fvc=merge(merge(merge(dat[dat$V5==1185,c(1,4,7)], dat[dat$V5==1405,c(4,7)], by="V4",all.x=T), dat[dat$V5==1190,c(4,7)],by="V4",all.x=T),dat[dat$V5==1188,c(4,7)],by="V4",all.x=T)[,c(2:6)]
    names(fvc)=c("Pid","fvc_value","fvc_unit","fvc_delta","fvc_normal")
    fvc$fvc_value=as.numeric(as.character(fvc$fvc_value))
    fvc$fvc_delta=as.numeric(as.character(fvc$fvc_delta))
    fvc$fvc_normal=as.numeric(as.character(fvc$fvc_normal))
    fvc$ratio=fvc$fvc_value/fvc$fvc_normal
    fvc=fvc[fvc$fvc_delta<92 & !is.na(fvc$Pid) & !is.na(fvc$fvc_delta) & !is.na(fvc$fvc_value),]
    fvc=fvc[!is.na(fvc$fvc_delta),]
    fvc=fvc[!is.na(fvc$fvc_value),]
    return(fvc)
}

## 2.17 Function to derive the data for the svc(slow vital capacity) from the original data. 
svc_process_fun=function(dat){
    svc=merge(dat[dat$V5==1262,c(1,4,7)], dat[dat$V5==1267,c(4,7)], by="V4", all=T)[,2:4]
    names(svc)=c("Pid","svc_value","svc_delta")
    svc$svc_value=as.numeric(as.character(svc$svc_value))
    svc$svc_delta=as.numeric(as.character(svc$svc_delta))
    svc=svc[svc$svc_delta<92,]
    svc=svc[!is.na(svc$svc_delta),]
    svc=svc[!is.na(svc$svc_value),]
    return(svc)
}

## 2.18 Function to caculate the slope of fvc rate change of the patients. 
##    (1) Slope is defined as the coefficients of a fitted line. 
##    (2) Use MSE (mean square error to measure the fitness and consistency of the score before three month. 
##    (3) For the patients with just one data point before three month, the slope is set to be missing (will be imputed by the average of the three month slope for all the 
##        patients at the final step of data processing.)
cal_slope_fvc_fun=function(dat){
  a=rep(NA, length(unique(dat$Pid)))
  d=rep(NA, length(unique(dat$Pid)))
  for (i in (1:length(unique(dat$Pid)))){
      if (dim(dat[dat$Pid==unique(dat$Pid)[i],])[1]==1) {
           ##a[i]=0
           next
          }
      else{  
           lm_fit=lm(fvc_value~fvc_delta,data=dat[dat$Pid==unique(dat$Pid)[i],])
           a[i]=lm_fit$coefficients[2]*365.24/12
            d[i]=sqrt(deviance(lm_fit)/df.residual(lm_fit))
          }
  }
  c=as.data.frame(cbind(unique(dat$Pid), a, d))
  names(c)=c("Pid","fvc_slope", "MSE_fvc_slope")
  ##c$fvc_slope[is.na(c$fvc_slope)]=0
  return(c)
}

## 2.19 Function to caculate the slope of svc rate change of the patients. 
##    (1) Slope is defined as the coefficients of a fitted line. 
##    (2) Use MSE (mean square error to measure the fitness and consistency of the score before three month. 
##    (3) For the patients with just one data point before three month, the slope is set to be missing (will be imputed by the average of the three month slope for all the 
##        patients at the final step of data processing.)
cal_slope_svc_fun=function(dat){
  a=rep(NA, length(unique(dat$Pid)))
  d=rep(NA, length(unique(dat$Pid)))
  for (i in (1:length(unique(dat$Pid)))){
      if (dim(dat[dat$Pid==unique(dat$Pid)[i],])[1]==1) {
           ##a[i]=0
           next
          }
      else{  
          lm_fit=lm(svc_value~svc_delta,data=dat[dat$Pid==unique(dat$Pid)[i],])
          a[i]=lm_fit$coefficients[2]*365.24/12
          d[i]=sqrt(deviance(lm_fit)/df.residual(lm_fit))
          }
  }
  c=as.data.frame(cbind(unique(dat$Pid), a,d))
  names(c)=c("Pid","svc_slope","MSE_svc_slope")
  ##c$svc_slope[is.na(c$svc_slope)]=0
  return(c)
}

## 2.20 Function to combine the fvc_slope with svc_slope. vc_slope=fvc_slope if fvc_slope is available, otherwise svc_slope.
comb_vc_slope_fun=function(dat,dat1,dat2){
    unique_pid=as.data.frame(unique(dat$V1))
    names(unique_pid)=c("Pid")
    c=merge(dat1,dat2,by="Pid",all=T)
    c$fvc_ind=1
    c$fvc_ind[is.na(c$fvc_slope)]=0
    c$vc_slope=na_plus_fun(c$fvc_slope,c$svc_slope)
    c=merge(unique_pid,c,by="Pid",all.x=T)
    return(c)
}

## 2.21 Function to derive the weight data from original dataset and convert it to the same unit.  
weight_process_fun=function(dat){
    weight=merge(merge(dat[dat$V5==1178,c(1,4,7)],dat[dat$V5==1180,c(4,7)], by="V4", all.x=T), dat[dat$V5==1174,c(4,7)], by="V4")[,2:5]
    names(weight)=c("Pid","weight","weight_unit","weight_delta")
    weight$weight=as.numeric(as.character(weight$weight))
    weight$weight_delta=as.numeric(as.character(weight$weight_delta))
    weight$weight_unit=as.character(weight$weight_unit)
    weight=weight[weight$weight_delta<92 & !is.na(weight$weight) & !is.na(weight$weight_delta) & !is.na(weight$weight_unit),]
    ##weight$weight[weight$weight_unit=="Pounds" & !is.na(weight$weight)]=weight$weight[weight$weight_unit=="Pounds" & !is.na(weight$weight)]*0.453592
    weight$weight[weight$weight_unit=="Pounds"]=weight$weight[weight$weight_unit=="Pounds"]*0.453592
    weight$weight_unit="Kilograms"
    return(weight)
}

## 2.22 Function to caculate the slope of weight change of the patients. 
##    (1) Slope is defined as the coefficients of a fitted line. 
##    (2) Use MSE (mean square error to measure the fitness and consistency of the score before three month. 
##    (3) For the patients with just one data point before three month, the slope is set to be missing (will be imputed by the average of the three month slope for all the 
##        patients at the final step of data processing.)
cal_weight_slope_fun=function(dat){
 a=rep(NA, length(unique(dat$Pid)))
 b=rep(NA, length(unique(dat$Pid)))
 d=rep(NA, length(unique(dat$Pid)))
  for (i in (1:length(unique(dat$Pid)))){
      b[i]=mean(dat$weight[dat$Pid==unique(dat$Pid)[i]],na.rm=T)
      if (dim(dat[dat$Pid==unique(dat$Pid)[i],])[1]==1) {
           next
          }
      else{  
          lm_fit=lm(weight~weight_delta,data=dat[dat$Pid==unique(dat$Pid)[i],])
          a[i]=lm_fit$coefficients[2]*365.24/12
          d[i]=sqrt(deviance(lm_fit)/df.residual(lm_fit))
          }
  }
  c=as.data.frame(cbind(unique(dat$Pid), a,b,d))
  names(c)=c("Pid","weight_slope", "avg_weight","MSE_weight_slope")
  c$weight_percentage_slope=c$weight_slope/c$avg_weight
  return(c)
}


## 2.23 Function to caculate the slope of BMI (BMI=weight(kg)/height(m)^2) change of the patients. 
##    (1) Slope is defined as the coefficients of a fitted line. 
##    (2) Use MSE (mean square error to measure the fitness and consistency of the score before three month. 
##    (3) For the patients with just one data point before three month, the slope is set to be missing (will be imputed by the average of the three month slope for all the 
##        patients at the final step of data processing.)
cal_BMI_slope_fun=function(dat1,dat2){
 a=rep(NA, length(unique(dat$Pid)))
 b=rep(NA, length(unique(dat$Pid)))
 dat=merge(dat1,dat2, by="Pid")
 dat$BMI=dat$weight/(dat$height)^2
  for (i in (1:length(unique(dat$Pid)))){
      b[i]=mean(dat$BMI[dat$Pid==unique(dat$Pid)[i]],na.rm=T)
      if (dim(dat[dat$Pid==unique(dat$Pid)[i],])[1]==1) {
           a[i]=0
           next
          }
      else{  
           a[i]=(mean(dat$weight[dat$Pid==unique(dat$Pid)[i]]*dat$weight_delta[dat$Pid==unique(dat$Pid)[i]])
                 -mean(dat$weight[dat$Pid==unique(dat$Pid)[i]])*mean(dat$weight_delta[dat$Pid==unique(dat$Pid)[i]]))/var((dat$weight_delta[dat$Pid==unique(dat$Pid)[i]]))*365.24/12

          }
  }
  c=as.data.frame(cbind(unique(dat$Pid), a,b))
  names(c)=c("Pid","weight_slope", "avg_weight")
  c$weight_percentage_slope=c$weight_slope/c$avg_weight
  return(c)
}

## 2.24 Function to caculate the average test value of the uric acid test in the first three month.  
uric_acid_process_fun=function(dat){
    unique_pid=as.data.frame(unique(dat$V1))
    names(unique_pid)=c("Pid")
    clincial_id=dat[dat$V5==1250 & dat$V7=='Uric Acid', c(4,1)] 
    names(clincial_id)=c("clincial_id","Pid")
    test_delta=dat[dat$V5==1234, c(4,7)]
    names(test_delta)=c("clincial_id","uric_acid_test_delta")
    test_value=dat[dat$V5==1251, c(4,7)]
    names(test_value)=c("clincial_id","uric_acid_test_value")
    uric_acid=merge(merge(clincial_id, test_delta, by="clincial_id"), test_value, by="clincial_id")[,c(2:4)]
    uric_acid$uric_acid_test_delta=as.numeric(as.character(uric_acid$uric_acid_test_delta))
    uric_acid$uric_acid_test_value=as.numeric(as.character(uric_acid$uric_acid_test_value))
    uric_acid=uric_acid[uric_acid$uric_acid_test_delta<92,]
    uric_acid=tapply(uric_acid$uric_acid_test_value, uric_acid$Pid, mean)
    mean_uric_acid=as.data.frame(cbind(as.numeric(names(uric_acid)), as.numeric(uric_acid)))
    names(mean_uric_acid)=c("Pid","uric_acid_value")
    mean_uric_acid=merge(unique_pid, mean_uric_acid, by="Pid", all.x=T)
    mean_uric_acid$uric_acid_value_missing_ind[is.na(mean_uric_acid$uric_acid_value)]=1
    mean_uric_acid$uric_acid_value_missing_ind[!is.na(mean_uric_acid$uric_acid_value)]=0
    mean_uric_acid$uric_acid_value[is.na(mean_uric_acid$uric_acid_value)]=0
    return(mean_uric_acid)
}

## 2.25 Function to derive the average sodium lab test value from the first 3 months. 
sodium_process_fun=function(dat){
    unique_pid=as.data.frame(unique(dat$V1))
    names(unique_pid)=c("Pid")
    clincial_id=dat[dat$V5==1250 & dat$V7=='Sodium', c(4,1)] 
    names(clincial_id)=c("clincial_id","Pid")
    test_delta=dat[dat$V5==1234, c(4,7)]
    names(test_delta)=c("clincial_id","sodium_test_delta")
    test_value=dat[dat$V5==1251, c(4,7)]
    names(test_value)=c("clincial_id","sodium_test_value")
    sodium=merge(merge(clincial_id, test_delta, by="clincial_id"), test_value, by="clincial_id")[,c(2:4)]
    sodium$sodium_test_delta=as.numeric(as.character(sodium$sodium_test_delta))
    sodium$sodium_test_value=as.numeric(as.character(sodium$sodium_test_value))
    sodium=sodium[sodium$sodium_test_delta<92,]
    sodium=tapply(sodium$sodium_test_value, sodium$Pid, mean)
    mean_sodium=as.data.frame(cbind(as.numeric(names(sodium)), as.numeric(sodium)))
    names(mean_sodium)=c("Pid","sodium")
    mean_sodium=merge(unique_pid, mean_sodium, by="Pid", all.x=T)
    mean_sodium$sodium[is.na(mean_sodium$sodium)]=mean(mean_sodium$sodium, na.rm=T)
    return(mean_sodium)    
}

## 2.26 Function to comb all the available variable into a master table
dat_comb_fun=function(dat1,dat2,dat3,dat4,dat5,dat6,dat7,dat8,dat9,dat10,dat11){
    c=merge(merge(merge(merge(merge(merge(merge(merge(merge(merge(dat1,dat2,by="Pid",all=T),dat3,by="Pid", all=T),dat4,by="Pid", all=T),dat5,by="Pid",all=T)
       ,dat6,by="Pid",all=T),dat7,by="Pid",all=T),dat8,by="Pid",all=T),dat9, by="Pid",all=T),dat10,by="Pid",all=T),dat11,by="Pid",all=T)
    c$onset_slope=(40-c$first_score)/(c$onset_delta/365.24*12)
    c$onset_age=c$age+c$onset_delta/365
    c$BMI=c$avg_weight/(c$height/100)^2
    c$BMI_missing_ind=0
    c$BMI_missing_ind[is.na(c$BMI)]=1
    c$BMI[is.na(c$BMI)]=0
    c$score_three_month_log=log(c$score_three_month)
    c$RR_missing_ind=0
    c$RR_missing_ind[is.na(c$avg_RR)]=1
    c$pulse_missing_ind=0
    c$pulse_missing_ind[is.na(c$avg_pulse)]=1
    return(c)
}

#### 3 caculate score for cross validation training part
cal_score_fun=function(x,pred_col,actual_col){
    RMSD=sqrt(sum((x[pred_col]-x[actual_col])^2)/dim(x)[1])
    correlation=cor(x[pred_col], x[actual_col], method= c("pearson"))
    ls=list(RMSD, correlation)
    return(ls)
}



