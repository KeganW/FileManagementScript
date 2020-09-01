#Author: Kegan Wong
#Email: kmw037@ucsd.edu
#Purpose: Log any changes and notify the user of any changes made to the Design  
#		  History File. Changes include deletions and insertions. This script 
#		  runs automatically every week, and the toolbar helps with . 
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
bank = {}
doc_category_nums = {}
dbox_file_nums = {}
dh_file_nums = {}

#convert to empty set
bank = set()
doc_category_nums = set()
dbox_file_nums = set()
dh_file_nums = set()

#initialize empty array
inserted_fnames = []
columns = []
cbox_names = []
options = []
dmr_files = []
dhf_files = []

#paths to files
PATH_TO_LOG = "/Users/k3go/Desktop/FileHistoryLog/LastFileLog.txt"
PATH_TO_BANK = "/Users/k3go/Desktop/FileHistoryLog/Bank.txt"
PATH_TO_DFILE = "/Users/k3go/Desktop/FileHistoryLog/Deleted.txt"
PATH_TO_IFILE = "/Users/k3go/Desktop/FileHistoryLog/Inserted.txt"
PATH_TO_ALL = "/Users/k3go/Dropbox (ValenciaT)/Released Documents - PDF"
PATH_TO_EXCEL = "/Users/k3go/Desktop/TestExcel.xlsm"

#permissions
WRITE = "w"
READ = "r"
RW = "w+"

#messages
DELETE_MSG = "Appended deleted files in "
INSERT_MSG = "Appended inserted files in "
TITLE = "Updates for Design History File"
SUMMARY_I = "The following files were INSERTED but not recorded in the Design History File..."
SUMMARY_D = "The following files were DELETED but not recorded in the Design History File..."
SUMMARY_DMR = "The following files are to be inserted to the DMR:"
SUMMARY_DHF = "The following files are to be inserted to the DHF:"

#special strings
R_CLICK = "<Button-1>"
DIMENSION = "520x800"
VARIABLE = "variable"
SHEET = "Sheet1"
TEXT = "text"
CBOX_ID = "cbox_"
OPT_ID = "opt_"
EXTENSION = ".pdf"
ZERO_STR = "0"
ONE_STR = "1"

#special characters
VERTICAL = "y"
NEW_L = "\n"
HIDDEN_F = "."
DASH = "-"
SPACE = " "
EMPTY_S = ""

#magic numbers
VALID_TIME = 1584576000.0
C_SPAN = 5
SPLITS = 2
GAP = 2

#GUI constants
COLOR_1 = "green"
COLOR_2 = "red"

#the following methods are used to determine any changes in the DHF with dropbox
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

def create_bank(bank, inserted, deleted):

	for contents in b_file:
		bank.add(contents)

	for inum in inserted:
		if inum not in bank:
			write_file(b_file, inum)

	for dnum in deleted:
		if dnum not in bank:
			write_file(b_file, dnum)

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

def content_message(ls):

	if type(ls) is set:
		message = EMPTY_S
		for dnums in ls:
			message += NEW_L + dnums 
		return message

	return EMPTY_S

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

def write_file(file, content):

	file.write(content)
	file.write(NEW_L)

#the following methods are used for the GUI interactive popup
def fill_popup(ls, r, g_counter, isDHF, root):

	counter = 0
	c = 0
	
	for fnums in ls:
		if (counter%C_SPAN == 0 and counter != 0):
			r = r+1
			c = 0

		cbox_names[g_counter] = Checkbutton(root, text=fnums, variable = options[g_counter], offvalue = ONE_STR, onvalue=ZERO_STR)
		cbox_names[g_counter].bind(R_CLICK, lambda event, root = root: track_contents(event = event,ls=ls, isDHF = isDHF, root=root))
		cbox_names[g_counter].grid(row=r,column=c)
		
		g_counter = g_counter + 1
		counter = counter + 1
		c = c+1

def track_contents(event, ls, isDHF, root):

	if ((root.getvar((event.widget.cget(VARIABLE)))) == ZERO_STR):

		if (event.widget.cget(TEXT) in dmr_files):
			dmr_files.remove(event.widget.cget(TEXT))

	elif ((root.getvar((event.widget.cget(VARIABLE)))) == ONE_STR):

		if (event.widget.cget(TEXT) not in dmr_files):
			dmr_files.append(event.widget.cget(TEXT))

def list_dmr():
	#PROBLEM HERE
	if (len(dmr_files) == 0):
		print("No files currently tracked.")

	else:
		print("The following files are currently marked as belonging in the DMR:")

	for files in dmr_files:
		print(files)

def list_dhf():

	if (len(dhf_files) == 0):
		print("No files currently tracked.")

	else:
		print("The following files are currently marked as belonging in the DHF:")

	for files in dhf_files:
		print(files)

def check_all():

	for cbox in cbox_names:
		cbox.select()
		
		if (cbox.cget(TEXT) not in dmr_files):
			dmr_files.append(cbox.cget(TEXT))

def clear_all():

	#issue with selecting all after calling dhf_gui, maybe hanging references???
	for cbox in cbox_names:
		cbox.deselect()

		if (cbox.cget(TEXT) in dmr_files):
			dmr_files.remove(cbox.cget(TEXT))

def restart_gui(root):

	dmr_files.clear()
	dhf_files.clear()
	cbox_names.clear()

	deleted = dh_file_nums - dbox_file_nums
	inserted = dbox_file_nums - dh_file_nums

	root.destroy()

	launch_gui(inserted, deleted, False)

