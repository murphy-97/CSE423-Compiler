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

    # Iterate through children of root to find functions node
    # Is there a better way to get all children of a given node?
    func_node = None
    for node in ast.all_nodes():
        #node = ast.get_node(node)

        if (node.tag == "functions" and ast.parent(node.identifier).is_root()):
            func_node = node
            break

    assert(func_node is not None)

    # Iterate through children of function node
    for node in ast.all_nodes():
        if (ast.parent(node.identifier) == func_node):
            # Function header found
            func_name = node.tag[0]

            # Assign return type (cannot be none)
            type_return = None
            if (node.tag[1] in type_dict):
                type_return = type_dict[node.tag[1]]
            else:
                raise Exception("Unknown Type: " + node.tag[1])

            # List parameter types
            types_param = []
            for param in node.tag[2]:
                if (param in type_dict):
                    types_param.append(type_dict[param])
                else:
                    raise Exception("Unknown Type: " + param)

            # Define function type
            func_type = ir.FunctionType(type_return, tuple(types_param))

            # Create function
            function = ir.Function(module, func_type, name=func_name)

            # Build function
            block = function.append_basic_block(name="entry")
            builder = ir.IRBuilder(block)

            # FUNCTION IMPLEMENTATION BUILT HERE

            # PLACEHOLDER - RETURNS WITHOUT A VALUE
            builder.ret_void()

    # Return LLVM module
    return module

# Main function: setup sample AST and produce LLVM
def main():

    # Create dummy AST
    ast_dummy = Tree()
    ast_root = Node(tag="program")
    ast_dummy.add_node(ast_root)

    # Create child nodes for globals and functions
    ast_glob = Node(tag="globals")
    ast_func = Node(tag="functions")

    ast_dummy.add_node(ast_glob, parent=ast_root)
    ast_dummy.add_node(ast_func, parent=ast_root)

    # Create nodes for each function
    ast_dummy.add_node(
        Node(
            tag=("add_int", "int", ("int", "int",))
        ),
        parent=ast_func
    )

    ast_dummy.add_node(
        Node(
            tag=("main", "int", ("void",))
        ),
        parent=ast_func
    )

    # Print dummy AST
    print("=== DUMMY AST ===")
    ast_dummy.show(None, 0, True, None, None, False, 'ascii', None)

    # Convert dummy AST into LLVM
    llvm_ir = build_llvm(ast_dummy)

    # Output result
    print(llvm_ir)

# Boilerplate for calling main by running this module
if __name__ == "__main__":
    main()