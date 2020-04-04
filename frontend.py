# CSE423 Compilers
# backend.py: frontend systems for C-to-ASM compiler implemented in Python

# Import non-project modules
import re
import sys
sys.path.append('treelib-1.5.5/')
from treelib import Node, Tree
from collections import OrderedDict
# Import project modules
import errors


# Main method for frontend module
def run_frontend(code_lines, print_scn, print_prs):
    # Takes a list of code lines and returns a list of processed code lines
    print('Scanning')
    tokens = run_scanner(code_lines)
    # Command line option to print scanner output

    # print_scn = True
    if (print_scn):
        print("\n====== SCANNER OUTPUT ======")
        for token in tokens:
            print(str(token))

    print('Parsing')
    grammar = parse_grammar(open('grammar.txt', "r"))
    ast = run_parser(tokens, grammar)

    # Command line option to print parser output
    if (print_prs):
        print("\n====== PARSER OUTPUT ======")
        ast.show(key=lambda x: x.identifier, line_type='ascii')

    return ast


# Scanner/tokenizer for compiler frontend
def run_scanner(code_lines):
    # Reads source code and returns list of tokens"""

    input = code_lines
    entire_doc = ""
    replace_space_array = [";", "(", ")", "{", "}", "=", "<", ">", "+", "-",
                           ","]
    single_tokens = ["(", ")", "{", "}", ",", ";", "=", "++", "--", "+=", "-=",
                     "*=", "/=", "true", "false"]

    # replace_array = ["\n"] # Unused variable. Commented out

    tokens_descriptive = []

    # create string of input code

    for line in input:
        entire_doc = entire_doc + line

    # remove the non-allowed character $
    entire_doc = entire_doc.replace("$", "")

    # find, store and replace all strings "" from program
    # #to be replaced later

    strings_array = re.findall(r'".*?"', entire_doc)
    for string in strings_array:
        entire_doc = entire_doc.replace(string, "$string$", 1)

    # find, store, and replace all characters
    chars_array = re.findall(r"'.*?'", entire_doc)
    for char in chars_array:
        entire_doc = entire_doc.replace(char, "$char$", 1)

    entire_doc = entire_doc.replace("++", "$plus$")
    entire_doc = entire_doc.replace("--", "$minus$")
    entire_doc = entire_doc.replace("+=", "$plus_equals$")
    entire_doc = entire_doc.replace("!=", "$not_equals$")
    entire_doc = entire_doc.replace("-=", "$minus_equals$")
    entire_doc = entire_doc.replace("*=", "$mult_equals$")
    entire_doc = entire_doc.replace("/=", "$divide_equals$")
    entire_doc = entire_doc.replace("==", "$equals$")
    entire_doc = entire_doc.replace("<<", "$left$")
    entire_doc = entire_doc.replace(">>", "$right$")

    # add spaces arround all individual tokens for formating
    for value in replace_space_array:
        entire_doc = entire_doc.replace(value, " "+value+" ")

    # remove line comments (must be before line break removal)
    entire_doc = re.sub(r'//.*?\n', "\n", entire_doc)

    # prepare for line counts for error reporting and remove line breaks
    entire_doc = entire_doc.replace("\n", " $newline$ ")
    line_counter = 1

    # remove block comments (must be after line break removal)
    entire_doc = re.sub(r'//.*?$', "\n", entire_doc)
    entire_doc = re.sub(r'\/\*.*\*\/', "", entire_doc)

    # remove extra characters
    entire_doc = ' '.join(entire_doc.split())
    # add back in double operands
    entire_doc = entire_doc.replace("$plus$", " ++ ")
    entire_doc = entire_doc.replace("$minus$", " -- ")
    entire_doc = entire_doc.replace("$plus_equals$", " += ")
    entire_doc = entire_doc.replace("$not_equals$", " != ")
    entire_doc = entire_doc.replace("$minus_equals$", " -= ")
    entire_doc = entire_doc.replace("$mult_equals$", " *= ")
    entire_doc = entire_doc.replace("$divide_equals$", " /= ")
    entire_doc = entire_doc.replace("$equals$", " == ")
    entire_doc = entire_doc.replace("$left$", " << ")
    entire_doc = entire_doc.replace("$right$", " >> ")

    # remove extra spaces
    entire_doc = ' '.join(entire_doc.split())

    # split document into tokens
    entire_doc = entire_doc.replace(" ", "$replace$")
    tokens_base = entire_doc.split("$replace$")

    # categorize all tokens
    for token in tokens_base:

        try:
            # Token is an int
            int(token)
            tokens_descriptive.append([token, "NUMCONST", line_counter])
            continue
        except:
            # Token is not an int
            try:
                # Token is a float
                float(token)
                tokens_descriptive.append([token, "FLOATCONST", line_counter])
                continue
            except:
                # Token is neither an int nor a float
                pass

        if (token in ["$newline$"]):
            line_counter += 1
        elif (token in ["+", "-"]):
            tokens_descriptive.append([token, "sumop", line_counter])
        elif (token in ["&&"]):
            tokens_descriptive.append([token, "&&", line_counter])
        elif (token in ["||"]):
            tokens_descriptive.append([token, "||", line_counter])
        elif (token in ["!"]):
            tokens_descriptive.append([token, "!", line_counter])
        elif (token in ["?"]):
            tokens_descriptive.append([token, "unaryop", line_counter])
        elif (token in ["*", "/", "%"]):
            tokens_descriptive.append([token, "mulop", line_counter])
        elif (token in ["<=", "<", ">", ">=", "==", "!="]):
            tokens_descriptive.append([token, "relop", line_counter])
        elif (token in ["return"]):
            tokens_descriptive.append([token, "return", line_counter])
        elif (token in single_tokens):
            tokens_descriptive.append([token, token, line_counter])

        elif (token in [
            "auto", "break", "else", "long", "switch", "case", "register",
            "typedef", "extern", "union", "continue", "for", "signed",
            "do", "if", "static", "while", "default", "goto", "sizeof",
            "volatile", "const", "unsigned"
        ]):
            tokens_descriptive.append([token, "keyword", line_counter])
        elif (token in ["#include", "#define"]):
            tokens_descriptive.append([token, "preDirective", line_counter])
        elif (token in [
            "double", "int", "struct", "long", "enum", "char", "void", "float",
            "float", "short"
        ]):
            tokens_descriptive.append([token, "typeSpecifier", line_counter])
        elif (re.match(r"([a-zA-Z0-9\s_\\.\-\(\):])+(.h)$", token)):
            tokens_descriptive.append([token, "fileImport", line_counter])
        elif (re.match(r"^[a-zA-z_][a-zA-Z0-9_]*$", token)):
            tokens_descriptive.append([token, "ID", line_counter])
        elif (token == "$string$"):
            token = strings_array.pop(0)
            tokens_descriptive.append([token, "STRINGCONST", line_counter])
        elif (token == "$char$"):
            token = chars_array.pop(0)
            tokens_descriptive.append([token, "CHARCONST", line_counter])
        else:
            raise Exception(errors.ERR_BAD_TOKEN + " '" + token + "' on line "
                            + str(line_counter))
            # tokens_descriptive.append([token, "UNRECOGNIZED"])

    # for token in tokens_descriptive:
    # 	print(token)

    # Assign unique token IDs so no two tokens are identical
    token_id = 0
    for token in tokens_descriptive:
        token.append(token_id)
        token_id += 1

    return tokens_descriptive

