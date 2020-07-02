import numpy as np
import matplotlib.pyplot as plt
import pdfs as pdf
reload (pdf)

def getRangeValues(v1,v2, num=100):		
	return np.linspace(v1,v2,num)
	
def showResult(obj1,obj2, legend=None):	
	print(obj1.__str__())    
	print(obj2.__str__())    
	if legend is not None:
		obj1.plot('blue')
		obj2.plot('red')		
		obj2.legend(legend)

def testGamma(param, legend=None):
	bounds = pdf.Gamma.getBounds(param)
	gammaObj = pdf.Gamma(getRangeValues(bounds[0],bounds[1]),param)
	betaObj = gammaObj.getBeta()
	showResult(betaObj,gammaObj, legend)

def testWeibull(param, legend=None):
	bounds = pdf.Weibull.getBounds(param)
	weibullObj = pdf.Weibull(getRangeValues(bounds[0],bounds[1]),param)
	betaObj = weibullObj.getBeta()
	showResult(betaObj,weibullObj, legend)

def testGaussian(param, legend=None):
	bounds = pdf.Gaussian.getBounds(param)
	gaussianObj = pdf.Gaussian(getRangeValues(bounds[0],bounds[1]),param)
	betaObj = gaussianObj.getBeta()
	showResult(betaObj,gaussianObj, legend)

def testTriangular(param, legend=None):
	triangObj = pdf.Triangular(param)
	betaObj = triangObj.getBeta()
	showResult(betaObj,triangObj, legend)

def testBetaPert(param, legend=None):
	betaPertObj = pdf.BetaPert(param)
	betaObj = betaPertObj.getBeta()
	showResult(betaObj,betaPertObj, legend)

def testLognormal(param, legend=None):
	bounds = pdf.Lognormal.getBounds(param)
	lognormal = pdf.Lognormal(getRangeValues(bounds[0],bounds[1]),param)
	betaObj = lognormal.getBeta()
	showResult(betaObj,lognormal, legend)

def testLogistic(param, legend=None):
	bounds = pdf.Logistic.getBounds(param)
	logistic = pdf.Logistic(getRangeValues(bounds[0],bounds[1]),param)
	betaObj = logistic.getBeta()
	showResult(betaObj,logistic, legend)

def testLoglogistic(param, legend=None):
	bounds = pdf.Loglogistic.getBounds(param,0.99)
	loglogistic = pdf.Loglogistic(getRangeValues(bounds[0],bounds[1]),param)
	betaObj = loglogistic.getBeta()
	showResult(betaObj,loglogistic, legend)

def testNanLoglogistic():
	beta1 = pdf.Beta([1.304,3.48, 0.0,8.52028])
	t = pdf.Beta.computeThetaTest(1.304,3.48,0.0,8.52028)
	beta1.fit(t)
	beta2 = pdf.Beta([1.304,3.48, 0.0,8.52028])
	t = pdf.Beta.computeThetaTest(1.304,3.48,0.34,2.65)
	beta2.fit(t)
	showResult(beta1,beta2, ["Beta(Maintining hist. bounds)","Beta(Ignoring hist. bounds)"])
	
def testPearson3(param, legend=None):
	bounds = pdf.Pearson3.getBounds(param,0.9)
	pearson3 = pdf.Pearson3(getRangeValues(bounds[0],bounds[1]),param)
	betaObj = pearson3.getBeta()
	showResult(betaObj,pearson3, legend)

def testExponential(param, legend=None):
	bounds = pdf.Exponential.getBounds(param)
	exp = pdf.Exponential(getRangeValues(bounds[0],bounds[1]),param)
	betaObj = exp.getBeta()
	showResult(betaObj,exp, legend)
	
def testPareto(param, legend=None):
	bounds 	= pdf.Pareto.getBounds(param,0.999)
	pareto 	= pdf.Pareto(getRangeValues(bounds[0],bounds[1]),param)
	betaObj = pareto.getBeta()
	showResult(betaObj,pareto, legend)
	
