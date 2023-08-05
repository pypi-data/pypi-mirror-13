require(synapseClient)

#' Script to evaluate an uploaded model with source code from Synapse
#'
#' Function used by model evaluation harness to score submitted models.
#' @param submittedModelId the Synapse ID of the submitted model
#' @param trainingData training data used for evaluation. Loaded by default from Synapse if not specified.
#' @param testData test data used for evaluation. Loaded by default from Synapse if not specified.
#' @author Adam Margolin
#' @export

evaluateMetabricModelFromCode <- function(submittedModelId, trainingData=NULL, testData=NULL){
  print(paste("Model Synapse ID", submittedModelId))
  if(is.null(trainingData)){
    trainingData <- loadMetabricTrainingData()
  }
  if(is.null(testData)){
    testData <- loadMetabricTestData(loadSurvData=TRUE)
  }
  
  submittedModelLayer <- loadEntity(submittedModelId)
  
  for (curFile in submittedModelLayer$files[grepl(".R$", submittedModelLayer$files)]){
    print(paste(submittedModelLayer$cacheDir, curFile, sep="/"))
    source(paste(submittedModelLayer$cacheDir, curFile, sep="/"))
  }
  
  trainedModel <- submittedModelLayer$objects[["trainedModel"]]
  
  if (is.null(trainedModel)) {
    trainedModel <- submittedModelLayer$objects[[1]]
  }
  
  trainPredictions <- trainedModel$customPredict(trainingData$exprData, trainingData$copyData, trainingData$clinicalFeaturesData)
  trainPerformance <- SurvivalModelPerformance$new(as.numeric(trainPredictions), trainingData$clinicalSurvData)
  cIndex_train <- trainPerformance$getExactConcordanceIndex()
  
  testPredictions <- trainedModel$customPredict(testData$exprData, testData$copyData, testData$clinicalFeaturesData)
  testPerformance <- SurvivalModelPerformance$new(as.numeric(testPredictions), testData$clinicalSurvData)
  cIndex_test <- testPerformance$getExactConcordanceIndex()
  
  print(propertyValue(submittedModelLayer, "name"))
  print(paste("train concordance.index =", cIndex_train))
  print(paste("test concordance.index =", cIndex_test))
  cat("\n")
}
