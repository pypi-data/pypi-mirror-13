#!/usr/bin/env python
#Last-modified: 12 Feb 2016 03:58:04 PM

#         Module/Scripts Description
# 
# Copyright (c) 2008 Yunfei Wang <Yunfei.Wang1@utdallas.edu>
# 
# This code is free software; you can redistribute it and/or modify it
# under the terms of the BSD License (see the file COPYING included with
# the distribution).
# 
# @status:  experimental
# @version: 1.0.0
# @author:  Yunfei Wang
# @contact: yfwang0405@gmail.com

# ------------------------------------
# python modules
# ------------------------------------

import os
import sys
import numpy
import pandas
import rpy2.robjects as robjects 
from rpy2.robjects.packages import importr
from rpy2.robjects.numpy2ri import numpy2ri
from rpy2.robjects import pandas2ri

# ------------------------------------
# constants
# ------------------------------------

R = robjects.r
robjects.numpy2ri.activate()
pandas2ri.activate()

# ------------------------------------
# Misc functions
# ------------------------------------

# ------------------------------------
# Classes
# ------------------------------------

class Algorithms(object):
    '''
    Imporint R algorithms.
    '''
    def bh_qvalue(pvalues):
        '''
        Adjust pvalues using BH method. 
        Parameters:
            pvalues: list, numpy.ndarray or pandas.Series
                A list of pvalues.
        Returns:
            qval: rpy2.robjects.vectors.FloatVector
                A list of qvalues.
        '''
        R.assign('pvalues',pvalues)
        R('qvalues <- p.adjust(pvalues)')
        return list(R['qvalues'])
    bh_qvalue=staticmethod(bh_qvalue)
    def normalization(data,method='quantile'):
        '''
        Normalization among arrays.
        Parameters:
            data: pandas.DataFrame
                Expression matrix. N genes by M conditions.
            method: string
                Choices from "quantile", "none","scale" or "cyclicloess".
        Returns:
            ndata: pandas.DataFrame
                Normalized expression matrix.
        '''
        R("library('limma')")
        R.assign("data",data)
        R.assign("method",method)
        R("ndata <- normalizeBetweenArrays(as.matrix(data),method=method)")
        # convert back to dataframe
        ndata = pandas.DataFrame(pandas2ri.ri2py(R['ndata']),index=data.index,columns=data.columns)
        return ndata
    normalization=staticmethod(normalization)
    def limma_eBayes(data,group,tolog=False):
        '''
        Usiing Bayes method in limma call differential expression.
        Parameters:
            data: pandas.DataFrame
                Expression matrix.
            group: list
                Group information.
            tolog: bool
                Do log2 transformation or not.
        Returns:
            rst: pandas.DataFrame
                Statistics.
            ndata: pandas.DataFrame
                Processed data.
        '''
        group = robjects.FactorVector(group)
        if tolog:
            data = numpy.log2(data+1)
        R.assign('group',group)
        R.assign('data',data)
        # eBayes method
        importr('limma')
        R('group <- as.factor(group)')
        R('design <- model.matrix(~group)')
        R('fit <- lmFit(data, design)')
        R('fit <- eBayes(fit)')
        R('out <- topTable(fit, n=nrow(data), adjust = "BH")')
        R('rnames <- rownames(out)')
        # get result
        out = pandas2ri.ri2py(R['out'])
        out.columns = ['logFC','AvgExpr','tscore','pvalue','qvalue','B']
        out.index = pandas2ri.ri2py(R['rnames']) 
        out = out.ix[data.index,:] # reorder rows
        return out
    limma_eBayes=staticmethod(limma_eBayes)
    def CoxPH(data,onebyone=True):
        '''
        Cox (Proportional Hazards) Regression analysis.
        Parameters:
            data: pandas.DataFrame
                Clinical information with eg. expression values. 
                Required columns: 'E': 0 (event not observed) or 1 (event observed), 'T': integer, time of duration.
            onebyone: bool
                Do cox regression column by column if True.
        Returns:
            rst: pandas.DataFrame
                N genes by [ score, pvalue ]
        '''
        
        R.assign('clin',data.ix[:,['E','T']])
        names = list(data.columns)
        names.remove('E')
        names.remove('T')
        R("library('survival')")
        if onebyone and len(names):
            rst = pandas.DataFrame({'score':numpy.zeros(len(names)),'pvalue':numpy.zeros(len(names))},index=names)
            for name in names:
                R.assign('data',data.ix[:,name])
                R('coef<- coxph(Surv(T, E) ~ data, data=clin)')
                R('res <-summary(coef)$coefficients[,4:5]')
                rst.ix[name,:] = list(R['res'])
            return rst
        ###################
        # onebyone = False
        # to do
        ###################
    CoxPH=staticmethod(CoxPH)    

class Plot(object):
    '''
    '''
    def heatmap(data,outfile=None,col='gr'):
        '''
        Draw heatmap.
        '''
        importr('gplots')
        R.assign('data',data)
        if outfile:
            R.assign('outfile',outfile)
            R('pdf(outfile)')
        R('''ht2 <- heatmap.2(as.matrix(data),dendrogram="row",trace='none',Colv=NA,scale='row',hclustfun=function(x) hclust(x,method="complete"),distfun=function(x) as.dist((1-cor(t(x)))/2),col=greenred(75))''')
        if outfile:
            R('dev.off()')
        return R['ht2']
    heatmap=staticmethod(heatmap)


# ------------------------------------
# Main
# ------------------------------------

if __name__=="__main__":
    if len(sys.argv)==1:
        sys.exit("Example:"+sys.argv[0]+" file1 file2... ")
    for item in IO.BioReader(sys.argv[1],ftype='bed'):
        print item

