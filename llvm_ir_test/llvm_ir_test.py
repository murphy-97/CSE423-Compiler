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

# Main function: setup sample AST and produce LLVM
def main():

    # Create dummy AST
    ast_dummy = Tree()
    ast_root = Node(tag="program")
    ast_dummy.add_node(ast_root)

    ast_dummy.add_node(
        Node(
            tag=("add_int", "int", ("int", "int",))
        ),
        parent=ast_root
    )

    ast_dummy.add_node(
        Node(
            tag=("main", ("int", ("void",) ))
        ),
        parent=ast_root
    )

    # Print dummy AST
    print("=== DUMMY AST ===")
    ast_dummy.show(None, 0, True, None, None, False, 'ascii', None)

    # Convert dummy AST into LLVM
    

    # Output result
    return

# Boilerplate for calling main by running this module
if __name__ == "__main__":
    main()