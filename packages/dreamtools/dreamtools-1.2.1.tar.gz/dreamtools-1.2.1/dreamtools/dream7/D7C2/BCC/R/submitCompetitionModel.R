require(utils)
require(sessionTools)

#' Submit a trained model for a breast cancer competition
#'
#' Uploads a trained model and model code to Synapse to be evaluated in the breast cancer competition.
#'
#' @param modelName the name of the model that will be stored in Synapse
#' @param trainedModel object that has been trained using the training data. The customPredict() method of this model
#' will be called with the validation data to evaluate model performance.
#' @param rFiles list of files required to train the model. One of the files must be the class file defining the class of
#' trained model and defining the customTrain() and customPredict() methods. Other files are dependencies required to run
#' customTrain() and customPredict() on the class file.
#' @param cvPerformance optional argument containing an object of class SurvivalModelPerformanceCV as returned by the function
#' crossValidatePredictiveSurvivalModel.
#' @param isPracticeModel binary argument specifying if the model is uploaded to the Synapse dataset containing practice models
#' or models to be scored in the competition. Set to FALSE if you do not want the model to be evaluated.
#'
#' @author Adam Margolin
#' @export

submitCompetitionModel <- function(modelName = NULL, trainedModel=NULL,
                                   rFiles=NULL, cvPerformance=NULL, isPracticeModel = FALSE, parentDatasetId = NULL){
  if (is.null(parentDatasetId)){
    if (isPracticeModel) {
      parentDatasetId <- "syn375517"
    }else{
      parentDatasetId <- "syn1125643"
    }
  }
  
  submittedModelLayer <- Data(list(name = modelName, parentId = parentDatasetId))
  
  for (curRFile in rFiles){
    submittedModelLayer <- addFile(submittedModelLayer, curRFile)
  }
  
  submittedModelLayer <- addObject(submittedModelLayer, trainedModel, "trainedModel")
  submittedModelLayer <- addObject(submittedModelLayer, cvPerformance, "cvPerformance")
  submittedModelLayer <- addObject(submittedModelLayer, sessionSummary(), "sessionSummary")
  
  submittedModelLayer <- storeEntity(submittedModelLayer)
  
  propertyValue(submittedModelLayer, "id")
}
