#Author: Kegan Wong
#
#Email: kmw037@ucsd.edu
#
#Purpose: Read into a directory that has multiple pdfs, extracts the text in each pdf for key words, 
#		  and uses those key words as a determination to where it is placed in the Design History 
#		  File.
#
#Notice:  Project temporarily halted... Left off after extracting key words, and obtaining all their 
#		  counts from pdfs of different types.	
#
#Future Use: Change the path to whatever directory Drop Box is synced to. If pdf quality varies, 
#			 play with the custom_config, which determines the properties of optical character
#			 recognition. Modifying the image (grayscale, width, etc) or careful scanning of the
#			 document may also help improve accuracy.
#      
#!/Users/k3go/anaconda3/bin/python
from pdf2image import convert_from_path
from unique import inserted_fnames, parse_dropbox_files
from PIL import Image

import pytesseract
import pdfplumber
import cv2
import os

dictionary = {}

REMOVE_CHARS = [".", "?", ",", ":", ";", "_", "(", ")","\""]
FILE_EXTENSIONS = ["pdf", "png"]

TRACK_NUMB = "Scanning page: %d"
TRACK_PAGE = "Extracting contents from %s..."
PATH_TO_ALL = "/Users/k3go/Dropbox (ValenciaT)/Released Documents - PDF/"
PATH_TO_IMG = "/Users/k3go/Desktop/TestImages/"
custom_config = r'--oem 3 --psm 6'
EMPTY = ""

curr_page_num = 0
num_pages = 0
count = 0

def track_page_num(page_num):

	print(TRACK_NUMB % page_num)

def track_page_str(page_str):

	print(TRACK_PAGE % page_str)

def update_dictionary(text):

	for words in text:
		if words not in dictionary.keys():
			dictionary[words] = 1
		else:
			dictionary[words] = dictionary[words] + 1

def file_check(f):

	return not f.startswith(REMOVE_CHARS[0]) and len(parse_dropbox_files(f)) > 0

def clean_str(word):

	if (len(word) > 0):
		word = word.lower()
		for char in REMOVE_CHARS:
			word = word.replace(char, EMPTY)
	return word

for root, dirs, files in os.walk(PATH_TO_ALL):

	for f in files:

		#deals with files that were inserted but not in design history file
		if (file_check(f) and (parse_dropbox_files(f) in inserted_fnames)):	

			if (f.lower().endswith(FILE_EXTENSIONS[0])):
				
				#open the pdf file to extract contents
				with pdfplumber.open(os.path.join(root,f)) as pdf:
			
					track_page_str(f)
					num_pages = len(pdf.pages)

					#loop through the number of pages in the pdf
					while (curr_page_num != num_pages):

						if (curr_page_num < num_pages):

							#extract the text of the current page being read using pdfplumber
							curr_page = pdf.pages[curr_page_num]
							text = curr_page.extract_text()
					
							#non-scanned pdf, extract words and update dictionary
							if type(text) is str:

								text = clean_str(text)
								text = text.split()
								update_dictionary(text)

							#scanned pdf, use optical character recognition to extract words
							else:
								
								#convert all pdf pages into images 
								image = convert_from_path(pdf_path = os.path.join(root,f), output_folder = PATH_TO_IMG, first_page = curr_page_num + 1, last_page = curr_page_num + 1, fmt = FILE_EXTENSIONS[1])

								for root_I, dirs_I, files_I in os.walk(PATH_TO_IMG):

									#loop through all images
									for fi in files_I:
										if (fi.lower().endswith(FILE_EXTENSIONS[1])):

											#extract the text from each image file
											img = cv2.imread(PATH_TO_IMG + fi)
											text = clean_str(pytesseract.image_to_string(img, config=custom_config))
											text = text.split()
											update_dictionary(text)
				
											#remove the image after the contents are extracted							
											try:
												os.remove(os.path.join(root_I, fi))
												

											except OSError as error:
												print(error)

									curr_page_num = curr_page_num + 1
									break
								continue									

						curr_page_num = curr_page_num + 1
						track_page_num(curr_page_num)
						
					#make determination of where the label goes here, and then clear the dictionary

					curr_page_num = 0

print(sorted(dictionary.items(), key = lambda kv: (kv[1], kv[0])))