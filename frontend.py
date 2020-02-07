# CSE423 Compilers
# backend.py: frontend systems for C-to-ASM compiler implemented in Python

# Import non-project modules
import re
from treelib import Node, Tree
import sys
from collections import OrderedDict
# Import project modules
import errors


### Main method for frontend module
def run_frontend(code_lines, print_scn, print_prs):
	"""Takes a list of code lines and returns a list of processed code lines"""
	tokens = run_scanner(code_lines)

	# Command line option to print scanner output
	if (print_scn):
		print("\n====== SCANNER OUTPUT ======")
	for line in code_lines:
		print(str(line))

	grammar = parse_grammar(open('grammar.txt', "r"))
	ast = run_parser(tokens, grammar)
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
	replace_space_array = [";", "(", ")", "{", "}", "=", "<", ">", "+", "-", ","]
	single_tokens = ["(", ")", "{", "}", ",", ";", "=", "++", "--", "+=", "-=", "*=", "/=", "true", "false"]

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
	entire_doc = entire_doc.replace("+=", "$plus_equals$")
	entire_doc = entire_doc.replace("!=", "$not_equals$")
	entire_doc = entire_doc.replace("-=", "$minus_equals$")
	entire_doc = entire_doc.replace("*=", "$mult_equals$")
	entire_doc = entire_doc.replace("/=", "$divide_equals$")
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
	entire_doc = entire_doc.replace("$plus_equals$", " += ")
	entire_doc = entire_doc.replace("$not_equals$", " != ")
	entire_doc = entire_doc.replace("$minus_equals$", " -= ")
	entire_doc = entire_doc.replace("$mult_equals$", " *= ")
	entire_doc = entire_doc.replace("$divide_equals$", " /= ")
	entire_doc = entire_doc.replace("$equals$", " == ")
	entire_doc = entire_doc.replace("$left$", " << ")
	entire_doc = entire_doc.replace("$right$", " >> ")
	
	#remove extra spaces
	entire_doc = ' '.join(entire_doc.split())

	#split document into tokens
	entire_doc = entire_doc.replace(" ", "$replace$")
	tokens_base = entire_doc.split("$replace$")

	#categorize all tokens
	for token in tokens_base:

		try:
			# Token is an int
			int(token)
			tokens_descriptive.append([token, "NUMCONST"])
			continue
		except:
			# Token is not an int
			try:
				# Token is a float
				float(token)
				tokens_descriptive.append([token, "FLOATCONST"])
				continue
			except:
				# Token is neither an int nor a float
				pass
				
		if (token in ["+", "-"]): #
			tokens_descriptive.append([token, "sumop"])
		elif (token in ["&&"]): #
			tokens_descriptive.append([token, "&&"])
		elif (token in ["||"]): #
			tokens_descriptive.append([token, "||"])
		elif (token in ["!"]): #
			tokens_descriptive.append([token, "!"])
		elif (token in ["-", "*", "?"]): #
			tokens_descriptive.append([token, "unaryop"])
		elif (token in ["*", "/", "%"]): #
			tokens_descriptive.append([token, "mulop"])
		elif (token in ["<=", "<", ">", ">=", "==", "!="]): #
			tokens_descriptive.append([token, "relop"])
		elif (token in ["return"]): #
			tokens_descriptive.append([token, "return"])
		elif (token in single_tokens): #
			tokens_descriptive.append([token, token])

		elif (token in [
			"auto", "break", "else", "long", "switch", "case", "register",
			"typedef", "extern", "union", "continue", "for", "signed",
			"do", "if", "static", "while", "default", "goto", "sizeof",
			"volatile", "const", "unsigned"
		]):
			tokens_descriptive.append([token, "keyword"])
		elif (token in ["#include", "#define"]):
			tokens_descriptive.append([token, "preDirective"])
		elif (token in [
			"double", "int", "struct", "long", "enum", "char", "void", "float",
			"float", "short"
		]):
			tokens_descriptive.append([token, "typeSpecifier"])
		elif (re.match(r"([a-zA-Z0-9\s_\\.\-\(\):])+(.h)$", token)):
			# For some reason this isn't catching anything....
			tokens_descriptive.append([token, "fileImport"])
		elif (re.match(r"^[a-zA-z_][a-zA-Z0-9_]*$", token)):
			tokens_descriptive.append([token, "ID"])
		elif (token == "$string$"):
			token = strings_array.pop(0)
			tokens_descriptive.append([token, "STRINGCONST"])
		else:
			raise Exception(errors.ERR_BAD_TOKEN + " '" + token + "'")
			# tokens_descriptive.append([token, "UNRECOGNIZED"])

	# for token in tokens_descriptive:
	# 	print(token)
	return tokens_descriptive