def testChi(param, legend=None):
	bounds 	= pdf.Chi.getBounds(param)
	chi 	= pdf.Chi(getRangeValues(bounds[0],bounds[1]),param)
	betaObj = chi.getBeta()
	showResult(betaObj,chi, legend)
	
def testPoisson(param, legend=None):
	bounds 	= pdf.Poisson.getBounds(param)
	poisson = pdf.Poisson(range(0,int(bounds[1])),param)
	betaObj = poisson.getBeta()
	showResult(betaObj,poisson, legend)

def testBernoulli(param, legend=None):
	bernoulli = pdf.Bernoulli(param)
	betaObj = bernoulli.getBeta()
	showResult(betaObj,bernoulli, legend)

def testBinomial(param, legend=None):
	bounds 	= pdf.Binomial.getBounds(param,1)
	binomial = pdf.Binomial(range(int(bounds[0]),int(bounds[1])),param)	
	betaObj = binomial.getBeta()
	showResult(betaObj,binomial, legend)

def testUniform(param, legend=None):
	uniform 	= pdf.Uniform(getRangeValues(param[0],param[1]),param)
	betaObj = uniform.getBeta()
	showResult(betaObj,uniform, legend)
	
def testHistogram(legend=None):
	a=[0,1,2,3,4,5,6,7,8,9,10,11,12,13]
	bins=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
	w=[2,3,6,4,4,2,4,2,2,2,2,1,1,0]

	hist, bin_edges = np.histogram(a,bins,weights=w,density=True)	
	histogram 	= pdf.Histogram([a,hist,bin_edges])		
	betaObj = histogram.getBeta()
	showResult(betaObj,histogram, legend)	

def testHistogram1(legend=None):
	a=[5,6,7,9,10]
	bins=[5,6,7,9,10,11]
	w=[2,2,2,2,2]

	hist, bin_edges = np.histogram(a,bins,weights=w,density=True)	
	histogram 	= pdf.Histogram([a,hist,bin_edges])		
	betaObj = histogram.getBeta()
	showResult(betaObj,histogram, legend)	

def testXYChart(legend=None):
	plt.figure(1)
	x=[0,4,8,12,16,20]
	y=[0.04,0.97,1,1,1,1]
	s = float(sum(y))
	y1 = [y0/s for y0 in y]
	plt.subplot(121)
	plt.ylim([min(y)-0.01,max(y)+0.01])
	plt.plot(x,y,color='red')
	plt.subplot(122)
	pw 	= pdf.Piecewise(x,y1)
	betaObj = pw.getBeta()
	showResult(betaObj,pw, legend)

def scaleXYChart(x,y, minXRange,maxXRange,minYRange,maxYRange):
	minX		= min(x)
	minY		= min(y)
	xWidth		= max(x)- minX
	yWidth		= max(y)- minY
	boxWidth	= maxXRange-minXRange
	boxHeight	= maxYRange-minYRange
	scaleRateToBoxWidth			 	= boxWidth/xWidth
	scaleRateToBoxHeight		 	= boxHeight/yWidth
	#Computing the shifting values of chart's lower-left corner to origin(0,0) 
	minXRangeTranslateValueTo0		= 0 - minX
	minYRangeTranslateValueTo0		= 0 - minY
	#Computing the shifting values of chart's lower-left corner to box's left lower-bound corner 
	zeroTranslateValueToBoxX	= minXRange
	zeroTranslateValueToBoxY 	= minYRange
	for i in range(len(x)):
		x[i] = (x[i] + minXRangeTranslateValueTo0) * scaleRateToBoxWidth + zeroTranslateValueToBoxX
		y[i] = (y[i] + minYRangeTranslateValueTo0) * scaleRateToBoxHeight + zeroTranslateValueToBoxY		
	
	return [x, y]

	

