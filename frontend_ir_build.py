# CSE423 Compilers
# front_ir_build.py: Builds LLVM from an AST

'''
TO DO:
- Test unary operations (requires parser progress)
- Constant types other than int or float?
- Global variables?
'''

# Import non-project modules
from treelib import Node, Tree
from llvmlite import ir

# Debug values
ALLOW_IMPLICIT_VAR_DEC = False

# Global values
__module = None
__ir_funcs = {}         # Stores function objects for use when calling functions
__node_results = {}     # Used to keep track of IR results by node ID (intermediate steps)
__variable_counter = 0  # Guarantees that variables have globally-unique names
__block_counter = 0     # Guarantees that blocks have globally-unique names
__var_nodes = {}        # Used to store which nodes have declared variables
__symbol_table = {}     # Used to read variable types from the parser

# Type dictionary used in parsing the AST
__type_dict = {
    "int":    ir.IntType(32),   # Assuming 4 byte ints for now
    "float": ir.DoubleType(),
    "double": ir.DoubleType(),
    "void":   ir.VoidType()
}

# Iterative function to build LLVM representation
def build_llvm(ast, symbol_table):
    global __symbol_table
    __symbol_table = symbol_table

    global __module
    __module = ir.Module(name="program")

    assert(ast.get_node(ast.root).tag == "program")
    global_vars = {}    # Stores global variable objects

    # Iterate through children of root
    for node in ast.children(ast.root):
        if (node.tag.index("func:") == 0):
            # Function definition found
            func_name = node.tag[5:]
            func_return = ""
            func_params = []

            # Iterate through node children to:
            #   Define type
            #   Define params
            #   Find body

            func_body = None    # Used to keep track of the func_body node

            for child in ast.children(node.identifier):
                if (child.tag == "return_type"):
                    func_return = ast.children(child.identifier)[0].tag
                    assert(len(func_return) > 0)

                elif (child.tag == "params"):
                    for param in ast.children(child.identifier):
                        param_type = param.tag
                        param_name = ast.children(param.identifier)[0].tag
                        func_params.append([param_type, param_name])

                elif (child.tag == "func_body"):
                    func_body = child

            assert(func_body is not None)   # Check that we found the func_body

            # Verify that types are known and update from strings to IR type objects
            if (func_return in __type_dict):
                func_return = __type_dict[func_return]
            else:
                raise Exception("IR Builder Unknown Type: " + func_return)

            for param in func_params:
                if (param[0] in __type_dict):
                    param[0] = __type_dict[param[0]]
                else:
                    raise Exception("IR Builder Unknown Type: " + param[0])

            # Create function in LLVM
            func_type = ir.FunctionType(
                func_return,                        # Return type
                tuple([p[0] for p in func_params])  # Tuple of param types
            )

            function = ir.Function(__module, func_type, name=func_name)
            __ir_funcs[func_name] = function          # Store function object by name

            # Build function
            block = function.append_basic_block(name="entry")   # Create function block
            builder = ir.IRBuilder(block)   # Create builder object to work within block
            build_block(ast, func_body, global_vars, func_params, function, builder)

        elif (True):
            print("Handle case for global variables")

    # Return LLVM module
    return __module

