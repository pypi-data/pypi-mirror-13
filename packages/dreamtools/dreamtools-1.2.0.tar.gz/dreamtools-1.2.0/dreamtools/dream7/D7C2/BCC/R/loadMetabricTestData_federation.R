#' Load test data for the metabric competition
#'
#' Loads data for gene expression, copy number, clinical covariates and clinical survival times for the test dataset
#' used to evlauate model scores.
#'
#' @param loadSurvData specifies if survival data is loaded. Should be set to false to users who do not have access
#' to validation data. Set to true for automated model evaluation harness.
#' @return a list with elements: exprData, containing an ExpressionSet of gene expression features;
#' copyData, containing an ExpressionSet of copy number features; clinicalFeaturesData, containing an
#' AnnotatedDataFrame of clinical covariates; and clinicalSurvData, if loadSurvData=TRUE, containing a Surv object
#' of survival times and censor values.
#' @author Adam Margolin
#' @export

loadMetabricTestData_federation <- function(loadSurvData=FALSE){
  metabricTestData <- list()
  
  idExpressionLayer <- "160784"
  expressionLayer <- loadEntity(idExpressionLayer)
  metabricTestData$exprData <- expressionLayer$objects[[1]]
  
  idCopyLayer <- "160786"
  copyLayer <- loadEntity(idCopyLayer)
  metabricTestData$copyData <- copyLayer$objects[[1]]
  
  idClinicalFeaturesLayer <- "160788"
  clinicalFeaturesLayer <- loadEntity(idClinicalFeaturesLayer)
  metabricTestData$clinicalFeaturesData <- clinicalFeaturesLayer$objects[[1]]@data
  
  if(loadSurvData){
    idClinicalSurvLayer <- "160790"
    clinicalSurvLayer <- loadEntity(idClinicalSurvLayer)
    metabricTestData$clinicalSurvData <- clinicalSurvLayer$objects[[1]]
  }
  
  return(metabricTestData)
}