def dhf_gui(root, inserted, deleted):

	dmr_set = set(dmr_files)
	ins_set = set(inserted)
	del_set = set(deleted)

	remaining_insert = ins_set - dmr_set
	remaining_delete = del_set - dmr_set

	cbox_names.clear()

	root.destroy()

	launch_gui(remaining_insert, remaining_delete, True)

def launch_gui(inserted, deleted, isDHF):

	g_counter = 0
	r = 1 

	for index in range(len(inserted) + len(deleted)):
		cbox_names.append(CBOX_ID + str(index))
		options.append(OPT_ID + str(index))

	root = Tk()
	root.title(TITLE)
	root.geometry(DIMENSION)


	main_menu = Menu(root)
	root.config(menu=main_menu)

	tool_menu = Menu(main_menu)
	command_menu = Menu(main_menu)

	main_menu.add_cascade(label = "Tools", menu= tool_menu)
	tool_menu.add_command(label="Check All", command = check_all)
	tool_menu.add_command(label="Clear All", command = clear_all)
	tool_menu.add_command(label="List Design Master Record", command = list_dmr)
	tool_menu.add_command(label="List Design History File", command = list_dhf)

	main_menu.add_cascade(label = "Commands", menu= command_menu)
	command_menu.add_command(label="Restart", command = lambda: restart_gui(root))
	if (not isDHF):
		command_menu.add_command(label="DHF", command = lambda: dhf_gui(root, inserted, deleted))

	if ((len(inserted) != 0) or (len(deleted) != 0)):

		title_i = Label(root, text=SUMMARY_I, bg=COLOR_1)
		title_i.grid(row = 0,columnspan=C_SPAN)

		fill_popup(inserted, r, g_counter, isDHF, root)

		g_counter = g_counter + len(inserted)

		if (r % C_SPAN != 0):
			r = int(len(inserted) / C_SPAN) + 1 
		else:
			r = len(inserted)/C_SPAN

		title_d = Label(root, text=SUMMARY_D, bg=COLOR_2)
		title_d.grid(row = r+1, columnspan = C_SPAN)

		fill_popup(deleted, r+GAP, g_counter, isDHF, root)

	else:
		s_bar = Scrollbar(root)
		s_bar.pack(side=RIGHT, fill= VERTICAL)

		content = Text(root, yscrollcommand = s_bar.set, spacing1=10)
		content.pack(side=LEFT, fill = Y)

		if (len(dmr_files) > 0):
			set_temp = set(dmr_files)
			content.insert(END, SUMMARY_DMR + content_message(set_temp))
		if (len(dhf_files) > 0):
			set_temp = set(dhf_files)
			content.insert(END, SUMMARY_DHF + content_message(set_temp))
	
		s_bar.config(command=content.yview)

	root.mainloop()

last_file_log = open(PATH_TO_LOG, RW)
create_prev_hist_log(last_file_log)

b_file = open(PATH_TO_BANK, RW)
d_file = open(PATH_TO_DFILE, WRITE)
i_file = open(PATH_TO_IFILE, WRITE)

#obtain all files and sub-directories in current DropBox directory
for root, dirs, files in os.walk(PATH_TO_ALL):	
	for f in files:
		if (not f.startswith(HIDDEN_F)):
			if(parse_dropbox_files(f) != EMPTY_S):
				if ((os.path.getmtime(os.path.join(root,f)) >= VALID_TIME) or (parse_dropbox_files(f) in dh_file_nums)):			
					dbox_file_nums.add(parse_dropbox_files(f))

deleted = dh_file_nums - dbox_file_nums
inserted = dbox_file_nums - dh_file_nums
					
#Case 1:  Most current version has same files as old version(dbox_file_nums.issubset(dh_file_nums) AND dh_file_nums.issubset(dbox_file_nums), no change
if dbox_file_nums.issubset(dh_file_nums) and dh_file_nums.issubset(dbox_file_nums):
	sys.exit(0)
	
#Case 2: Most current version is a strict subset of the old version (dbox_file_nums.issubset(dh_file_nums) = true), deletion
elif dbox_file_nums.issubset(dh_file_nums):

	print(DELETE_MSG + PATH_TO_DFILE)

	for dStr in deleted:
		write_file(d_file, dStr)

#Case 3: Most current version is a strict superset of the old version (dbox_file_nums.issuperset(dh_file_nums) = true), insertion
elif dbox_file_nums.issuperset(dh_file_nums):
	
	print(INSERT_MSG + PATH_TO_IFILE)

	for iStr in inserted:
		inserted_fnames.append(iStr)
		write_file(i_file, iStr)

#Case 4: Some hybrid of insertions and deletions(perform deletions first, then insertions).
else:

	print(DELETE_MSG + PATH_TO_DFILE)
	print(INSERT_MSG + PATH_TO_IFILE)

	for dStr in deleted:
		write_file(d_file, dStr)

	for iStr in inserted:
		inserted_fnames.append(iStr)
		write_file(i_file, iStr)

create_bank(b_file, inserted, deleted)

last_file_log.close()
b_file.close()
d_file.close()
i_file.close()

#notify the user with a popup once per week(crontab runs behind the scenes)
if (len(inserted) > 0 or len(deleted) > 0):
	launch_gui(inserted, deleted, False)