### Parser for compiler frontend
def run_parser(tokens, grammar):
	output = ""
	cond_pass = 0
	cur_token = "program"
	cur_node = "program"
	stack = []
	list_of_tokens = []

	tree = Tree()
	#create root node
	tree.create_node(cur_token, cur_token)  # root node
	# tree.create_node("Jane", "jane", parent="harry")
	# tree.create_node("Bill", "bill", parent="harry")
	# tree.create_node("Diane", "diane", parent="jane")
	# tree.create_node("Mary", "mary", parent="diane")
	# tree.create_node("Mark", "mark", parent="jane")
	# tree.show()

	for j in range(0, len(tokens)):
		if (tokens[j][0] == "main"):
			j = j - 1
			break

	i = 0
	for i in range (j, len(tokens)):
		list_of_tokens.append(tokens[i])
		result = check_rules(cur_node, list_of_tokens, grammar)
		if (result[0] > 1):
			continue
		elif (result[0] == 1):
			#special cases for rules that include blocks and parenthesies?
			if (result[1][0] == "funDeclaration"):
				k = 0
				# while (tokens[i] != ")"):

				list_of_tokens.pop()
				list_of_tokens.pop()
				list_of_tokens.pop()
			continue
			#push onto tree
			#pop stuff pushed
		elif(result[0] == 0):
			#reject
			exit(1)
			

	#Parses tokens using language grammar
	# TO DO: Implement parser
	return output

#checks if the current token should result in:
#rejection, (0 matches)
#possible acceptance, (>=1 match)
#accept, (1 match and complete rule)
def check_rules(cur_node, tokens, grammar):
	# print(tokens)
	# print(grammar["funDeclaration"])
	stack_possible_matches = []
	stack_actual_matches = []
	stack = []

	for elem in grammar:
		for rule in grammar[elem]:
			if (rule[:len(tokens)] == get_some_elems_of_list(tokens, 1)):
				if elem not in stack_possible_matches:
					stack_possible_matches.append(elem)
				# print(tokens)
	
	tmp_rules = grammar[cur_node]
	for elem in stack_possible_matches:
		# if that rule can appear after cur_node
		if (is_possible_rule(cur_node, elem, grammar)):
			stack_actual_matches.append(elem)

	if (len(stack_actual_matches) == 1):
		print(stack_actual_matches)
		print("accept this line")
		print("fix handeling of blocks and things in parenthesies. That is why nothing is accepted after a funDeclaration")
	return ((len(stack_actual_matches), stack_actual_matches))

#checks if the current token is allwed after the previous token
def is_possible_rule(cur_node, match, grammar):
	stack = []
	tmp_rules = grammar[cur_node]
	for elem in tmp_rules:
		stack.append(elem)
	while (len(stack) != 0):
		elem = stack.pop()
		index = get_index_in_dict(grammar, elem)
		i = 0
		for key, value in grammar.items():
			if (i == index):
				break
			for rule in value:
				# print(elem)
				if (rule == elem):
					stack.append(key)
					return 1
			i = i + 1

#gets index of key in a ordered dictionary
def get_index_in_dict(grammar, match):
	i = 0
	for key, value in grammar.items():
		if (key == match):
			return i
		i = i + 1

#gets elements of list of lists by shared index
def get_some_elems_of_list(input, n):
	return [item[n] for item in input]

#parses a input grammar file and outputs
#a properly formated dictionary
def parse_grammar(grammar_file):
	grammar = OrderedDict()
	for line in grammar_file:
		line = line.replace("\n", "")
		tmp_list = line.split("~")
		values = tmp_list[1]
		values = ' '.join(values.split())
		values = values.split("|")
		for i in range(0, len(values)):
			values[i] = ' '.join(values[i].split())
			values[i] = values[i].split(" ")
			values[i] = [j for j in values[i] if j]
		grammar[' '.join(tmp_list[0].split())] = values
	return(grammar)

if __name__ == '__main__':
	if (len(sys.argv) < 2):
		print("No input file")
		exit(1)

	input_file = open(sys.argv[1], "r")
	run_frontend(input_file, 0, 0)
