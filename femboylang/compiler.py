from .lexer import Lexer
from .parser import Parser
from .semantic import SemanticAnalyzer
from .transpiler import Transpiler

class Compiler:
    def __init__(self, source: str):
        self.source = source

    def compile(self):
        # 1. Lexing
        lexer = Lexer(self.source)
        tokens = lexer.tokenize()

        # 2. Parsing
        parser = Parser(tokens)
        ast = parser.parse()

        # 3. Semantic Analysis
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)

        # 4. Transpilation
        transpiler = Transpiler()
        python_code = transpiler.transpile(ast)

        return python_code
