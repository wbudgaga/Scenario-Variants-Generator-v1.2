import numpy as np
import math
from scipy import optimize 
from scipy import stats 
from scipy import misc 
import matplotlib.pyplot as plt
import sys
from math import exp
			
class PDF:	
    defaultCI			= 0.99
    defaultNrPoints		= 500
    defaultBoundingBox	= 0.2	
    maxLen				= 3
	
    def __init__(self,name, type='continuous',distParam=[]): # type:discrete or continuous
		self.name			= name		
		self.type			= type	
		self.distParam		= distParam
		plt.ion()
		self.theta			= [0,0,0,0,0]		#[min,max,mean,var,skewness]
		self.boxBound		= PDF.defaultBoundingBox
		self.meanRange		= [0,0]
		self.varianceRange	= [0,0]
		self.skewnessRange	= [0,0]	
		self.meanBox		= [0,0]
		self.varianceBox	= [0,0]
		self.skewnessBox	= [0,0]	
		#self.allowedDiff	= 0.0001
		
    def setParam(self, idx, value):
		self.distParam[idx]=value
		
    def __str__(self,paraNames=None):
		s = "\n\nDistribution <<<%s (%s)>>>" % (self.name, self.type)
		s = "%s\nTheta:\n(min:%f, max:%f, mean:%f, var:%f, skewness:%f)" \
			%(s,self.theta[0],self.theta[1],self.theta[2],self.theta[3],self.theta[4])				
		if paraNames is not None:
			p ="\n\nDistribution Parameters:\n"
			for para, value in zip(paraNames,self.distParam):
				p="%s %-10s= %f \n"%(p,para, value) 
			s =	"%s%s"% (s,p)
		return s
		
	
    @staticmethod
    def adjustRangesToLocalBounds(boundMin, boundMax, hMin, hMax, msg):
		"""shrink long historical bounds by relying on the distributions bounds."""
		if boundMin < hMin or boundMin > hMax or boundMax< hMin or boundMax > hMax:
			print "ERROR: The distribution bounds(%s,%s) are out of the historical ranges(%s,%s)"%(boundMin, boundMax, hMin, hMax)
			print msg
			#sys.exit(0)
		len20 = (hMax - hMin) * 0.20 
		min1 =  boundMin - len20
		max1 =  boundMax + len20
		if hMin < min1:
			hMin=min1
		if hMax>max1:
			hMax=max1
		return hMin, hMax
	
    def adjustHboundsToLocalBounds(self, idx, v1, v2):
		if abs(self.theta[idx]-v1)>abs(self.theta[idx]-v2):		
			dec_digits =  len(str(v2-int(v2))[2:])
		else:
			dec_digits =  len(str(v1-int(v1))[2:])
		if self.theta[idx]<0:
			dec_digits = dec_digits - 1
		v = round(self.theta[idx],dec_digits)
		if v < v1 or v > v2:
			print "ERROR: Value of theta[%s]=%s is out of historical range(%s,%s)"%(idx,self.theta[idx], v1,v2)
			print self.__str__()
			#sys.exit(0)
		if self.theta[idx] ==0:
		    m2= 1
		    if idx==3:
		        m1= 0
		    else:
		        m1= -1
		else:
		    m = abs(PDF.maxLen * self.theta[idx])
		    m1= self.theta[idx] - m
		    m2= self.theta[idx] + m

		if v1 < m1:
			v1=m1
		if v2>m2:
			v2=m2
		return v1, v2
		
		
    def setHRanges(self,mean1,mean2,var1,var2,skewness1,skewness2):
		mean1, mean2 			= self.adjustHboundsToLocalBounds(2,mean1, mean2)
		var1, var2 				= self.adjustHboundsToLocalBounds(3,var1, var2)
		skewness1, skewness2 	= self.adjustHboundsToLocalBounds(4,skewness1, skewness2)
		self.meanRange[0]		= mean1
		self.meanRange[1]		= mean2
		self.varianceRange[0]	= var1
		self.varianceRange[1]	= var2
		self.skewnessRange[0]	= skewness1
		self.skewnessRange[1]	= skewness2
		self.applyBoxBound()

    def getTheta(self):	
		return self.theta

    def getThetaVariant(self,lhsMean,lhsVar,lhsSkewness):	
		mean 	= self.meanBox[0] 	+ (self.meanBox[1]	- self.meanBox[0])	* lhsMean
		var 	= self.varianceBox[0] 	+ (self.varianceBox[1] 	- self.varianceBox[0]) 	* lhsVar		
		skewness= self.skewnessBox[0] 	+ (self.skewnessBox[1] 	- self.skewnessBox[0]) 	* lhsSkewness		
		return [self.theta[0],self.theta[1],mean,var,skewness]
		
    def applyBoxBound(self):		
		temp		 	 	= (self.meanRange[1] - self.meanRange[0]) * self.boxBound
		self.meanBox[0]  	= self.theta[2] - temp
		self.meanBox[1]  	= self.theta[2] + temp	
		temp 	 			= (self.varianceRange[1] - self.varianceRange[0]) * self.boxBound
		self.varianceBox[0]	= self.theta[3] - temp
		self.varianceBox[1]	= self.theta[3] + temp		
		temp 	 			= (self.skewnessRange[1] - self.skewnessRange[0]) * self.boxBound
		self.skewnessBox[0]	= self.theta[4] - temp
		self.skewnessBox[1]	= self.theta[4] + temp	
		self.adjustBoundingBox()
		
    def adjustBoundingBox(self):	   
		if (self.meanBox[0] < self.meanRange[0]):
			self.meanBox[0]  = self.meanRange[0]			
		if (self.meanBox[1] > self.meanRange[1]):
			self.meanBox[1]  = self.meanRange[1]
		if (self.varianceBox[0] < self.varianceRange[0]):
			self.varianceBox[0]  = self.varianceRange[0]			
		if (self.varianceBox[1] > self.varianceRange[1]):
			self.varianceBox[1]  = self.varianceRange[1]
		if (self.skewnessBox[0] < self.skewnessRange[0]):
			self.skewnessBox[0]  = self.skewnessRange[0]			
		if (self.skewnessBox[1] > self.skewnessRange[1]):
			self.skewnessBox[1]  = self.skewnessRange[1]
			
    def setHRangesAsList(self,rangesList):
		self.setHRanges(rangesList[0],rangesList[1],rangesList[2],rangesList[3],rangesList[4],rangesList[5])
		
    def plot(self,x,y,c):
		plt.plot(x,y,'-',color=c,linewidth=1)
		plt.show()
    def legend(self,legend):
		plt.legend(legend, 'best')
    def saveFig(self,fName):
		plt.savefig(fName)
		plt.close()

