# CSE423 Compilers
# backend.py: frontend systems for C-to-ASM compiler implemented in Python

### Main method for frontend module
def run_frontend(code_lines):
    """Takes a list of code lines and returns a list of processed code lines"""
    code_lines = run_scanner(code_lines)
    code_lines = run_parser(code_lines)
    return code_lines

### Scanner/tokenizer for compiler frontend
def run_scanner(code_lines):
    """Reads source code and returns list of tokens"""
    # TO DO: Implement scanner
    return code_lines

### Parser for compiler frontend
def run_parser(code_lines):
    """Parses tokens using language grammar"""
    # TO DO: Implement parser
    return code_lines