def build_block(ast, block_root, global_vars, func_params, function, builder):
    # Bulider is passed in by caller. Caller creates block object and builder
    global __variable_counter   # Used when explicitly declaring variables
    global __block_counter      # Used when creating blocks

    traversal_stack = []    # Used to traverse tree build node_stack (excludes subblocks)
    node_stack = []         # Used to build function. Nodes pushed in level order, popped in reverse level order
    traversal_stack.append(block_root)

    while (len(traversal_stack) > 0):
        iter_node = traversal_stack.pop()   # Get next node from traversal_stack
        node_stack.append(iter_node)        # Add current node to node_stack

        # Add children to the traversal_stack
        if (iter_node.tag not in ['if', 'while', 'block'] and iter_node.tag not in __type_dict):
            for child in ast.children(iter_node.identifier):
                traversal_stack.append(child)
        elif (iter_node.tag in ['if', 'while']):
            # Append only the condition, not the body
            traversal_stack.append(ast.children(iter_node.identifier)[0])

    # Use reverse level order traversal to build function by popping node_stack
    func_locals = {}    # Used to keep track of local variable names by node tag
        # dictionary key (node tag) is the variable's name in the parse tree
        # dictionary value is the variable's name generated by the IR builder

    # Define block scope (should place everything in since func_locals is empty)
    # Function args have priority when checking against this later

    # Begin reverse level order traversal of parse tree

    bin_ops = ['=', '+', '-', '*', '/', '%', '&&', '||', '<', '>', "<=",
        '>=', '==', '+=', '-=', '*=', '/=', '<<', '>>']
    una_ops = ['++', '--']

    while (len(node_stack) > 0):

        iter_node = node_stack.pop()

        if (iter_node.tag in bin_ops):
            build_bin_op(
                ast,
                iter_node,
                func_locals,
                global_vars,
                func_params,
                function,
                builder
            )

        elif (iter_node.tag in una_ops):
            build_una_op(
                ast,
                iter_node,
                func_locals,
                global_vars,
                func_params,
                function,
                builder
            )

        elif (iter_node.tag == 'return'):
            if (len(ast.children(iter_node.identifier)) == 0):
                # Void return
                assert(func_return == __type_dict["void"])
                builder.ret_void()
            else:
                # Returning an expression
                child_id = ast.children(iter_node.identifier)[0].identifier
                result = __node_results[child_id]
                builder.ret(result)

        elif (iter_node.tag in ['if', 'while']):
            # condition is first child, body is second child
            cond_node = ast.children(iter_node.identifier)[0]
            body_node = ast.children(iter_node.identifier)[1]

            # Build scope for the if-statement sub-blocks
            scope_vars = {}
            for v in func_locals:
                if v not in scope_vars:
                    scope_vars[v] = func_locals[v]

            for v in global_vars:
                if v not in scope_vars:
                    scope_vars[v] = global_vars[v]

            # Build if-then blocks
            if_body_block = builder.append_basic_block(name="block_"+str(__block_counter))
            __block_counter += 1
            if_after_block = builder.append_basic_block(name="block_"+str(__block_counter))
            __block_counter += 1

            # Build condition
            cond_result = builder.icmp_signed(
                '!=',
                __node_results[ast.children(cond_node.identifier)[0].identifier],
                ir.Constant(__type_dict["int"], 0)
            )
            __node_results[cond_node.identifier] = cond_result

            # Create initial branch
            builder.cbranch(cond_result, if_body_block, if_after_block)

            # Build body block
            builder.position_at_start(if_body_block)
            build_block(
                ast,
                body_node,
                scope_vars,
                func_params,
                function,
                builder
            )

            # Append jump to end of while-oop
            if (iter_node.tag == 'while'):
                try:
                    cond_result = builder.icmp_signed(
                        '!=',
                        __node_results[ast.children(cond_node.identifier)[0].identifier],
                        ir.Constant(__type_dict["int"], 0)
                    )
                    __node_results[cond_node.identifier] = cond_result
                    builder.cbranch(cond_result, if_body_block, if_after_block)
                except AssertionError:
                    # Likely due to return within while-loop
                    # Leave as if-statement
                    pass

            # Finish construction of if/while
            builder.position_at_start(if_after_block)

        elif (iter_node.tag == 'block'):

            body_node = iter_node
            # Change name to prevent infinite recursion
            body_node.tag = 'block_root'

            # Build scope for the if-statement sub-blocks
            scope_vars = {}
            for v in func_locals:
                if v not in scope_vars:
                    scope_vars[v] = func_locals[v]

            for v in global_vars:
                if v not in scope_vars:
                    scope_vars[v] = global_vars[v]

            body_block = builder.append_basic_block(name="block_"+str(__block_counter))
            __block_counter += 1

            builder.position_at_start(body_block)
            build_block(
                ast,
                body_node,
                scope_vars,
                func_params,
                function,
                builder
            )

        else:
            # Node is either a constant, variable ID, or function call
            if (iter_node.tag in ['func_body', 'condition', 'condition_body', 'block_root']):
            # First node in subtree is just for finding the children
            # Can be ignored in function building
                pass
            elif (iter_node.tag[:5] == "func:"):
                # Function call
                func_name = iter_node.tag[5:]
                arg_list = []
                for child in ast.children(iter_node.identifier):
                    if (child.identifier in __var_nodes):
                        # Need to load variable from pointer
                        var_load = builder.load(__node_results[child.identifier])
                        arg_list.append(var_load)
                    else:
                        # Can pass constant directly
                        arg_list.append(__node_results[child.identifier])

                builder.call(__ir_funcs[func_name], arg_list)
            
            elif (iter_node.tag in __type_dict):
                # Explicit variable declaration
                # Currently expects declaration without initialization

                var_type = iter_node.tag
                var_name = ast.children(iter_node.identifier)[0].tag

                assert(__module is not None)
                func_locals[var_name] = ir.GlobalVariable(
                    __module,
                    __type_dict[var_type],
                    var_name + "_" + str(__variable_counter)
                )
                __variable_counter += 1
                result = func_locals[var_name]
                
            else:
                # Constant or variable
                assert(len(ast.children(iter_node.identifier)) == 0)

                var_type = ""
                is_numeral = iter_node.tag.isdigit() # if true, then int

                if (is_numeral):
                    var_type = "int"
                else:
                    try:
                        float(iter_node.tag)
                        var_type = "float"
                        is_numeral = True
                    except:
                        pass
                    
                if (is_numeral):
                    # Constant
                    assert(len(var_type) > 0)
                    assert(__type_dict[var_type] is not None)
                    result = get_constant(iter_node.tag, var_type)

                else:
                    # Variable
                    if (iter_node.tag not in [p[1] for p in func_params]):
                        # Local variable

                        # NOTE: Check locals first because arguments
                        # that are changed by assignment are copied to
                        # local variables, so thats where the most up
                        # to date value will be stroed

                        result = get_variable(
                            iter_node.tag,
                            func_locals,
                            func_params,
                            function,
                            builder,
                            global_vars,
                        )
                        __var_nodes[iter_node.identifier] = result

                    else:
                        # Function argument
                        result = function.args[
                            [p[1] for p in func_params].index(iter_node.tag)
                        ]

            __node_results[iter_node.identifier] = result