###############################################################################################	
class Beta(PDF):
    paramList = ['alpha','beta','location','scale'] 
    def __init__(self,param=[0,0,0,1],name='beta',type='continuous'):
		PDF.__init__(self,name,type,param)	

    @staticmethod
    def getParam(parser, element):		
		paraList = parser.parseParameters(element,Beta.paramList)
		return [float(i) for i in paraList]
		
    @staticmethod		
    def getInstance(distParam,ranges, nrOfPoints):
		distParam[3]= distParam[3]-distParam[2]	# scale = max -min
		distObj = Beta(distParam)
		distObj.computeTheta()
		distObj.setHRangesAsList(ranges[2:])
		return 	distObj
		
    def __str__(self):
		return PDF.__str__(self,Beta.paramList)
		
    def setAlphaBeta(self,alpha,beta): 		
		self.distParam[0]= alpha
		self.distParam[1]= beta		

    def getAsXMLElement(self,parser):
		return parser.getBetaElement(self.distParam[0], self.distParam[1], self.distParam[2],self.distParam[3])
		
    def computeTheta(self):	
		self.theta[0]	= self.distParam[2] #loc
		self.theta[1]	= self.distParam[2] + self.distParam[3]	#max = loc + scale
		self.theta[2], self.theta[3], self.theta[4] = stats.beta.stats(self.distParam[0], self.distParam[1],scale= self.distParam[3],loc= self.distParam[2],moments="mvs")
		
    def getBetaVariant(self,lhsMean,lhsVar,lhsSkewness):
		thisBeta 	= Beta([self.distParam[0], self.distParam[1], self.distParam[2],self.distParam[3]])
		thetaVariant= self.getThetaVariant(lhsMean,lhsVar,lhsSkewness)
		thisBeta.fit(thetaVariant)
		return thisBeta

    def getBeta(self):
		return  Beta([self.distParam[0], self.distParam[1], self.distParam[2],self.distParam[3]])
		
    def __residual(self,param, desiredTheta=[]):
        	newMin = param[2]
        	newMax = param[2]+param[3]
        	diffMin = 0
        	diffMax = 0
        	th =[param[2], newMax, 0.0,0.0,0.0]
        	th[2], th[3], th[4] = stats.beta.stats(param[0], param[1],loc= param[2], scale= param[3], moments='mvs') #, loc=self.distParam[2], scale=self.distParam[3]
        	diff = [x - y for x, y in zip(desiredTheta[2:],th[2:])]
        	if newMin < desiredTheta[0]:
            		diffMin = abs(desiredTheta[0] - newMin)*1000
        	if newMax > desiredTheta[1]:
            		diffMax = abs(desiredTheta[1] - newMax)*1000
           
        	return np.array([diffMin,diffMax,diff[0], diff[1],diff[2]])     

    def fittingStatus(self):
	return math.isnan(self.distParam[0])==False and math.isnan(self.distParam[1])==False and self.distParam[0]>0 and self.distParam[1]>0  
		
    def fit(self, desiredTheta=[]):
		guess = [1.0,2.0, desiredTheta[0], desiredTheta[1]-desiredTheta[0]]#[alpha, beta, loc=min, scale=max-min
		p2, C, info, msg, success = optimize.leastsq( self.__residual, guess , args =(desiredTheta),full_output=True, maxfev=6000)
		p2[2]=round(p2[2],4)
		self.distParam = p2
	

    def plot(self,c):
		x = np.linspace(self.distParam[2],self.distParam[2] +self.distParam[3],100)
		y = stats.beta.pdf(x,self.distParam[0],self.distParam[1],self.distParam[2],self.distParam[3])
		PDF.plot(self,x,y,c)
