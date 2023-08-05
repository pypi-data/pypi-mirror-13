
#' Function to retrain all models originally trained using overall survival and train and evaluate using
#' disease specific survival
#'
#' @author Adam Margolin
#' @export
#' 
retrainAllOSModels <- function(){
  trainingData <- loadMetabricTrainingData()
  
  submittedModelIds_orig <- synapseQuery("SELECT id FROM entity WHERE entity.parentId == 'syn1125643'")
  
  for (modelCtr in 1:nrow(submittedModelIds_orig)){
    curModelId_orig <- submittedModelIds_orig$entity.id[modelCtr]
    print(paste("Retraining", modelCtr, "of", nrow(submittedModelIds_orig), ":", curModelId_orig))
    try( retrainOSModel(curModelId_orig) )
  }
}
