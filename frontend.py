# CSE423 Compilers
# frontend.py: converts C code to LLVM IR via scanner, parser, and IR builder

# Import non-project modules
import re
import sys
sys.path.append('treelib-1.5.5/')
from treelib import Node, Tree
# Import project modules
import frontend_scanner as scn
import frontend_parser as prs
import frontend_ir_build as irb
import errors


# Main method for frontend module
def run_frontend(code_lines, print_scn, print_prs, print_ir):
    # Takes a list of code lines and returns a list of processed code lines
    print('\nScanning...')
    tokens = scn.run_scanner(code_lines)
    # Command line option to print scanner output

    # print_scn = True
    if (print_scn):
        print("====== SCANNER OUTPUT ======")
        for token in tokens:
            print(str(token))
        print("")

    print('Parsing...')
    grammar = prs.parse_grammar(open('grammar.txt', "r"))
    prs_out = prs.run_parser(tokens, grammar, clear_symbol_table=True)
    ast = prs_out[0]
    symbol_table = prs_out[2]

    # Command line option to print parser output
    if (print_prs):
        print("====== PARSER OUTPUT =======")
        ast.show(key=lambda x: x.identifier, line_type='ascii')
        print("")

    # Convert tree to IR
    print("Building IR...")
    ir = irb.build_llvm(ast, symbol_table)
    if (print_ir):
        print("====== IR OUTPUT ===========")
        print(ir)
        print("")

    # Command line option to print IR output

    return ir