###############################################################################################
class Chart(PDF):
    paramList = ['x','y']
    def __init__(self,x,y,distParam=[], name='chart', type='discrete'):
		self.x			= x	
		self.y			= y		
		self.minxRange	= [-1,-1]
		self.maxxRange	= [-1,-1]
		self.minyRange	= [-1,-1]
		self.maxyRange	= [-1,-1]
		self.minX		= min(self.x)
		self.minY		= min(self.y)
		self.maxX		= max(self.x)
		self.maxY		= max(self.y)
		self.xWidth		= self.maxX- self.minX
		self.yWidth		= self.maxY- self.minY
		PDF.__init__(self,name,type,distParam)		
		
    @staticmethod
    def getParam(parser, element):	
		return parser.parsePiecewiseParameters(element,Chart.paramList)
			
    def updateChartValues(self,parser,xmlELement,lhsMinx,lhsMaxx,lhsMiny,lhsMaxy):
		minx 	= self.minxRange[0]	+ (self.minxRange[1] - self.minxRange[0]) * lhsMinx
		maxx 	= self.maxxRange[0]	+ (self.maxxRange[1] - self.maxxRange[0]) * lhsMaxx
		miny 	= self.minyRange[0]	+ (self.minyRange[1] - self.minyRange[0]) * lhsMiny
		maxy 	= self.maxyRange[0]	+ (self.maxyRange[1] - self.maxyRange[0]) * lhsMaxy
		[x,y] = self.scaleXYChart(minx,maxx,miny,maxy)	
		parser.replaceChartOldValues(xmlELement,x,y)
							
    @staticmethod		
    def getInstance(distParam,ranges, nrOfPoints):	# distParam:[x,y],  ranges:[minx,maxx,miny,maxy]
		chartObj = Chart(distParam[0],distParam[1])
		chartObj.applyBoxBound(ranges)
		chartObj.adjustBoundingBox(ranges)
		return 	chartObj

    def scaleXYChart(self,minXRange,maxXRange,minYRange,maxYRange):
		if (self.xWidth==0):
			scaleRateToBoxWidth = 1
		else:
			boxWidth			= maxXRange - minXRange
			scaleRateToBoxWidth	= boxWidth/self.xWidth

		if (self.yWidth==0):
			scaleRateToBoxHeight = 1
		else:
			boxHeight			= maxYRange - minYRange
			scaleRateToBoxHeight= boxHeight/self.yWidth
		#Computing the shifting values of chart's lower-left corner to origin(0,0) 
		minXRangeTranslateValueTo0		= 0 - self.minX
		minYRangeTranslateValueTo0		= 0 - self.minY
		#Computing the shifting values of chart's lower-left corner to box's left lower-bound corner 
		zeroTranslateValueToBoxX	= minXRange
		zeroTranslateValueToBoxY 	= minYRange
		x =[]
		y =[]
		for i in range(len(self.x)):
			x.append((self.x[i] + minXRangeTranslateValueTo0) * scaleRateToBoxWidth + zeroTranslateValueToBoxX)
			y.append((self.y[i] + minYRangeTranslateValueTo0) * scaleRateToBoxHeight + zeroTranslateValueToBoxY)	
		return [x,y]

    def applyBoxBound(self,ranges):	
		xWidthScaledValue = (ranges[1]- ranges[0]) * self.boxBound
		if xWidthScaledValue > self.xWidth/2.0:
			xWidthScaledValue = self.xWidth/2.0
		
		yWidthScaledValue = (ranges[3]- ranges[2]) * self.boxBound
		if yWidthScaledValue > self.yWidth/2.0:
			yWidthScaledValue = self.yWidth/2.0

		self.minxRange[0] = self.minX - xWidthScaledValue
		self.minxRange[1] = self.minX + xWidthScaledValue		
		self.maxxRange[0] = self.maxX - xWidthScaledValue
		self.maxxRange[1] = self.maxX + xWidthScaledValue				
		
		self.minyRange[0] = self.minY - yWidthScaledValue
		self.minyRange[1] = self.minY + yWidthScaledValue		
		self.maxyRange[0] = self.maxY - yWidthScaledValue
		self.maxyRange[1] = self.maxY + yWidthScaledValue
		
    def adjustBoundingBox(self,ranges):	   
		if (self.minxRange[0] < ranges[0]):
			self.minxRange[0] = ranges[0]
		if (self.maxxRange[1] > ranges[1]):
			self.maxxRange[1] = ranges[1]

		if (self.minyRange[0] < ranges[2]):
			self.minyRange[0] = ranges[2]
		if (self.maxyRange[1] > ranges[3]):
			self.maxyRange[1] = ranges[3]			
###############################################################################################		
class Piecewise(PDF):
    paramList = ['x','y']	
    def __init__(self,x,y,distParam=[], name='piecewise', type='discrete'):
		self.x			= x	
		self.y			= y		
		self.n			= len(self.x)	
		self.min		= min(self.x)	
		self.max		= max(self.x)	
		PDF.__init__(self,name,type,distParam)		
		self.theta[0]	= self.min
		self.theta[1]	= self.max
		self.computeTheta()

    @staticmethod
    def getParam(parser, element):		
		return parser.parsePiecewiseParameters(element,Piecewise.paramList)
		
    @staticmethod		
    def getInstance(distParam,ranges, nrOfPoints):	
		distObj = Piecewise(distParam[0],distParam[1])
		distObj.setHRangesAsList(ranges[2:])
		return 	distObj

    def __g(self,k,a,b,fa,fb):
		slope=(fb-fa)/(b-a)
		out=slope*(b**(k+2.0)-a**(k+2.0))/(k+2.0)+(fa-slope*a)*(b**(k+1.0)-a**(k+1.0))/(k+1.0)
		return (out)
		
    def computeTheta(self):	
		m=np.zeros(4) # m[0] not uses. needed?
		for i in range(1,self.n):
			if self.x[i] > self.x[i-1]:
				for j in range(4):
					m[j]+=self.__g(j,self.x[i-1],self.x[i],self.y[i-1],self.y[i])
		self.theta = [self.min,self.max,m[1],m[2]-m[1]**2,(m[3]-3*m[1]*m[2]+2*m[1]**3)/(m[2]-m[1]**2)**1.5]
			
    def getBeta(self):
		betaObj = Beta([0,0,self.min,self.max - self.min])
		xyTheta = self.getTheta()
		betaObj.fit(xyTheta)
		return betaObj
		
    def getBetaVariant(self,lhsMean,lhsVar,lhsSkewness):
		betaObj = Beta([0,0,self.min,self.max - self.min])
		thetaVariant = self.getThetaVariant(lhsMean,lhsVar,lhsSkewness)
		betaObj.fit(thetaVariant)
		return betaObj
		
    def plot(self,c):
		PDF.plot(self,self.x,self.y,c)

##################################################################################
class BetaPert(Beta):
    paramList = ['min','mode','max']
    def __init__(self,param,name='beta-pert',type='continuous'):
		mu = (param[0] + 4.0 * param[1] + param[2])/6.0
		alpha = 6.0 * ((mu-param[0])/(param[2]-param[0]))
		beta  = 6.0 * ((param[2] - mu)/(param[2]-param[0]))		
		Beta.__init__(self,[alpha, beta, param[0], param[2] - param[0]],name)
		
    @staticmethod
    def getParam(parser, element):		
		paraList = parser.parseParameters(element,BetaPert.paramList)
		return [float(i) for i in paraList]
		
    @staticmethod		
    def getInstance(distParam,ranges, nrOfPoints):	
		distObj = BetaPert(distParam)
		distObj.computeTheta()
		distObj.setHRangesAsList(ranges[2:])
		return 	distObj
		
    def __str__(self):
		return PDF.__str__(self,BetaPert.paramList)
						
