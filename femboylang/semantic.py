from typing import List, Dict, Any, Union, Optional
from .ast_nodes import *

class SemanticAnalyzer:
    """Performs semantic analysis on the AST, such as symbol table management."""

    def __init__(self):
        self.scopes: List[Dict[str, str]] = [{}] # Symbol table stack

    def error(self, message: str):
        raise Exception(f"Semantic Error: {message}")

    def analyze(self, node: Any):
        """Dispatches node to its corresponding visitor method."""
        if isinstance(node, list):
            for item in node:
                self.analyze(item)
            return

        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: Any):
        if hasattr(node, '__dict__'):
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
        
        # Create function scope and analyze body
        new_scope = {param: 'variable' for param in node.params}
        self.scopes.append(new_scope)
        for stmt in node.body:
            self.analyze(stmt)
        self.scopes.pop()

    def visit_Identifier(self, node: Identifier):
        # Resolve identifier in lexical scopes
        for scope in reversed(self.scopes):
            if node.name in scope:
                return
        # Simple placeholder for undefined identifiers
        pass

    def visit_CallExpression(self, node: CallExpression):
        for arg in node.arguments:
            self.analyze(arg)

    def visit_IfStatement(self, node: IfStatement):
        self.analyze(node.condition)
        self.analyze(node.then_branch)
        if node.else_branch:
            self.analyze(node.else_branch)

    def visit_LoopStatement(self, node: LoopStatement):
        self.analyze(node.condition)
        self.analyze(node.body)
