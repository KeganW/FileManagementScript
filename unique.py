#Author: Kegan Wong
#Email: kmw037@ucsd.edu
#Purpose: Log any changes made to the master directory. This script is to be used in conjunction 
#		  with the excel macro that updates the file in charge of tracking the device history record, 
#		  device master record and the device history file.
#Future Use: Change the path to whatever directory Drop Box is synced to. For full path to a file,
#	         use os.path.join(root,f) 
#!/usr/bin/python
import pathlib
import sys
import os

#initialize empty dictionaries
oldFiles = {}
oldDirs = {}
newFiles = {}
newDirs = {}

#convert to empty set
oldFiles = set()
oldDirs = set()
newFiles = set()
newDirs = set()

#paths to files
pathToLog = "/Users/k3go/Desktop/FileHistoryLog/LastFileLog.txt"
pathToDFile = "/Users/k3go/Desktop/FileHistoryLog/Deleted.txt"
pathToIFile = "/Users/k3go/Desktop/FileHistoryLog/Inserted.txt"
pathToAll = "/Users/k3go/Dropbox (ValenciaT)/Released Documents - PDF"

#permissions
append = "a"
write = "w"
read = "r"

#special characters and strings
newL = "\n"
hiddenF = "."
extension = ".pdf"


def checkValidFile(fileName):
	return fileName.lower().endswith(extension)

def createFirstHistLog(fileFHL, pathToAll, files):

	for f in files:
		if (checkValidFile(f)):
			fileFHL.write(f)
			fileFHL.write(newL)

def writeDFile(dFile, content):

	dFile.write(content)
	dFile.write(newL)

def writeIFile(iFile, content):

	iFile.write(content)
	iFile.write(newL)

#obtain all files and sub-directories in current DropBox directory
for root, dirs, files in os.walk(pathToAll):	
	for f in files:
		if (not f.startswith(hiddenF)):
			print(f)
			newFiles.add(f)
	for d in dirs:
		newDirs.add(d)

#cases for non-existing files
if (not os.path.exists(pathToLog)):
	old = open(pathToLog, append)
	createFirstHistLog(old, pathToAll, newFiles)
	old.close()
	sys.exit(0)

dFile = open(pathToDFile, write)
iFile = open(pathToIFile, write)
old = open(pathToLog, read)

#read from old version history
for line in old:
	line = line.rstrip(newL)
	oldFiles.add(line)

#Case 1:  Most current version has same files as old version(newFiles.issubset(oldFiles) AND oldFiles.issubset(newFiles), no change
if newFiles.issubset(oldFiles) and oldFiles.issubset(newFiles):
	sys.exit(0)
#Case 2: Most current version is a strict subset of the old version (newFiles.issubset(oldFiles) = true), deletion
elif newFiles.issubset(oldFiles):
	deleted = oldFiles - newFiles

	for dStr in deleted:
		writeDFile(dFile, dStr)

	dFile.close()

#Case 3: Most current version is a strict superset of the old version (newFiles.issuperset(oldFiles) = true), insertion
elif newFiles.issuperset(oldFiles):
	inserted = newFiles - oldFiles

	for iStr in inserted:
		writeIFile(iFile, iStr)

	iFile.close()

#Case 4: Some hybrid of insertions and deletions(perform deletions first, then insertions).
else:
	deleted = oldFiles - newFiles
	inserted = newFiles - oldFiles

	for dStr in deleted:
		writeDFile(dFile, dStr)

	for iStr in inserted:
		writeIFile(iFile, iStr)

	dFile.close()
	iFile.close()