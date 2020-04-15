# Import non-project modules
import sys
sys.path.append('treelib-1.5.5/')
from treelib import Node, Tree
from collections import OrderedDict
# Import project modules
import errors

# Global variables
__symbol_tables = {}  # Key = func name, Value = symbol table

# Parser for compiler frontend
def run_parser(tokens, grammar, look_for_brace=False, root_name="program", clear_symbol_table=False):
    # Create dictionary of symbol tables
    global __symbol_tables
    if (clear_symbol_table):
        __symbol_tables = {}
    # Create base abstract syntax tree
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

        result = check_rules("program", list_of_tokens, grammar)
        if (result[0] > 1): #matches more than one possible rule
            continue
        elif (result[0] == 1): #matches one possible rule
            help_fun_tuple = help_func_manager(
                result,
                grammar,
                tokens[i - len(list_of_tokens) + 1:]
            )
            sub_tree = help_fun_tuple[0]
            num_tokens_to_skip = help_fun_tuple[1] - len(list_of_tokens)

            tree.paste(root.identifier, sub_tree)
            #call helper function
            list_of_tokens = []
        elif (result[0] == 0):
            #matches zero rules. parser crash
            tree.show(key=lambda x: x.identifier, line_type='ascii')
            print("ERRONEOUS RESULT:", result)
            print("ERRONEOUS TOKEN LIST:", list_of_tokens)
            raise Exception(errors.ERR_NO_RULE + " '" + tokens[i][0] +
                            "' on line " + str(tokens[i][2]))

    return [tree, num_tokens_to_skip, __symbol_tables]