def build_bin_op(ast, iter_node, func_locals, global_vars, func_params, function, builder):
    # Binary operation

    # Get operand node identifiers
    child_l = ast.children(iter_node.identifier)[0].identifier
    child_r = ast.children(iter_node.identifier)[1].identifier

    # Get IR representations of operand nodes
    operand_l = __node_results[child_l]
    operand_r = __node_results[child_r]
    # Convert variable address to variable value
    if (child_r in __var_nodes):
        operand_r = builder.load(operand_r)

    result = None

    if (iter_node.tag in ['+=', '-=', '*=', '/=', '%=', '=']):
        # Local variables only exist in the builder and not the final IR
        # Values are stored in the func_locals dictionary
        #   Key = variable name as seen in iter_node.tag
        #   Value = IR generated result from right hand of assignment
        var_name = ast.children(iter_node.identifier)[0].tag

        if (iter_node.tag in ['+=', '-=', '*=', '/=', '%=']):
            # Get current value of left operand
            operand_l = get_variable(
                var_name,
                func_locals,
                func_params,
                function,
                builder,
                global_vars,
            )

            # Evaluate right side operand
            if (iter_node.tag == '+='):
                operand_r = builder.fadd(operand_l, operand_r)

            elif (iter_node.tag == '-='):
                operand_r = builder.fsub(operand_l, operand_r)

            elif (iter_node.tag == '*='):
                operand_r = builder.fmul(operand_l, operand_r)

            elif (iter_node.tag == '/='):
                operand_r = builder.fdiv(operand_l, operand_r)

            elif (iter_node.tag == '%='):
                operand_r = builder.frem(operand_l, operand_r)

        # Assign new value
        result = set_variable(operand_r, var_name, func_locals, func_params, function, builder, global_vars)

    else:
        # Convert variable address to variable value
        if (child_l in __var_nodes):
            operand_l = builder.load(operand_l)

        if (iter_node.tag == '+'):
            result = builder.fadd(operand_l, operand_r)

        elif (iter_node.tag == '-'):
            result = builder.fsub(operand_l, operand_r)

        elif (iter_node.tag == '*'):
            result = builder.fmul(operand_l, operand_r)

        elif (iter_node.tag == '/'):
            result = builder.fdiv(operand_l, operand_r)

        elif (iter_node.tag == '%'):
            result = builder.frem(operand_l, operand_r)

        elif (iter_node.tag == '&&'):
            # Must be implmemented using other operators
            # (x && y) is equivialent to ((x * y) != 0)
            step_1 = builder.fmul(operand_l, operand_r)
            step_2 = ir.Constant(__type_dict["int"], 0)
            result = builder.icmp_signed('!=', step_1, step_2)
            result = builder.zext(result, __type_dict["int"])

        elif (iter_node.tag == '||'):
            # Must be implmemented using other operators
            # (x || y) is equivialent to ((x + y)+(x * y) != 0)
            step_1 = builder.fadd(operand_l, operand_r)
            step_2 = builder.fmul(operand_l, operand_r)
            step_3 = builder.fadd(step_1, step_2)
            step_4 = ir.Constant(__type_dict["int"], 0)
            result = builder.icmp_signed('!=', step_3, step_4)
            result = builder.zext(result, __type_dict["int"])

        elif (iter_node.tag in ['<', '>', '<=', '>=', '==', '!=']):
            result = builder.icmp_signed(iter_node.tag, operand_l, operand_r)
            # This is the signed comparison.
            # There's also an unsigned comparison if we care about that

        elif (iter_node.tag == '<<'):
            result = builder.shl(operand_l, operand_r)

        elif (iter_node.tag == '>>'):
            # Using arithmetic right shift (C/C++ norm) instead of logical shift
            result = builder.ashr(operand_l, operand_r)

        if (result is None):
            # Verify that one of the above cases was satisfied
            raise Exception("Result not set for binary operator '" + iter_node.tag + "'")

    __node_results[iter_node.identifier] = result # Store IR result

