#' Load training data for the metabric competition
#'
#' Loads data for gene expression, copy number, clinical covariates and clinical survival times for the training dataset
#' used to train predicitve models.
#'
#' @return a list with elements: exprData, containing an ExpressionSet of gene expression features;
#' copyData, containing an ExpressionSet of copy number features; clinicalFeaturesData, containing an
#' AnnotatedDataFrame of clinical covariates; and clinicalSurvData, containing a Surv object
#' of survival times and censor values.
#' @author Adam Margolin, Matt Furia, Erhan Bilal
#' @export


loadMetabricTrainingData <- function(){

  ##
  ## subroutine for generating error message when user has not signed
  ## terms of use
  ##
  touMsg <- function(){
    "You must sign the Terms of Use before gaining access to the Metabric data.
Please visit https://synapse.sagebase.org/#Synapse:syn1125612 and click the
'Download' button."
  }

  ##
  ## subroutine for generating error message when entity contains no data
  ##
  missingMsg <- function(id){
    sprintf("Unable to load data for synapse id %s. Please visit support.sagebase.org for assistance.",
            id)
  }

  ##
  ## subroutine for fetching an entity's ID based on parent id and name
  ##
  doIdQry <- function(parent, name){
    ## genrate the error message for a query retuning no results
    qryMsg <- function(which){
      sprintf("Unable to find data entity '%s'. Please visit support.sagebase.org for assistance.",
            which)
    }

    ## build the query string
    makeQry <- function(parent, name){
      sprintf("select id from entity where entity.parentId == '%s' && entity.name == '%s'", parent, name)
    }

    qryString <- makeQry(parent, name)
    result <- synapseQuery(qryString)
    id <- result$entity.id

    if(is.null(id))
      stop(qryMsg(name))

    id
  }

  ## entity id for the Metabric Project
  METABRICID <- 'syn1125147'

  ## entity names to be retrieved
  entities <- list(
    exprData = 'Training METABRIC Gene Expression Data',
    copyData = 'Training METABRIC Copy Number Data',
    clinicalFeaturesData = 'Training METABRIC Clinical Features Data',
    clinicalSurvData = 'Training METABRIC Clinical Survival Data',
    clinicalSurvData_ds = 'Training METABRIC Clinical Survival Data (Disease Specific)'
  )

  ## initialize return value
  retVal <- list()

  ## return data for each of the entities
  for(i in 1:length(entities)){
    ## get the entity id
    entityId <- doIdQry(METABRICID, entities[[i]])

    ## load the entity
    entity <- loadEntity(entityId)

    ## check for data
    if(length(entity$objects) == 0L){
      ## on the first iteration, it's most likely that the user
      ## hasn't signed the terms of use. If on subsequent iterations
      ## it is likely that the data were deleted from Synapse
      switch(i,
        "1" = stop(touMsg()),
         stop(missingMsg(entityId))
      )

    }else{
      ## data was found. add to the return value
      retVal[[names(entities)[i]]] <- entity$objects[[1]]
    }
  }

  ## return the list containing the Metabric data
  retVal
}
