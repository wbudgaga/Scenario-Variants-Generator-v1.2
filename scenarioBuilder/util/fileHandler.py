import numpy as np
class FileHandler:
    def __init__(self,fileName, op): 
		#op is one of 'r', 'w', 'a', or  'r+'
        self.file = open(fileName, op)
               
    def addToFile(self, data=""):
        self.file.write(data)
        self.file.write('\n')
       
    def getAsArray(self):
	data=[]
	for line in self.file:
		rec = map(float, line.strip().split(','))
		data.append(rec)
	return np.array(data)
        
    def closeFile(self):
        self.file.close()
		
    @staticmethod     
    def convertListToString(data):
        s=""
        for item in data:
            s="%s,%s"%(s,item)
        return s[1:]