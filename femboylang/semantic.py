from .ast_nodes import *

class SemanticAnalyzer:
    def __init__(self):
        self.scopes = [{}] # Stack of symbol tables

    def error(self, message):
        raise Exception(f"Semantic Error: {message}")

    def analyze(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        if isinstance(node, list):
            for item in node:
                self.analyze(item)
        elif hasattr(node, '__dict__'):
            for value in node.__dict__.values():
                if isinstance(value, (ASTNode, list)):
                    self.analyze(value)

    def visit_Program(self, node: Program):
        for stmt in node.statements:
            self.analyze(stmt)

    def visit_VariableDeclaration(self, node: VariableDeclaration):
        self.analyze(node.value)
        self.scopes[-1][node.name] = 'variable'

    def visit_FunctionDeclaration(self, node: FunctionDeclaration):
        self.scopes[-1][node.name] = 'function'
        # New scope for function
        new_scope = {param: 'variable' for param in node.params}
        self.scopes.append(new_scope)
        for stmt in node.body:
            self.analyze(stmt)
        self.scopes.pop()

    def visit_Identifier(self, node: Identifier):
        for scope in reversed(self.scopes):
            if node.name in scope:
                return
        # We'll allow global builtins or just report error
        # For now, let's keep it simple
        pass

    def visit_CallExpression(self, node: CallExpression):
        # Check if function exists (optional for now)
        for arg in node.arguments:
            self.analyze(arg)

    def visit_IfStatement(self, node: IfStatement):
        self.analyze(node.condition)
        for stmt in node.then_branch:
            self.analyze(stmt)
        if node.else_branch:
            for stmt in node.else_branch:
                self.analyze(stmt)

    def visit_LoopStatement(self, node: LoopStatement):
        self.analyze(node.condition)
        for stmt in node.body:
            self.analyze(stmt)