# Parser for compiler frontend
def run_parser(tokens, grammar, look_for_brace=False, root_name="program"):
    tree = Tree()
    # create root node
    root = Node(tag=root_name)
    tree.add_node(root, parent=None)
    num_tokens_to_skip = 0
    list_of_tokens = []

    for i in range(0, len(tokens)):
        if (num_tokens_to_skip > 0):
            num_tokens_to_skip -= 1
            continue
        if (look_for_brace and tokens[i][0] == "}"):
            break
        list_of_tokens.append(tokens[i])    # append token and metadata

        result = check_rules("program", list_of_tokens, grammar) # Verify first parameter is correct
        if (result[0] > 1): #matches more than one possible rule
            continue
        elif (result[0] == 1): #matches one possible rule
            help_fun_tuple = help_func_manager(
                result,
                grammar,
                tokens[i - len(list_of_tokens) + 1:] #may be off by one
            )
            sub_tree = help_fun_tuple[0]
            num_tokens_to_skip = help_fun_tuple[1]
            #may or may not need to subtract one from num_tokes_to_skip
            #print("Hannah: add the sub_tree here to root as a child")
            tree.paste(root.identifier, sub_tree)

            tree.show(key=lambda x: x.identifier, line_type='ascii')
            #call helper function
            list_of_tokens = []
        elif (result[0] == 0):
            #matches zero rules. parser crash
            raise Exception(errors.ERR_NO_RULE + " '" + tokens[i][0] +
                            "' on line " + str(tokens[i][2]))

    return [tree, num_tokens_to_skip]


