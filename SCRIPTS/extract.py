from pdf2image import convert_from_path
from unique import inserted_fnames
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
PATH_TO_ALL = "/Users/k3go/Dropbox (ValenciaT)/Released Documents - PDF"
PATH_TO_IMG = "/Users/k3go/Desktop/TestImages/"
custom_config = r'--oem 3 --psm 6'
EMPTY = ""

curr_page_num = 0
num_pages = 0

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

def clean_str(word):

	if (len(word) > 0):
		word = word.lower()
		for char in REMOVE_CHARS:
			word = word.replace(char, EMPTY)
	return word

for root, dirs, files in os.walk(PATH_TO_ALL):

	for f in files:

		if (f in inserted_fnames):		

			if (f.lower().endswith(FILE_EXTENSIONS[0])):
		
				with pdfplumber.open(PATH_TO_ALL + f) as pdf:
			
					track_page_str(f)
					num_pages = len(pdf.pages)

					while (curr_page_num != num_pages):

						if (curr_page_num < num_pages):

							curr_page = pdf.pages[curr_page_num]
							text = curr_page.extract_text()
					
							if type(text) is str:

								text = clean_str(text)
								text = text.split()

								update_dictionary(text)

							#place check for where labels go here, then clear dictionary						

							else:
				
								image = convert_from_path(pdf_path = PATH_TO_ALL + f, output_folder = PATH_TO_IMG, fmt = FILE_EXTENSIONS[1])

								for rootI, dirsI, filesI in os.walk(PATH_TO_IMG):
									for f in filesI:
										if (f.lower().endswith(FILE_EXTENSIONS[1])):

											img = cv2.imread(PATH_TO_IMG + f)
											text = clean_str(pytesseract.image_to_string(img, config=custom_config))
											text = text.split()
											update_dictionary(text)									

								break

						track_page_num(curr_page_num + 1)
						curr_page_num = curr_page_num + 1

					curr_page_num = 0

	#print(sorted(dictionary.items(), key = lambda kv: (kv[1], kv[0])))
