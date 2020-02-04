# CSE423 Compilers
# backend.py: frontend systems for C-to-ASM compiler implemented in Python

import re

### Main method for frontend module
def run_frontend(code_lines, print_scn, print_prs):
    """Takes a list of code lines and returns a list of processed code lines"""
    code_lines = run_scanner(code_lines)

	# Command line option to print scanner output
    if (print_scn):
        print("\n====== SCANNER OUTPUT ======")
        for line in code_lines:
            print(str(line))

    code_lines = run_parser(code_lines)
	# Command line option to print parser output
    if (print_prs):
        print("\n====== PARSER OUTPUT ======")
        for line in code_lines:
            print(str(line))

    return code_lines

### Scanner/tokenizer for compiler frontend
def run_scanner(code_lines):
	"""Reads source code and returns list of tokens"""
	input = code_lines
	entire_doc = ""
	replace_space_array = ["#", ";", "(", ")", "{", "}", "=", "==", "<", ">"]
	# replace_array = ["\n"] # Unused variable. Commented out
	tokens_descriptive = []

	#create string of input code
	for line in input:
		entire_doc = entire_doc + line

	#remove comments
	entire_doc = re.sub(re.compile("//.*?\n"), "\n", entire_doc)
	entire_doc = re.sub(re.compile("/\*.*?\*/"), "", entire_doc)

	entire_doc = entire_doc.replace("$", "")

	strings_array = re.findall(r'".*?"', entire_doc)
	for string in strings_array:
		entire_doc = entire_doc.replace(string, "$", 1)

	for value in replace_space_array:
		entire_doc = entire_doc.replace(value, " "+value+" ")

	entire_doc = ' '.join(entire_doc.split())
	entire_doc = entire_doc.replace(" ", "$replace$")
	tokens_base = entire_doc.split("$replace$")


	for i in range (1, len(tokens_base)):
		if (tokens_base[i] == "$"):
			tokens_base[i] = strings_array.pop(0)

	for token in tokens_base:
		try:
			# Token is an int
			int(token)
			tokens_descriptive.append([token, "int"])
			continue
		except:
			# Token is not an int
			try:
				# Token is a float
				float(token)
				tokens_descriptive.append([token, "float"])
				continue
			except:
				# Token is neither an int nor a float
				pass
				
		if (token == "not" or token == "and" or token == "or"):
			tokens_descriptive.append([token, "bool"])
		elif ("<" in token or ">" in token or "!" in token):
			tokens_descriptive.append([token, "equal types"])
		elif ("==" in token):
			tokens_descriptive.append([token, "equal types"])
		else:
			tokens_descriptive.append([token, "string"])

	# NOTE: In the future, when detecting an unrecongized token, raise an error
	# raise Exception(error.ERR_BAD_TOKEN + " '" + token + "'")

	#for token in tokens_descriptive:
	#	print(token)
	 return tokens_descriptive

### Parser for compiler frontend
def run_parser(code_lines):
    """Parses tokens using language grammar"""
    # TO DO: Implement parser
    return code_lines
