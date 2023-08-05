#' Load training data for the metabric competition
#'
#' Loads data for gene expression, copy number, clinical covariates and clinical survival times for the training dataset
#' used to train predicitve models.
#'
#' @return a list with elements: exprData, containing an ExpressionSet of gene expression features;
#' copyData, containing an ExpressionSet of copy number features; clinicalFeaturesData, containing an
#' AnnotatedDataFrame of clinical covariates; and clinicalSurvData, containing a Surv object
#' of survival times and censor values.
#' @author Adam Margolin
#' @export

loadMetabricTrainingData_federation <- function(){
  metabricTrainingData <- list()
  
  idExpressionLayer <- "160776"
  expressionLayer <- loadEntity(idExpressionLayer)
  metabricTrainingData$exprData <- expressionLayer$objects[[1]]
  
  idCopyLayer <- "160778"
  copyLayer <- loadEntity(idCopyLayer)
  metabricTrainingData$copyData <- copyLayer$objects[[1]]
  
  idClinicalFeaturesLayer <- "160780"
  clinicalFeaturesLayer <- loadEntity(idClinicalFeaturesLayer)
  metabricTrainingData$clinicalFeaturesData <- clinicalFeaturesLayer$objects[[1]]@data
  
  idClinicalSurvLayer <- "160782"
  clinicalSurvLayer <- loadEntity(idClinicalSurvLayer)
  metabricTrainingData$clinicalSurvData <- clinicalSurvLayer$objects[[1]]
  
  return(metabricTrainingData)
}

