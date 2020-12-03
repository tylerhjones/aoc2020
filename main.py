import sys
import importlib
import pretty_errors

if __name__ == "__main__":
    day = sys.argv[1]
    print("Running day: "+day)
    my_module = importlib.import_module(day)
    my_module.main(day+'/input.txt')