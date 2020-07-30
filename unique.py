#Author: Kegan Wong
#Email: kmw037@ucsd.edu
#Purpose: Log any changes made to the master directory. This script is to be used in conjunction 
#		  with another python script that extracts key words from pdf(s) and makes a decision on
#		  where to insert the pdf file into the design history file.
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
dh_files = {}
dbox_file_nums = {}
doc_category = {}

#convert to empty set
dh_files = set()
dbox_file_nums = set()
doc_category = set()

#initialize empty array
inserted_fnames = []
columns = []

#paths to files
PATH_TO_LOG = "/Users/k3go/Desktop/FileHistoryLog/LastFileLog.txt"
PATH_TO_DFILE = "/Users/k3go/Desktop/FileHistoryLog/Deleted.txt"
PATH_TO_IFILE = "/Users/k3go/Desktop/FileHistoryLog/Inserted.txt"
PATH_TO_ALL = "/Users/k3go/Dropbox (ValenciaT)/Released Documents - PDF"
PATH_TO_EXCEL = "/Users/k3go/Desktop/TestExcel.xlsm"

#permissions
WRITE = "w"
RW = "w+"

#messages
DELETE_MSG = "Appended deleted files in "
INSERT_MSG = "Appended inserted files in "

#special character and strings
EXTENSION = ".pdf"
SHEET = "Sheet1"
NEW_L = "\n"
HIDDEN_F = "."
DASH = "-"
SPACE = " "
EMPTY_S = ""

#magic numbers
VALID_TIME = 1584576000.0
SPLITS = 2

def checkValidFile(fileName):
	return fileName.lower().endswith(EXTENSION)

def checkDocNumFormat(documentNumber):
	
	contents = []

	if (isinstance(documentNumber, str)):
		contents = documentNumber.split(DASH, SPLITS)

	return len(contents) == SPLITS and checkExcelDigits(contents)

def checkExcelDigits(arrayOfContents):

	status = True

	for contents in arrayOfContents:
		if (not contents.isnumeric()):
			status = False
			break

	return status

def createPrevHistLog(fileFHL):
	
	df = pd.read_excel(PATH_TO_EXCEL, SHEET)
	columnNames = df.columns
	
	for column in columnNames:
		columns.append(column)

	docNums = df[columns[0]]

	for numStr in docNums:

		if(isinstance(numStr,str) and checkDocNumFormat(numStr)):
			doc_category.add(numStr.split(DASH)[0])
			dh_files.add(numStr)
			fileFHL.write(numStr)
			fileFHL.write(NEW_L)

def parseDropBoxFiles(fname):

	fContents = fname.split(SPACE)

	for contents in fContents:
		counter = 0
		if (contents.count(DASH) >= 1):
			fNumStr = contents.split(DASH,contents.count(DASH))
			for parts in fNumStr:
				if (parts.isnumeric()):
					counter = counter + 1

			if(counter == len(fNumStr)):
				if (contents.split(DASH)[0] in doc_category):
					return contents.split(DASH)[0] + DASH +  contents.split(DASH)[1]

	return EMPTY_S

def writeDFile(dFile, content):

	dFile.write(content)
	dFile.write(NEW_L)

def writeIFile(iFile, content):

	iFile.write(content)
	iFile.write(NEW_L)

lastFileLog = open(PATH_TO_LOG, RW)
createPrevHistLog(lastFileLog)

dFile = open(PATH_TO_DFILE, WRITE)
iFile = open(PATH_TO_IFILE, WRITE)

#obtain all files and sub-directories in current DropBox directory
for root, dirs, files in os.walk(PATH_TO_ALL):	
	for f in files:
		if (not f.startswith(HIDDEN_F)):
			if(parseDropBoxFiles(f) != EMPTY_S):	
				if ((os.path.getmtime(os.path.join(root,f)) >= VALID_TIME) or (parseDropBoxFiles(f) in dh_files)):				
					dbox_file_nums.add(parseDropBoxFiles(f))
					
#Case 1:  Most current version has same files as old version(dbox_file_nums.issubset(dh_files) AND dh_files.issubset(dbox_file_nums), no change
if dbox_file_nums.issubset(dh_files) and dh_files.issubset(dbox_file_nums):
	sys.exit(0)
	
#Case 2: Most current version is a strict subset of the old version (dbox_file_nums.issubset(dh_files) = true), deletion
elif dbox_file_nums.issubset(dh_files):

	print(DELETE_MSG + PATH_TO_DFILE)
	deleted = dh_files - dbox_file_nums

	for dStr in deleted:
		writeDFile(dFile, dStr)

#Case 3: Most current version is a strict superset of the old version (dbox_file_nums.issuperset(dh_files) = true), insertion
elif dbox_file_nums.issuperset(dh_files):
	
	print(INSERT_MSG + PATH_TO_IFILE)
	inserted = dbox_file_nums - dh_files

	for iStr in inserted:
		inserted_fnames.append(iStr)
		writeIFile(iFile, iStr)

#Case 4: Some hybrid of insertions and deletions(perform deletions first, then insertions).
else:

	print(DELETE_MSG + PATH_TO_DFILE)
	print(INSERT_MSG + PATH_TO_IFILE)

	deleted = dh_files - dbox_file_nums
	inserted = dbox_file_nums - dh_files

	for dStr in deleted:
		writeDFile(dFile, dStr)

	for iStr in inserted:
		inserted_fnames.append(iStr)
		writeIFile(iFile, iStr)

lastFileLog.close()
dFile.close()
iFile.close()