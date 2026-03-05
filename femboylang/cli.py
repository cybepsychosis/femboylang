import sys
import argparse
import os
from .compiler import Compiler

def run():
    parser = argparse.ArgumentParser(description="femboylang CLI")
    parser.add_argument("command", choices=["run", "compile"], help="Command to execute")
    parser.add_argument("filename", help="Path to .fml file")
    
    args = parser.parse_args()

    if not args.filename.endswith(".fml"):
        print(f"Error: {args.filename} is not a .fml file")
        sys.exit(1)

    if not os.path.exists(args.filename):
        print(f"Error: File {args.filename} not found")
        sys.exit(1)

    with open(args.filename, "r") as f:
        source = f.read()

    compiler = Compiler(source)
    try:
        python_code = compiler.compile()
        
        if args.command == "compile":
            output_file = args.filename.replace(".fml", ".py")
            with open(output_file, "w") as f:
                f.write(python_code)
            print(f"Compiled to {output_file}")
        elif args.command == "run":
            exec(python_code)
    except Exception as e:
        print(f"Error: {e}")
        # sys.exit(1)

if __name__ == "__main__":
    run()
