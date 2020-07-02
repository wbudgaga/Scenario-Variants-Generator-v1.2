import numpy as np
import pdfs
reload (pdfs)
from pdfs import PDF
import pdfParser 
reload (pdfParser)
import sys
import string
class XMLElment:# think of class hierarchical structure
    def __init__(self, objType,n,xmlElement, obj):
		self.type 		= objType # dist, int, chart
		self.nrOfVar	= n
		self.xmlElement	= xmlElement
		self.obj		= obj
		
    def replaceDistElement(self,lhs1,lhs2,lhs3):
		betaVarient = self.obj.getBetaVariant(lhs1,lhs2,lhs3)
		betaVarient.distParam[3] = betaVarient.distParam[3] + betaVarient.distParam[2] # transfer scale to max
		newElement = betaVarient.getAsXMLElement(pdfParser.Parser) 
		oldChild = self.xmlElement.getchildren()[0]
		self.xmlElement.remove(oldChild)
		self.xmlElement.insert(0,newElement)
		
    def replaceChartElement(self,lhs1,lhs2,lhs3,lhs4):
		self.obj.updateChartValues(pdfParser.Parser,self.xmlElement.getchildren()[0],lhs1,lhs2,lhs3,lhs4) 
	
    def replaceOldElement(self,lhsValues):		
		if self.type == "dist":	
			self.replaceDistElement(lhsValues[0],lhsValues[1],lhsValues[2])
		elif self.type == "chart":	
			self.replaceChartElement(lhsValues[0],lhsValues[1],lhsValues[2],lhsValues[3])
		elif self.type == "range":	
			self.obj.updateRangeValue(pdfParser.Parser,self.xmlElement,lhsValues[0])


