import xml.etree.ElementTree as ET
import parsingManager 
reload (parsingManager)
import time
import sys
import os
from pyDOE import *
import copy
import thread
from util import fileHandler as fh
reload (fh)
import warnings
import socket
hostname = socket.gethostname()
mainWorkDir="/s/%s/a/tmp"%hostname
class scenarioBuilder:
    def __init__(self,sampleScenario,paramRanges, workDir =None):
		#warnings.simplefilter("ignore", RuntimeWarning) 
		
		self.OUTPUT_DIR 	= "%s/%s/scenarios"%(mainWorkDir,workDir)
		self.LHS_DIR 		= "%s/%s/lhs"%(mainWorkDir,workDir)
		self.SCENARIO_NAME 	= "scenario_"		
		self.mainTree 		= ET.parse(sampleScenario)
		self.root 			= self.mainTree.getroot()
		self.PDFmanager 	= parsingManager.PDFManager(paramRanges)		
		self.paramElementList	= []		
		self.samples		= []
		self.dim			= 0
		
		#if workDir is not None:
		#	self.setOutputDir(workDir)
		self.checkOutputDir(self.OUTPUT_DIR)

    def getRoot(self):		
		return self.root 

    def setOutputDir(self,dir):		
		self.OUTPUT_DIR = dir
			
    def checkOutputDir(self,folder):
		try:	
			if not os.path.exists(folder):
				os.makedirs(folder)	
		except Exception:
			pass
 		
    def parse(self,parent):	
		for child in parent.getchildren():
			objList  = self.PDFmanager.parse(child)
			for obj in objList:
					self.dim += obj.nrOfVar
					self.paramElementList.append(obj)
			if len(objList)==0:
				self.parse(child)
			
    def storeScenario(self, variantIdx):
		scenarioFile = "%s/%s%s.xml"%(self.OUTPUT_DIR, self.SCENARIO_NAME, str(variantIdx))
		self.mainTree.write(scenarioFile,  xml_declaration=True, )

    def createSample(self,variantIdx, offset):	
		lhsSample = self.samples[variantIdx-1,:]
		lhsIdx1 = lhsIdx2 = 0
		for obj in self.paramElementList:		
			lhsIdx2 += obj.nrOfVar
			obj.replaceOldElement(lhsSample[lhsIdx1:lhsIdx2])
			lhsIdx1 = lhsIdx2
		self.storeScenario(variantIdx + offset)
		
    def createSamples(self,numberOfVariants, offset):
		for i in range(numberOfVariants):
			self.createSample(i+1, offset)
			
    def loadSamples(self, idx):	
		fHandler 	= fh.FileHandler('%s/samples_%s.lhs'%(self.LHS_DIR,idx),'r')
		self.samples 	= fHandler.getAsArray()
		return self.samples.shape[0]

if __name__ == '__main__':
#    if len(sys.argv)!=5:
#		print("You have to enter the file name of the scenario(Ex:scenario.xml), parameter ranges(Ex:paramRanges.xml), and chunckNumber")	
#		sys.exit(0)
		
    scenario 	= sys.argv[1]
    paramRanges = sys.argv[2]
    chunckNumber= int(sys.argv[3])
    chunckSize  = int(sys.argv[4])
    workDir		= sys.argv[5]
    sb 		= scenarioBuilder(scenario, paramRanges, workDir)
    ts 		= time.time()	
    sb.parse(sb.getRoot())	
    nrOfVariants = sb.loadSamples(chunckNumber)
    offset = chunckNumber * chunckSize 
    sb.createSamples(nrOfVariants, offset)
    print("The time spent on creating %i variants (each has %i dimensions) is %f seconds"% (nrOfVariants, sb.dim,time.time() - ts))
 