def help_func_manager(result, grammar, tokens):
    # if (#is preprocessor):
    #     return (None, #something)

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

    tokens_skip = 0
    # Remove leading and trailing ( and )
    while (len(tokens) > 0 and (tokens[0][0] == '(' or tokens[0][0] == ')')):
        tokens.pop(0)
        tokens_skip += 1
    while (len(tokens) > 0 and (tokens[-1][0] == '(' or tokens[-1][0] == ')')):
        tokens.pop()
        tokens_skip += 1

    # Check for subexpression denoted by parentheses
    op_depth = []
    depth = 0
    paren_open = -1
    paren_close = -1
    for i in range(len(tokens)):
        if (tokens[i][0] == ';'):
            break   # End of expression
        elif (tokens[i][0] == '('):
            depth += 1
            paren_open = i
        elif (tokens[i][0] == ')'):
            paren_close = i
            depth -= 1
        op_depth.append(depth)
    
    # Find the lowest precedence operator
    lowest_prec_op = []
    op_precedence = {
        "&&":    50,
        "||":    40,
        "relop": 30,
        "mulop": 20,
        "sumop": 10,
        "=": 0,
        "+=": 0,
        "-=": 0,
        "*=": 0,
        "\=": 0,
        "%=": 0,
    }

    for token in tokens:
        if (token[0] == ';'):
            break
        elif (token[1] in op_precedence):

            if (len(lowest_prec_op) == 0):
                lowest_prec_op = token
            else:
                cur_token_depth = op_depth[tokens.index(token)]
                lowest_prec_depth = op_depth[tokens.index(lowest_prec_op)]

                if (cur_token_depth < lowest_prec_depth):
                    # Higher depth guarantees replacement
                    lowest_prec_op = token
                elif (
                    cur_token_depth == lowest_prec_depth and
                    op_precedence[token[1]] <= op_precedence[lowest_prec_op[1]]
                ):
                    # To replace, must be on same depth and lower precedence
                    lowest_prec_op = token


    if (len(lowest_prec_op) == 0):
        # Check if "expression" is just a single constant
        if (len(tokens) > 1 and tokens[0][1] == "ID" and tokens[1][1] == "("):
            # Create node with function name
            tree = Tree()
            call_node = Node(tag="func:"+tokens[0][0])
            tree.add_node(call_node, parent=None)
            tokens_skip += 2

            # Children of node are function parameters
            # Iterate through tokens to find each parameter
            # Parameters split on ',' with depth=0
            depth = 0
            token_depth = []
            end_point = -1

            for i in range(2, len(tokens)):
                tokens_skip += 1
                if (tokens[i][0] == "("):
                    depth += 1
                elif (tokens[i][0] == ")"):
                    depth -= 1
                
                token_depth.append(depth)

                if (depth < 0):
                    # End ) found
                    end_point = i
                    break

            if (end_point < 0):
                end_point = len(tokens)
                #raise Exception("No ending ')' for function call '" +
                #    tokens[0][0] + "'")

            # Find split points for the expressions
            split_points = [2]
            for i in range(len(token_depth)):
                if (token_depth[i] == 0 and tokens[i+2][0] == ','):
                    split_points.append(i+3)
            
            split_points.append(end_point)

            func_params = []
            for i in range(len(split_points)-1):
                print([split_points[i], split_points[i+1]])
                func_params.append(tokens[split_points[i]:split_points[i+1]])

            # Add parameters to tree
            for p in func_params:
                print("Parameter:", p)
                # Needs to call expression handler to evaluate parameters
                # - Currently, operators in function calls are lower prec than the function for some reason
                # - Exceptions caused by nesting function calls
                param_node = Node(tag=p[0][0])
                tree.add_node(param_node, parent=call_node)

            return [tree, tokens_skip]
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
            tokens_skip += 1
            tree = Tree()
            value_node = Node(tag=tokens[0][0])
            tree.add_node(value_node, parent=None)
            return [tree, tokens_skip]
        else:
            raise Exception("Unknown token sequence: " + str(tokens))

    # Lowest precedence operator found
    # Lowest precedence operator is root.
    tree = Tree()
    op_node = Node(tag=lowest_prec_op[0])
    tree.add_node(op_node, parent=None)

    # Recursive calls to make left and right subtrees
    tokens_skip += 1

    tokens_l = tokens[:tokens.index(lowest_prec_op)]
    tokens_r = tokens[tokens.index(lowest_prec_op)+1:]

    has_tokens_l = False
    for token in tokens_l:
        if (token[0] != '(' and token[0] != ')'):
            has_tokens_l = True
            break

    has_tokens_r = False
    for token in tokens_r:
        if (token[0] != '(' and token[0] != ')'):
            has_tokens_r = True
            break

    if (len(tokens_l) > 0 and has_tokens_l):
        expr_l = help_func_expression(grammar, tokens_l)
        tree.paste(op_node.identifier, expr_l[0])
        tokens_skip += expr_l[1]
    else:
        tokens_skip += len(tokens_l)

    if (len(tokens_r) > 0 and has_tokens_r):
        expr_r = help_func_expression(grammar, tokens_r)
        tree.paste(op_node.identifier, expr_r[0])
        tokens_skip += expr_r[1]
    else:
        tokens_skip += len(tokens_r)

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
    func_name = tokens[1][0]
    func_root = Node(tag="func:"+func_name)
    return_type = Node(tag=tokens[0][0])
    # Create symbol subtable
    __symbol_tables[func_name] = {}

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

    #call help_func_block
    #parser_out = run_parser(body_tokens, grammar, look_for_brace=True, root_name="func_body") #may be off by one
    block_out = help_func_block(grammar, body_tokens, root_name="func_body", function=func_name)
    body_tree = block_out[0]
    skip_tokens += block_out[1]
    tree.paste(func_root.identifier, body_tree)

    return [tree, skip_tokens]

