import xml.etree.ElementTree as ET
import numpy as np
import pdfs
import re

class Parser:
    betaElement = None
    def __init__(self):
		self.distRanges			= {}

    def parseNaming(self,input='naming.xml'):	
		mainTree 			= ET.parse(input)	
		root 				= mainTree.getroot() 
		mappingElement		= root.find('paramName_mapping')	
		return self.parseMapping(mappingElement)
	
    def parseSetting(self,input='setting.xml'):	
		mainTree 			= ET.parse(input)	
		root 				= mainTree.getroot() 
		outputDist			= root.find('outputDistribution')		
		varElement			= root.find('defaultAppValues')		
		variables			= self.parseVarTextElement(varElement)		
		Parser.betaElement 	= outputDist.getchildren()[0]
		distList			={}
		inputDist			= root.find('inputDistributions')		
		for child in inputDist.getchildren():		
			dName 			= child.get('name')
			dClass 			= getattr(pdfs,child.get('class'))
			distList[dName] = dClass					
		return distList , variables, self.parseMapping(root.find('production-type_mapping')), self.parseMapping(root.find('paramName_mapping'))

    def parseMapping(self, element):
		mapping={}
		for item in element.getchildren(): 
			mapping[item.get('returnedName')] =  re.compile(item.get('exp'))
		return mapping
		
    def parseParamRanges(self,input):	
		
		mainTree 			= ET.parse(input)	
		root 				= mainTree.getroot()		
		parameters			= root.find('parameters')
		for child in parameters.getchildren():
			paraType  = child.get('type')
			if paraType =="distribution":
				paramValues = self.parseDistParameters(child)
			elif paraType =="chart":
				paramValues = self.parseChartParameters(child)
			elif paraType =="range":
				paramValues = self.parseRangeParameters(child)
			if paramValues is None:
				continue
			paraID = self.createParamID(child.get('name'),child.get('production-type'),child.get('from-production-type'),child.get('to-production-type'))

			self.distRanges[paraID]= paramValues

    def createParamID(self, name, pt, from_pt, to_pt):	
		pID='%s '%name
		if pt      is not None:
			pID ="%s%s "%(pID,pt)
		if from_pt is not None:
			pID ="%s%s "%(pID,from_pt)
		if to_pt   is not None:
			pID ="%s%s "%(pID,to_pt  )
			
		return Parser.getParamID(pID)
				
    def parseRangeParameters(self, element):
		paralist  = self.parseParameters(element,['bounds'])
		bounds   = self.toRangeFormat(paralist[0])
		return[bounds[0],bounds[1]]
		
    def parseChartParameters(self, element):
		paralist  = self.parseParameters(element,['xBounds','yBounds'])
		xBounds   = self.toRangeFormat(paralist[0])
		yBounds   = self.toRangeFormat(paralist[1])
		return[xBounds[0],xBounds[1],yBounds[0],yBounds[1]]

    def toRangeFormat(self, para):
		if para is None:
			return [-1,-1]
		val = para.split(',')
		if len(val) < 2:
			return [float(val[0]),float(val[0])]
		return [float(val[0]),float(val[1])]
		
    def parseDistParameters(self, element):
		paralist  = self.parseParameters(element,['bounds','mean','variance', 'skewness'])
		if len (paralist) ==0:
			return None
	
		bounds    = self.toRangeFormat(paralist[0])
		means     = self.toRangeFormat(paralist[1])
		variances = self.toRangeFormat(paralist[2])
		skewness  = self.toRangeFormat(paralist[3])

		return 	[bounds[0],bounds[1],means[0],means[1],variances[0],variances[1],skewness[0],skewness[1]]
				
    def parseParameters(self, element,paraList):
		outList=[]
		for para in paraList:
			elem = element.find(para)
			if elem is not None:
				outList.append(elem.text)
		return outList

    def parseVarTextElement(self, element):
		variableList				={}	
		for child in element.getchildren():		
			variableList[child.get('var')] = float(child.text)					
		return variableList
		
    def parsePiecewiseParameters(self, element, paraList):
		x	=[]
		y 	=[]
		allValues = element.findall("value")
		for item in allValues:
			itemValues=self.parseParameters(item,paraList)
			x.append(float(itemValues[0]))
			y.append(float(itemValues[1]))			
		return [x,y]
		
    def parseHistogramParameters(self, element, paraList):
		a		=[]
		bins	=[]
		weights	=[]
		allValues = element.findall("value")
		for item in allValues:
			itemValues=self.parseParameters(item,paraList)
			a.append(float(itemValues[0]))
			bins.append(float(itemValues[1]))
			weights.append(float(itemValues[2]))
			
		bins.insert(0,a[0])
		return [a,bins,weights]

    @staticmethod	
    def getParamID(paramID):
		return paramID.strip().replace(" ", "_")	
		
    @staticmethod	
    def getBetaClone():
		copiedBeta = Parser.betaElement.copy()
		for child in Parser.betaElement.getchildren():
			copiedChildElement = child.copy()
			copiedBeta.remove(child)
			copiedBeta.append(copiedChildElement)
		return copiedBeta	
		
    @staticmethod
    def getBetaElement(alpha,beta,loc,scale):
		betaElem = Parser.getBetaClone()
		children = betaElem.getchildren()
		children[0].text = str(alpha)
		children[1].text = str(beta)
		children[2].text = str(loc)
		children[3].text = str(scale)
		return betaElem		
		
    @staticmethod		
    def replaceChartOldValues(element, x,y):	
		allValues = element.findall("value")
		i = 0		
		for item in allValues:
			item[0].text = str(x[i])
			item[1].text = str(y[i])
			i = i + 1
			
    @staticmethod		
    def replaceRangeOldValue(element, value):	
		element.text = str(value)
			
    def getParamRanges(self,key):		
		if self.distRanges.has_key(key):
			return self.distRanges.get(key)
		return None 

    def isReplacableDistribution(self,key):					
		if self.distRanges.has_key(key):
			return True
		return False