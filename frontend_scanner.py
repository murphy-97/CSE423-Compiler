# CSE423 Compilers
# frontend_scanner.py: tokenizer used by the frontend

# Import non-project modules
import re
# Import project modules
import errors

# Scanner/tokenizer for compiler frontend
def run_scanner(code_lines):
    # Reads source code and returns list of tokens"""

    input = code_lines
    entire_doc = ""
    replace_space_array = [";", "(", ")", "{", "}", "=", "<", ">", "+", "-",
                           ","]
    single_tokens = ["(", ")", "{", "}", ",", ";", "=", "++", "--", "+=", "-=",
                     "*=", "/=", "%=", "true", "false"]

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
    entire_doc = entire_doc.replace("%=", "$mod_equals$")
    entire_doc = entire_doc.replace("==", "$equals$")
    entire_doc = entire_doc.replace("<<", "$left$")
    entire_doc = entire_doc.replace(">>", "$right$")
    entire_doc = entire_doc.replace("<=", "$lesseq$")
    entire_doc = entire_doc.replace(">=", "$greateq$")
    entire_doc = entire_doc.replace("+", "$plus_sm$")
    entire_doc = entire_doc.replace("-", "$minus_sm$")
    entire_doc = entire_doc.replace("*", "$times_sm$")
    entire_doc = entire_doc.replace("/", "$divide_sm$")
    entire_doc = entire_doc.replace("%", "$mod_sm$")

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
    entire_doc = entire_doc.replace("$mod_equals$", " %= ")
    entire_doc = entire_doc.replace("$equals$", " == ")
    entire_doc = entire_doc.replace("$left$", " << ")
    entire_doc = entire_doc.replace("$right$", " >> ")
    entire_doc = entire_doc.replace("$lesseq$", " <= ")
    entire_doc = entire_doc.replace("$greateq$", " >= ")
    entire_doc = entire_doc.replace("$plus_sm$", " + ")
    entire_doc = entire_doc.replace("$minus_sm$", " - ")
    entire_doc = entire_doc.replace("$times_sm$", " * ")
    entire_doc = entire_doc.replace("$divide_sm$", " / ")
    entire_doc = entire_doc.replace("$mod_sm$", " % ")

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
        elif (token in ["=", "+=", "-=", "*=", "/=", "%="]):
             tokens_descriptive.append([token, token, line_counter])
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
        elif (token in ["<<", ">>"]):
            tokens_descriptive.append([token, "shiftop", line_counter])
        elif (token in ["*", "/", "%"]):
            tokens_descriptive.append([token, "mulop", line_counter])
        elif (token in ["<=", "<", ">", ">=", "==", "!="]):
            tokens_descriptive.append([token, "relop", line_counter])
        elif (token in ["return"]):
            tokens_descriptive.append([token, "return", line_counter])
        elif (token in single_tokens):
            tokens_descriptive.append([token, token, line_counter])
        elif (token in [ "if", "while" ]):
            tokens_descriptive.append([token, token, line_counter])
        elif (token in [
            "auto", "break", "else", "long", "switch", "case", "register",
            "typedef", "extern", "union", "continue", "for", "signed",
            "do", "static", "default", "goto", "sizeof", "volatile", "const",
            "unsigned"
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
