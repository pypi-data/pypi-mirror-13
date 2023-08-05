
#' Function to take a model trained using OS, retore the session and create a new model to be retrained
#' disease specific survival
#'
#' @author Adam Margolin
#' @export

restoreSessionAndCreateNewModelFromOSModel <- function(modelEntity_orig){
  modelEntity_new <- Data(list(name = paste(modelEntity_orig$properties$name, "(RETRAINED)"), 
                               parentId = "syn1419781"))
  ### restore the session from the submitted model using sessionTools
  try(restoredSessionSummary <- modelEntity_orig$objects[["sessionSummary"]])
  try(restorePackages(restoredSessionSummary))
  
  for (curFile in modelEntity_orig$files[grepl(".R$", modelEntity_orig$files)]){
    curFilePath <- paste(modelEntity_orig$cacheDir, curFile, sep="/")
    print(curFilePath)
    source(curFilePath)
    modelEntity_new <- addFile(modelEntity_new, curFilePath)
  }
  
  modelEntity_new$annotations$retrainedFromOS <- TRUE
  
  modelObjectNames_orig <- names(modelEntity_orig$objects)
  modelObjectNames_orig[-which(modelObjectNames_orig %in% c("cvPerformance", "trainedModel"))]
  for (curModelObjectName in modelObjectNames_orig){
    modelEntity_new <- addObject(modelEntity_new, modelEntity_orig$objects[[curModelObjectName]], name=curModelObjectName)  
  }
  
  return(modelEntity_new)
}