def help_func_manager(result, grammar, tokens):
    # if (#is preprocessor):
    #     return (None, #something)

    print("Create case for block detection!")
    # Block detection:
    # Advance until encoutner { or }
    # If {: Then call block handler on tokens starting at {
    # If }: Then call parser on tokens between { and }

    if (result[1][0] == "varDeclaration"):
        return help_func_varDeclaration(grammar, tokens)
    if (result[1][0] == "funDeclaration"):
        return help_func_funDeclaration(grammar, tokens)
    if (result[1][0] == "compoundStmt"):
        return help_func_compoundStmt(grammar, tokens)
    if (result[1][0] == "selectionStmt"):
        return help_func_selectionStmt(grammar, tokens)
    if (result[1][0] == "iterationStmt"):
        return help_func_iterationStmt(grammar, tokens)
    if (result[1][0] == "returnStmt"):
        return help_func_return(grammar, tokens)
    # ERROR CASE
    print("Did not account for case: " + result[1][0])
    print("Tokens:", tokens)

def help_func_varDeclaration(grammar, tokens):
    # Called only by the help_func_manager
    # PLACEHOLDER RETURN STATEMENT
    tree = Tree()
    tree.add_node(Node(tag="Placeholder Var Dec"), parent=None)
    return [tree, 0]

def help_func_compoundStmt(grammar, tokens):
    # Called only by the help_func_manager
    # PLACEHOLDER RETURN STATEMENT
    print("Compound:", tokens)
    tree = Tree()
    tree.add_node(Node(tag="Placeholder Compound"), parent=None)
    return [tree, 0]

def help_func_selectionStmt(grammar, tokens):
    # Called only by the help_func_manager
    # PLACEHOLDER RETURN STATEMENT
    tree = Tree()
    tree.add_node(Node(tag="Placeholder Selection"), parent=None)
    return [tree, 0]

def help_func_iterationStmt(grammar, tokens):
    # Called only by the help_func_manager
    # PLACEHOLDER RETURN STATEMENT
    tree = Tree()
    tree.add_node(Node(tag="Placeholder Iterationt"), parent=None)
    return [tree, 0]

print("Go back through and fix all tokens to actually refer to the correct index like tokens[i][0] or tokens[i][1]")
def help_func_return(grammar, tokens):
    tree = Tree()
    return_node = Node(tag=tokens[0][1])
    tree.add_node(return_node, parent=None)

    skip_tokens = 0
    if (tokens[1][0] != ';') :
        expr_help_out = help_func_expression(grammar, tokens[1:])
        tree.paste(return_node.identifier, expr_help_out[0])
        skip_tokens = expr_help_out[1]
        
    return [tree, skip_tokens + 2]