def testxyChartVariants():
	#x=[0,4,8,12,16,20]
	#y=[0.04,0.97,1,1,1,1]
	#x=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]
	#y=[0.0004,0.0004,0.0181,0.2296,0.9793,0.9959,0.9897,0.9733,0.9389,0.8804,0.7967,0.6905,0.572,0.4547,0.349,0.2601,0.19,0.1362,0.0968,0.0678,0.0472,0.0328,0.0227,0.0156,0.0108,0]	
	#x=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
	#y=[0.1,0.1071,0.1795,0.5546,0.9277,0.9643,0.9565,0.9259,0.872,0.7846,0.675,0.5556,0.4444,0.3333,0.25,0.1694,0.1173,0.0769,0.0455,0.0234,0]

	x=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100]
	y=[0,0,0,0,1,0,0,1,0,1,1,0,2,0,2,1,1,2,1,2,2,5,5,5,5,5,5,5,5,5,5,5,5,5,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10]

	mxX = max(x)
	mnX = min(x)
	mxY = max(y)
	mnY = min(y)
	wdthx=mxX-mnX
	wdthy=mxY-mnY
	plt.ylim([mnY - wdthy*0.20,mxY + wdthy*0.20])
	plt.xlim([mnX - wdthx*0.20,mxX + wdthx*0.20])
	plt.plot(x,y,color='red')
	
	chart=scaleXYChart(x,y,mnX - wdthx*0.20,mxX,mnY,mxY)
	plt.plot(chart[0],chart[1],color='gray')
	chart=scaleXYChart(x,y,mnX + wdthx*0.18,mxX + wdthx*0.20,mnY,mxY)
	plt.plot(chart[0],chart[1],color='gray')
	
	scaleXYChart(x,y,mnX+wdthx*.16,mxX+wdthx*.02,mnY-wdthy*0.18,mxY+wdthy*0.12)
	scaleXYChart(x,y,mnX-wdthx*.14,mxX-wdthx*.04,mnY+wdthy*0.16,mxY-wdthy*0.10)
	chart=scaleXYChart(x,y,mnX-wdthx*.12,mxX+wdthx*.06,mnY-wdthy*0.14,mxY+wdthy*0.18)
	plt.plot(chart[0],chart[1],color='gray')
	scaleXYChart(x,y,mnX+wdthx*.10,mxX+wdthx*.08,mnY+wdthy*0.12,mxY-wdthy*.14)

	scaleXYChart(x,y,mnX+wdthx*.08,mxX+wdthx*.12,mnY-wdthy*0.10,mxY-wdthy*.06)	
	
	scaleXYChart(x,y,mnX-wdthx*.2,mxX+wdthx*.2,mnY-wdthy*0.20,mxY+wdthy*.2)	
	plt.show()
	
if __name__ == '__main__':
	#testGamma([13.14, 0.72],('Beta','Gamma'))
	#testGamma([2.09, 1.09],('Beta','Gamma'))	
	#testGamma([2.11, 1.03],('Beta','Gamma'))		
	#testWeibull([1.782, 3.974],('Beta','Weibull'))
	#testGaussian([3.7,0.8],('Beta','Gaussian'))
	#testGaussian([4.1,40.1],('Beta','Gaussian'))	
	#testTriangular([2,4,6],('Beta','Triangular'))			
	#testTriangular([2,5,12],('Beta','Triangular'))		
	#testBetaPert([28,180,220],('Beta','Beta-Pert'))			
	#testLognormal([12,3],('Beta','Lognormal'))	################ check			
	#testLogistic([15,2],('Beta','Logistic'))
	#testLoglogistic([4,3,10],('Beta','Loglogistic'))	
	#testPearson3([3,1],('Beta','Pearson3'))
	#testExponential([12],('Beta','Exponential'))	
	#testPareto([10,14],('Beta','Pareto'))		
	#testChi([10,0,4],('Beta','Chi'))			
	#testPoisson([5],('Beta','Poisson'))				
	#testBernoulli([0.4],('Beta','Bernoulli'))			
	#testBinomial([10,0.3],('Beta','Binomial'))				
	#testUniform([3,10],('Beta','Uniform'))		
	#testHistogram(('Beta','Histogram'))			
	#testXYChart(('Beta','XY-Chart'))
	#testxyChartVariants()
	#testGamma([216.62, 0.15],('Beta','Gamma'))
	#testLoglogistic([24.05,0,30.58],('Beta','Loglogistic'))
	testLoglogistic([4.13,0.0,0.96],('Beta','Loglogistic'))	
	#testNanLoglogistic()