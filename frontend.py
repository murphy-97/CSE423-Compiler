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
	replace_space_array = ["#", ";", "(", ")", "{", "}", "=", "<", ">", "+", "-"]
	# replace_array = ["\n"] # Unused variable. Commented out
	tokens_descriptive = []

	#create string of input code
	for line in input:
		entire_doc = entire_doc + line

	#remove comments
	entire_doc = re.sub(re.compile("//.*?\n"), "\n", entire_doc)
	entire_doc = re.sub(re.compile("/\*.*?\*/"), "", entire_doc)

	#remove the non-allowed character $
	entire_doc = entire_doc.replace("$", "")

	#find, store and replace all strings "" from program
	#to be replaced later
	strings_array = re.findall(r'".*?"', entire_doc)
	for string in strings_array:
		entire_doc = entire_doc.replace(string, "$string$", 1)

	entire_doc = entire_doc.replace("++", "$plus$")
	entire_doc = entire_doc.replace("--", "$minus$")
	entire_doc = entire_doc.replace("==", "$equals$")
	entire_doc = entire_doc.replace("<<", "$left$")
	entire_doc = entire_doc.replace(">>", "$right$")

	#add spaces arround all individual tokens for formating
	for value in replace_space_array:
		entire_doc = entire_doc.replace(value, " "+value+" ")

	#remove extra characters
	entire_doc = ' '.join(entire_doc.split())
	#add back in double operands
	entire_doc = entire_doc.replace("$plus$", " ++ ")
	entire_doc = entire_doc.replace("$minus$", " -- ")
	entire_doc = entire_doc.replace("$equals$", " == ")
	entire_doc = entire_doc.replace("$left$", " << ")
	entire_doc = entire_doc.replace("$right$", " >> ")
	
	#remove extra spaces
	entire_doc = ' '.join(entire_doc.split())

	#split document into tokens
	entire_doc = entire_doc.replace(" ", "$replace$")
	tokens_base = entire_doc.split("$replace$")

	#place all unedited strings back into program
	for i in range (1, len(tokens_base)):
		if (tokens_base[i] == "$string$"):
			tokens_base[i] = strings_array.pop(0)

	#categorize all tokens
	for token in tokens_base:
		try:
			# Token is an int
			int(token)
			tokens_descriptive.append([token, "intConst"])
			continue
		except:
			# Token is not an int
			try:
				# Token is a float
				float(token)
				tokens_descriptive.append([token, "floatConst"])
				continue
			except:
				# Token is neither an int nor a float
				pass
				
		if (token in ["not", "and", "or"]):
			tokens_descriptive.append([token, "bool"])
		elif ("<" in token or ">" in token or "!" in token):
			tokens_descriptive.append([token, "comparison"])
		elif ("==" in token):
			tokens_descriptive.append([token, "comparison"])
		elif (token == "="):
			tokens_descriptive.append([token, "assignment"])
		elif (token in [
			"auto", "break", "else", "long", "switch", "case", "register",
			"typedef", "extern", "return", "union", "continue", "for", "signed",
			"do", "if", "static", "while", "default", "goto", "sizeof",
			"volatile", "const", "unsigned"
		]):
			tokens_descriptive.append([token, "keyword"])
		elif (token in [
			"double", "int", "struct", "long", "enum", "char", "void", "float",
			"float", "short"
		]):
			tokens_descriptive.append([token, "typeKeyword"])
		elif (re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", token)):
			# For some reason this isn't catching anything....
			tokens_descriptive.append([token, "identifier"])
		else:
			tokens_descriptive.append([token, "string"])

	# NOTE: In the future, when detecting an unrecongized token, raise an error
	# raise Exception(error.ERR_BAD_TOKEN + " '" + token + "'")

	return tokens_descriptive

### Parser for compiler frontend
def run_parser(code_lines):
    """Parses tokens using language grammar"""
    # TO DO: Implement parser
    return code_lines