def help_func_expression(grammar, tokens):
    # Called by help_funcs that are called by the manager
    #assert(
    #    (len(tokens) >= 1 and tokens[0][0] == ';') or
    #    len(tokens) >= 2
    #)

    # Find first semi-colon
    semi_colon_index = -1
    for i in range(len(tokens)):
        if tokens[i][0] == ';':
            semi_colon_index = i

    # Find the lowest precedence operator
    lowest_prec_op = []
    op_precedence = {
        "&&":    50,
        "||":    40,
        "relop": 30,
        "mulop": 20,
        "sumop": 10
    }

    for token in tokens:
        if (token[0] == ';'):
            break
        elif (token[1] in op_precedence):
            if (
                (len(lowest_prec_op) == 0) or
                (op_precedence[token[1]] <= op_precedence[lowest_prec_op[1]])
            ):
                lowest_prec_op = token

    if (len(lowest_prec_op) == 0):
        # Check if "expression" is just a single constant
        if (tokens[0][1] == "ID" and tokens[1][1] == "("):
            # Create node with function name
            tree = Tree()
            call_node = Node(tag=tokens[0][0])
            tree.add_node(call_node, parent=None)
            token_skip = 3

            # Children of node are function parameters
            for i in range(2, len(tokens)):
                if (tokens[i][1] == "("):
                    break
                else:
                    token_skip += 1
                    param_node = Node(tag=tokens[i][0])
                    tree.add_node(param_node, parent=param_node)
            return [tree, token_skip]
        elif (
            (
                tokens[0][1] == "NUMCONST" or 
                tokens[0][1] == "FLOATCONST" or
                tokens[0][1] == "CHARCONST" or
                tokens[0][1] == "STRINGCONST" or
                tokens[0][1] == "true" or
                tokens[0][1] == "false" or
                tokens[0][1] == "ID"
            )
        ):
            # Expression is a constant or named variable
            tree = Tree()
            value_node = Node(tag=tokens[0][0])
            tree.add_node(value_node, parent=None)
            return [tree, 1]
        else:
            print("TODO: THROW ERROR")
            print("Tokens:", tokens)
            sys.exit(1)

    # Lowest precedence operator found
    # Lowest precedence operator is root.
    tree = Tree()
    op_node = Node(tag=lowest_prec_op[0])
    tree.add_node(op_node, parent=None)

    # Recursive calls to make left and right subtrees
    tokens_skip = 1

    tokens_l = tokens[:tokens.index(lowest_prec_op)]
    tokens_r = tokens[tokens.index(lowest_prec_op)+1:]

    if (len(tokens_l) > 0):
        expr_l = help_func_expression(grammar, tokens_l)
        tree.paste(op_node.identifier, expr_l[0])
        tokens_skip += expr_l[1]

    if (len(tokens_r) > 0):
        expr_r = help_func_expression(grammar, tokens_r)
        tree.paste(op_node.identifier, expr_r[0])
        tokens_skip += expr_r[1]

    return [tree, tokens_skip]

def help_func_funDeclaration(grammar, tokens):
    #first token is return type
    #the next token is the name
    #the third token is the (
    #sometime after that should be a 
    #)
    assert(len(tokens) >= 4)

    tree = Tree()

    # organization nodes
    return_node = Node(tag="return_type")
    params_node = Node(tag="params")
    body_node = Node(tag="func_body")

    # create root node
    func_root = Node(tag="func:"+tokens[1][0])
    return_type = Node(tag=tokens[0][0])

    # Assemble basic subtree
    tree.add_node(func_root, parent=None)
    tree.add_node(return_node, parent=func_root)
    tree.add_node(params_node, parent=func_root)

    tree.add_node(return_type, parent=return_node)

    # Create and add params nodes
    params = []
    var_case = 0    # 0 = empty, 1 = void, 2 = variables
    for i in range (3, len(tokens), 3):
        if (i == 3 and tokens[i][0] == 'void'):
            var_case = 1
            break
        elif (tokens[i][0] == ")"):
            break
        else:
            try:
                params.append((tokens[i][0], tokens[i+1][0]))
                # i+0 = type
                # i+1 = name
                # i+3 = comma if it exists
                var_case = 2
            except:
                raise Exception(errors.ERR_BAD_FUNC_PAR + " '" + tokens[i][0] +
                                "' on line " + str(tokens[i][2]))
            if (tokens[i+2][0] != ','):
                break

    for param in params:
        type_node = Node(tag=param[0])
        name_node = Node(tag=param[1])

        tree.add_node(type_node, parent=params_node)
        tree.add_node(name_node, parent=type_node)
        #check grammar rules

    # Create and add body 
    body_tokens = []
    skip_tokens = 0
    if (var_case % 3 == 0):
        # Empty parameters
        body_tokens = tokens[5:]
        skip_tokens = 5
        pass
    elif (var_case % 3 == 1):
        # Void parameter
        body_tokens = tokens[6:]
        skip_tokens = 6
        pass
    elif (var_case % 3 == 2):
        # Has paremeters
        body_tokens = tokens[4 + (3*(len(params))):]
        skip_tokens = 4 + (3*(len(params)))
        pass

    parser_out = run_parser(body_tokens, grammar, look_for_brace=True, root_name="func_body") #may be off by one
    body_tree = parser_out[0]
    tree.paste(func_root.identifier, body_tree)

    return [tree, skip_tokens + parser_out[1]]