###############################################################################		
class Weibull(Piecewise):
    paramList = ['alpha','beta']
    def __init__(self,x,param,name='weibull', type='continuous'):
		y = stats.weibull_min.pdf(x,param[0],scale=param[1])
		Piecewise.__init__(self,x,y,param,name,type)
		
    def computeTheta(self):			 
		self.theta[2], self.theta[3], self.theta[4] = stats.weibull_min.stats(self.distParam[0], scale= self.distParam[1],moments="mvs")

    @staticmethod
    def getParam(parser, element):		
		paraList= parser.parseParameters(element,Weibull.paramList)
		return [float(i) for i in paraList]

    @staticmethod
    def getInstance(distParam,ranges, nrOfPoints):	
		bounds=Weibull.getBounds(distParam)
		ranges[0] , ranges[1] = PDF.adjustRangesToLocalBounds(bounds[0],bounds[1],ranges[0] , ranges[1], "%s"%ranges)
		distObj = Weibull(np.linspace(ranges[0] , ranges[1],nrOfPoints), distParam)
		distObj.setHRangesAsList(ranges[2:])
		return 	distObj
		
    @staticmethod
    def getBounds(param,ci=PDF.defaultCI):		
		boundMin 		= stats.weibull_min.ppf(1- ci,param[0], scale=param[1])
		boundMax 		= stats.weibull_min.ppf(ci,   param[0], scale=param[1])
		return [boundMin,boundMax]
		
    def __str__(self):
		return PDF.__str__(self,Weibull.paramList)
		
    def plot(self,c):
		PDF.plot(self,self.x,self.y,c)
###############################################################################		
class Gaussian(Piecewise):
    paramList = ['mean','stddev']
    def __init__(self,x,param,name='gaussian', type='continuous'):
		y = stats.norm.pdf(x, loc=param[0], scale=param[1])
		Piecewise.__init__(self,x,y,param,name, type)

    def computeTheta(self):			 
		self.theta[2], self.theta[3], self.theta[4] = stats.norm.stats(loc=self.distParam[0], scale= self.distParam[1],moments="mvs")
		
    @staticmethod
    def getParam(parser, element):		
		paraList= parser.parseParameters(element,Gaussian.paramList)
		return [float(i) for i in paraList]
		
    @staticmethod
    def getInstance(distParam,ranges, nrOfPoints):	
		bounds=Gaussian.getBounds(distParam)
		ranges[0] , ranges[1] = PDF.adjustRangesToLocalBounds(bounds[0],bounds[1],ranges[0] , ranges[1], "%s"%ranges)
		distObj = Gaussian(np.linspace(ranges[0] , ranges[1],nrOfPoints), distParam)
		distObj.setHRangesAsList(ranges[2:])
		return 	distObj
		
    @staticmethod
    def getBounds(param,ci=PDF.defaultCI):		
		min 		= stats.norm.ppf(1- ci,loc=param[0], scale=param[1])
		max 		= stats.norm.ppf(ci,   loc=param[0], scale=param[1])
		return [min,max]

    def __str__(self):
		return PDF.__str__(self,Gaussian.paramList)
				
    def plot(self,c):
		PDF.plot(self,self.x,self.y,c)

###############################################################################		
class InvGaussian(Piecewise):
    paramList = ['mu','lambda']
    def __init__(self,x,param,name='gaussian', type='continuous'):
		y = stats.norm.pdf(x, loc=param[0], scale=param[1])
		Piecewise.__init__(self,x,y,param,name, type)

    def computeTheta(self):			 
		self.theta[2], self.theta[3], self.theta[4] = stats.norm.stats(self.distParam[0], scale= self.distParam[1],moments="mvs")
		
    @staticmethod
    def getParam(parser, element):		
		paraList= parser.parseParameters(element,InvGaussian.paramList)
		return [float(i) for i in paraList]
		
    @staticmethod
    def getInstance(distParam,ranges, nrOfPoints):	
		bounds=Gaussian.getBounds(distParam)
		ranges[0] , ranges[1] = PDF.adjustRangesToLocalBounds(bounds[0],bounds[1],ranges[0] , ranges[1], "%s"%ranges)
		distObj = InvGaussian(np.linspace(ranges[0] , ranges[1],nrOfPoints), distParam)
		distObj.setHRangesAsList(ranges[2:])
		return 	distObj
		
    @staticmethod
    def getBounds(param,ci=PDF.defaultCI):		
		min 		= stats.invgauss.ppf(1- ci,param[0], scale=param[1])
		max 		= stats.invgauss.ppf(ci,   param[0], scale=param[1])
		return [min,max]

    def __str__(self):
		return PDF.__str__(self,InvGaussian.paramList)
				
    def plot(self,c):
		PDF.plot(self,self.x,self.y,c)
		
###############################################################################		
class Lognormal(Piecewise):
    paramList = ['zeta','sigma']
    def __init__(self,x,param,name='lognormal', type='continuous'):
		y = stats.lognorm.pdf(x, param[1], scale=exp(param[0])) #need checking, Now shape=sigma, loc=zeta
		Piecewise.__init__(self,x,y,param,name, type)

    def computeTheta(self):			 
		self.theta[2], self.theta[3], self.theta[4] = stats.lognorm.stats(self.distParam[1], scale=exp(self.distParam[0]),moments="mvs")
				
    @staticmethod
    def getParam(parser, element):		
		paraList= parser.parseParameters(element,Lognormal.paramList)
		return [float(i) for i in paraList]
		
    @staticmethod
    def getInstance(distParam,ranges, nrOfPoints):	
		bounds=Lognormal.getBounds(distParam)
		ranges[0] , ranges[1] = PDF.adjustRangesToLocalBounds(bounds[0],bounds[1],ranges[0] , ranges[1], "%s"%ranges)
		distObj = Lognormal(np.linspace(ranges[0] , ranges[1],nrOfPoints), distParam)
		distObj.setHRangesAsList(ranges[2:])
		return 	distObj
		
    @staticmethod
    def getBounds(param,ci=PDF.defaultCI):		
		min 		= stats.lognorm.ppf(1- ci,param[1], scale=exp(param[0]))
		max 		= stats.lognorm.ppf(ci,   param[1], scale=exp(param[0]))
		return [min,max]
		
    def __str__(self):
		return PDF.__str__(self,Lognormal.paramList)
				
    def plot(self,c):
		PDF.plot(self,self.x,self.y,c)	
