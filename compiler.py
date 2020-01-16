# CSE423 Compilers
# compiler.py: main file for C-to-ASM compiler implemented in Python

# Import non-project modules
import sys
import getopt
# Import project modules
import frontend
import optimizer
import backend

# Debug contstant for debug statements
DEBUG = True

### Main function for running this module
def main():
    """Interprets command line arguments and runs compilers
    Command line arguments:
    -i  Input file name
    -o  Output file name
    -h  Prints usage statement
    """

    # Read in input file and output file from user command line options
    i_file = ""
    o_file = ""

    try:
        # Omit first argument (module name) by list slice
        opts, args = getopt.getopt(sys.argv[1:],"hi:o:",["i_file=","o_file="])
    except getopt.GetoptError:
        usage()
        sys.exit(1)

    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit(0)
            
        elif opt in ("-i", "--i_file"):
            i_file = arg

        elif opt in ("-o", "--o_file"):
            o_file = arg

    # Require input file
    if not i_file:
        print("ERROR: Input file not specified")
        usage()
        sys.exit(1)

    # If user did not specify output file, assume i-file.ASM
    if not o_file:
        o_file = i_file + ".ASM"

    # DEBUG: Print command line arguments to the user
    if DEBUG:
        print("i_file = " + i_file)
        print("o_file = " + o_file)

    # Read in input file
    try:
        with open(i_file, "r") as code_source:
            try:
                with open(o_file, "w") as code_out:
                    # code_source acts like a list of lines of code from i_file
                    # use code_out.write("ASM goes here") to write new code
                    
                    # !! MAIN COMPILER FUNCTIONALITY CALLED HERE !!
                    code_source = frontend.run_frontend(code_source)
                    code_source = optimizer.run_optimizer(code_source)
                    code_source = backend.run_backend(code_source)
                    # !! END MAIN COMPILER FUNCTIONALITY !!

                    # Write compiled file to disk
                    for line in code_source:
                        code_out.write(line)

            except OSError:
                print("Failed to write output file '{}'".format(o_file))
            except:
                print("Failed to compile '{}".format(i_file))
    except OSError:
        print("Failed to open input file '{}'".format(i_file))

### Prints usage for the module
def usage():
    """Prints module usage statement"""
    print("Usage: python compiler -i 'input-file'\n")
    
    print(
        "Optional arguments:\n" +
        "-o  Output file. Requires argument"
        "-h  Prints usage statement"
    )

# Boilerplate for calling main by running this module
if __name__ == "__main__":
    main()