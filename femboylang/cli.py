import sys
import argparse
import os
import time
from typing import Optional
from .compiler import Compiler
from .logo import LOGO

# Optional rich integration for enhanced CLI experience
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.table import Table
    from rich.theme import Theme
    from rich.progress import Progress, SpinnerColumn, TextColumn
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# FemboyLang brand theme
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "fml": "bold magenta",
})

if HAS_RICH:
    console = Console(theme=custom_theme)
else:
    class FakeConsole:
        def print(self, *args, **kwargs):
            if "style" in kwargs:
                style = kwargs.pop("style")
                if "red" in style: print("ERROR:", *args)
                elif "yellow" in style: print("WARNING:", *args)
                elif "green" in style: print("SUCCESS:", *args)
                else: print(*args)
            else:
                print(*args)
    console = FakeConsole()

VERSION = "0.1.0"

def show_banner():
    """Displays the FemboyLang banner and version."""
    if HAS_RICH:
        console.print(f"[magenta]{LOGO}[/magenta]")
        banner_text = "[fml]FEMBOYLANG[/fml] [white]v" + VERSION + "[/white]\n[italic]A modern, cute and expressive programming language[/italic]"
        console.print(Panel(banner_text, border_style="magenta", expand=False))
    else:
        print(LOGO)
        print(f"--- FEMBOYLANG v{VERSION} ---")

def format_error(filename: str, source: str, message: str, line: int = 1, col: int = 1):
    """Prints a professional error snippet with source context."""
    console.print(f"\n[error]Error:[/error] {message}", style="error")
    console.print(f"  [info]at[/info] [white]{filename}:{line}:{col}[/white]")
    
    lines = source.splitlines()
    if 0 < line <= len(lines):
        error_line = lines[line - 1]
        
        # Show one line before and after for context
        start_idx = max(0, line - 2)
        end_idx = min(len(lines), line + 1)
        
        for i in range(start_idx, end_idx):
            ln_num = i + 1
            ln_content = lines[i]
            prefix = "> " if ln_num == line else "  "
            console.print(f"[dim]{ln_num:4} |[/dim] {prefix}{ln_content}")
            if ln_num == line:
                pointer = " " * (col + 7) + "^"
                console.print(f"[error]{pointer}[/error]")
    console.print("")

def cmd_run(args):
    """Entry point for the 'run' command."""
    if not os.path.exists(args.filename):
        console.print(f"File [white]{args.filename}[/white] not found", style="error")
        return

    def _run_once():
        with open(args.filename, "r") as f:
            source = f.read()

        try:
            if HAS_RICH and not args.quiet:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    transient=True,
                ) as progress:
                    progress.add_task(description="Lexing...", total=None)
                    time.sleep(0.05)
                    
                    compiler = Compiler(source)
                    
                    progress.add_task(description="Parsing & Analyzing...", total=None)
                    python_code = compiler.compile()
            else:
                compiler = Compiler(source)
                python_code = compiler.compile()

            console.print(f"[info]Running [/info][white]{args.filename}[/white]...")
            exec(python_code, {"__name__": "__main__"})
            console.print("[success]Success![/success]")
            
        except SyntaxError as e:
            msg = str(e)
            import re
            match = re.search(r"at line (\d+), (?:column|col) (\d+)", msg)
            line, col = 1, 1
            if match:
                line = int(match.group(1))
                col = int(match.group(2))
            
            format_error(args.filename, source, msg, line, col)
            if not args.watch: sys.exit(1)
        except Exception as e:
            console.print(f"Runtime Error: {e}", style="error")
            if not args.watch: sys.exit(1)

    if args.watch:
        console.print(f"[info]Watching [white]{args.filename}[/white] for changes...[/info]")
        last_mtime = os.path.getmtime(args.filename)
        _run_once()
        try:
            while True:
                time.sleep(0.1)
                mtime = os.path.getmtime(args.filename)
                if mtime != last_mtime:
                    last_mtime = mtime
                    console.clear()
                    show_banner()
                    console.print(f"[info]Change detected, re-running...[/info]")
                    _run_once()
        except KeyboardInterrupt:
            console.print("\n[info]Stopped watching.[/info]")
    else:
        _run_once()

def cmd_build(args):
    """Entry point for the 'build' command."""
    if not os.path.exists(args.filename):
        console.print(f"File [white]{args.filename}[/white] not found", style="error")
        return

    output_file = args.output or args.filename.replace(".fml", ".py")
    
    with open(args.filename, "r") as f:
        source = f.read()

    try:
        compiler = Compiler(source)
        python_code = compiler.compile()
        
        with open(output_file, "w") as f:
            f.write(python_code)
        
        console.print(f"Successfully compiled [white]{args.filename}[/white] to [white]{output_file}[/white]", style="success")
    except Exception as e:
        console.print(f"Compilation Failed: {e}", style="error")
        sys.exit(1)

def cmd_init(args):
    """Initializes a new FemboyLang project."""
    config_path = "fmlconfig.json"
    if os.path.exists(config_path):
        console.print(f"Config file [white]{config_path}[/white] already exists", style="warning")
        return

    import json
    default_config = {
        "name": "my-femboy-project",
        "version": "0.1.0",
        "entry": "main.fml",
        "compilerOptions": {
            "strict": True,
            "outDir": "./dist"
        }
    }
    
    with open(config_path, "w") as f:
        json.dump(default_config, f, indent=4)
    
    console.print(f"Initialized new project in [white]{config_path}[/white]", style="success")

def run():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="FemboyLang CLI", add_help=False)
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    run_parser = subparsers.add_parser("run", help="Compile and run a .fml file")
    run_parser.add_argument("filename", help="The .fml file to run")
    run_parser.add_argument("-q", "--quiet", action="store_true", help="Don't show compilation progress")
    run_parser.add_argument("-w", "--watch", action="store_true", help="Watch file for changes")

    build_parser = subparsers.add_parser("build", help="Compile a .fml file to Python")
    build_parser.add_argument("filename", help="The .fml file to build")
    build_parser.add_argument("-o", "--output", help="Output file name")

    subparsers.add_parser("init", help="Initialize a new FemboyLang project")
    subparsers.add_parser("version", help="Show FemboyLang version")
    subparsers.add_parser("help", help="Show this help message")

    args = parser.parse_args()

    if args.command == "version":
        show_banner()
    elif args.command == "run":
        cmd_run(args)
    elif args.command == "build":
        cmd_build(args)
    elif args.command == "init":
        cmd_init(args)
    elif args.command or len(sys.argv) == 1:
        show_banner()
        print("\nAvailable commands:")
        print("  run <file>    Compile and run a .fml file")
        print("  build <file>  Compile a .fml file to Python")
        print("  init          Initialize a new project")
        print("  version       Show version information")
        print("  help          Show this message")
        if args.command == "help":
            print("\nOptions for 'run':")
            print("  -w, --watch   Watch for file changes and re-run automatically")
            print("  -q, --quiet   Suppress compilation progress")
    else:
        parser.print_help()

if __name__ == "__main__":
    run()
