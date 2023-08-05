####1. Process Training Data
face_t=face_process_fun(tdat);
hand_t=hand_process_fun(tdat);
body_t=body_process_fun(tdat);
leg_t=leg_process_fun(tdat);
chest_t=chest_process_fun(tdat);
ALSFRS_t=ALSFRS_process_fun(tdat,face_t,hand_t,body_t,leg_t,chest_t);
three_m_slope_t=cal_three_month_slope_fun(ALSFRS_t);
onset_t=onset_process_fun(tdat);
family_hist_t=family_hist_process_fun(tdat);
fvc_t=fvc_process_fun(tdat);
svc_t=svc_process_fun(tdat);
fvc_slope_t=cal_slope_fvc_fun(fvc_t);
svc_slope_t=cal_slope_svc_fun(svc_t);
vc_slope_t=comb_vc_slope_fun(tdat,fvc_slope_t,svc_slope_t);
demo_t=demographic_process_fun(tdat);
group_t=treatment_group_process_fun(tdat);
weight_t=weight_process_fun(tdat);
weight_slope_t=cal_weight_slope_fun(weight_t);
uric_acid_t=uric_acid_process_fun(tdat);
RR_t=RR_process_fun(tdat);
pulse_t=pulse_process_fun(tdat);
RR_slope_t=cal_RR_slope_fun(RR_t);
pulse_slope_t=cal_pulse_slope_fun(pulse_t);
sodium_t=sodium_process_fun(tdat);

tdat_comb=merge(dat_comb_fun(three_m_slope_t,onset_t,family_hist_t,vc_slope_t,demo_t,weight_slope_t
                                   ,uric_acid_t,group_t,RR_slope_t,pulse_slope_t, sodium_t)
                      ,tdat_slope, by="Pid");  ##combine the predictors
tdat_comb=impute_avg_fun(tdat_comb)  ##impute the missing with average value

#### 3. fit the model 
##3.1 fit the base model
rm_fit=randomForest(slope ~ three_m_slope + first_score + score_three_month + score_three_month_26_abs +
                            face + body + hand + leg + chest + 
                            face_three_m_slope + hand_three_m_slope + body_three_m_slope + leg_three_m_slope + chest_three_m_slope + 
                            onset_delta_log + onset_age + onset_site + onset_slope + onset_diag_delta_diff + onset_diag_missing_ind + 
                            vc_slope + 
                            als_ind + neuro_disease_ind +
                            weight_slope + weight_percentage_slope + 
                            RR_slope + avg_RR + 
                            pulse_slope + avg_pulse 
                    , data=tdat_comb);
save(rm_fit, file="rm_fit");

##3.2 fit the model when fvc data is available
rm_fit1=randomForest(slope ~ three_m_slope + score_three_month + first_score + score_three_month_26_abs +
                            face + body + hand + leg + chest + 
                            face_three_m_slope + hand_three_m_slope + body_three_m_slope + leg_three_m_slope + chest_three_m_slope + 
                            onset_delta_log + onset_age + onset_site + onset_slope + onset_diag_missing_ind +
                            als_ind + neuro_disease_ind + 
                            fvc_slope +
                            weight_slope + weight_percentage_slope +
                            uric_acid_value + uric_acid_value_missing_ind
                    , data=tdat_comb[tdat_comb$fvc_ind==1,]);
save(rm_fit1, file="rm_fit1");

##3.3 fit the model when uric_acid_value is available
rm_fit2=randomForest(slope ~ three_m_slope +  score_three_month_26_abs +
                             onset_delta_log + + onset_diag_delta_diff + onset_diag_missing_ind + 
                             onset_site + 
                             vc_slope + 
                             uric_acid_value 
                    , ntree=1000, corr.bias=T 
                    , data=tdat_comb[tdat_comb$uric_acid_value_missing_ind==0,]);
save(rm_fit2, file="rm_fit2");

##3.4 fit the model when diagnosis delta data is available
rm_fit3=randomForest(slope~three_m_slope +  score_three_month_26_abs +
                     face + body + hand + leg + chest + 
                     face_three_m_slope + hand_three_m_slope + body_three_m_slope + leg_three_m_slope + chest_three_m_slope + 
                     onset_delta_log + onset_age  + onset_diag_delta_diff +
                     vc_slope + 
                     avg_pulse + uric_acid_value + uric_acid_value_missing_ind
                    , data=tdat_comb[tdat_comb$onset_diag_missing_ind==0,]);
save(rm_fit3, file="rm_fit3");