def build_una_op(ast, iter_node, func_locals, global_vars, func_params, function, builder):
    # Unary operation

    # Get operand node identifiers
    child = ast.children(iter_node.identifier)[0].identifier
    # Get IR representations of operand nodes
    var_name = ast.children(iter_node.identifier)[0].tag
    operand = get_variable(
        var_name,
        func_locals,
        func_params,
        function,
        builder,
        global_vars
    )

    result = None

    # Construct arithmetic statement
    if (iter_node.tag in ['++', '--']):
        print("Unary Ops: ++ and -- modify value but act like assignment")

        if (iter_node.tag == '++'):
            result = builder.fadd(
                operand,
                ir.Constant(__type_dict["int"], 1)
            )

        elif (iter_node.tag == '--'):
            result = builder.fsub(
                operand,
                ir.Constant(__type_dict["int"], 1)
            )

        assert(result is not None)
        # Assign new value
        result = set_variable(result, var_name, func_locals, func_params, function, builder, global_vars)

    assert(result is not None)  # Verify that one of the above cases was satisfied
    __node_results[iter_node.identifier] = result # Store IR result

def set_variable(value, var_name, func_locals, func_params, function, builder, global_vars):    
    global __variable_counter

    if (var_name in func_locals):
        # 1st check: local vars and modified arguments in this scope
        operand = func_locals[var_name]
    elif (var_name in [p[1] for p in func_params]):
        # 2nd check: arguments in this scope that have not been modified
        arg = function.args[
            [p[1] for p in func_params].index(var_name)
        ]
        # args can't be modified via store. Need to create variable
        var_index = [p[1] for p in func_params].index(var_name)
        # var_type is already converted from __type_dict
        var_type = [p[0] for p in func_params][var_index]
        
        assert(__module is not None)
        func_locals[var_name] = ir.GlobalVariable(
            __module,
            var_type,
            var_name + "_" + str(__variable_counter)
        )
        __variable_counter += 1
        operand = func_locals[var_name]

    elif (var_name in global_vars):
        # 3rd check: variables from the above scopes
        operand = global_vars[var_name]
    else:
        if (var_name in __symbol_table[function._get_name()]):
            var_type = __symbol_table[function._get_name()][var_name]
            assert(__module is not None)
            func_locals[var_name] = ir.GlobalVariable(
                __module,
                __type_dict[var_type],
                var_name + "_" + str(__variable_counter)
            )
            __variable_counter += 1
            operand = func_locals[var_name]

        elif (ALLOW_IMPLICIT_VAR_DEC):
            print("WARNING! Implicit declaration of variable '" + var_name + "' (set_variable)")
            print("Assuming type is int")
            var_type = "int"
            
            assert(__module is not None)
            func_locals[var_name] = ir.GlobalVariable(
                __module,
                __type_dict[var_type],
                var_name + "_" + str(__variable_counter)
            )
            __variable_counter += 1
            operand = func_locals[var_name]
        else:
            raise Exception("Undeclared variable '" + var_name + "'")

    return builder.store(value, operand)

