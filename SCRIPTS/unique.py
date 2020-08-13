#Author: Kegan Wong
#Email: kmw037@ucsd.edu
#Purpose: Log any changes and notify the user of any changes made to the master 
#		  directory. This script is to be used in conjunction with another 
#		  python script that extracts key words from pdf(s) and makes a decision 
#		  on where to insert the pdf file into the design history file.
#Future Use: Change the path to whatever directory Drop Box is synced to. For full path to a file,
#	         use os.path.join(root,f) 
#!/Users/k3go/anaconda3/bin/python
import pandas as pd

from pandas import ExcelWriter
from pandas import ExcelFile
from tkinter import *

import pathlib
import sys
import os
import time

#initialize empty dictionaries
doc_category_nums = {}
dbox_file_nums = {}
dh_file_nums = {}

#convert to empty set
doc_category_nums = set()
dbox_file_nums = set()
dh_file_nums = set()

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
TITLE = "Updates for Design History File"
SUMMARY_I = "The following files were INSERTED but not recorded in the Design History File..."
SUMMARY_D = "The following files were DELETED but not recorded in the Design History File..."

#special character and strings
EXTENSION = ".pdf"
SHEET = "Sheet1"
NEW_L = "\n"
HIDDEN_F = "."
DASH = "-"
SPACE = " "
EMPTY_S = ""
VERTICAL = "y"


#magic numbers
VALID_TIME = 1584576000.0
SPLITS = 2

def check_valid_file(fileName):

	return fileName.lower().endswith(EXTENSION)

def check_docnum_format(documentNumber):
	
	contents = []

	if (isinstance(documentNumber, str)):
		contents = documentNumber.split(DASH, SPLITS)

	return len(contents) == SPLITS and check_excel_digits(contents)

def check_excel_digits(arrayOfContents):

	status = True

	for contents in arrayOfContents:
		if (not contents.isnumeric()):
			status = False
			break

	return status

def create_prev_hist_log(fileFHL):
	
	df = pd.read_excel(PATH_TO_EXCEL, SHEET)
	columnNames = df.columns
	
	for column in columnNames:
		columns.append(column)

	docNums = df[columns[0]]

	for numStr in docNums:

		if(isinstance(numStr,str) and check_docnum_format(numStr)):
			doc_category_nums.add(numStr.split(DASH)[0])
			dh_file_nums.add(numStr)
			fileFHL.write(numStr)
			fileFHL.write(NEW_L)

def parse_dropbox_files(fname):

	fContents = fname.split(SPACE)

	for contents in fContents:
		counter = 0
		if (contents.count(DASH) >= 1):
			fNumStr = contents.split(DASH,contents.count(DASH))
			for parts in fNumStr:
				if (parts.isnumeric()):
					counter = counter + 1

			if(counter == len(fNumStr)):
				if (contents.split(DASH)[0] in doc_category_nums):
					return contents.split(DASH)[0] + DASH +  contents.split(DASH)[1]

	return EMPTY_S

def content_message(ls):

	if type(ls) is set:
		message = ""
		for dnums in ls:
			message += NEW_L + dnums 
		return message

	return EMPTY_S

def write_file(file, content):

	file.write(content)
	file.write(NEW_L)

last_file_log = open(PATH_TO_LOG, RW)
create_prev_hist_log(last_file_log)

d_file = open(PATH_TO_DFILE, WRITE)
i_file = open(PATH_TO_IFILE, WRITE)

#obtain all files and sub-directories in current DropBox directory
for root, dirs, files in os.walk(PATH_TO_ALL):	
	for f in files:
		if (not f.startswith(HIDDEN_F)):
			if(parse_dropbox_files(f) != EMPTY_S):	
				if ((os.path.getmtime(os.path.join(root,f)) >= VALID_TIME) or (parse_dropbox_files(f) in dh_file_nums)):				
					dbox_file_nums.add(parse_dropbox_files(f))
					
#Case 1:  Most current version has same files as old version(dbox_file_nums.issubset(dh_file_nums) AND dh_file_nums.issubset(dbox_file_nums), no change
if dbox_file_nums.issubset(dh_file_nums) and dh_file_nums.issubset(dbox_file_nums):
	sys.exit(0)
	
#Case 2: Most current version is a strict subset of the old version (dbox_file_nums.issubset(dh_file_nums) = true), deletion
elif dbox_file_nums.issubset(dh_file_nums):

	print(DELETE_MSG + PATH_TO_DFILE)
	deleted = dh_file_nums - dbox_file_nums

	for dStr in deleted:
		write_file(d_file, dStr)

#Case 3: Most current version is a strict superset of the old version (dbox_file_nums.issuperset(dh_file_nums) = true), insertion
elif dbox_file_nums.issuperset(dh_file_nums):
	
	print(INSERT_MSG + PATH_TO_IFILE)
	inserted = dbox_file_nums - dh_file_nums

	for iStr in inserted:
		inserted_fnames.append(iStr)
		write_file(i_file, iStr)

#Case 4: Some hybrid of insertions and deletions(perform deletions first, then insertions).
else:

	print(DELETE_MSG + PATH_TO_DFILE)
	print(INSERT_MSG + PATH_TO_IFILE)

	deleted = dh_file_nums - dbox_file_nums
	inserted = dbox_file_nums - dh_file_nums

	for dStr in deleted:
		write_file(d_file, dStr)

	for iStr in inserted:
		inserted_fnames.append(iStr)
		write_file(i_file, iStr)

last_file_log.close()
d_file.close()
i_file.close()

#notify the user with a popup once per week(crontab runs behind the scenes)
if (len(inserted) > 0 or len(deleted) > 0):
	root = Tk()
	root.title(TITLE)

	s_bar = Scrollbar(root)
	s_bar.pack(side=RIGHT, fill= VERTICAL)

	content = Text(root, yscrollcommand = s_bar.set)
	content.pack()

	if (len(inserted) > 0):
		content.insert(END, SUMMARY_I + content_message(inserted))

	if (len(deleted) > 0):	
		content.insert(END, NEW_L + SUMMARY_D + content_message(deleted))

	s_bar.config(command=content.yview)
	root.mainloop()
#to run a script every certain day, look into crontab
