from .lexer import Lexer
from .parser import Parser
from .semantic import SemanticAnalyzer
from .transpiler import Transpiler

class Compiler:
    """The main entry point for the FemboyLang compilation pipeline."""

    def __init__(self, source: str):
        self.source = source

    def compile(self) -> str:
        """Runs the full compilation pipeline: Lexing -> Parsing -> Semantic Analysis -> Transpilation."""
        # Lexical analysis
        lexer = Lexer(self.source)
        tokens = lexer.tokenize()

        # Syntax analysis
        parser = Parser(tokens)
        ast = parser.parse()

        # Semantic analysis
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)

        # Transpilation to Python
        transpiler = Transpiler()
        return transpiler.transpile(ast)
