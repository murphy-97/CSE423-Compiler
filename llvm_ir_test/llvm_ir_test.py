# CSE423 Compilers
# llvm_ir_test.py: basic test for producing LLVM from an AST

'''
DUMMY C PROGRAM:

int add_int(int x, int y) {
    return x + y;
}

int main(void) {
    int a;
    int b;
    int c;

    a = 1;
    b = 2;
    c = add_int(a, b);

    return 0;
}

'''

# Import non-project modules
from treelib import Node, Tree
from llvmlite import ir

# Iterative function to build LLVM representation
def build_llvm(ast):

    assert(ast.get_node(ast.root).tag == "program")

    # Type dictionary used in parsing the AST
    type_dict = {
        "int":    ir.IntType(8),        # Assuming 8 bit ints for testing
        "double": ir.DoubleType(),
        "void":   ir.VoidType()
    }

    ir_funcs = {}

    # Create module
    module = ir.Module(name="program")

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

            func_body = None

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

            assert(func_body is not None)

            # Verify that types are known and update to IR type objects
            if (func_return in type_dict):
                func_return = type_dict[func_return]
            else:
                raise Exception("Unknown Type: " + func_return)

            for param in func_params:
                if (param[0] in type_dict):
                    param[0] = type_dict[param[0]]
                else:
                    raise Exception("Unknown Type: " + param[0])

            # Create function in LLVM
            func_type = ir.FunctionType(
                func_return,
                tuple([p[0] for p in func_params]) # Tuple of param types
            )

            function = ir.Function(module, func_type, name=func_name)
            ir_funcs[func_name] = function

            # Build function
            block = function.append_basic_block(name="entry")
            builder = ir.IRBuilder(block)

            # FUNCTION IMPLEMENTATION BUILT HERE
            traversal_stack = []    # Used to build node_stack
            node_stack = []         # Used to build function
            traversal_stack.append(func_body)

            while (len(traversal_stack) > 0):
                iter_node = traversal_stack.pop()
                node_stack.append(iter_node)
                for child in ast.children(iter_node.identifier):
                    traversal_stack.append(child)

            # Convert node_stack from level order to reverse level order
            #node_stack = node_stack[::-1]

            # Use reverse level order traversal to build function
            node_results = {}   # Used to keep track of IR results by node ID
            func_locals = {}    # Used to keep track of local variable names by node tag

            bin_ops = ['=', '+', '-', '*', '/', '%', '&&', '||', '<', '>', "<=",
                '>=', '==']
            una_ops = ['++', '--', '+=', '-=', '*=', '/=', '<<', '>>']

            while (len(node_stack) > 0):

                iter_node = node_stack.pop()

                if (iter_node.tag == "func_body"):
                    # First node in subtree
                    pass
                elif (iter_node.tag in bin_ops):
                    child_l = ast.children(iter_node.identifier)[0].identifier
                    child_r = ast.children(iter_node.identifier)[1].identifier

                    operand_l = node_results[child_l]
                    operand_r = node_results[child_r]

                    result = None

                    if (iter_node.tag == '='):
                        if (iter_node.tag in [p[1] for p in func_params]):
                            # Assigning new value to function parameter
                            print("Add case for assigning value to parameter")
                            pass
                        elif (iter_node.tag in func_locals):
                            # Assigning new value to existing local variable
                            print("Add case for assigning value to variable")
                            pass
                        else:
                            # Defining new local variable
                            print("Add case for defining new local variable")
                            pass

                    elif (iter_node.tag == '+'):
                        result = builder.fadd(operand_l, operand_r)

                    elif (iter_node.tag == '-'):
                        result = builder.fsub(operand_l, operand_r)
                        pass

                    elif (iter_node.tag == '*'):
                        result = builder.fmul(operand_l, operand_r)
                        pass

                    elif (iter_node.tag == '/'):
                        result = builder.fdiv(operand_l, operand_r)
                        pass

                    elif (iter_node.tag == '%'):
                        result = builder.frem(operand_l, operand_r)
                        pass

                    elif (iter_node.tag == '&&'):
                        pass

                    elif (iter_node.tag == '||'):
                        pass

                    elif (iter_node.tag == '<'):
                        pass

                    elif (iter_node.tag == '>'):
                        pass

                    elif (iter_node.tag == '<='):
                        pass

                    elif (iter_node.tag == '>='):
                        pass

                    elif (iter_node.tag == '=='):
                        pass

                    assert(result is not None)
                    node_results[iter_node.identifier] = result

                elif (iter_node.tag in una_ops):
                    print("TO DO: Support for unary operators")
                    pass

                elif (iter_node.tag == 'return'):
                    if (len(ast.children(iter_node.identifier)) == 0):
                        # Void return
                        builder.ret_void()
                    else:
                        # Returning an expression
                        child_id = ast.children(iter_node.identifier)[0].identifier
                        result = node_results[child_id]
                        builder.ret(result)
                else:
                    # Node is either a constant, variable ID, or function call
                    if (iter_node.tag in ir_funcs):
                        # Function call
                        arg_list = []
                        for child in ast.children(iter_node.identifier):
                            arg_list.append(node_results[child.identifier])

                        builder.call(ir_funcs[iter_node.tag], arg_list)
                        
                    else:
                        # Constant or variable
                        assert(len(ast.children(iter_node.identifier)) == 0)

                        var_type = ""
                        is_numeral = iter_node.tag.isdigit()    # int
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
                            assert(type_dict[var_type] is not None)
                            
                            constant = 0
                            if (var_type == "int"):
                                constant = int(iter_node.tag)
                            elif (var_type == "float"):
                                constant = float(iter_node.tag)
                            else:
                                print("Unaccounted for type")

                            result = ir.Constant(type_dict[var_type], constant)

                        else:
                            # Variable
                            if (iter_node.tag in [p[1] for p in func_params]):
                                # Function argument
                                result = function.args[
                                    [p[1] for p in func_params].index(iter_node.tag)
                                ]
                            else:
                                # Local variable
                                result = func_locals[iter_node.tag]

                    node_results[iter_node.identifier] = result

        elif (True):
            print("Handle case for global variables")

    # Return LLVM module
    return module

