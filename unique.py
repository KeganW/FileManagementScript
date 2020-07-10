#Author: Kegan Wong
#Email: kmw037@ucsd.edu
#Purpose: Log any changes made to the master directory. This script is to be used in conjunction 
#		  with the excel macro that updates the file in charge of tracking the device history record, 
#		  device master record and the device history file.
#Future Use: Change the path to whatever directory Drop Box is synced to. For full path to a file,
#	         use os.path.join(root,f) 
#!/usr/bin/python
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile

import pathlib
import sys
import os
import time

#initialize empty dictionaries
dhFiles = {}
dbFiles = {}
docTypes = {}

#convert to empty set
dhFiles = set()
dbFiles = set()
docTypes = set()

#initialize empty array
columns = []

#paths to files
pathToLog = "/Users/k3go/Desktop/FileHistoryLog/LastFileLog.txt"
pathToDFile = "/Users/k3go/Desktop/FileHistoryLog/Deleted.txt"
pathToIFile = "/Users/k3go/Desktop/FileHistoryLog/Inserted.txt"
pathToAll = "/Users/k3go/Dropbox (ValenciaT)/Released Documents - PDF"
pathToExcel = "/Users/k3go/Desktop/TestExcel.xlsx"

#permissions
write = "w"
read = "r"
rw = "w+"

#special characters, magic numbers and strings
newL = "\n"
hiddenF = "."
emptyS = ""
space = " "
dash = "-"
extension = ".pdf"
sheet = "Sheet1"
splits = 2
validTime = 1584576000.0

def checkValidFile(fileName):
	return fileName.lower().endswith(extension)

def checkDocNumFormat(documentNumber):
	
	contents = []

	if (isinstance(documentNumber, str)):
		contents = documentNumber.split(dash, splits)

	return len(contents) == splits and checkExcelDigits(contents)

def checkExcelDigits(arrayOfContents):

	status = True

	for contents in arrayOfContents:
		if (not contents.isnumeric()):
			status = False
			break

	return status

def createPrevHistLog(fileFHL):
	
	df = pd.read_excel(pathToExcel, sheet)
	columnNames = df.columns
	
	for column in columnNames:
		columns.append(column)

	docNums = df[columns[0]]

	for numStr in docNums:

		if(isinstance(numStr,str) and checkDocNumFormat(numStr)):
			docTypes.add(numStr.split(dash)[0])
			dhFiles.add(numStr)
			fileFHL.write(numStr)
			fileFHL.write(newL)

def parseDropBoxFiles(fname):
	#FOR NEXT TIME: FILES THAT ARE IN THE DROP BOX DIRECTORY ARE INCLUDED IN THE FHL, so
	#if we put a later date, then some of the files won't be recorded... fix: track old files,
	#and put them in a set. condition checks condition 1 OR in set
	fContents = fname.split(space)

	for contents in fContents:
		counter = 0
		if (contents.count(dash) >= 1):
			fNumStr = contents.split(dash,contents.count(dash))
			for parts in fNumStr:
				if (parts.isnumeric()):
					counter = counter + 1

			if(counter == len(fNumStr)):
				if (contents.split(dash)[0] in docTypes):
					return contents.split(dash)[0] + dash +  contents.split(dash)[1]

	return emptyS

def writeDFile(dFile, content):

	dFile.write(content)
	dFile.write(newL)

def writeIFile(iFile, content):

	iFile.write(content)
	iFile.write(newL)

lastFileLog = open(pathToLog, rw)
createPrevHistLog(lastFileLog)

dFile = open(pathToDFile, write)
iFile = open(pathToIFile, write)

#obtain all files and sub-directories in current DropBox directory
for root, dirs, files in os.walk(pathToAll):	
	for f in files:
		if (not f.startswith(hiddenF)):
			if(parseDropBoxFiles(f) != emptyS):	
				if ((os.path.getmtime(os.path.join(root,f)) >= validTime) or (parseDropBoxFiles(f) in dhFiles)):				
					dbFiles.add(parseDropBoxFiles(f))
					#print("last modified: %s" % os.path.getmtime(os.path.join(root,f)))

#read from old version history
#for line in lastFileLog:
#	print(line)
#	line = line.rstrip(newL)
#	dhFiles.add(line)

#Case 1:  Most current version has same files as old version(dbFiles.issubset(dhFiles) AND dhFiles.issubset(dbFiles), no change
if dbFiles.issubset(dhFiles) and dhFiles.issubset(dbFiles):
	sys.exit(0)
#Case 2: Most current version is a strict subset of the old version (dbFiles.issubset(dhFiles) = true), deletion
elif dbFiles.issubset(dhFiles):
	print("Entered case 2:")
	deleted = dhFiles - dbFiles

	for dStr in deleted:
		writeDFile(dFile, dStr)

#Case 3: Most current version is a strict superset of the old version (dbFiles.issuperset(dhFiles) = true), insertion
elif dbFiles.issuperset(dhFiles):
	
	print("Entered case 3:")
	inserted = dbFiles - dhFiles

	for iStr in inserted:
		writeIFile(iFile, iStr)

#Case 4: Some hybrid of insertions and deletions(perform deletions first, then insertions).
else:
	print("Entered case 4:")
	deleted = dhFiles - dbFiles
	inserted = dbFiles - dhFiles

	for dStr in deleted:
		writeDFile(dFile, dStr)

	for iStr in inserted:
		writeIFile(iFile, iStr)

lastFileLog.close()
dFile.close()
iFile.close()