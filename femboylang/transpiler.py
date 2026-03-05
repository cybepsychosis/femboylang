from .ast_nodes import *

class Transpiler:
    def __init__(self):
        self.indent_level = 0

    def get_indent(self):
        return "    " * self.indent_level

    def transpile(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f"No visit_{type(node).__name__} method")

    def visit_Program(self, node: Program):
        return "\n".join(self.transpile(stmt) for stmt in node.statements)

    def visit_VariableDeclaration(self, node: VariableDeclaration):
        return f"{self.get_indent()}{node.name} = {self.transpile(node.value)}"

    def visit_PrintStatement(self, node: PrintStatement):
        exprs = ", ".join(self.transpile(e) for e in node.expressions)
        return f"{self.get_indent()}print({exprs})"

    def visit_FunctionDeclaration(self, node: FunctionDeclaration):
        params = ", ".join(node.params)
        header = f"{self.get_indent()}def {node.name}({params}):"
        self.indent_level += 1
        body_lines = [self.transpile(stmt) for stmt in node.body]
        if not body_lines:
            body_lines = [f"{self.get_indent()}pass"]
        self.indent_level -= 1
        body = "\n".join(body_lines)
        return f"{header}\n{body}"

    def visit_IfStatement(self, node: IfStatement):
        header = f"{self.get_indent()}if {self.transpile(node.condition)}:"
        self.indent_level += 1
        then_body = "\n".join(self.transpile(stmt) for stmt in node.then_branch)
        self.indent_level -= 1
        result = f"{header}\n{then_body}"
        if node.else_branch:
            else_header = f"{self.get_indent()}else:"
            self.indent_level += 1
            else_body = "\n".join(self.transpile(stmt) for stmt in node.else_branch)
            self.indent_level -= 1
            result += f"\n{else_header}\n{else_body}"
        return result

    def visit_LoopStatement(self, node: LoopStatement):
        header = f"{self.get_indent()}while {self.transpile(node.condition)}:"
        self.indent_level += 1
        body = "\n".join(self.transpile(stmt) for stmt in node.body)
        self.indent_level -= 1
        return f"{header}\n{body}"

    def visit_ReturnStatement(self, node: ReturnStatement):
        val = self.transpile(node.value) if node.value else ""
        return f"{self.get_indent()}return {val}"

    def visit_BinaryExpression(self, node: BinaryExpression):
        return f"({self.transpile(node.left)} {node.operator} {self.transpile(node.right)})"

    def visit_UnaryExpression(self, node: UnaryExpression):
        return f"{node.operator}{self.transpile(node.right)}"

    def visit_CallExpression(self, node: CallExpression):
        args = ", ".join(self.transpile(a) for a in node.arguments)
        return f"{node.callee}({args})"

    def visit_Literal(self, node: Literal):
        if isinstance(node.value, str):
            return f'"{node.value}"'
        return str(node.value)

    def visit_Identifier(self, node: Identifier):
        return node.name
