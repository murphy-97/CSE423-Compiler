def main():
	# find location of all functions and add to list to run propagation and folding in those bounds
	# for each bounds
	# 	loop forever
	# 		result1 = run propagation
	# 		result2 = run folding
	# 		if result1 == no change and result2 == no change
	# 			break
	print("Hannah, we need to take into account when the leading value might be a keyword rather than a varaible")
	print("Hannah, make sure that every token is seperated by spaces in the created ir\n\n")
	fname = "ir_example.ir"
	file_text = copy_file(fname)
	outer_bounds = get_bounds_for_functions(fname)
	cp_result = 0
	cf_result = 0
	keywords = []

	while (len(outer_bounds) != 0):
		for bound in outer_bounds:
			# for i in range (bound[0], bound[1]):
			cp_result = constant_propagation(file_text[bound[0]:bound[1]], keywords)
			if (cp_result[0] == 1):
				# print("edited from cp")
				file_text[bound[0]:bound[1]] = cp_result[1]

			cf_result = constant_folding(file_text[bound[0]:bound[1]], keywords)
			if (cf_result[0] == 1):
				# print("edited from cf")
				file_text[bound[0]:bound[1]] = cf_result[1]

			if ((cp_result[0] == 0) and (cf_result[0] == 0)):
				outer_bounds.remove(bound)
				# print("Removed element "),
				# print(bound)

			# print(file_text[bound[0]:bound[1]])
			# print("\n"),

	for elem in file_text:
		print(elem)
	# print(outer_bounds)

#returns 1 on success and change in input
#returns 0 on failure and no change in input
def constant_propagation(file_text, keywords):
	file_text_edit = list(file_text)
	variable_values = {}
	for i in range(0, len(file_text_edit)):
		file_text_edit[i] = " ".join(file_text_edit[i].split())

		tmp_list = file_text_edit[i].split(" ")
		#add and remove from dictionary
		if (("=" in tmp_list)):
			if ((len(tmp_list) == 3) and tmp_list[2].isdigit()):
				variable_values[tmp_list[0]] = tmp_list[2]
				# print("Added value to dictionary")
			else:
				if (check_key(variable_values, tmp_list[0])):
					del variable_values[tmp_list[0]]
					# print("removed value: "),
					# print(tmp_list[0])
		#propagate
		for j in range (1, len(tmp_list)):
			if (tmp_list[j] in keywords):
				continue
			if (check_key(variable_values, tmp_list[j])):
				tmp_list[j] = variable_values[tmp_list[j]]
				# print("Propagated")
		file_text_edit[i] = list_to_string(tmp_list)

		# print(file_text_edit[i])

	if (file_text == file_text_edit):
		return((0, "file_text_edit"))
	else:
		return((1, file_text_edit))

def list_to_string(str_inp):
	string = " "
	return (string.join(str_inp))

#returns 1 on success and change in input
#returns 0 on failure and no change in input
def constant_folding(file_text, keywords):
	file_text_edit = list(file_text)
	operators = ["+", "-", "*", "/", "%"]
	skip_flag = 0
	for i in range(0, len(file_text_edit)):
		file_text_edit[i] = " ".join(file_text_edit[i].split())

		tmp_list = file_text_edit[i].split(" ")
		#add and remove from dictionary
		if (("=" in tmp_list) and (len(tmp_list) > 3)):
			skip_flag = 0
			for j in range (2, len(tmp_list)):
				if ((tmp_list[j] in operators) or (tmp_list[j].isdigit())):
					pass
				else:
					skip_flag = 1
			#evaluate and fold
			if (skip_flag == 0):
				tmp_store = (eval(list_to_string(tmp_list[2:])))
				tmp_store = str(tmp_store)
				del tmp_list[2:]
				tmp_list.append(tmp_store)

		file_text_edit[i] = list_to_string(tmp_list)

				# print("Propagated")
		# print(list_to_string(tmp_list))

	if (file_text == file_text_edit):
		return((0, "file_text_edit"))
	else:
		return((1, file_text_edit))

def check_key(dict, key):
	if (key in dict.keys()):
		return True
	else:
		return False

def copy_file(fname):
	output_list = []
	open_file = open(fname, "r")
	for line in open_file:
		output_list.append(line)
	return(output_list)

def get_bounds_for_functions(fname):
	input_file = open(fname, "r")
 	function_locs = []
 	i = 0
 	first_flag = 0
	for line in input_file:
		line_split = line.split(" ")
		if (line_split[0] == "function"):
			if (first_flag != 0):
				function_locs.append(i-1)
			function_locs.append(i)
			first_flag = 1
		i += 1
	function_locs.append(i)
	input_file.close()

	output_list = []
	for i in range (0, len(function_locs), 2):
		tmp_list = [function_locs[i], function_locs[i+1]]
		output_list.append(tmp_list)
	return (output_list)

if __name__ == '__main__':
	main()
