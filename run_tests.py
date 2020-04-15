# Attempts to compile all ./tests/*.c files and reports failures

# Import non-project modules
from os import listdir
from os.path import isfile, join
# Import project modules
import compiler

if __name__ == "__main__":
    test_dir = "./tests/"
    tests = [f for f in listdir(test_dir) if
        isfile(join(test_dir, f)) and
        f[-2:] == '.c' and
        f[:2] != '.#'
    ]

    tests_passed = 0
    tests_attempted = 0
    failed_tests = []

    for t in tests:
        tests_attempted += 1
        try:
            compiler.main(['compiler.py', '-i', 'tests/' + t])
            tests_passed += 1
        except Exception as e:
            failed_tests.append(t)

    # Report results
    print("=== TEST RESULTS ===")
    print("Passed " + str(tests_passed) + "/" + str(tests_attempted) + " tests")
    if (len(failed_tests) > 0):
        print("Failed tests:")
        for t in failed_tests:
            print("  ", t)

