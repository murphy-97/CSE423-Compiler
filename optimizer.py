# CSE423 Compilers
# backend.py: optimizer systems for C-to-ASM compiler implemented in Python

### Main method for optimizer module
def run_optimizer(code_module):
    # Convert module into lines
    file_text = str(code_module).split('\n')

    # find location of all functions and add to list to run propagation and folding in those bounds
    # for each bounds
    #     loop forever
    #         result1 = run propagation
    #         result2 = run folding
    #         if result1 == no change and result2 == no change
    #             break
    
    outer_bounds = get_bounds_for_functions(file_text)
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

    return file_text

#returns 1 on success and change in input
#returns 0 on failure and no change in input
def constant_propagation(file_text, keywords):
    file_text_edit = list(file_text)
    variable_values = {}

    for i in range(0, len(file_text_edit)):
        file_text_edit[i] = " ".join(file_text_edit[i].split())
        file_text_edit[i] = file_text_edit[i].replace(",", "")

        tmp_list = file_text_edit[i].split(" ")

        if ("store" in tmp_list and tmp_list[2].isdigit()):
            # Place in dictionary for later load commands
            variable_values[tmp_list[4]] = tmp_list[2]
            # Store line no longer needed
            file_text_edit[i] = ""

        elif ("load" in tmp_list and tmp_list[5] in variable_values):
            # Place in dictionary for later substitution
            variable_values[tmp_list[0]] = variable_values[tmp_list[5]]
            # Load line no longer needed
            file_text_edit[i] = ""

        elif (
            len(tmp_list) == 6 and
            tmp_list[1] == "=" and
            not "icmp" in tmp_list
        ):
            # Arithmetic operation - substitute values already found
            if (tmp_list[4] in variable_values):
                tmp_list[4] = variable_values[tmp_list[4]]
                
            if (tmp_list[5] in variable_values):
                tmp_list[5] = variable_values[tmp_list[5]]
                
            file_text_edit[i] = " ".join(tmp_list)

    # Remove empty lines
    file_text_tmp = ""
    in_func = False
    for line in file_text_edit:
        if ('{' in line):
            in_func = True
            file_text_tmp += line + "\n"
        elif ('}' in line):
            in_func = False
            file_text_tmp += line + "\n"
        elif (in_func and line != ""):
            file_text_tmp += "  " + line + "\n"

    file_text_edit = file_text_tmp.split('\n')

    print("Stored Values:")
    print(variable_values)
    if (file_text == file_text_edit):
        return((0, "file_text_edit"))
    else:
        return((1, file_text_edit))

#returns 1 on success and change in input
#returns 0 on failure and no change in input
def constant_folding(file_text, keywords):
    # BEGIN DEBUG CODE - DISABLE CONSTANT FOLDING
    return((0, "file_text_edit"))
    # END DEBUG CODE

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
                tmp_store = (eval(" ".join(tmp_list[2:])))
                tmp_store = str(tmp_store)
                del tmp_list[2:]
                tmp_list.append(tmp_store)

        file_text_edit[i] = " ".join(tmp_list)

                # print("Propagated")
        # print(" ".join(tmp_list))

    if (file_text == file_text_edit):
        return((0, "file_text_edit"))
    else:
        return((1, file_text_edit))

def get_bounds_for_functions(ir_lines):
    function_locs = []
    i = 0
    first_flag = 0
    for line in ir_lines:
        line_split = line.split(" ")
        if (line_split[0] == "define"):
            if (first_flag != 0):
                function_locs.append(i-1)
            function_locs.append(i)
            first_flag = 1
        i += 1
    function_locs.append(i)

    output_list = []
    for i in range (0, len(function_locs), 2):
        tmp_list = [function_locs[i], function_locs[i+1]]
        output_list.append(tmp_list)
    return (output_list)

if __name__ == '__main__':
    main()
