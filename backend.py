# CSE423 Compilers
# backend.py: backend systems for C-to-ASM compiler implemented in Python

__var_adrs = {}     # Stores addresses allocated by the store command
INIT_VARS_TO_ZERO = True

### Main method for backend module
def run_backend(code_lines):
    """Takes a list of code lines and returns a list of processed code lines"""
    # TO DO: Implement backend
    print("\nBuilding ASM...")

    global __var_adrs
    __var_adrs = {}

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

        elif ("load" in raw_code[i]):
            # print("load:", i)
            found_return_flag = 0
            id_value = lgrab_params(raw_code[i], id_variables, id_value, output_code)

        elif ("ret" in raw_code[i]):
            # print("ret:", i)
            found_return_flag = 1
            fparams = rgrab_params(raw_code[i], id_variables, id_value, output_code)

        elif ("call" in raw_code[i]):
            # print("call:", i)
            found_return_flag = 1
            fparams = cgrab_params(raw_code[i], id_variables, id_value, output_code)

        elif ("icmp" in raw_code[i]):
            # print("icmp", i)
            found_return_flag = 0
            #id_value = cmpgrab_params(raw_code[i], id_variables, id_value, output_code)
            output_code.append("\tCOMPARISON")

        elif ("br" in raw_code[i]):
            # print("br", i)
            output_code.append("\tBRANCH")

        elif (raw_code[i].strip()[0:6] == "block_"):
            # Create label
            output_code.append("." + raw_code[i].strip())

        else:
            raise Exception("Unknown command found in IR:\n" + str(raw_code[i]))

    #call function to do rest

    if (found_return_flag == 0):
        output_code.append("\tpopq\t%rbp")
        output_code.append("\tretq")
    output_code.append("\t\t\t\t\t\t\t\t\t\t## -- End function")
    # new_code.insert(0, "\n.p2align")
    return output_code

def cgrab_params(code_line, id_variables, id_value, output_code):
    print("HANNAH I just wrote this quickly and it is broken: you can fix/rewrite it easily")
    #make sure order is correct for operands
    new_id_value = id_value
    variables = []
    split = code_line.replace(",", "")
    split = split.replace("\t", "")
    split = split.split(" ")
    div_flag = 0

    registers = ["%edi", "%esi", "%edx", "%ecx", "r8d", "r9d"]
    cur_reg = 0

    print("values: ", split[0])
    print("len: ", len(split))

    #HANNAH: you can prob account for no parameters here by just having a if statemnt capturing most of this

    print ("HANNAH take into account more than 6 variables if i did not")

    for i in range (0, int((len(split) - 6)/2), 2):
        #check for cur_reg > 5
        #check for it here like i did before
        if (split[4].find("\"") != -1): #is a constant
            string = "\tmovl    " + registers[cur_reg] + ", $" + split[6 + i + 1]
        else: #is a constant
            string = "\tmovl    " + registers[cur_reg] + ", " + str(id_variables[split[6 + i + 1]])
        cur_reg += 1
        output_code.append(string) ## parameters begin at 6 and account for off by 1
    tmp = split[6 + i+1 + 2][:len(split[6 + i+1 + 2])-1]
    if (cur_reg < 5):
        if (tmp.find("\"") != -1): #is a constant
            string = "\tmovl    " + registers[cur_reg] + ", " + str(id_variables[tmp])
        else: #is a var
            string = "\tmovl    " + registers[cur_reg] + ", $" + tmp
        #still room in registers]
    else:
        print ("HANNAH take into account more than 6 variables if i did not")
    output_code.append(string)

    print("HANNAH: put in a jump here")

    # if (tmp.find("\"") != -1): #is a variable
    #     string = "\tmovl\t" + registers[cur_reg] + ", " + str(id_variables[split[4]])
    # else: #is a constant
    #     string = "\tmovl\t" + registers[cur_reg] + ", $" + split[6 + i+1]
    # cur_reg += 1

    return(new_id_value)


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
        print ("HANNAH take into account more than 6 variables")

        if (mapping_elem < 6):
            output_code.append("\tmovl    " + mapping[mapping_elem] + ", "+ str(i) + "(%rbp)")
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

    asm_fun_call = None
    if (split[2] == "fadd"):
        asm_fun_call = "add     "
    elif (split[2] == "fsub"):
        asm_fun_call = "sub     "
    elif (split[2] == "fmul"):
        asm_fun_call = "imul    "
    elif (split[2] == "fdiv"):
        asm_fun_call = "idivl   "
        div_flag = 1
    if (asm_fun_call is None):
        raise Exception("Unknown fp operation '" + split[2] + "' in IR")

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
        output_code.append("\tmovl    " + str(id_variables[split[4]]) + "(%rbp)" + ", %eax")
    else: #constant
        output_code.append("\tmovl    $" + split[4] + ", %eax")

    if (div_flag):
        output_code.append("\tcltd")
        if (split[5].find("\"") != -1):
            output_code.append("\t" + asm_fun_call + str(id_variables[split[5]]) + "(%rbp)")
        else: #constant
            output_code.append("\t" + asm_fun_call + "$" + split[5])

    else:
        if (split[5].find("\"") != -1):
            output_code.append("\t" + asm_fun_call + str(id_variables[split[5]]) + "(%rbp)" + ", %eax")

        else:#constant

            output_code.append("\t" + asm_fun_call + "$" + split[5] + ", %eax")

    assert(split[0].find("\"") != -1)
    output_code.append("\tmovl    %eax"  + ", " + str(id_variables[split[0]]) + "(%rbp)")
    return(new_id_value)

