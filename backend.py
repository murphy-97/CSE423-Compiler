# CSE423 Compilers
# backend.py: backend systems for C-to-ASM compiler implemented in Python

### Main method for backend module
def run_backend(code_lines):
    """Takes a list of code lines and returns a list of processed code lines"""
    # TO DO: Implement backend
    print("\nBuilding ASM...")

    #bein line number function
    fun_body_lines = []
    def_lines = []
    tmp_arr = []
    ir = str(code_lines)
    ir_split = ir.split("\n")
    tmp = define_bounds(ir)
    def_lines = tmp[0]
    fun_body_lines = tmp[1]
    output_code = []

    print(code_lines)

    # print("BODY LINES")
    # print(fun_body_lines)
    # print("DEFINE LINES")
    # print(def_lines)

    for i in range (0, len(fun_body_lines)):
        tmp_def_line = ir_split[def_lines[i]]
        fun_name = get_fun_name(tmp_def_line) #is a string
        fun_parameters = get_fun_parameters(tmp_def_line) #is a list
        fun_code = get_fun_code(ir_split, fun_body_lines[i], fun_name, fun_parameters) #is a list
        # print("\n")
        # print("name:", fun_name)
        # print("parmaters:", fun_parameters)
        for line in fun_code:
            output_code.append(line)
        # print("code:", fun_code)
        # print(tmp_def_line, "\n")
    output_code.insert(0, "\t.section\t__TEXT,__text,regular,pure_instructions")
    
    # for line in output_code:
    #     print(line)

    return "\n".join(output_code)


def get_fun_code(ir_split, indexs, fun_name, fun_parameters):
    raw_code = ir_split[indexs[0]:indexs[1]]
    return fix_raw_code(raw_code, indexs, fun_name, fun_parameters)

def fix_raw_code(raw_code, indexs, fun_name, fun_parameters):
    new_code = raw_code
    output_code = []

    for i in range(1, len(new_code)):
        new_code[i] = " ".join(new_code[i].split())
        new_code[i] = "\t" + new_code[i]
    output_code.append("\t.globl  "+"_" + fun_name+"\t\t\t\t\t## -- Begin function "+fun_name)
    output_code.append("\t.p2align\t4, 0x90")
    output_code.append("_" + fun_name + ":" + "\t\t\t\t\t## @" + fun_name)
    output_code.append("## %bb.0:")
    output_code.append("\tpushq\t%rbp")
    output_code.append("\tmoveq\t%rsp, %rbp")

    passed_offset = 0
    local_offset = 0

    id_variables = id_params(fun_parameters, output_code)
    # print("HERE ID VAR: ", id_variables)
    id_value = -4 - (4 * len(id_variables))

    found_return_flag = 0

    #identify case for each line in the function and change it to assembly via helper fuctions
    #helper functions return arrays of created lines
    #loop though lines appending them to output_code
    print("\n\CODE FOR FUNCTION")
    for i in range(1, len(raw_code)):
        if ("fadd" in raw_code[i]):
            # print("fadd:", i)
            id_value = fgrab_params(raw_code[i], id_variables, id_value, output_code)
            #now call function to check if variable being assigned to has negative value in id_variables
            #if so, then push it onto the stack with its value
            #replace references to other values with appropiate values based on value in id_variables
            #return list of strings to be appended
            # print("Id Variables: ", id_variables)
            # print("Line of code: ", raw_code[i])

        elif ("fsub" in raw_code[i]):
            # print("fsub:", i)
            found_return_flag = 0
            id_value = fgrab_params(raw_code[i], id_variables, id_value, output_code)

        elif ("fmul" in raw_code[i]):
            # print("fmul:", i)
            found_return_flag = 0
            id_value = fgrab_params(raw_code[i], id_variables, id_value, output_code)

        elif ("fdiv" in raw_code[i]):
            # print("fdiv:", i)
            found_return_flag = 0
            id_value = fgrab_params(raw_code[i], id_variables, id_value, output_code)

        elif ("frem" in raw_code[i]):
            # print("frem:", i)
            found_return_flag = 0
            id_value = fgrab_params(raw_code[i], id_variables, id_value, output_code)

        elif ("store" in raw_code[i]):
            # print("store:", i)
            found_return_flag = 0
            id_value = sgrab_params(raw_code[i], id_variables, id_value, output_code)
            # print("Id Variables: ", id_variables)
            # print("Line of code: ", raw_code[i])

        elif ("ret" in raw_code[i]):
            # print("ret:", i)
            found_return_flag = 1
            fparams = rgrab_params(raw_code[i], id_variables, id_value, output_code)
        else:
            print("Error: command found in ir with unknown command")
            print(raw_code[i])
            exit(1)

    #call function to do rest

    if (found_return_flag == 0):
        output_code.append("\tpopq\t%rbp")
        output_code.append("\tretq")
    output_code.append("\t\t\t\t\t\t\t\t\t\t## -- End function")
    # new_code.insert(0, "\n.p2align")
    return output_code

def id_params(fun_parameters, output_code):
    output = {}
    mapping = ["%edi", "%esi", "%edx", "%ecx", "%r8d", "%r9d"]
    mapping_elem = 0

    i = -4
    for j in range(len(fun_parameters)-1, -1, -1):
        output[fun_parameters[j]] = i
        i -= 4
    i = -4

    for elem in fun_parameters:
        if (mapping_elem < 6):
            output_code.append("\tmovl\t" + mapping[mapping_elem] + ", "+ str(i) + "(%rbp)")
            mapping_elem += 1
        i -= 4

    return output


