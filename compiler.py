# CSE423 Compilers
# compiler.py: main file for C-to-ASM compiler implemented in Python

# Import non-project modules
import sys
import getopt
# Import project modules
import frontend
import optimizer
import backend
import errors
# Used for debugging
import traceback

# Debug contstant for debug statements
DEBUG = True

### Main function for running this module
def main(args=None):
    if (args is None):
        args = sys.argv
        
    """Interprets command line arguments and runs compilers
    Command line arguments:
    -i  Input file name
    -o  Output file name
    -h  Prints usage statement
    """

    # Read in input file and output file from user command line options
    i_file = ""
    o_file = ""

    # Command line options/arguments
    opt_print_scn = False   # Print scanner output in run_frontend()
    opt_print_prs = False   # Print parser output in run_frontend()
    opt_print_ir = False    # Print IR output in run_frontend()
    opt_print_opt = False   # Print optimizer output in this function
    opt_print_asm = False   # Print backend output in this function

    try:
        # Omit first argument (module name) by list slice
        opts, _ = getopt.getopt(
            args[1:],
            "hi:o:",
            [
                # File I/O options
                "i_file=",      # Specify input file
                "o_file=",      # Specify output file
                # Print statement options
                "p-scn",        # Print scanner output
                "p-prs",        # Print parser output
                "p-ir",         # Print IR output
                "p-opt",        # Print optimizer output
                "p-asm"         # Print backend output
            ]
        )
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

        elif opt == '--p-scn':
            opt_print_scn = True

        elif opt == '--p-prs':
            opt_print_prs = True

        elif opt == '--p-ir':
            opt_print_ir = True

        elif opt == '--p-opt':
            opt_print_opt = True

        elif opt == '--p-asm':
            opt_print_asm = True

    # Require input file
    if not i_file:
        print("Error: " + errors.ERR_NO_INPUT)
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
                    code_ir = frontend.run_frontend(
                        code_source,
                        opt_print_scn,  # Command line arg: print scanner out
                        opt_print_prs,  # Command line arg: print parser out
                        opt_print_ir    # Command line arg: print IR out
                    )

                    print('\nOptimizing...')
                    code_ir = optimizer.run_optimizer(code_ir)

                    if (opt_print_opt):
                        print("====== OPTIMZED IR OUTPUT ==")
                        for line in code_ir:
                            print(line)

                    code_source = backend.run_backend(code_ir)
                    if (opt_print_asm):
                        print("====== ASM BUILDER OUTPUT ==")
                        print(code_source)
                    # !! END MAIN COMPILER FUNCTIONALITY !!

                    # Write compiled file to disk
                    code_out.write(str(code_source)) 

            except OSError as e:
                print("OS Error: " + str(e))
                raise e     # Raise for test file
            except Exception as e:
                print("Failed to compile '{}".format(i_file))
                print("Error: " + str(e))
                if (DEBUG):
                    track = traceback.format_exc()
                    print(track)
                raise e     # Raise for test file

    except OSError as e:
        print("OS Error: " + str(e))
        raise e     # Raise for test file

### Prints usage for the module
def usage():
    """Prints module usage statement"""
    print("\nUsage: python compiler.py -i 'input-file'\n")
    
    print(
        "Optional arguments:\n" +
        " -o       Output file. Requires argument 'output-file'\n" +
        " -h       Prints usage statement\n" +
        " --p-scn  Prints scanner output\n" +
        " --p-prs  Prints parser output\n" +
        " --p-ir   Prints IR output\n" +
        " --p-opt  Prints optimized IR output\n" +
        " --p-asm  Prints ASM output"
    )

    print("If no ouptut file is specified, output written is to 'input-file'.ASM")

# Boilerplate for calling main by running this module
if __name__ == "__main__":
    main()