def help_func_block(grammar, tokens):

    print("FUNCTION TO BE REVISED. SEE COMMENTS - help_func_block(), frontend.py")
    # How does the subtree for this block get added to the parse tree?
    # Parse tree could be added to the passed parameters, or
    # Subtree could be returned as function result

    # Should return (tree, tokens to skip)

    for i in range(0, len(tokens)):
        if (num_tokens_to_skip > 0):
            num_tokens_to_skip -= 1
            continue
        list_of_tokens.append(tokens[i])

        result = check_rules(tokens[i][1], list_of_tokens, grammar)
        if (result[0] > 1): #matches more than one possible rule
            continue
        elif (result[0] == 1): #matches one possible rule
            help_fun_tuple = help_func_manager(
                result,
                grammar,
                tokens[i - len(list_of_tokens):-1] #may be off by one
            )
            sub_tree = help_fun_tuple[0]
            num_tokens_to_skip = help_fun_tuple[1]
            #may or may not need to subtract one from num_tokes_to_skip
            #print("Hannah: add the sub_tree here to root as a child")
            tree.paste(root.identifier, sub_tree)
            #call helper function
            list_of_tokens = []
        elif (result[0] == 0):
            #matches zero rules. parser crash
            raise Exception(errors.ERR_NO_RULE + " '" + tokens[i][0] +
                            "' on line " + str(tokens[i][2]))

# checks if the current token should result in:
# rejection, (0 matches)
# possible acceptance, (>=1 match)
# accept, (1 match and complete rule)
def check_rules(node_rule, tokens, grammar):
    # print(tokens)
    # print(grammar["funDeclaration"])
    stack_possible_matches = []
    stack_actual_matches = []

    for elem in grammar:
        for rule in grammar[elem]:
            if (rule[:len(tokens)] == get_some_elems_of_list(tokens, 1)):
                if elem not in stack_possible_matches:
                    stack_possible_matches.append(elem)
                # print(tokens)

    for elem in stack_possible_matches:
        # if that rule can appear after cur_node
        if (is_possible_rule(node_rule, elem, grammar)):
            stack_actual_matches.append(elem)

    '''if (len(stack_actual_matches) == 1):
        print(stack_actual_matches)'''

        # print("accept this line")
        # print("fix handeling of blocks and things in parenthesies. That is why"
        # " nothing is accepted after a funDeclaration")
    return ((len(stack_actual_matches), stack_actual_matches))


# checks if the current token is allwed after the previous token
def is_possible_rule(node_rule, match, grammar):
    stack = []
    tmp_rules = grammar[node_rule]
    for elem in tmp_rules:
        stack.append(elem)
    while (len(stack) != 0):
        elem = stack.pop()
        index = get_index_in_dict(grammar, elem)
        i = 0
        for key, value in grammar.items():
            if (i == index):
                break
            for rule in value:
                # print(elem)
                if (rule == elem):
                    stack.append(key)
                    return 1
            i = i + 1


# gets index of key in a ordered dictionary
def get_index_in_dict(grammar, match):
    i = 0
    for key, value in grammar.items():
        if (key == match):
            return i
        i = i + 1


# gets elements of list of lists by shared index
def get_some_elems_of_list(input, n):
    return [item[n] for item in input]


# parses a input grammar file and outputs
# a properly formated dictionary
def parse_grammar(grammar_file):
    grammar = OrderedDict()
    for line in grammar_file:
        line = line.replace("\n", "")
        tmp_list = line.split("~")
        values = tmp_list[1]
        values = ' '.join(values.split())
        values = values.split("|")
        for i in range(0, len(values)):
            values[i] = ' '.join(values[i].split())
            values[i] = values[i].split(" ")
            values[i] = [j for j in values[i] if j]
        grammar[' '.join(tmp_list[0].split())] = values
    return(grammar)