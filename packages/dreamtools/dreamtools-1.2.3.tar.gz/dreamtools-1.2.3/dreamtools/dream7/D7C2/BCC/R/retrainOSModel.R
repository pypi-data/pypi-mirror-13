
#' Function to retrain one model originally trained using overall survival and train and evaluate using
#' disease specific survival
#'
#' @author Adam Margolin
#' @export

retrainOSModel <- function(modelEntityId_orig, trainingData=NULL){
  print("**********************************************************")
  print("**********************************************************")
  print(paste("retraining", modelEntityId_orig))
  print("**********************************************************")
  print("**********************************************************")
  
  if(is.null(trainingData)){
    trainingData <- loadMetabricTrainingData()
  }
  modelEntity_orig <- loadEntity(modelEntityId_orig)
  modelEntity_new <- restoreSessionAndCreateNewModelFromOSModel(modelEntity_orig)
  
  modelClass <- class(modelEntity_orig$objects$trainedModel)
  model_new <- new(modelClass)
  model_new$customTrain(trainingData$exprData, trainingData$copyData, trainingData$clinicalFeaturesData, trainingData$clinicalSurvData_ds)
  modelEntity_new <- addObject(modelEntity_new, model_new, "trainedModel")
  storeEntity(modelEntity_new)
}
