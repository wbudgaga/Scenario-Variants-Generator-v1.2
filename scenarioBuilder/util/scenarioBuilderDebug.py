import sys
sys.path.insert(1, '/s/chopin/b/grad/wbudgaga/noaa/scenarioBuilderWorkDir/scenarioBuilder_distVersion')
sys.path.insert(1, '/s/chopin/b/grad/wbudgaga/noaa/scenarioBuilderWorkDir/scenarioBuilder_distVersion/scenarioData')
import xml.etree.ElementTree as ET
import parsingManager 
reload (parsingManager)
import time
import sys
import os
import copy
import thread
import fileHandler as fh
reload (fh)
import warnings
import socket

class scenarioBuilder:
    def __init__(self,sampleScenario,paramRanges, outputDir=None):
		self.mainTree 		= ET.parse(sampleScenario)
		self.root 			= self.mainTree.getroot()
		self.PDFmanager 	= parsingManager.PDFManager(paramRanges)		
		self.paramElementList	= []		
		self.samples		= []
		self.dim		= 0
		self.SCENARIO_NAME	= 'scenario_%s.xml'

    def getRoot(self):		
		return self.root 
			 		
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

    def printTag(self,paremType):
		for obj in self.paramElementList:		
			dist = obj.obj
			typ  = obj.type
			if typ == paremType:
				print "%s"% obj.xmlElement.getchildren()[0].rag

    def checkVariant(self,l):	
		updated=False
		for obj in self.paramElementList:		
			dist = obj.obj
			typ  = obj.type
			if typ == "dist":	
				if obj.xmlElement.get('name').startswith('Dist') or obj.xmlElement.get('name').startswith('Lg Swine indirect')or obj.xmlElement.get('name').startswith('Sm Swine Ind') or obj.xmlElement.get('name').startswith('Sm Swine direct') or obj.xmlElement.get('name').startswith('LG Swine direct'):
					elem=obj.xmlElement.getchildren()[0].find('location')
					v= float(elem.text)

					if v < 0:
						elem.text=str(v*-1)
						print "Scenario:%s,    %s"%(l, v)
						updated=True
		
		if updated==True:
			self.mainTree.write('/s/red-rock/a/nobackup/budgaga/scenarios/mn_variants_failed3/scenario_%s.xml'%l,  xml_declaration=True, )
		
if __name__ == '__main__':	
    #scenario 	= sys.argv[1]
    paramRanges = "/s/chopin/b/grad/wbudgaga/noaa/scenarioBuilderWorkDir/scenarioBuilder_distVersion/scenarioData/paramRanges_v11.xml"  #sys.argv[2]
    #failedList = [704,2381,4301,6172,6862,11795,14451,15529,16565,18966,19148,21342,27109,33899,34263,34505,36583,39063,39905,40268,42862,45703,48418,48841,52740,54186,55635,58619,59457,66803,70515,71178,71846,74508,77042,77960,80706,81531,83493,83817,85737,86245,87083,88131,88817,88819,88855,93972,94429,95995,96073,96828]
    s="/s/chopin/b/grad/wbudgaga/noaa/scenarioBuilderWorkDir/scenarioBuilder_distVersion/scenarioData/naadsm_texas.xml"
    sb 		= scenarioBuilder(s, paramRanges)
    sb.parse(sb.getRoot())
    sb.printTag("dist")
    #for i in range(100000):
	#l=i+1
	#s="/s/chopin/b/grad/wbudgaga/noaa/scenarioBuilderWorkDir/scenarioBuilder_distVersion/scenarioData/naadsm_texas.xml"
    	#sb 		= scenarioBuilder(s, paramRanges)
    	#sb.parse(sb.getRoot())	
    	#sb.printTag("dist")
    	#sb.checkVariant(l)
    #print("The time spent on creating 1 variants (each has %i dimensions) is %f seconds"% (sb.dim,time.time()))
 
