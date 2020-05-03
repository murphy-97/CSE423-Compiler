# CSE423 Compilers
# backend.py: optimizer systems for C-to-ASM compiler implemented in Python

import utility_funcs as uf

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

    # Remove unsused stores (initial call)
    file_text = rem_extra_stores(file_text)
    # Remove unused load statements
    file_text = rem_extra_loads(file_text)
    # Remove unused store statements (must be repeated after load)
    file_text = rem_extra_stores(file_text)

    # CLEAN-UP: Remove blank lines and indent instructions that occur within functions
    in_func = False
    file_text_out = []
    for line in file_text:
        if (not in_func and '{' in line):
            in_func = True
            file_text_out.append(line)

        elif (in_func and '}' in line):
            in_func = False
            file_text_out.append(line)

        elif (in_func and len(line) > 0 and line[-1] != ':'):
            file_text_out.append("  " + line)

        elif (not in_func or (len(line) > 0 and line[-1] == ':')):
            file_text_out.append(line)

    return file_text_out

#returns 1 on success and change in input
#returns 0 on failure and no change in input
def constant_propagation(file_text, keywords):
    file_text_edit = list(file_text)
    variable_values = {}

    for i in range(0, len(file_text_edit)):
        file_text_edit[i] = " ".join(file_text_edit[i].split())
        file_text_edit[i] = file_text_edit[i].replace("(", " ")
        file_text_edit[i] = file_text_edit[i].replace(")", " ")
        file_text_edit[i] = file_text_edit[i].replace(",", " ")

        tmp_list = file_text_edit[i].strip().split(" ")

        if ("store" in tmp_list and uf.IsInt(tmp_list[2])):
            # Place in dictionary for later load commands
            variable_values[tmp_list[4]] = tmp_list[2]

        elif ("load" in tmp_list and tmp_list[5] in variable_values):
            # Place in dictionary for later substitution
            variable_values[tmp_list[0]] = variable_values[tmp_list[5]]

        elif ("call" in tmp_list):
            # Check function parameters for substitution
            for j in range(6, len(tmp_list), 2):
                if (tmp_list[j] in variable_values):
                    tmp_list[j] = variable_values[tmp_list[j]]
                
            file_text_edit[i] = " ".join(tmp_list)

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

        elif ("icmp" in tmp_list):
            # Comparison operation - substitute values already found
            if (tmp_list[5] in variable_values):
                tmp_list[5] = variable_values[tmp_list[5]]
                
            if (tmp_list[6] in variable_values):
                tmp_list[6] = variable_values[tmp_list[6]]
                
            file_text_edit[i] = " ".join(tmp_list)

        elif ("ret" in tmp_list):
            # Return statement - substitute values already found
            if (tmp_list[2] in variable_values):
                tmp_list[2] = variable_values[tmp_list[2]]
                
            file_text_edit[i] = " ".join(tmp_list)


    if (file_text == file_text_edit):
        return((0, "file_text_edit"))
    else:
        return((1, file_text_edit))

#returns 1 on success and change in input
#returns 0 on failure and no change in input
def constant_folding(file_text, keywords):
    file_text_edit = list(file_text)
    variable_values = {}

    # NOTE: LLVM IR does not support direct declaration of variables
    # Constant folding requires some level of constant propogation

    for i in range(0, len(file_text_edit)):
        file_text_edit[i] = " ".join(file_text_edit[i].split())
        file_text_edit[i] = file_text_edit[i].replace(",", "")

        tmp_list = file_text_edit[i].split(" ")

        # Perform substitutions on this line (technically constant propogation)
        for j in range(1, len(tmp_list)):
            if (tmp_list[j] in variable_values):
                #print("Replacing " + tmp_list[j] + " with " + variable_values[tmp_list[j]])
                tmp_list[j] = variable_values[tmp_list[j]]
        file_text_edit[i] = " ".join(tmp_list)

        # Perform folding on this line
        if (
            len(tmp_list) == 6 and
            tmp_list[1] == "=" and
            uf.IsInt(tmp_list[4]) and
            uf.IsInt(tmp_list[5]) and
            not "icmp" in tmp_list
        ):
            # Arithmetic operation of constants
            a = int(tmp_list[4])
            b = int(tmp_list[5])

            if (tmp_list[2] == "fadd"):
                c = a + b
            elif (tmp_list[2] == "fsub"):
                c = a - b
            elif (tmp_list[2] == "fmul"):
                c = a * b
            elif (tmp_list[2] == "fdiv"):
                c = a // b  # // is integer division
            elif (tmp_list[2] == "frem"):
                c = a % b
            elif (tmp_list[2] == "shl"):
                c = a << b
            elif (tmp_list[2] == "ashr"):
                c = a >> b

            # Store folded value in dictionary
            variable_values[tmp_list[0]] = str(c)
            # Remove unneeded line
            file_text_edit[i] = ""

        elif (
            "icmp" in tmp_list and
            uf.IsInt(tmp_list[5]) and
            uf.IsInt(tmp_list[6])
        ):
            # Comparison operation of constants
            a = int(tmp_list[5])
            b = int(tmp_list[6])

            if (tmp_list[3] == "sgt"):
                cond = (a > b)
            elif (tmp_list[3] == "slt"):
                cond = (a < b)
            elif (tmp_list[3] == "sge"):
                cond = (a >= b)
            elif (tmp_list[3] == "sle"):
                cond = (a <= b)
            elif (tmp_list[3] == "eq"):
                cond = (a == b)
            elif (tmp_list[3] == "ne"):
                cond = (a != b)
            
            c = 1 if (cond) else 0

            # Store folded value in dictionary
            variable_values[tmp_list[0]] = str(c)
            # Remove unneeded line
            file_text_edit[i] = ""

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
    
def rem_extra_stores(ir_lines):
    # A store is extra if its value is never loaded
    for i in range(0, len(ir_lines)):
        i_split = ir_lines[i].split()

        if ("store" in i_split):
            value_used = False

            for j in range(i+1, len(ir_lines)):
                j_split = ir_lines[j].split()
                if ("load" in j_split and i_split[4] == j_split[5]):
                    # This stored value is loaded
                    value_used = True
                    break
                elif ("ret" in j_split and i_split[4] == j_split[2]):
                    # Value is used by a return statement
                    value_used = True
                    break
                elif ("store" in j_split and i_split[4] == j_split[4]):
                    # A new value is stored before the old value is loaded
                    break

            # If the value was not used, then remove the line
            if (not value_used):
                ir_lines[i] = ""

    return ir_lines

def rem_extra_loads(ir_lines):
    # A load is extra if the loaded value is never used
    for i in range(0, len(ir_lines)):
        i_split = ir_lines[i].split()

        if ("load" in i_split):
            value_used = False

            for j in range(i+1, len(ir_lines)):
                j_split = ir_lines[j].split()

                # Check all terms EXCEPT the one being assigned
                for k in range(j+1, len(j_split)):
                    if (j_split[k] == i_split[0]):
                        value_used = True
                        break

            # If the value was not used, then remove the line
            if (not value_used):
                ir_lines[i] = ""

    return ir_lines
