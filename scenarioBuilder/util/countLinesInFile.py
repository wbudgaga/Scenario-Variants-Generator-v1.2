import shutil	as s
import os

f = open("/s/red-rock/a/tmp/frameworkWorkDir/data/output.csv", 'r',0)
c=0
for line in f:
	c=c+1
	print "count= %s"%c
