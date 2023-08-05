require(rms)
require(MASS)
require(survival)
require(predictiveModeling)
require(gbm)
require(caret)
#source("CreateMetageneSpace.R")

if(!require(DreamBox7)){
  download.file("http://dl.dropbox.com/u/11986954/Dream7BCC/DreamBox7_0.212.tar.gz", destfile="./DreamBox7_0.212.tar.gz")
  install.packages("./DreamBox7_0.212.tar.gz", repos=NULL)
  library(DreamBox7)
}

setRefClass(Class = "PredictiveModel")

#' GoldiModel
#'
#' Modified from DemoClinicalOnlyModel from BCC challenge.
#'
#' @author Wei-Yi Cheng, Tai-Hsien Ou Yang, and Dimitris Anastassiou
#' @export

GoldiModel <- setRefClass(Class  = "GoldiModel",
                          contains = "PredictiveModel",
                          fields   = c("model", "attractome", "cnvome",  "annot", "annot.cnv", "predictions", "ocgenes", "chosenProbes", "chosenProbes_g", "mdns"),
                          methods  = list(
                            
                            initialize = function(...){
                              	data(attractome.minimalist)
				.self$attractome = attractome.minimalist
				data(map)
                              	.self$annot = map
				data(oncogenes)
				.self$ocgenes = oncogenes
				data(metacnv)
				.self$cnvome = metacnv
				data(cnvmap)
				.self$annot.cnv = cnvmap
                              return(.self)
                            },
                            
                            customTrain = function(exprData, copyData, clinicalFeaturesData,clinicalSurvData,...)
                            {
                              if(class(clinicalSurvData) != "Surv"){
                                stop("Expecting 'responseData' object of type 'Surv'")
                              }
				ntrees = 1500
				#meta.cnv = CreateMetageneSpace(exprs(copyData), .self$cnvome, .self$annot.cnv)$metaSpace
                              # no need for cnv data, remove it
                              rm(copyData)
				clnc = lazyImputeDFClncFULL(clinicalFeaturesData)
                              	clinical <- expandClncFULL(clnc)

			cat("Create metagene space...");flush.console()
                              o = CreateMetageneSpace(exprs(exprData), .self$attractome, .self$annot)
				meta = o$metaSpace
				.self$chosenProbes = o$pbs
                              o = CreateMetageneSpace(exprs(exprData), .self$ocgenes, .self$annot)
				gs = o$metaSpace
				.self$chosenProbes_g = o$pbs
				tp53 = gs["TP53_g",]
				gs = t(apply(gs, 1, function(x){ x - median(x)}))
				
				ls = meta["ls",]
				col11a1 = exprs(exprData)["ILMN_2392803",]
				.self$mdns = apply(meta, 1, median)
				meta = t(apply(meta, 1, function(x){ x - median(x)}))
				#meta = meta - matrix(.self$mdns, nrow=nrow(meta), ncol=ncol(meta))
			#===== Conditioning mesenchymal transition metagene by lymph node status
				idx = (clinical[,"lymph_nodes_positive"]<1 & clinical[,"size"] < 30)
				mes.lymphneg = meta["mt",] * idx
				.self$mdns = c(.self$mdns, median(mes.lymphneg[idx]))
				mes.lymphneg[idx] = mes.lymphneg[idx] - median(mes.lymphneg[idx])
				meta = rbind(meta, mes.lymphneg)
				col11a1.lymphneg30 = col11a1 * idx
				col11a1.lymphneg30[idx] = col11a1.lymphneg30[idx] - median(col11a1.lymphneg30[idx])

				idx = (clinical[,"lymph_nodes_positive"] > 3)
				ls.lymphpos = ls * idx
				.self$mdns = c(.self$mdns, median(ls.lymphpos[idx]))
				ls.lymphpos[idx] = ls.lymphpos[idx] - median(ls.lymphpos[idx])
				meta = rbind(meta, ls.lymphpos)

				idx = (meta["er",] < 0 & meta["erbb2", ] < 0)
				ls.erneg = ls * idx
				.self$mdns = c(.self$mdns, median(ls.erneg[idx]))
				ls.erneg[idx] = ls.erneg[idx] - median(ls.erneg[idx])
				meta = rbind(meta, ls.erneg)
				
				names(.self$mdns) = rownames(meta)

				lymph = clinical[,"lymph_nodes_positive"]
				lsxlym = ls *lymph
				lsxlym = lsxlym - median(lsxlym)

				idx = meta["er",] < 0
				tp53.erneg = tp53 * idx
				tp53.erneg[idx] = tp53.erneg[idx] - median(tp53.erneg[idx])
				gs = rbind(gs, tp53.erneg)

				meta = rbind(meta, gs)

				#idx = meta["ls",] < 0
				#chr17p12 = meta.cnv["chr17p12",]
				#chr17p12.lsneg = chr17p12 * idx
				#meta = rbind(meta, chr17p12.lsneg)
			rm(exprData)

				#meta = rbind(meta, meta.cnv)

                        cat("done!\n");flush.console()
			
#===== 1. AIC models metagenes only =======
                        cat("1.  Training model with metagenes ...");flush.console()
                              #X = cbind(data.frame(t(meta))#[c("mitotic", "erbb2", "er", "chr7p11.2", "mes.lymphneg"),]))
				#	,clinical)
				X = data.frame(t(meta))
                              upper = terms(clinicalSurvData~(.), data = X)
                              coxmodel = step(coxph(clinicalSurvData~(.), data=X), scope=upper, direction="both", k=2, trace=FALSE)
                        cat("done!\n");flush.console()
#===== 2. GBM model =========
			cat("2.  Training gbm model...");flush.console()
				X = data.frame(t(meta))
				gbmmodel = gbm.cvrun(clinicalSurvData~.,data=X, distribution="coxph", shrinkage=0.002, n.trees=ntrees, interaction.depth=6, cv.folds=5, verbose=F, seed=913) # my bday ;D
			cat("done!\n");flush.console()
#===== 3. AIC models clinical only =====
			cat("3.  Training AIC model using only clinical features...");flush.console()
				X = clinical
                                upper = terms(clinicalSurvData~(.), data = X)
				cm = step(coxph(clinicalSurvData~1, data=X),scope=upper, direction="both", k=2, trace=FALSE)
                        cat("done!\n");flush.console()
#===== 4. GBM model =====
			cat("4.  Training gbm model...");flush.console()
				X = X[, attr(cm$terms, "term.labels")]
                                cgbm <- gbm.cvrun(clinicalSurvData~., data=X ,distribution="coxph", shrinkage=0.002, n.trees=ntrees, interaction.depth=10, cv.folds=5, verbose=F, seed=53) 
			cat("done!\n");flush.console()
#===== 5. AIC models on recycled features =======
                        cat("5.  Training AIC model with recycled features ...");flush.console()
                              #X = cbind(data.frame(t(meta))#[c("mitotic", "erbb2", "er", "chr7p11.2", "mes.lymphneg"),]))
				#	,clinical)
				X = cbind(data.frame(t(meta)), clinical)
				X = X[, removeTaggedFeatures(colnames(X), c(  attr(coxmodel$terms, "term.labels"), attr(cm$terms,"term.labels")   ))]
				#X = X[, setdiff(colnames(X), c(  attr(coxmodel$terms, "term.labels"), attr(cm$terms,"term.labels")   ))]
				#X = cbind(data.frame(t(meta)))
				#X = X[, setdiff(colnames(X), attr(coxmodel$terms, "term.labels") )]

                              upper = terms(clinicalSurvData~., data = X)
                              recycle = step(coxph(clinicalSurvData~(.), data=X), scope=upper, direction="both", k=2, trace=FALSE)
                        cat("done!\n");flush.console()

#===== 6. KNN model ======
			cat("6. Creating KNN database ...");flush.console()
			t = clinicalSurvData[,1]
			defSurvSamples = which(clinicalSurvData[,2]==1 | clinicalSurvData[,1] > 365 * 10)
			ccdi = getAllCCDIWz(meta, clinicalSurvData)
			#idx = ccdi[c("er", "mitotic", "puf60", "erbb2", "chr7p11.2", "ls", "mt", "chr15q26.1"
			#	, "VEGFA_g", "TP53_g","chr17q21.31", "chr19q13.2", "chrXp11.23")]
			idx = ccdi[c( "mitotic", "erbb2","ls", "mt", "chr7p11.2")]
			knnmodel = list()
			knnmodel$x.train = list(meta=meta[names(idx), defSurvSamples], time=t[defSurvSamples], concordance=idx)
			
			#clnc = lazyImputeDFClnc(clinicalFeaturesData)
			knnmodel$c.train = preproClncKNN(clnc, clinicalSurvData, ccdi.upper=0.6, ccdi.lower=0.4)

			cat("done!\n");flush.console()
#===== 7. Training cox model using minimal features =======
                        cat("7. Training clinical model with minimalist features...");flush.console()
				X = data.frame( cbind(meta["mitotic",], meta["ls.erneg",], clinical$lymph_nodes_positive, meta["mes.lymphneg",], meta["susd3",], clinical$age_at_diagnosis, clinical$tr.RT, clinical$tr.CT) )
				colnames(X) = c("CIN", "LYM_ERNeg", "lymNum", "MES_lymNumNeg", "SUSD3", "age", "tr.RT", "tr.CT")
				
                              cox.a = coxph(clinicalSurvData~., data=X)
                        cat("done!\n");

#===== 8. Training GBM model using minimal features =========
			cat("8. Training gbm model...");flush.console()
                        	#gbmmodel = gbm.fit(X,clinicalSurvData,distribution="coxph", shrinkage=0.001, n.trees=2000, interaction.depth=7, bag.fraction=1, train.fraction=1, verbose=F)
                                gbm.a <- gbm.cvrun(clinicalSurvData~., data=X ,distribution="coxph", shrinkage=0.002, n.trees=ntrees, interaction.depth=8, cv.folds=5, verbose=F, seed=913) #seed = my birthday :D !
			cat("done!\n");flush.console()
#===== 9. Training cox model using minimal features =======
                        cat("9. Training model with oncogene minimalist features...");flush.console()
				X = data.frame( cbind(meta["zmynd10",], col11a1.lymphneg30, clinical$age_at_diagnosis, clinical$tr.RT, clinical$tr.CT, meta["ls.erneg",], meta["TP53_g",], lsxlym, meta["VEGFA_g",]) )
				colnames(X) = c("ZMYND10", "COL11A1g_lymNumNeg", "age", "RT", "CT", "lym.erneg", "TP53g", "VEGFAg")
				
                              cox.b = coxph(clinicalSurvData~., data=X)
                        cat("done!\n");

#===== 10. Training GBM model using minimal features =========
			cat("10. Training gbm model...");flush.console()
                        	#gbmmodel = gbm.fit(X,clinicalSurvData,distribution="coxph", shrinkage=0.001, n.trees=2000, interaction.depth=7, bag.fraction=1, train.fraction=1, verbose=F)
                                gbm.b <- gbm.cvrun(clinicalSurvData~., data=X ,distribution="coxph", shrinkage=0.002, n.trees=ntrees, interaction.depth=8, cv.folds=5, verbose=F, seed=503) #seed = my birthday :D !
			cat("done!\n");flush.console()

                              .self$model <- list(coxmodel=coxmodel, 
						gbmmodel=gbmmodel, 
						cm=cm, 
						cgbm=cgbm, 
						recycle = recycle,
						knnmodel=knnmodel,
						cox.a=cox.a,
						gbm.a=gbm.a,
						cox.b=cox.b,
						gbm.b=gbm.b
						)
                            },
#================================
#
# customPredict
#
#====================================

                            customPredict = function(exprData, copyData, clinicalFeaturesData)
                            {
				#meta.cnv = CreateMetageneSpace(exprs(copyData), .self$cnvome, .self$annot.cnv)$metaSpace
                              rm(copyData)

				clnc = lazyImputeDFClncFULL(clinicalFeaturesData)
                              	clinical <- expandClncFULL(clnc)

                        cat("Create metagene space...");flush.console()
                              #meta = CreateMetageneSpace(exprs(exprData), .self$attractome, .self$annot)$metaSpace
                              meta = CreateMetageneSpace(exprs(exprData), chosenProbes = .self$chosenProbes)
				#meta = t(sapply(.self$chosenProbes, function(pbs){apply(exprs(exprData)[pbs,], 2, mean)}))
				#meta = t( sapply(.self$attractome, function(pbs){ apply(exprs(exprData)[pbs,] , 2, function(a){mean(a, na.rm=TRUE)}) }  ) )
                              gs = CreateMetageneSpace(exprs(exprData), chosenProbes = .self$chosenProbes_g)
				tp53 = gs["TP53_g",]
				gs = t(apply(gs, 1, function(x){ x - median(x)}))
				ls = meta["ls",]
				col11a1 = exprs(exprData)["ILMN_2392803",]
				meta = t(apply(meta, 1, function(x){ x - median(x)}))
				#meta = t(sapply(rownames(meta), function(a){meta[a,] - .self$mdns[a]}))
			#===== Conditioning mesenchymal transition metagene by lymph node status
				idx = (clinical[,"lymph_nodes_positive"]<1 & clinical[,"size"] < 30)
				mes.lymphneg = meta["mt",] * idx
				mes.lymphneg[idx] = mes.lymphneg[idx] - median(mes.lymphneg[idx])
				#mes.lymphneg[idx] = mes.lymphneg[idx] - .self$mdns["mes.lymphneg"]
				meta = rbind(meta, mes.lymphneg)
				col11a1.lymphneg30 = col11a1 * idx
				col11a1.lymphneg30[idx] = col11a1.lymphneg30[idx] - median(col11a1.lymphneg30[idx])
				
				idx = (clinical[,"lymph_nodes_positive"] > 3)
				ls.lymphpos = ls * idx
				ls.lymphpos[idx] = ls.lymphpos[idx] - median(ls.lymphpos[idx])
				#ls.lymphpos[idx] = ls.lymphpos[idx] - .self$mdns["ls.lymphpos"]
				meta = rbind(meta, ls.lymphpos)
				#meta = rbind(meta, gs)

				idx = (meta["er",] < 0 & meta["erbb2", ] < 0)
				ls.erneg = ls * idx
				ls.erneg[idx] = ls.erneg[idx] - median(ls.erneg[idx])
				#ls.erneg[idx] = ls.erneg[idx] - .self$mdns["ls.erneg"]
				meta = rbind(meta, ls.erneg)

				idx = meta["er",] < 0
				tp53.erneg = tp53 * idx
				tp53.erneg[idx] = tp53.erneg[idx] - median(tp53.erneg[idx])
				gs = rbind(gs, tp53.erneg)

				meta = rbind(meta, gs)

				#idx = meta["ls",] < 0
				#chr17p12 = meta.cnv["chr17p12",]
				#chr17p12.lsneg = chr17p12 * idx
				#meta = rbind(meta, chr17p12.lsneg)

				lymph = clinical[,"lymph_nodes_positive"]
				lsxlym = ls *lymph
				lsxlym = lsxlym - median(lsxlym)
			rm(exprData)
				#meta = rbind(meta, meta.cnv)
                        cat("done!\n");flush.console()
				p = matrix(NA, nrow=length(.self$model), ncol=nrow(clinical))
#===== 1. Predict using metagenes only model =====
			cat("1.  Predicting using metagenes AIC model...");flush.console()
				X = data.frame(t(meta))
                              p[1,] = predict(.self$model$coxmodel, X)
                        cat("done!\n");flush.console()
#===== 2. Predict using Attractor + clinical GBM model =====
			cat("2.  Predicting using gbm model...");flush.console()
                              X = data.frame(t(meta))
                              best.iter=gbm.perf(.self$model$gbmmodel, method="cv", plot.it=FALSE)
			      cat("Best iter: ", best.iter, "\n", sep="");flush.console()
			      p[2,] = predict.gbm(.self$model$gbmmodel, X, best.iter)
			      #p2 = predict.gbm(.self$model[[2]], X, 1500)
			cat("done!\n");flush.console()
#===== 3. Predict using clinical only model =====
			cat("3.  Predicting using clinical AIC model...");flush.console()
				X = clinical
                              p[3,] = predict(.self$model$cm, X)
			cat("done!\n");flush.console()
#===== 4. Predict using gbm model =====
			cat("4.  Predicting using clinical GBM model...");flush.console()
				X = X[, attr(.self$model$cm$terms, "term.labels")]
                              best.iter=gbm.perf(.self$model$cgbm, method="cv", plot.it=FALSE)
			      cat("Best iter: ", best.iter, "\n", sep="");flush.console()
			      p[4,] = predict.gbm(.self$model$cgbm, X, best.iter)
			cat("done!\n");flush.console()
#===== 5. Predict using recycled model =====
			cat("5.  Predicting using recycle model...");flush.console()
				#X = cbind(data.frame(t(meta)))
				#X = X[, setdiff(colnames(X), attr(.self$model$coxmodel$terms, "term.labels") )]
				X = cbind(data.frame(t(meta)), clinical)
				X = X[, removeTaggedFeatures(colnames(X), c(  attr(.self$model$coxmodel$terms, "term.labels"), attr(.self$model$cm$terms,"term.labels")   ))]
				#X = X[, setdiff(colnames(X), c(  attr(.self$model$coxmodel$terms, "term.labels"), attr(.self$model$cm$terms,"term.labels")   ))]
                              p[5,] = predict(.self$model$recycle, X)
                        cat("done!\n");flush.console()

#===== 6. Predict using KNN model =====
			cat("6.  Predicting using KNN model ...");flush.console()
				knnmodel = .self$model$knnmodel
				qX = meta[names(knnmodel$x.train$concordance),]
				qC = clnc[,colnames(knnmodel$c.train$clinical)]
				qC = t(preproClncKNN(qC, isFactorIn=knnmodel$c.train$isFactor, dwIn=knnmodel$c.train$distWeight)$clinical)
				wvec = c(abs(knnmodel$x.train$concordance-0.5), abs(knnmodel$c.train$concordance-0.5))
				qAll = rbind(qX, qC)
				trainDB = rbind(knnmodel$x.train$meta, t(knnmodel$c.train$clinical))
				trainTime = knnmodel$x.train$time
				out=ewknn.predict(trainDB, trainTime, qAll, wvec, k=floor(0.1*ncol(trainDB)))
				p[6,] = out
                        cat("done!\n");flush.console()
#===== 7. Predict using minimalist model =====
			cat("7.  Predicting using protective minimalist model ...");flush.console()
				X = data.frame( cbind(meta["mitotic",], meta["ls.erneg",], clinical$lymph_nodes_positive, meta["mes.lymphneg",], meta["susd3",], clinical$age_at_diagnosis, clinical$tr.RT, clinical$tr.CT) )
				colnames(X) = c("CIN", "LYM_ERNeg", "lymNum", "MES_lymNumNeg", "SUSD3", "age", "tr.RT", "tr.CT")
                              p[7,] = predict(.self$model$cox.a, X)
                        cat("done!\n");flush.console()
#===== 8. Predict using minimalist model =====
			cat("8.  Predicting using gbm model...");flush.console()
                              best.iter=gbm.perf(.self$model$gbm.a, method="cv", plot.it=FALSE)
			      cat("Best iter: ", best.iter, "\n", sep="");flush.console()
			      p[8,] = predict.gbm(.self$model$gbm.a, X, best.iter)
			      #p2 = predict.gbm(.self$model[[2]], X, 2000)
			cat("done!\n");flush.console()
#===== 9. Predict using minimalist model =====
			cat("9.  Predicting using oncogene minimalist model ...");flush.console()
				X = data.frame( cbind(meta["zmynd10",], col11a1.lymphneg30, clinical$age_at_diagnosis, clinical$tr.RT, clinical$tr.CT, meta["ls.erneg",], meta["TP53_g",], lsxlym, meta["VEGFA_g",]))
				colnames(X) = c("ZMYND10", "COL11A1g_lymNumNeg", "age", "RT", "CT", "lym.erneg", "TP53g", "VEGFAg")
                              p[9,] = predict(.self$model$cox.b, X)
                        cat("done!\n");flush.console()
#===== 10. Predict using minimalist model =====
			cat("10.  Predicting using gbm model...");flush.console()
                              best.iter=gbm.perf(.self$model$gbm.b, method="cv", plot.it=FALSE)
			      cat("Best iter: ", best.iter, "\n", sep="");flush.console()
			      p[10,] = predict.gbm(.self$model$gbm.b, X, best.iter)
			      #p2 = predict.gbm(.self$model[[2]], X, 2000)
			cat("done!\n");flush.console()

#===== Combining predictions =====
				
                              .self$predictions = p
				pout = matrix(NA, nrow=2, ncol=ncol(p))
				pout[1,] = apply(p[c(1:5, 9, 10),], 2, sum) +  365/p[6,]
				pout[2,] = p[7,] + p[8,]
				pz = t(apply(pout, 1, function(x){ (x-mean(x)) / sd(x)}))
                              p = apply(pz, 2, sum)
				#p = apply(pz, 1, mean)
                              return (p)
                            }
                            
                            )
                          )
