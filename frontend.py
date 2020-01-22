# CSE423 Compilers
# backend.py: frontend systems for C-to-ASM compiler implemented in Python

from enum import Enum

class ERROR(Enum):
	NUMARGS = 1
	UNRECOVERABLE = 2

### Main method for frontend module
def run_frontend(code_lines):
    """Takes a list of code lines and returns a list of processed code lines"""
    code_lines = run_scanner(code_lines) #takes in a file name, returns a list of tokens
    code_lines = run_parser(code_lines)
    return code_lines

### Scanner/tokenizer for compiler frontend
def run_scanner(code_lines):
    """Reads source code and returns list of tokens"""
    # TO DO: Implement scanner
	if (len(sys.argv) == 1):
		error(ERROR['NUMARGS'])

	input = open(sys.argv[1], 'r')
	entire_doc = ""
	replace_space_array = ["#", ";", "(", ")", "{", "}", "=", "==", "<", ">"]
	replace_array = ["\n"]
	tokens_descriptive = []

	for line in input:
		entire_doc = entire_doc + line
	for value in replace_space_array:
		entire_doc = entire_doc.replace(value, " "+value+" ")
	entire_doc = ' '.join(entire_doc.split())
	entire_doc = entire_doc.replace(" ", "$replace$")
	tokens_base = entire_doc.split("$replace$")
	for token in tokens_base:
		if (token.isnumeric()):
			tokens_descriptive.append([token, "int"])
		elif (token == "not" or token == "and" or token == "or"):
			tokens_descriptive.append([token, "bool"])
		elif ("<" in token or ">" in token or "!" in token):
			tokens_descriptive.append([token, "equal types"])
		elif ("==" in token):
			tokens_descriptive.append([token, "equal types"])
		else:
			tokens_descriptive.append([token, "string"])
    return tokens_descriptive

### Parser for compiler frontend
def run_parser(code_lines):
    """Parses tokens using language grammar"""
    # TO DO: Implement parser
    return code_lines

import sys
from enum import Enum

class ERROR(Enum):
	NUMARGS = 1

def error(input):
	if (input == ERROR['NUMARGS']):
		print("Incorrect number of command line arguments")
		exit(1)
