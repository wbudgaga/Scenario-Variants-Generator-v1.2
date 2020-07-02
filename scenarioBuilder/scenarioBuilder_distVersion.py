import xml.etree.ElementTree as ET
import parsingManager 
reload (parsingManager)
import time
import sys
import os
from pyDOE import *
from util import fileHandler as fh
import concurrent.futures
import warnings
import socket

hostname = socket.gethostname()
mainWorkDir="/s/%s/a/tmp"%hostname

class scenarioBuilder:
    def __init__(self,numberOfVariants, sampleScenario,paramRanges, workDir=None):
		warnings.simplefilter("ignore", RuntimeWarning) 
		self.workDir			= workDir
		self.LHS_DIR 			= "%s/%s/lhs"%(mainWorkDir,workDir)
		self.sampleScenario		= sampleScenario
		self.paramRanges		= paramRanges
		self.mainTree 			= ET.parse(sampleScenario)
		self.root 				= self.mainTree.getroot()
		self.PDFmanager 		= parsingManager.PDFManager(paramRanges)		
		self.numberOfVariants	= numberOfVariants
		self.paramElementList	= []		
		self.unparsableELements	= set()
		self.dim				= 0
		#if workDir is not None:
		#	self.setOutputDir(workDir)
		self.checkOutputDir(self.LHS_DIR)

    def getRoot(self):		
		return self.root 

    def setOutputDir(self,dir):		
		self.OUTPUT_DIR = dir
			
    def checkOutputDir(self, dir):
		try:	
			if not os.path.exists(dir):
				os.makedirs(dir)	
		except Exception:
			pass
 		
    def parse(self, parent):	
		for child in parent.getchildren():
			objList  = self.PDFmanager.parse(child)
			for obj in objList:
					self.dim += obj.nrOfVar
					self.paramElementList.append(obj)
			if len(objList)==0:
				self.unparsableELements.add(child.tag)
				self.parse(child)
				
    def printUnparsableList(self):
		print "-----------------------------------"
		print "| The unparsable main elements:   |"
		print "-----------------------------------"
		for item in self.unparsableELements:                
			print item
		print "-----------------------------------"
		
    def arrayToString(self, data):
            rec = ""
            for item in data:                
                rec ="%s,%s"%(rec,item)
	    return rec[1:]
            

    def storeChunck(self, samples, idx):	
		fHandler = fh.FileHandler('%s/samples_%s.lhs'%(self.LHS_DIR,idx),'w')
		for i in range(samples.shape[0]):	
			t=self.arrayToString(samples[i])
			fHandler.addToFile(self.arrayToString(samples[i]))
		fHandler.closeFile()
		os.system('./scripts/remoteScenarioBuilder.sh %s %s %s %s %s'%(self.sampleScenario,self.paramRanges,idx, int(self.chunkSize), self.workDir))
		


    def createSamples(self, partitions):
		self.chunkSize = int(round(self.numberOfVariants / float(partitions)))
		start = 0
		generatedSamples = lhs(self.dim,samples = self.numberOfVariants )
		for i in range(partitions-1):
			end = start + self.chunkSize
			with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
				executor.submit(self.storeChunck,generatedSamples[start:end],i)
			start = end
		if start < self.numberOfVariants:
			self.storeChunck(generatedSamples[start:],partitions-1)	

    def storeCodesForParsedElem(self, fileName, content):
        fHandler = fh.FileHandler(fileName,'w')
        fHandler.addToFile(content)
        fHandler.closeFile()
		
if __name__ == '__main__':
    if len(sys.argv)!=6:
		print("Distributed version of scenario builder \n  run scenarioBuilder_distVersion.py.py  [#Variants] [Scenario] [ParamRanges] [#Partitions] [workDir]")	
		sys.exit(0)

    nrOfVariants= int(sys.argv[1])
    scenario 	= sys.argv[2]
    paramRanges = sys.argv[3]
    paritions   = int(sys.argv[4])
    wDir		= sys.argv[5]
    sb 			= scenarioBuilder(nrOfVariants,scenario, paramRanges, wDir)
    ts 			= time.time()	
    sb.parse(sb.getRoot())
    sb.createSamples(paritions)
    print("The time spent on creating %i variants (each has %i dimensions) is %f seconds"% (nrOfVariants, sb.dim,time.time() - ts))
    param, pt = sb.PDFmanager.getParemetersCodes()
    sb.storeCodesForParsedElem('parsedParameters.par', param)
    sb.storeCodesForParsedElem('productionTypes.pt', fh.FileHandler.convertListToString(pt))
    sb.printUnparsableList()