###############################################################################		
class Logistic(Piecewise):
    paramList = ['location','scale']
    def __init__(self,x,param,name='logistic', type='continuous'):
		y = stats.logistic.pdf(x, loc=param[0], scale=param[1])
		Piecewise.__init__(self,x,y,param,name, type)
		
    def computeTheta(self):			 
		self.theta[2], self.theta[3], self.theta[4] = stats.logistic.stats(loc=self.distParam[0], scale= self.distParam[1],moments="mvs")
		
    @staticmethod
    def getParam(parser, element):		
		paraList = parser.parseParameters(element,Logistic.paramList)
		return  [float(i) for i in paraList]
		
    @staticmethod
    def getInstance(distParam,ranges, nrOfPoints):	
		bounds=Logistic.getBounds(distParam)
		ranges[0] , ranges[1] = PDF.adjustRangesToLocalBounds(bounds[0],bounds[1],ranges[0] , ranges[1], "%s"%ranges)
		distObj = Logistic(np.linspace(ranges[0] , ranges[1],nrOfPoints), distParam)
		distObj.setHRangesAsList(ranges[2:])
		return 	distObj
		
    @staticmethod
    def getBounds(param,ci=PDF.defaultCI):		
		min 	= stats.logistic.ppf(1- ci, loc=param[0], scale=param[1])
		max 	= stats.logistic.ppf(ci,    loc=param[0], scale=param[1])
		return [min,max]
		
    def __str__(self):
		return PDF.__str__(self,Logistic.paramList)
				
    def plot(self,c):
		PDF.plot(self,self.x,self.y,c)
	
###############################################################################		
class Loglogistic(Piecewise):
    paramList = ['shape','location','scale']
    def __init__(self,x,param,name='loglogistic', type='continuous'):
		y = stats.fisk.pdf(x,  param[0], loc=param[1], scale=param[2])
		Piecewise.__init__(self,x,y,param,name, type)

    def computeTheta(self):			 
		self.theta[2], self.theta[3], self.theta[4] = stats.fisk.stats(self.distParam[0], loc=self.distParam[1], scale= self.distParam[2],moments="mvs")
		
    @staticmethod
    def getParam(parser, element):		
		paraList= parser.parseParameters(element,Loglogistic.paramList)
		return [float(i) for i in paraList]

    @staticmethod
    def getInstance(distParam,ranges, nrOfPoints):	
		if distParam[0] <=3: #the skewness is undefined if the shape parameter is <= 3.
			return None
		bounds=Loglogistic.getBounds(distParam)
		ranges[0] , ranges[1] = PDF.adjustRangesToLocalBounds(bounds[0],bounds[1],ranges[0] , ranges[1], "%s"%ranges)
		distObj = Loglogistic(np.linspace(ranges[0] , ranges[1],nrOfPoints), distParam)
		distObj.setHRangesAsList(ranges[2:])
		return 	distObj
		
    @staticmethod
    def getBounds(param,ci=PDF.defaultCI):	
		min 		= stats.fisk.ppf(1- ci,param[0], loc=param[1], scale=param[2])
		max 		= stats.fisk.ppf(ci,   param[0], loc=param[1], scale=param[2])
		return [min,max]

    def __str__(self):
		return PDF.__str__(self,Loglogistic.paramList)
				
    def plot(self,c):
		PDF.plot(self,self.x,self.y,c)
		
###############################################################################	
class Gamma(Piecewise):
    paramList = ['alpha','beta']
    def __init__(self,x,param,name='gamma', type='continuous'):
		y = stats.gamma.pdf(x, param[0],scale= param[1])
		Piecewise.__init__(self,x,y,param,name,type)
		
    def computeTheta(self):			 
		self.theta[2], self.theta[3], self.theta[4] = stats.gamma.stats(self.distParam[0], scale= self.distParam[1],moments="mvs")

    @staticmethod
    def getParam(parser, element):		
		paraList= parser.parseParameters(element,Gamma.paramList)
		return [float(i) for i in paraList]
		
    @staticmethod
    def getInstance(distParam,ranges, nrOfPoints):	
		bounds=Gamma.getBounds(distParam)
		ranges[0] , ranges[1] = PDF.adjustRangesToLocalBounds(bounds[0],bounds[1],ranges[0] , ranges[1], "%s"%ranges)
		distObj = Gamma(np.linspace(ranges[0] , ranges[1],nrOfPoints), distParam)
		distObj.setHRangesAsList(ranges[2:])
		return 	distObj
		
    @staticmethod
    def getBounds(param, ci=PDF.defaultCI):		
		min 	= stats.gamma.ppf(1-ci,param[0],scale= param[1])
		max 	= stats.gamma.ppf(ci,param[0],scale= param[1])
		return [min,max]

    def __str__(self):
		return PDF.__str__(self,Gamma.paramList)
				
    def plot(self,c):
		PDF.plot(self,self.x,self.y,c)
				