# Main function: setup sample AST and produce LLVM
def main():

    # Create dummy AST
    ast_dummy = Tree()
    ast_root = Node(tag="program")
    ast_dummy.add_node(ast_root, parent=None)

    # Create nodes for add_int()
    func_root = Node(tag="func:add_int")
    func_type = Node(tag="return_type")
    func_param = Node(tag="params")
    func_body = Node(tag="func_body")

    ast_dummy.add_node(func_root, parent=ast_root)
    ast_dummy.add_node(func_type, parent=func_root)
    ast_dummy.add_node(func_param, parent=func_root)
    ast_dummy.add_node(func_body, parent=func_root)

    ### add_int(): return and params
    return_type = Node(tag="int")
    ast_dummy.add_node(return_type, parent=func_type)

    param_type = Node(tag="int")
    ast_dummy.add_node(param_type, parent=func_param)
    ast_dummy.add_node(Node(tag="x"), parent=param_type)
    param_type = Node(tag="int")
    ast_dummy.add_node(param_type, parent=func_param)
    ast_dummy.add_node(Node(tag="y"), parent=param_type)

    ### add_int(): body
    body_node_0 = Node(tag="return")
    ast_dummy.add_node(body_node_0, parent=func_body)
    body_node_1 = Node(tag="+")
    ast_dummy.add_node(body_node_1, parent=body_node_0)
    body_node_2 = Node(tag="x")
    ast_dummy.add_node(body_node_2, parent=body_node_1)
    body_node_2 = Node(tag="y")
    ast_dummy.add_node(body_node_2, parent=body_node_1)

    # Create nodes for main()
    func_root = Node(tag="func:main")
    func_type = Node(tag="return_type")
    func_param = Node(tag="params")
    func_body = Node(tag="func_body")

    ast_dummy.add_node(func_root, parent=ast_root)
    ast_dummy.add_node(func_type, parent=func_root)
    ast_dummy.add_node(func_param, parent=func_root)
    ast_dummy.add_node(func_body, parent=func_root)

    ### add_int(): return and params
    return_type = Node(tag="int")
    ast_dummy.add_node(return_type, parent=func_type)

    ### add_int(): body
    body_node_0 = Node(tag="return")
    ast_dummy.add_node(body_node_0, parent=func_body)
    body_node_1 = Node(tag="add_int")
    ast_dummy.add_node(body_node_1, parent=body_node_0)
    body_node_2 = Node(tag="1")
    ast_dummy.add_node(body_node_2, parent=body_node_1)
    body_node_2 = Node(tag="2")
    ast_dummy.add_node(body_node_2, parent=body_node_1)

    # Print dummy AST
    print("=== DUMMY AST ===")
    ast_dummy.show(key=lambda x: x.identifier, line_type='ascii')

    # Convert dummy AST into LLVM
    llvm_ir = build_llvm(ast_dummy)

    # Output result
    print("=== LLVM IR OUTPUT ===")
    print(llvm_ir)

# Boilerplate for calling main by running this module
if __name__ == "__main__":
    main()