########################################################################################################
class PDFManager:
    def __init__(self,paraRangesFile):
		self.parser 					= pdfParser.Parser()
		self.parser.parseParamRanges(paraRangesFile)		
		self.distList, var, self.PTMap, self.PNMap	= self.parser.parseSetting()
		
		PDF.defaultCI 								= var.get("defaultCI")
		PDF.defaultNrPoints 						= var.get("defaultNrPoints")
		PDF.defaultBoundingBox 						= var.get("defaultBoundingBox")			
		self.ParsableMainElements					= ["disease-model",  "contact-spread-model", "detection-model", "airborne-spread-model", 
													   "contact-recorder-model", "test-model", "resources-and-implementation-of-controls-model",
													   "ring-vaccination-model","vaccine-model", "zone-model"]
		self.contactDict							= {}
		self.parsedParamList                        = []
        		        
    def getParamRanges(self,paramID):
		paramRange  	= self.parser.getParamRanges(paramID)
		if paramRange is None:
			raise ValueError("ERORR: The parameter: %s does not have historical ranges"%(paramID))
		return paramRange

    def getInstance(self,paramID,element):		
		classObj = self.distList.get(element.tag)
		if classObj is not None:
			ranges  	= self.getParamRanges(paramID)
			rangesClone = [r for r in ranges]
			distParam	= classObj.getParam(self.parser, element)
			return classObj.getInstance(distParam,rangesClone,PDF.defaultNrPoints)
		return None

    def getProductionTypes(self,objID):
		pt =[]
		for i in range(1,len(objID)):
			if objID[i] is not None:
				pt.append(objID[i])
		return pt

    def encodeParemeters(self,objRecords, allProductionTypes):
        content =''
        ptCodes =  string.digits + string.letters
        for obj in objRecords:
            objCode = obj[0]
            for i in range(3, len(obj)):
                objCode = "%s%s"%(objCode,ptCodes[allProductionTypes.index(obj[i])])
            objCode="%s:%s:%s"%(objCode, obj[1], obj[2])            
            content = "%s,%s"%(content, objCode)
        return content[1:]
	
    def getParemetersCodes(self):
		allProductionTypes 	= []
		objRecords 			= []
		namingMapList		= self.parser.parseNaming()
		for objData in self.parsedParamList:
			pnCode = self.getActualName(namingMapList, objData[0][0])
			
			if pnCode is None:
				print("ERORR: There is no naming code for the parameter name '%s'"%(objData[0]))
				print "(%s)"%objData[0][0].strip().lower()
				sys.exit(0)
			pt = self.getProductionTypes(objData[0])
                 		
			objRec = [pnCode, objData[1],objData[2]]
			for i in range(len(pt)):
                
                		pt_l = pt[i].lower()                
				if pt[i].lower() not in allProductionTypes:
					allProductionTypes.append(pt_l)
				objRec.append(pt_l)
			objRecords.append(objRec)
		allProductionTypes.sort()
		return self.encodeParemeters(objRecords,allProductionTypes) , allProductionTypes
		
    def getActualName(self,mapList, givenName):
		if givenName is None:
			return None
		for actualPT, matcher in mapList.iteritems():
			if matcher.match(givenName.strip().lower()) is not None:
				return actualPT
		return None 
		
    def isReplacableDistribution(self,key):
		if self.distList.has_key(key):
			return True
		return False 

    def parse(self, element):	
		elementObjects =[]
		pt0 		= element.get('production-type')
		fpt0 		= element.get('from-production-type')
		tpt0 		= element.get('to-production-type')
		zone0 		= element.get('zone')
		pt 		= self.getActualName(self.PTMap, pt0)
		fpt 		= self.getActualName(self.PTMap, fpt0)
		tpt 		= self.getActualName(self.PTMap, tpt0)
		zone 		= self.getActualName(self.PTMap, zone0)
		preName = ''
		contactType =''
		if element.tag == "contact-spread-model" or element.tag == "contact-recorder-model":
			contactType 	= self.getActualName(self.PNMap, element.get('contact-type'))

		if element.tag == "test-model":
			preName 	= 'test '
			
		if element.tag == "ring-vaccination-model":
			preName 	= 'vaccination-'
			tpt= None
		if element.tag == "vaccine-model":
			preName 	= 'vaccine-'
		if element.tag == "zone-model":
			pt0 ,r        	=  self.getZoneAsPT(element)
			if (r==0):                
                		return []
			preName 	= 'zone-'
			
		if element.tag in self.ParsableMainElements:
			for paramElement in element.getchildren():
				paramName 				= self.getActualName(self.PNMap,"%s%s"%(preName,paramElement.tag))
				if paramName is None or paramName=="noparse":
					continue
				
				paramNameAndDecimalLen 	= paramName.split(',')
				paramName 	= "%s %s"%(contactType,paramNameAndDecimalLen[0])
				
				if len(paramNameAndDecimalLen) ==1:
					roundLen = 0
				else:
					roundLen = paramNameAndDecimalLen[1]
                    		
				if preName     == 'vaccination-' and paramName == 'min time between vaccinations':
					pt =fpt = None
                		elif preName     == 'vaccination-' and paramName == 'vaccination radius':
                    			pt =tpt = None  
				
				if paramName.endswith('direct rate'):                    
				    obj         = self.parseContactValue(paramElement, roundLen, paramName, fpt0, fpt, tpt0)     
				    if obj is None:
				        self.parsedParamList.append([[paramName,fpt0,pt0,tpt0, None],1,'range'])                            
				else:
				    obj 		= self.parseParamValue(paramElement, roundLen, paramName, pt,fpt,tpt)
				
				if obj is not None:
				    self.parsedParamList.append([[paramName,fpt0,pt0,tpt0, zone0],obj.nrOfVar,obj.type])
				    elementObjects.append(obj)
					
		return elementObjects

    def    getZoneAsPT(self, paramElement):
        pt0         = paramElement.find('name').text.lower()
        radiusElem  = paramElement.find('radius')
        #unitElem    = radiusElem.find('units').getchildren()[0]
        #r            = "%s %s"%(radiusElem.find('value').text, unitElem.text)
        return pt0,float(radiusElem.find('value').text)
            
    def parseContactValue(self, paramElement, roundLen, paramName, fpt0=None, fpt=None, tpt0=None):
        pID         = self.parser.createParamID(paramName,None,fpt0,None)
        paramRange  = self.getParamRanges(self.parser.createParamID(paramName,None,fpt,None))
        xmlElment   = paramElement.getchildren()[0]
        value       = float(xmlElment.text)
        if self.contactDict.has_key(pID)==True:
            contactObj = self.contactDict.get(pID)
            obj = None
        else:
            contactObj= ContactRateClass.getInstance(pID,paramRange,roundLen)
            self.contactDict[pID]=contactObj
            obj = XMLElment("range",1,xmlElment, contactObj)
            
        contactObj.add(xmlElment, tpt0, value)
        return obj
		
    def parseParamValue(self, paramElement, roundLen, paramName, pt=None, fpt=None,tpt=None):
		pID               = self.parser.createParamID(paramName,pt,fpt,tpt)
		elemChildren      = paramElement.getchildren()
		if len(elemChildren) == 0:
			return self.processRangeElement(pID,paramElement, roundLen)
			
		paramValue = elemChildren[0]
		
		if paramValue.tag == "probability-density-function":
			return self.parseNewStyleDistribution(pID,paramValue)
		elif paramValue.tag == "relational-function":
			return self.parseNewStyleRelFunction(pID, paramElement, paramValue)
		elif paramValue.tag == "value":         
			return self.processRangeElement(pID,paramValue, roundLen)
			
		return None
 		
    def parseNewStyleDistribution(self,pID, element):			
		distElement = element.getchildren()[0]
		if self.isReplacableDistribution(distElement.tag):
			paramID = pdfParser.Parser.getParamID(pID)
			distObj = self.getInstance(paramID, distElement)	
			if distObj is None:
				return None	
			obj = XMLElment("dist",3,element, distObj)
			#self.parsedParamList.append([pID,3,'dist'])
			return obj
		return None

    def parseNewStyleRelFunction(self,pID, parent, chartElement):	
		paramID 	= pdfParser.Parser.getParamID(pID)
		chartObj 	= self.getInstance(paramID, chartElement)			
		obj 		= XMLElment("chart",4,parent, chartObj)
		#self.parsedParamList.append([pID,4,'chart'])
		return obj

    def processRangeElement(self,pID, replacedElement,roundLen=6):		
		paramRange  	= self.getParamRanges(pID)
		value 	= [float(replacedElement.text)]
		rangeObj= RangeClass.getInstance(value,paramRange,roundLen)
		return XMLElment( "range",1,replacedElement, rangeObj)
	