###############################################################################	<pearson5> <<<<<<
class Pearson5(Piecewise):  
    paramList = ['alpha','beta']
    def __init__(self,x,param,name='pearson5', type='continuous'):
		y = stats.invgamma.pdf(x, param[0],scale= param[1])
		Piecewise.__init__(self,x,y,param,name,type)

    def computeTheta(self):			 
		self.theta[2], self.theta[3], self.theta[4] = stats.invgamma.stats(self.distParam[0], scale= self.distParam[1],moments="mvs")
		
    @staticmethod
    def getParam(parser, element):		
		paraList= parser.parseParameters(element,Pearson5.paramList)
		return [float(i) for i in paraList]
		
    @staticmethod
    def getInstance(distParam,ranges, nrOfPoints):	
		bounds=Pearson5.getBounds(distParam)
		ranges[0] , ranges[1] = PDF.adjustRangesToLocalBounds(bounds[0],bounds[1],ranges[0] , ranges[1], "%s"%ranges)
		distObj = Pearson5(np.linspace(ranges[0], ranges[1],nrOfPoints), distParam)
		distObj.setHRangesAsList(ranges[2:])
		return 	distObj
		
    @staticmethod
    def getBounds(param, ci=PDF.defaultCI):		
		min 	= stats.invgamma.ppf(1-ci,param[0],scale= param[1])
		max 	= stats.invgamma.ppf(ci,param[0],scale= param[1])
		return [min,max]
		
    def __str__(self):
		return PDF.__str__(self,Pearson3.paramList)
				
    def plot(self,c):
		PDF.plot(self,self.x,self.y,c)		



class Pearson3(Piecewise):  
    paramList = ['theta','alpha']
    def __init__(self,x,param,name='pearson3', type='continuous'):
		y = stats.pearson3.pdf(x, param[0],scale= param[1])
		Piecewise.__init__(self,x,y,param,name,type)

    def computeTheta(self):			 
		self.theta[2], self.theta[3], self.theta[4] = stats.pearson3.stats(self.distParam[0], scale= self.distParam[1],moments="mvs")
		
    @staticmethod
    def getParam(parser, element):		
		paraList= parser.parseParameters(element,Pearson3.paramList)
		return [float(i) for i in paraList]
		
    @staticmethod
    def getInstance(distParam,ranges, nrOfPoints):	
		bounds=Pearson3.getBounds(distParam)
		ranges[0] , ranges[1] = PDF.adjustRangesToLocalBounds(bounds[0],bounds[1],ranges[0] , ranges[1], "%s"%ranges)
		distObj = Pearson3(np.linspace(ranges[0], ranges[1],nrOfPoints), distParam)
		distObj.setHRangesAsList(ranges[2:])
		return 	distObj
		
    @staticmethod
    def getBounds(param, ci=PDF.defaultCI):		
		min 	= stats.pearson3.ppf(1-ci,param[0],scale= param[1])
		max 	= stats.pearson3.ppf(ci,param[0],scale= param[1])
		return [min,max]
		
    def __str__(self):
		return PDF.__str__(self,Pearson3.paramList)
				
    def plot(self,c):
		PDF.plot(self,self.x,self.y,c)		
###############################################################################	
class Exponential(Piecewise):
    paramList = ['mean']
    def __init__(self,x,param,name='exponential', type='continuous'):
		y = stats.expon.pdf(x, scale= param[0])
		Piecewise.__init__(self,x,y,param,name,type)
		
    def computeTheta(self):			 
		self.theta[2], self.theta[3], self.theta[4] = stats.expon.stats(scale= self.distParam[0],moments="mvs")

    @staticmethod
    def getParam(parser, element):		
		paraList= parser.parseParameters(element,Exponential.paramList)
		return [float(i) for i in paraList]
		
    @staticmethod
    def getInstance(distParam,ranges, nrOfPoints):	
		bounds=Exponential.getBounds(distParam)
		ranges[0] , ranges[1] = PDF.adjustRangesToLocalBounds(bounds[0],bounds[1],ranges[0] , ranges[1],"%s"%ranges)
		distObj = Exponential(np.linspace(ranges[0], ranges[1],nrOfPoints), distParam)
		distObj.setHRangesAsList(ranges[2:])
		return 	distObj
		
    @staticmethod
    def getBounds(param, ci=PDF.defaultCI):		
		min 	= stats.expon.ppf(1-ci, scale= param[0])
		max 	= stats.expon.ppf(ci, scale= param[0])
		return [min,max]
		
    def __str__(self):
		return PDF.__str__(self,Exponential.paramList)
				
    def plot(self,c):
		PDF.plot(self,self.x,self.y,c)				
###############################################################################	
class Pareto(Piecewise):
    paramList = ['theta','mode']
    def __init__(self,x,param,name='pareto', type='continuous'):
		y = stats.pareto.pdf(x, param[0],scale= param[1])
		Piecewise.__init__(self,x,y,param,name, type)

    def computeTheta(self):			 
		self.theta[2], self.theta[3], self.theta[4] = stats.pareto.stats(self.distParam[0], scale=self.distParam[1],moments="mvs")
		
    @staticmethod
    def getParam(parser, element):		
		paraList= parser.parseParameters(element,Pareto.paramList)
		return [float(i) for i in paraList]
		
    @staticmethod
    def getInstance(distParam,ranges, nrOfPoints):	
		bounds=Pareto.getBounds(distParam)
		ranges[0] , ranges[1] = PDF.adjustRangesToLocalBounds(bounds[0],bounds[1],ranges[0] , ranges[1], "%s"%ranges)
		distObj = Pareto(np.linspace(ranges[0] , ranges[1],nrOfPoints), distParam)
		distObj.setHRangesAsList(ranges[2:])
		return 	distObj
		
    @staticmethod
    def getBounds(param, ci=PDF.defaultCI):		
		min 	= stats.pareto.ppf(1-ci,param[0],scale= param[1])
		max 	= stats.pareto.ppf(ci,param[0],scale= param[1])
		return [min,max]
		
    def __str__(self):
		return PDF.__str__(self,Pareto.paramList)
				
    def plot(self,c):
		PDF.plot(self,self.x,self.y,c)
		
