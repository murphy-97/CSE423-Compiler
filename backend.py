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

    #identify case for each line in the function and change it to assembly via helper fuctions
    #helper functions return arrays of created lines
    #loop though lines appending them to output_code
    print("\n\nFSFEFSFESF")
    for i in range(1, len(raw_code)):
        if ("fadd" in raw_code[i]):
            print("fadd:", i)

        if ("fsub" in raw_code[i]):
            print("fsub:", i)

        if ("fmul" in raw_code[i]):
            print("fmul:", i)

        if ("fdiv" in raw_code[i]):
            print("fdiv:", i)

        if ("frem" in raw_code[i]):
            print("frem:", i)

        if ("store" in raw_code[i]):
            print("store:", i)
            
        if ("ret" in raw_code[i]):
            print("ret:", i)

    #call function to do rest

    output_code.append("\tpopq\t%rbp")
    output_code.append("\tretq")
    output_code.append("\t\t\t\t\t\t\t\t\t\t## -- End function")
    # new_code.insert(0, "\n.p2align")
    return output_code

    

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