def lgrab_params(code_line, id_variables, id_value, output_code):

    global __var_adrs
    
    new_id_value = id_value
    variables = []
    split = code_line.replace(",", "")
    split = split.replace("\t", "")
    split = split.split(" ")

    var_name = split[5]

    if (var_name not in __var_adrs):
        if (INIT_VARS_TO_ZERO):
            print("WARNING: '" + var_name + "' used uninitialized. Setting value to 0")
            adrs_src = "$0"
        else:
            raise Exception("IR loading unitialized variable '" + var_name + "'")
    else:
        adrs_src = __var_adrs[var_name]

    if (split[0] not in id_variables and "\"" in split[0]):
        id_variables[split[0]] = new_id_value
        new_id_value -= 4

    adrs_dst = str(id_variables[split[0]]) + "(%rbp)"
    code_line = "Load " + var_name + " from " + adrs_src + " into " + adrs_dst
    output_code.append("\tmovl    " + adrs_src + ", " + "%eax")
    output_code.append("\tmovl    " + "%eax" + ", " + adrs_dst)

    return(new_id_value)

def sgrab_params(code_line, id_variables, id_value, output_code):

    global __var_adrs

    var_name = ""
    address = ""

    # print("ID VAR: ", id_variables)
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
            var_name = split[4]
            address = str(id_variables[split[4]]) + "(%rbp)"
            output_code.append("\tmovl    $" + split[2] + ", " + address)
        else:
            var_name = split[4]
            address = str(id_variables[split[4]]) + "(%rbp)"
            output_code.append("\tmovl    " + str(id_variables[split[2]]) + "(%rbp)" + ", " + "%eax")
            output_code.append("\tmovl    " + "%eax" + ", " + address)
            # output_code.append("\tmovl\t" + split[2] + ", " + str(id_variables[split[2]]) + "(%rbp)")
        # output_code.append("\tmovl from set" + split[4])
        new_id_value -= 4
    # output_code.append("\tmovl\t$" + split[2] + ", %eax")
    __var_adrs[var_name] = address
    return(new_id_value)

def cmpgrab_params(code_line, id_variables, id_value, output_code):
    print("Comparisons are a work in progress")
    new_id_value = id_value
    variables = []
    split = code_line.replace(",", "")
    split = split.replace("\t", "")
    split = split.split(" ")

    var_name = split[5]

    if (var_name not in __var_adrs):
        if (INIT_VARS_TO_ZERO):
            print("WARNING: '" + var_name + "' used uninitialized. Setting value to 0")
            adrs_src = "$0"
        else:
            raise Exception("IR loading unitialized variable '" + var_name + "'")
    else:
        adrs_src = __var_adrs[var_name]

    if (split[0] not in id_variables and "\"" in split[0]):
        id_variables[split[0]] = new_id_value
        new_id_value -= 4

    adrs_dst = str(id_variables[split[0]]) + "(%rbp)"
    code_line = "Load " + var_name + " from " + adrs_src + " into " + adrs_dst
    output_code.append("\tmovl    " + adrs_src + ", " + "%eax")
    output_code.append("\tmovl    " + "%eax" + ", " + adrs_dst)

    return(new_id_value)

def rgrab_params(code_line, id_variables, id_value, output_code):
    # print("ID VAR: ", id_variables)
    variables = []
    split = code_line.replace(",", "")
    split = split.split(" ")
    # variables.append(split[2])
    if (split[2].find("\"") == -1):
        output_code.append("\tmovl    $" + split[2] + ", %eax")
    else:
        output_code.append("\tmovl    " + str(id_variables[split[2]]) + "(%rbp)" + ", %eax")
    output_code.append("\tpopq    %rbp")
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