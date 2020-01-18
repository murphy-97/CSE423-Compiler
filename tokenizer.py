import sys
from enum import Enum

class ERROR(Enum):
	NUMARGS = 1

def main():
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
 

	for token in tokens_descriptive:
		print(token)

def error(input):
	if (input == ERROR['NUMARGS']):
		print("Incorrect number of command line arguments")
		exit(1)

if __name__ == '__main__':
	main()