###############################################################################	
class Chi(Piecewise):
    paramList = ['df','location','scale']
    def __init__(self,x,param,name='chi', type='continuous'):
		y = stats.chi.pdf(x, param[0],loc= param[1],scale= param[2])
		Piecewise.__init__(self,x,y,param,name, type)

    def computeTheta(self):			 
		self.theta[2], self.theta[3], self.theta[4] = stats.chi.stats(self.distParam[0], loc=self.distParam[1], scale=self.distParam[2],moments="mvs")
		
    @staticmethod
    def getParam(parser, element):		
		paraList= parser.parseParameters(element,Chi.paramList)
		return [float(i) for i in paraList]
		
    @staticmethod
    def getInstance(distParam,ranges, nrOfPoints):	
		bounds=Chi.getBounds(distParam)
		ranges[0] , ranges[1] = PDF.adjustRangesToLocalBounds(bounds[0],bounds[1],ranges[0] , ranges[1], "%s"%ranges)
		distObj = Chi(np.linspace(ranges[0] , ranges[1],nrOfPoints), distParam)
		distObj.setHRangesAsList(ranges[2:])
		return 	distObj
		
    @staticmethod
    def getBounds(param, ci=PDF.defaultCI):		
		min 	= stats.chi.ppf(1-ci, param[0],loc= param[1],scale= param[2])
		max 	= stats.chi.ppf(ci, param[0],loc= param[1],scale= param[2])
		return [min,max]
				
    def __str__(self):
		return PDF.__str__(self,Chi.paramList)
				
    def plot(self,c):
		PDF.plot(self,self.x,self.y,c)
				
###############################################################################	
class Poisson(Piecewise):
    paramList = ['mean']
    def __init__(self,x,param,name='poisson', type='discrete'):
		dist = stats.poisson(param[0])	
		y = dist.pmf(x)
		Piecewise.__init__(self,x,y,param,name, type)
		
    def computeTheta(self):			 
		self.theta[2], self.theta[3], self.theta[4] = stats.poisson.stats(self.distParam[0] ,moments="mvs")

    @staticmethod
    def getParam(parser, element):		
		paraList= parser.parseParameters(element,Poisson.paramList)
		return [float(i) for i in paraList]
		
    @staticmethod
    def getInstance(distParam,ranges, nrOfPoints):	
		bounds=Poisson.getBounds(distParam)
		ranges[0] , ranges[1] = PDF.adjustRangesToLocalBounds(bounds[0],bounds[1],ranges[0] , ranges[1], "%s"%ranges)
		distObj = Poisson(range(0, int(ranges[1])),distParam)
		distObj.setHRangesAsList(ranges[2:])
		return 	distObj
		
    @staticmethod
    def getBounds(param, ci=PDF.defaultCI):		
		min 	= stats.poisson.ppf(1-ci,param[0])
		max 	= stats.poisson.ppf(ci,param[0])
		return [min,max]
		
    def __str__(self):
		return PDF.__str__(self,Poisson.paramList)
				
    def plot(self,c):
		plt.vlines(self.x,0,self.y,lw=2,color=c)
		
###############################################################################		
class Bernoulli(Piecewise):
    paramList = ['p']
    def __init__(self,param,name='bernoulli', type='discrete'):
		x = [0,1]
		y = [1-param[0],param[0]]
		Piecewise.__init__(self,x,y,param,name,type)
		
    def computeTheta(self):			 
		self.theta[2], self.theta[3], self.theta[4] = stats.bernoulli.stats(self.distParam[0] ,moments="mvs")

    @staticmethod
    def getParam(parser, element):		
		paraList= parser.parseParameters(element,Bernoulli.paramList)
		return [float(i) for i in paraList]

    @staticmethod
    def getInstance(distParam,ranges, nrOfPoints):	
		distObj = Bernoulli(distParam)
		distObj.setHRangesAsList(ranges[2:])
		return 	distObj
		
    @staticmethod
    def getBounds(param,ci=PDF.defaultCI):		
		min = stats.bernoulli.ppf(1- ci,param[0])
		max = stats.bernoulli.ppf(ci,   param[0])
		return [min,max]
		
    def __str__(self):
		return PDF.__str__(self,Bernoulli.paramList)
				
    def plot(self,c):
		plt.axis([-1,2,0,1])
		plt.vlines(self.x,0,self.y,lw=3,color=c)
		
###############################################################################		
class Binomial(Piecewise):
    paramList = ['n','p']
    def __init__(self,x, param,name='binomial', type='discrete'):
		y= [misc.comb(param[0],i)*(param[1]**i)*((1-param[1])**(param[0]-i)) for i in x]
		Piecewise.__init__(self,x,y,param,name,type)

    @staticmethod
    def getParam(parser, element):		
		paraList= parser.parseParameters(element,Binomial.paramList)
		return [float(i) for i in paraList]

    def computeTheta(self):			 
		self.theta[2], self.theta[3], self.theta[4] = stats.binom.stats(self.distParam[0] , self.distParam[1],moments="mvs")

    @staticmethod
    def getInstance(distParam,ranges, nrOfPoints):	
		bounds=Binomial.getBounds(distParam)
		ranges[0] , ranges[1] = PDF.adjustRangesToLocalBounds(bounds[0],bounds[1],ranges[0] , ranges[1], "%s"%ranges)
		distObj = Binomial(range(int(ranges[0]),int(ranges[1])),distParam)
		distObj.setHRangesAsList(ranges[2:])
		return 	distObj
		
    @staticmethod
    def getBounds(param,ci=PDF.defaultCI):		
		min 		= stats.binom.ppf(1- ci,param[0],param[1])
		max 		= stats.binom.ppf(ci,   param[0],param[1])
		return [min,max]
		
    def __str__(self):
		return PDF.__str__(self,Binomial.paramList)
				
    def plot(self,c):
		plt.vlines(self.x,0,self.y,lw=3,color=c)
