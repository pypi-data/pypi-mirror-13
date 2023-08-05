#! /usr/bin/env python

"""
Copyright (C) 2016  Wesley Fraser

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


__author__ = 'Wesley Fraser (@wtfastro, github: fraserw <westhefras@gmail.com>), Academic email: wes.fraser@qub.ac.uk'

import numpy as num, scipy as sci,emcee
from trippy import bgFinder

def lnprob(r,dat,lims,psf,ue,useLinePSF,verbose=False):
    psf.nForFitting+=1
    (x,y,amp)=r
    (a,b)=dat.shape
    if  amp<=0 or x>=b or x<=0 or y<=0 or y>=a: return -num.inf
    diff=psf.remove(x,y,amp,dat,useLinePSF=useLinePSF)[lims[0]:lims[1],lims[2]:lims[3]]
    chi=-0.5*num.sum(diff**2/ue[lims[0]:lims[1],lims[2]:lims[3]]**2)**0.5
    if verbose: print '{:6d} {: 8.3f} {: 8.3f} {: 8.3f} {: 10.3f}'.format(psf.nForFitting,x,y,amp,chi)
    return chi


def lnprobDouble(r,dat,psf,ue,useLinePSF,verbose=False):
    psf.nForFitting+=1
    (A,B)=dat.shape
    (X,Y,AMP,x,y,amp)=r
    if amp<=0 or AMP<=0 or X<0 or X>B or x<0 or x>B or Y<0 or Y>A or y<0 or y>A: return -num.inf

    diff=psf.remove(X,Y,AMP,dat,useLinePSF=useLinePSF)
    diff=psf.remove(x,y,amp,diff,useLinePSF=useLinePSF)
    chi=-0.5*num.sum((diff**2/ue**2))#/(A*B-7)
    #chi=-num.sum(diff**2)**0.5
    if verbose:
        print '{:6d} {: 8.3f} {: 8.3f} {: 8.3f} {: 8.3f} {: 8.3f} {: 8.3f} {: 10.3f}'.format(psf.nForFitting,x,y,amp,X,Y,AMP,chi)
    return chi



class MCMCfitter:

    def __init__(self,psf,imageData):
        self.psf=psf
        self.imageData=num.copy(imageData)
        self.fitted=False

    def fitWithModelPSF(self,x_in,y_in,m_in=-1.,fitWidth=20,
                        nWalkers=20,nBurn=10,nStep=20,
                        bg=None,useErrorMap=False,
                        useLinePSF=False,verbose=False):

        """
        Using emcee (It's hammer time!) the provided image is fit using
        the provided psf to find the best x,y and amplitude, and confidence
        range on the fitted parameters.

        x_in, y_in, m_in - initial guesses on the true centroid and amplitude of the object
        fitWidth - the width +- of x_in/y_in of the data used in the fit
        nWalkers, nBurn, nStep - emcee fitting paramters. If you don't know what these are RTFM
        bg - the background of the image. Needed for the uncertainty table.
             **Defaults to None.** When set to default, it will invoke
             the background measurement and apply that. Otherwise, it assumes you are dealing with
             background subtracted data already.
        useErrorMap - if true, a simple pixel uncertainty map is used in the fit. This is adopted as
                      ue_ij=(imageData_ij+bg)**0.5, that is, the poisson noise estimate. Note the fit confidence range
                      is only honest if useErrorMap=True.
        useLinePSF - use the TSF? If not, use the PSF
        verbose - if set to true, lots of information printed to screen
        """

        self.nForFitting=0
        self.useLinePSF=useLinePSF

        if fitWidth>self.psf.boxSize:
            raise NotImplementedError('Need to keep the fitWidth <= boxSize.')

        (A,B)=self.imageData.shape
        ai=max(0,int(y_in)-fitWidth)
        bi=min(A,int(y_in)+fitWidth+1)
        ci=max(0,int(x_in)-fitWidth)
        di=min(B,int(x_in)+fitWidth+1)
        dat=num.copy(self.imageData)



        if bg==None:
            bgf=bgFinder.bgFinder(self.imageData)
            bg=bgf.smartBackground()
            dat-=bg

        if not useErrorMap:
            ue=dat*0.0+1.
        else:
            ue=(dat+bg)**0.5

        if m_in==-1.:
            if useLinePSF:
                m_in=self.psf.repFact*self.psf.repFact*num.sum(dat)/num.sum(self.psf.longPSF)
            else:
                m_in=self.psf.repFact*self.psf.repFact*num.sum(dat)/num.sum(self.psf.fullPSF)

        nDim=3
        r0=[]
        for ii in range(nWalkers):
            r0.append(num.array([x_in,y_in,m_in])+sci.randn(3)*num.array([0.1,0.1,m_in*0.25]))
        r0=num.array(r0)


        sampler=emcee.EnsembleSampler(nWalkers,nDim,lnprob,args=[dat,(ai,bi,ci,di),self.psf,ue,useLinePSF,verbose])
        pos, prob, state=sampler.run_mcmc(r0,nBurn)
        sampler.reset()
        pos, prob, state = sampler.run_mcmc(pos, nStep, rstate0=state)
        self.samps=sampler.chain
        self.probs=sampler.lnprobability
        self.dat=num.copy(dat)
        self.fitted=True


    def fitResults(self,confidenceRange=0.67):
        """
        Return the best point and confidence interval.

        confidenceRange - the range for the returned confidence interval

        Returns (bestPoint, confidenceArray) Will return None if a fit hasn't been run yet.
        """

        if not self.fitted:
            print "You haven't actually run a fit yet!"
            return None

        (Y,X,b)=self.samps.shape
        goodSamps=[]
        for ii in range(Y):
            for jj in range(X):
                g=[]
                for kk in range(b):
                    g.append(self.samps[ii,jj][kk])
                g.append(self.probs[ii,jj])
                goodSamps.append(g)
        goodSamps=num.array(goodSamps)
        args=num.argsort(goodSamps[:,b])
        goodSamps=goodSamps[args]

        bp=goodSamps[-1]
        print 'Best point:',bp
        self.residual=self.psf.remove(bp[0],bp[1],bp[2],self.dat,useLinePSF=self.useLinePSF)
        if b==6:
            self.residual=self.psf.remove(bp[3],bp[4],bp[5],self.residual,useLinePSF=useLinePSF)
        self.fitFlux=num.sum(self.psf.model)*self.psf.fitFluxCorr

        uncert=[]
        for ii in range(b):
            args=num.argsort(goodSamps[:,ii])
            x=goodSamps[args][:,ii]
            uncert.append([x[int((confidenceRange/2)*len(x))],
                           x[int((1-confidenceRange/2)*len(x))]])
        return (bp,uncert)


    def fitDoubleWithModelPSF(self,x_in,y_in,X_in,Y_in,bRat_in,m_in=-1.,bg=None,
                              fitWidth=20,nWalkers=30,nBurn=50,nStep=100,
                              useErrorMap=False,
                              useLinePSF=False,verbose=False):
        """
        Using emcee (It's hammer time!) two sources are fit using
        the provided psf to find the best x,y and amplitude, and confidence
        range on the fitted parameters.

        x_in, y_in, m_in, X_in, Y_in, bRat - initial guesses on the true centroids, the amplitude and brightness ratio
                                             of the two sources
        fitWidth - the width +- of x_in/y_in of the data used in the fit
        nWalkers, nBurn, nStep - emcee fitting paramters. If you don't know what these are RTFM
        bg - the background of the image. Needed for the uncertainty table.
             **Defaults to None.** When set to default, it will invoke
             the background measurement and apply that. Otherwise, it assumes you are dealing with
             background subtracted data already.
        useErrorMap - if true, a simple pixel uncertainty map is used in the fit. This is adopted as
                      ue_ij=(imageData_ij+bg)**0.5, that is, the poisson noise estimate. Note the fit confidence range
                      is only honest if useErrorMap=True.
        useLinePSF - use the TSF? If not, use the PSF
        verbose - if set to true, lots of information printed to screen
        """

        print "\n\n\nTHIS HASN'T BEEN FULLY TESTED YET!!!\n\n\n"

        (A,B)=self.imageData.shape
        ai=max(0,int((y_in+Y_in)/2)-fitWidth)
        bi=min(A,int((y_in+Y_in)/2)+fitWidth)
        ci=max(0,int((x_in+X_in)/2)-fitWidth)
        di=min(B,int((x_in+X_in)/2)+fitWidth)
        dat=self.imageData[ai:bi,ci:di]

        if bg==None:
            bgf=bgFinder.bgFinder(imageData)
            bg=bgf.smartBackground()
            dat-=bg


        if not useErrorMap:
            ue=dat*0.0+1.
        else:
            ue=(dat+bg)**0.5



        if m_in==-1.:
            if useLinePSF:
                m_in=num.sum(dat)/num.sum(self.psf.longPSF)
            else:
                m_in=num.sum(dat)/num.sum(self.psf.fullPSF)

        nDim=6
        r0=[]
        for ii in range(nWalkers):
            r0.append(num.array([x_in-ci,y_in-ai,m_in,X_in-ci,Y_in-ai,m_in*bRat_in])+sci.randn(6)*num.array([1.,1.,
                                                                                                          m_in*0.4,
                                                                                                    1.,1.,
                                                                                               m_in*0.4*bRat_in]))
        r0=num.array(r0)

        sampler=emcee.EnsembleSampler(nWalkers,nDim,lnprobDouble,args=[dat,self.psf,ue,useLinePSF,verbose])
        pos, prob, state=sampler.run_mcmc(r0,nBurn)
        sampler.reset()
        pos, prob, state = sampler.run_mcmc(pos, nStep, rstate0=state)
        self.samps=sampler.chain
        self.probs=sampler.lnprobability
        self.dat=num.copy(dat)
        self.fitted=True