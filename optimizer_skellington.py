def main():
	# find location of all functions and add to list to run propagation and folding in those bounds
	# for each bounds
	# 	loop forever
	# 		result1 = run propagation
	# 		result2 = run folding
	# 		if result1 == no change and result2 == no change
	# 			break
	fname = "ir_example.ir"
	file_text = copy_file(fname)
	outer_bounds = get_bounds_for_functions(fname)
	cp_result = 0
	cf_result = 0

	while (len(outer_bounds) != 0):
		for bound in outer_bounds:
			# for i in range (bound[0], bound[1]):
			cp_result = constant_propagation(file_text[bound[0]:bound[1]])
			if (cp_result[0] == 1):
				file_text[bound[0]:bound[1]] = cp_result[1]

			cf_result = constant_folding(file_text[bound[0]:bound[1]])
			if (cf_result[0] == 1):
				file_text[bound[0]:bound[1]] = cp_result[1]

			if ((cp_result[0] == 0) and (cf_result[0] == 0)):
				outer_bounds.remove(bound)
				print("Removed element "),
				print(bound)
				
			# print(file_text[bound[0]:bound[1]])
			print("\n"),
	print(outer_bounds)

#returns 1 on success and change in input
#returns 0 on failure and no change in input
def constant_propagation(file_text):
	file_text_edit = list(file_text)
	if (file_text == file_text_edit):
		return((0, "file_text_edit"))
	else:
		return((1, file_text_edit))

#returns 1 on success and change in input
#returns 0 on failure and no change in input
def constant_folding(file_text):
	file_text_edit = list(file_text)
	if (file_text == file_text_edit):
		return((0, "file_text_edit"))
	else:
		return((1, file_text_edit))


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
		# print(line_split)
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