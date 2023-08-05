require(MASS)
require(survival)
require(predictiveModeling)
require(randomSurvivalForest)

setRefClass(Class = "PredictiveModel")

#' DemoModel
#'
#' Simple example of an implementatiopn of a predictive model used in the package demo example and used as a baseline
#' to evaluate performance of other models. This model builds a random survival forest using clinical covariates
#' known to relate to breast cancer survival, gene expression and copy number data. It also imputes missing covariates.
#' NAs should be expected in all clinical covariates, in both training and test data sets.
#' 
#' @author Erhan Bilal
#' @export

DemoModel <- setRefClass(Class  = "DemoModel",
    contains = "PredictiveModel",
    fields   = c("rsf.model.fit"),
    methods  = list(
        initialize = function(...){
            return(.self)
        },
                                       
        customTrain = function(exprData, copyData, clinicalFeaturesData,clinicalSurvData,...) {
            if(class(clinicalSurvData) != "Surv"){
                stop("Expecting 'responseData' object of type 'Surv'")
            }
            # Extract the expression data
            exprData.exprs <- exprs(exprData)
            copyData.exprs <- exprs(copyData)          
            rowsWithoutNas <- rowSums(is.na(copyData.exprs)) == 0
            copyData.exprs <- copyData.exprs[rowsWithoutNas,]
            
            # Calculate the Genomic Instability Index
            GII <- colSums(copyData.exprs < -1 | copyData.exprs > 1) / sum(rowsWithoutNas)
            
            # Pick some relevant genes
            # Estrogen pathway genes
            ER_exp <- exprData.exprs[which(rownames(exprData.exprs) == "ILMN_1678535"),]
            PR_exp <- exprData.exprs[which(rownames(exprData.exprs) == "ILMN_1811014"),]
            # HER2 amplicon genes
            ERBB2_exp <- exprData.exprs[which(rownames(exprData.exprs) == "ILMN_1728761"),]
            GRB7_exp <- exprData.exprs[which(rownames(exprData.exprs) == "ILMN_1740762"),]
            # Immune response genes
            CXCL10_exp <- exprData.exprs[which(rownames(exprData.exprs) == "ILMN_1791759"),]
            STAT1_exp <- exprData.exprs[which(rownames(exprData.exprs) == "ILMN_1691364"),]
            GBP1_exp <- exprData.exprs[which(rownames(exprData.exprs) == "ILMN_2148785"),]
            GZMA_exp <- exprData.exprs[which(rownames(exprData.exprs) == "ILMN_1779324"),]
            CD19_exp <- exprData.exprs[which(rownames(exprData.exprs) == "ILMN_1782704"),]            
                        
            # Merge the new features with the clinical covariates
            featureData <- cbind(clinicalFeaturesData,GII,ER_exp,PR_exp,ERBB2_exp,GRB7_exp,CXCL10_exp,STAT1_exp,
                                 GBP1_exp,GZMA_exp,CD19_exp)
            
            survTime <- clinicalSurvData[,1]
            survStatus <- clinicalSurvData[,2]          
            
            # Fit a random survival forest with tree based imputation of NAs in the clinical covariates
            .self$rsf.model.fit <- rsf(Surv(time,status) ~ age_at_diagnosis + size + lymph_nodes_positive + grade + 
                                       ER_IHC_status + HER2_SNP6_state + Treatment + ER.Expr + PR.Expr + GII + 
                                       CXCL10_exp + STAT1_exp + GBP1_exp + GZMA_exp + CD19_exp, 
                                       data=data.frame(featureData,time=survTime,status=survStatus), 
                                       ntree=1000, na.action="na.impute", splitrule="logrank", nsplit=1, 
                                       importance="randomsplit", seed=-1)
                                                     
                                         
        },
                                       
        customPredict = function(exprData, copyData, clinicalFeaturesData){
            exprData.exprs <- exprs(exprData)
            copyData.exprs <- exprs(copyData)
            rowsWithoutNas <- rowSums(is.na(copyData.exprs)) == 0
            copyData.exprs <- copyData.exprs[rowsWithoutNas,]
            
            # Calculate the Genomic Instability Index
            GII <- colSums(copyData.exprs < -1 | copyData.exprs > 1) / sum(rowsWithoutNas)
            # Estrogen pathway genes
            ER_exp <- exprData.exprs[which(rownames(exprData.exprs) == "ILMN_1678535"),]
            PR_exp <- exprData.exprs[which(rownames(exprData.exprs) == "ILMN_1811014"),]
            # HER2 amplicon genes
            ERBB2_exp <- exprData.exprs[which(rownames(exprData.exprs) == "ILMN_1728761"),]
            GRB7_exp <- exprData.exprs[which(rownames(exprData.exprs) == "ILMN_1740762"),]
            # Immune response genes
            CXCL10_exp <- exprData.exprs[which(rownames(exprData.exprs) == "ILMN_1791759"),]
            STAT1_exp <- exprData.exprs[which(rownames(exprData.exprs) == "ILMN_1691364"),]
            GBP1_exp <- exprData.exprs[which(rownames(exprData.exprs) == "ILMN_2148785"),]
            GZMA_exp <- exprData.exprs[which(rownames(exprData.exprs) == "ILMN_1779324"),]
            CD19_exp <- exprData.exprs[which(rownames(exprData.exprs) == "ILMN_1782704"),]            
            
            featureData <- cbind(clinicalFeaturesData,GII,ER_exp,PR_exp,ERBB2_exp,GRB7_exp,CXCL10_exp,STAT1_exp,
                                 GBP1_exp,GZMA_exp,CD19_exp)
            
            predictedResponse <- predict(object=.self$rsf.model.fit, na.action="na.impute", test=featureData)$mortality
            return(predictedResponse)
        }
    )
)
