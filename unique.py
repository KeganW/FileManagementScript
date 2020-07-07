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
pathToLog = "/Users/k3go/Desktop/FileHistoryLog/MasterFileLog.txt"
pathToDFile = "/Users/k3go/Desktop/FileHistoryLog/Deleted.txt"
pathToIFile = "/Users/k3go/Desktop/FileHistoryLog/Inserted.txt"
pathToAll = "/Users/k3go/Desktop/Smarty"

#permissions
append = "a"
write = "w"
read = "r"

#special characters
newL = "\n"

def createFirstHistLog(fileFHL, pathToAll):
	for root, dirs, files in os.walk(pathToAll):
		for f in files:
			fileFHL.write(os.path.join(root,f))
			fileFHL.write(newL)

#obtain all files and sub-directories in current DropBox directory
for root, dirs, files in os.walk(pathToAll):	
	for f in files:
		newFiles.add(os.path.join(root,f))
		
	for d in dirs:
		newDirs.add(os.path.join(root,d))

if (not os.path.exists(pathToLog)):
	old = open(pathToLog, append)
	createFirstHistLog(old, pathToAll)
	old.close()
	sys.exit(0)

if (not os.path.exists(pathToDFile)):
	dFile = open(pathToDFile, append)

if (not os.path.exists(pathToIFile)):
	iFile = open(pathToIFile, append)

old = open(pathToLog, read)

for line in old:
	line = line.rstrip(newL)
	oldFiles.add(line)

#Case 1:  Most current version has same files as old version(newFiles.issubset(oldFiles) AND oldFiles.issubset(newFiles), no change
if newFiles.issubset(oldFiles) and oldFiles.issubset(newFiles):
	sys.exit(0)
#Case 2: Most current version is a strict subset of the old version (newFiles.issubset(oldFiles) = true), deletion
elif newFiles.issubset(oldFiles):
	deleted = oldFiles - newFiles

#Case 3: Most current version is a strict superset of the old version (newFiles.issuperset(oldFiles) = true), insertion
elif newFiles.issuperset(oldFiles):
	inserted = newFiles - oldFiles

#Case 4: Some hybrid of insertions and deletions(perform deletions first, then insertions)... iterate from oldFiles, and compare every
#		 file to the most recent version. If they are not in it, then its a delete. Conversely, newFiles - oldFiles yields what was 
#		 inserted.
else:
	deleted = oldFiles - newFiles
	inserted = newFiles - oldFiles