def get_variable(var_name, func_locals, func_params, function, builder, global_vars):    
    global __variable_counter

    if (var_name in func_locals):
        # 1st check: local vars and modified arguments in this scope
        operand = func_locals[var_name]
    elif (var_name in [p[1] for p in func_params]):
        # 2nd check: arguments in this scope that have not been modified
        operand = function.args[
            [p[1] for p in func_params].index(var_name)
        ]
    elif (var_name in global_vars):
        # 3rd check: variables from the above scopes
        operand = global_vars[var_name]
    else:
        if (var_name in __symbol_table[function._get_name()]):
            var_type = __symbol_table[function._get_name()][var_name]
            assert(__module is not None)
            func_locals[var_name] = ir.GlobalVariable(
                __module,
                __type_dict[var_type],
                var_name + "_" + str(__variable_counter)
            )
            __variable_counter += 1
            operand = func_locals[var_name]

        elif (ALLOW_IMPLICIT_VAR_DEC):
            print("WARNING! Implicit declaration of variable '" + var_name + "' (get_variable)")

            print("Assuming type is int")
            var_type = "int"

            assert(__module is not None)
            func_locals[var_name] = ir.GlobalVariable(
                __module,
                __type_dict[var_type],
                var_name + "_" + str(__variable_counter)
            )
            __variable_counter += 1
            operand = func_locals[var_name]

        else:
            raise Exception("Undeclared variable '" + var_name + "'")

    return operand

def get_constant(var_value, var_type=None):
    # Determine type
    if (var_type is None):
        var_type = ""
        is_numeral = var_value.isdigit() # if true, then int

        if (is_numeral):
            var_type = "int"
        else:
            try:
                float(var_value)
                var_type = "float"
                is_numeral = True
            except:
                pass

    # Create consant
    constant = 0
    if (var_type == "int"):
        constant = int(var_value)
    elif (var_type == "float"):
        constant = float(var_value)
    else:
        raise Exception("IR Builder Unknown Type: " + var_type)

    return ir.Constant(__type_dict[var_type], constant)