###############################################################################		
class NBinomial(Binomial):
    paramList = ['s','p']
    def __init__(self,x, param,name='nbinomial', type='discrete'):
		Binomial.__init__(self,x,param,name,type)

    @staticmethod
    def getInstance(distParam,ranges, nrOfPoints):	
		bounds=NBinomial.getBounds(distParam)
		ranges[0] , ranges[1] = PDF.adjustRangesToLocalBounds(bounds[0],bounds[1],ranges[0] , ranges[1], "%s"%ranges)
		distObj = NBinomial(range(int(ranges[0]),int(ranges[1])),distParam)
		distObj.setHRangesAsList(ranges[2:])
		return 	distObj
    @staticmethod
    def getBounds(param,ci=PDF.defaultCI):		
		min 		= stats.nbinom.ppf(1- ci,param[0],param[1])
		max 		= stats.nbinom.ppf(ci,   param[0],param[1])
		return [min,max]
    @staticmethod
    def getParam(parser, element):		
		paraList= parser.parseParameters(element,NBinomial.paramList)
		return [float(i) for i in paraList]
		
##################################################################################from scipy.stats import nbinom
class Triangular(Piecewise):
    #paramList = ['min','mode','max']
    paramList = ['a','c','b']	
    def __init__(self,x,param,name='triangular', type='continuous'):
		m1 	= (param[1]-param[0])*(param[2]-param[0])
		m2 	= (param[2]-param[1])*(param[2]-param[0])
		y 	=  np.zeros(len(x))
		for i in range(len(x)):
			if x[i] < param[1]:
				y[i] = 2*(x[i]-param[0])/m1
			else:
				y[i] = 2*(param[2]-x[i])/m2
		Piecewise.__init__(self,x,y,param,name, type)
		
    @staticmethod
    def getParam(parser, element):		
		paraList= parser.parseParameters(element,Triangular.paramList)
		return [float(i) for i in paraList]

    def computeTheta(self):		
		self.theta[2], self.theta[3], self.theta[4] = stats.triang.stats(loc=self.distParam[0] , scale = (self.distParam[2]- self.distParam[0]), c=(self.distParam[1]- self.distParam[0])/(self.distParam[2]- self.distParam[0]),moments="mvs")    	    			 
		#self.theta[2], self.theta[3], self.theta[4] = stats.triang.stats(loc=self.distParam[0] , scale = (self.distParam[2]-self.distParam[0]), c=self.distParam[1],moments="mvs")

    @staticmethod
    def getInstance(distParam,ranges, nrOfPoints):	
		bounds=Triangular.getBounds(distParam)
		ranges[0] , ranges[1] = PDF.adjustRangesToLocalBounds(bounds[0],bounds[1],ranges[0] , ranges[1], "%s"%ranges)
		distObj = Triangular(np.linspace(ranges[0] , ranges[1],nrOfPoints), distParam)
		distObj.setHRangesAsList(ranges[2:])
		return 	distObj

    @staticmethod
    def getBounds(param,ci=PDF.defaultCI):		
		return [param[0],param[2]]	

    def __str__(self):
		return PDF.__str__(self,Triangular.paramList)
				
    def plot(self,c):
		PDF.plot(self,self.x,self.y,c)
		
###############################################################################	
class Uniform(Piecewise):
    #paramList = ['min','max']
    paramList = ['a','b']
    def __init__(self,x, param,name='uniform', type='discrete'):
		y = stats.uniform.pdf(x, loc = param[0],scale= param[1] - param[0])
		Piecewise.__init__(self,x,y,param,name, type)

    def computeTheta(self):			 
		self.theta[2], self.theta[3], self.theta[4] = stats.uniform.stats(loc = self.theta[0],scale= self.theta[1] - self.theta[0],moments="mvs")
		
    @staticmethod
    def getParam(parser, element):		
		paraList 	= parser.parseParameters(element,Uniform.paramList)
		return [float(i) for i in paraList]

    @staticmethod
    def getInstance(distParam,ranges, nrOfPoints):	
		bounds=Uniform.getBounds(distParam)
		ranges[0] , ranges[1] = PDF.adjustRangesToLocalBounds(bounds[0],bounds[1],ranges[0] , ranges[1], "%s"%ranges)
		distObj = Uniform(np.linspace(ranges[0] , ranges[1],nrOfPoints), distParam)	
		distObj.setHRangesAsList(ranges[2:])
		return 	distObj

    @staticmethod		
    def getBounds(param, ci=PDF.defaultCI):		
		return [param[0],param[1]]		
		
    def __str__(self):
		return PDF.__str__(self,Uniform.paramList)
				
    def plot(self,c):
		plt.xlim([self.x[0]-1,self.x[-1]+1])	
		PDF.plot(self,self.x,self.y,c)	
		plt.vlines([self.x[0],self.x[-1]],0,[self.y[0]],color=c)
		
###############################################################################	
class Histogram(Piecewise):
    paramList = ['x0','x1','p']
    def __init__(self,param=[],name='histogram', type='discrete'):#param[]:[a,hist,bin_edges]
		Piecewise.__init__(self,param[0],param[1],[0,0,0],name, type)	

    @staticmethod
    def getParam(parser, element):		
		paraList 		= parser.parseHistogramParameters(element,Histogram.paramList)
		hist, bin_edges = np.histogram(paraList[0],paraList[1],weights=paraList[2],density=True)		
		y 				= hist#*np.diff(bin_edges)		
		return [paraList[0] , y, bin_edges]
		
    @staticmethod
    def getInstance(distParam,ranges, nrOfPoints):	
		distObj = Histogram(distParam)
		distObj.setHRangesAsList(ranges[2:])
		return 	distObj

    @staticmethod		
    def getBounds(param, ci=PDF.defaultCI):		
		return [param[0][0],param[0][-1]]
		
    def __str__(self):
		return PDF.__str__(self,Histogram.paramList)
								
    def plot(self,c):
		bar= plt.bar(self.x, self.y, width=1, color=c)	
								
###############################################################################			
class Bimodal(Piecewise):
    def __init__(self,x,y):
		Piecewise.__init__(self,x,y)	