def fgrab_params(code_line, id_variables, id_value, output_code):
    #make sure order is correct for operands
    new_id_value = id_value
    variables = []
    split = code_line.replace(",", "")
    split = split.replace("\t", "")
    split = split.split(" ")
    div_flag = 0

    asm_fun_call = "TMP"
    if (split[2] == "fadd"):
        asm_fun_call = "add"
    if (split[2] == "fsub"):
        asm_fun_call = "sub"
    if (split[2] == "fmul"):
        asm_fun_call = "imul"
    if (split[2] == "fdiv"):
        asm_fun_call = "idivl"
        div_flag = 1

    if (split[0] not in id_variables and "\"" in split[0]):
        id_variables[split[0]] = new_id_value
        new_id_value -= 4
    if (split[4] not in id_variables and "\"" in split[4]):
        id_variables[split[4]] = new_id_value
        new_id_value -= 4
    if (split[5] not in id_variables and "\"" in split[5]):
        id_variables[split[5]] = new_id_value
        new_id_value -= 4
    if (split[4].find("\"") != -1):
        output_code.append("\tmovl\t" + str(id_variables[split[4]]) + "(%rbp)" + ", %eax")
    else: #constant
        output_code.append("\tmovl\t$" + split[4] + ", %eax")
    if (div_flag):
        output_code.append("\tcltd")
        output_code.append("\t" + asm_fun_call + "\t" + str(id_variables[split[5]]) + "(%rbp)")
    else:
        if (split[5].find("\"") != -1):
            output_code.append("\t" + asm_fun_call + "\t\t" + str(id_variables[split[5]]) + "(%rbp)" + ", %eax")
        else:#constant
            output_code.append("\t" + asm_fun_call + "\t\t$" + split[5] + ", %eax")
    assert(split[0].find("\"") != -1)
    output_code.append("\tmovl\t%eax"  + ", " + str(id_variables[split[0]]) + "(%rbp)")
    return(new_id_value)

print("THERE IS A EXTRA DOLLAR SIGN")
def sgrab_params(code_line, id_variables, id_value, output_code):
    print("ID VAR: ", id_variables)
    new_id_value = id_value
    variables = []
    split = code_line.replace(",", "")
    split = split.replace("\t", "")
    split = split.split(" ")
    if (split[2] not in id_variables and "\"" in split[0]):
        # assert(split[2].isdigit)
        # id_variables[split[2]] = new_id_value
        # output_code.append("\tmovl from set: " + split[2])
        # new_id_value -= 4
        pass

    if (split[4] not in id_variables and "\"" in split[4]):
        id_variables[split[4]] = new_id_value
        if (split[2].find("\"") == -1):
            output_code.append("\tmovl\t$" + split[2] + ", " + str(id_variables[split[4]]) + "(%rbp)")
        else:
            output_code.append("\tmovl\t" + str(id_variables[split[2]]) + "(%rbp)" + ", " + "%eax")
            output_code.append("\tmovl\t" + "%eax" + ", " + str(id_variables[split[4]]) + "(%rbp)")
            # output_code.append("\tmovl\t" + split[2] + ", " + str(id_variables[split[2]]) + "(%rbp)")
        # output_code.append("\tmovl from set" + split[4])
        new_id_value -= 4
    # output_code.append("\tmovl\t$" + split[2] + ", %eax")
    return(new_id_value)

def rgrab_params(code_line, id_variables, id_value, output_code):
    # print("ID VAR: ", id_variables)
    variables = []
    split = code_line.replace(",", "")
    split = split.split(" ")
    # variables.append(split[2])
    if (split[2].find("\"") == -1):
        output_code.append("\tmovl\t$" + split[2] + ", %eax")
    else:
        output_code.append("\tmovl\t" + str(id_variables[split[2]]) + "(%rbp)" + ", %eax")
    output_code.append("\tpopq\t%rbp")
    output_code.append("\tretq")
    return(id_value)

print("Hannah: what is the difference between @ and % in variable names and do we need to worrry about it")
def get_fun_name(input_line):
        begin_name_index = input_line.find("\"") + 1
        end_name_index = input_line.find("\"", begin_name_index+1, -1)
        return input_line[begin_name_index:end_name_index]

def get_fun_parameters(input_line):
        begin_name_index = input_line.find("(") + 1
        end_name_index = input_line.find(")")
        parameter_string = input_line[begin_name_index:end_name_index]
        params = parameter_string.split(",")
        for i in range(0, len(params)):
            params[i] = params[i].replace("i32", "")
            # params[i] = params[i].replace("\"", "")
            # params[i] = params[i].replace("%", "")
            params[i] = " ".join(params[i].split())
            if (params[i] == ""):
                params.remove("")
        return params



#finds the bounds for conversion
def define_bounds(ir):
    fun_body_lines = []
    def_lines = []
    tmp_arr = []
    b = ir.split("\n")
    for i in range (0, len(b)):
        c = b[i].split(" ")
        if (c[0] == "define"):
            def_lines.append(i)
        if (c[0] == "{"): #replace entry label with function name
            tmp_arr.append(i+1)
        if (c[0] == "}"):
            tmp_arr.append(i)

    for i in range(0, len(tmp_arr), 2):
        assert(tmp_arr[i] < tmp_arr[i+1])
        tmp = [tmp_arr[i], tmp_arr[i+1]]
        fun_body_lines.append(tmp)

    assert(len(fun_body_lines) == len(def_lines))

    return [def_lines, fun_body_lines]


          #todo change line 109 of compiler.py