######################################################################################################## 
class RangeClass(object):
    def __init__(self,value,roundLen=6):
		self.value 			= value
		self.roundLen 		= int(roundLen)
		self.valueRange		= [-1,-1]				
		self.valueRangeLen	= 0
    @staticmethod		
    def getInstance(param,ranges,roundLen=6):	# param:<value>,  ranges:[min,max]
		rangeObj      = RangeClass(param[0],roundLen)
		if rangeObj.applyBoundingBox(ranges, PDF.defaultBoundingBox):
			rangeObj.mapBoundingBoxToHR(ranges)
		return 	rangeObj

    def applyBoundingBox(self,ranges,boundingBox ):
		length				= ranges[1] - ranges[0]
		if length ==0:
			self.valueRange[0] = self.value
			return False
		self.valueRange[0] 	= self.value - length * boundingBox
		self.valueRange[1] 	= self.value + length * boundingBox	
		return True
			
    def mapBoundingBoxToHR(self,ranges):
		if (self.valueRange[0]<ranges[0]):
			self.valueRange[0] = ranges[0]
		if (self.valueRange[1]>ranges[1]):
			self.valueRange[1] = ranges[1]		
		self.valueRangeLen = self.valueRange[1] - self.valueRange[0]			

    def mapLHSToBoundingBox(self,lhsValue):
		return (self.valueRange[0] + self.valueRangeLen * lhsValue)
			
    def updateRangeValue(self,parser,xmlELement,lhsValue):
		parser.replaceRangeOldValue(xmlELement,round(self.mapLHSToBoundingBox(lhsValue),self.roundLen))
		
########################################################################################################
class ContactRateClass(RangeClass):
    def __init__(self, fpt, roundLen=6):
		super(ContactRateClass,self).__init__(-1,roundLen)
		self.productionType = fpt
		self.hRange			= []
		self.tptList		= []				
		self.ValueList		= []
		self.xmlElmList		= []
						
    @staticmethod		
    def getInstance(fpt,ranges,roundLen=6):	# param:<value>,  ranges:[min,max]
		crObj = ContactRateClass(fpt,roundLen)
		crObj.hRange = ranges
		return crObj
						
    def add(self,xmlElement, tpt, value):
		self.tptList.append(tpt)
		self.ValueList.append(value)
		self.xmlElmList.append(xmlElement)			
	
    def updateRangeValueEvenProportion(self,parser,xmlELement,lhsValue):
		n = len (self.ValueList)
		for i in range(len(self.ValueList)):
			p 		= 1.0/n 
			pLHS 	= p * lhsValue
			parser.replaceRangeOldValue(self.xmlElmList[i],round(pLHS,self.roundLen))
	
    def updateRangeValue(self,parser,xmlELement, lhsValue):
		self.value 	= float(sum(self.ValueList))
		if self.value 	== 0:
			self.updateRangeValueEvenProportion(parser,xmlELement, lhsValue)
			return
		if self.applyBoundingBox(self.hRange, PDF.defaultBoundingBox):
			self.mapBoundingBoxToHR(self.hRange)
		scaledLHS 	= self.mapLHSToBoundingBox(lhsValue)
		for i in range(len(self.ValueList)):
			p 		= self.ValueList[i]/self.value 
			pLHS 	= p * scaledLHS
			parser.replaceRangeOldValue(self.xmlElmList[i],round(pLHS,self.roundLen))