def help_func_block(grammar, tokens, root_name="block", function=None):

    #go line by line
    #if }
        #return tree
    #if {
        #recursive help_func_block
    #grab up to till first ;
        #call expression handeler on that sub list
        #returns a tree which is appended

    tree = Tree()
    root_node = Node(tag=root_name)
    tree.add_node(root_node, parent=None)

    func_flag_no_init = 0
    func_flag_init = 0
    func_flag = 0
    front_index = 0
    num_tokens_to_skip = 0

    i = 0
    while (i < len(tokens)):
        if (tokens[i][0] == "}"):
            return [tree, num_tokens_to_skip + 1]

        elif (tokens[i][0] == "{"):
            result = help_func_block(grammar, tokens[i+1:], function=function)
            
            front_index += 1 + result[1]
            i += 1 + result[1]
            num_tokens_to_skip += 1 + result[1]

            tree.paste(root_node.identifier, result[0])

        elif (tokens[i][0] in ["if", "while"]):
            if_node = Node(tag=tokens[i][0])
            if_cond = Node(tag="condition")

            tree.add_node(if_node, parent=root_node)
            tree.add_node(if_cond, parent=if_node)

            first_bracket = -1
            for token in tokens[i:]:
                if (token[0] == '{'):
                    first_bracket = tokens.index(token)
                elif (token[0] == '}'):
                    break
            if (first_bracket < 0):
                raise Exception(tokens[i][0] + " without body '{' on line " + str(tokens[i][2]))

            cond_result = help_func_expression(grammar, tokens[i+2:first_bracket-1])
            body_result = help_func_block(grammar, tokens[first_bracket+1:], root_name="condition_body", function=function)

            # Increment i, num_tokens_to_skip, and front_index
            if_skip = 1    # if/while
            if_skip += 1   # opening bracket
            if_skip += 2   # parens
            if_skip += cond_result[1]
            if_skip += body_result[1]

            num_tokens_to_skip += if_skip
            front_index += if_skip
            i += if_skip

            tree.paste(if_cond.identifier, cond_result[0])
            tree.paste(if_node.identifier, body_result[0])

        elif (tokens[i][0] == "return"):
            result = help_func_return(grammar, tokens[i:])
            front_index += result[1]
            i += result[1]
            num_tokens_to_skip += result[1]

            tree.paste(root_node.identifier, result[0])

        elif (tokens[i][0] == ";"):
            back_index = i

            expr_tokens = tokens[front_index:back_index]

            # Remove leading and trailing ( and )
            while (len(expr_tokens) > 0 and (expr_tokens[0][0] == '(' or expr_tokens[0][0] == ')')):
                expr_tokens.pop(0)
                num_tokens_to_skip += 1
            while (len(expr_tokens) > 0 and (expr_tokens[-1][0] == '(' or expr_tokens[-1][0] == ')')):
                expr_tokens.pop(-1)
                num_tokens_to_skip += 1

            if (len(expr_tokens) > 0):
                if (len(expr_tokens) == 2 and expr_tokens[0][1] == 'typeSpecifier' and expr_tokens[1][1] == 'ID'):
                    func_flag = 1
                    func_flag_no_init = 1
                    # print("This is a variable declaration with no intilization")
                    var_type = expr_tokens[0][0]
                    var_name = expr_tokens[1][0]
                    __symbol_tables[function][var_name] = var_type
                    expr_tokens.pop(0)
                elif (len(expr_tokens) > 2 and expr_tokens[0][1] == 'typeSpecifier' and expr_tokens[1][1] == 'ID' and expr_tokens[2][1] == '='):
                    func_flag = 1
                    # print("This is a variable declaration with intilization")
                    var_type = expr_tokens[0][0]
                    var_name = expr_tokens[1][0]
                    __symbol_tables[function][var_name] = var_type
                    expr_tokens.pop(0)
                if (func_flag == 1):
                    tmp_tree = Tree()
                    tmp_tree_root = Node(tag=var_type)
                    tmp_tree.add_node(tmp_tree_root, parent=None)
                    tmp_tree.add_node(Node(tag=var_name), parent=tmp_tree_root)

                result = help_func_expression(grammar, expr_tokens)
                
                if (func_flag == 1):
                    result[1] += 1
                front_index = back_index + 1
                i += 1
                num_tokens_to_skip += 1 + result[1]
                if (func_flag_no_init != 1):
                    tree.paste(root_node.identifier, result[0])
                if (func_flag == 1):
                    # pass
                    tree.paste(root_node.identifier, tmp_tree)
                func_flag_no_init = 0
                func_flag_init = 0
                func_flag = 0
                tmp_tree = None

        else:
            i += 1

    # Iterated through tokens without closing '}'
    raise Exception(errors.ERR_NO_BLOCK_END + " on line " + str(tokens[i-1][2]))

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
