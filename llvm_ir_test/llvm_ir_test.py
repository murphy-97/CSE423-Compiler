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

            # Build function
            block = function.append_basic_block(name="entry")
            builder = ir.IRBuilder(block)

            # FUNCTION IMPLEMENTATION BUILT HERE

            # PLACEHOLDER - RETURNS WITHOUT A VALUE
            builder.ret_void()

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
