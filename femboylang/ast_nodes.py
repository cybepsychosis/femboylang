from dataclasses import dataclass, field
from typing import List, Optional, Any

@dataclass
class ASTNode:
    pass

@dataclass
class Expression(ASTNode):
    pass

@dataclass
class Statement(ASTNode):
    pass

@dataclass
class Program(ASTNode):
    statements: List[Statement]

@dataclass
class VariableDeclaration(Statement):
    name: str
    value: Expression

@dataclass
class PrintStatement(Statement):
    expressions: List[Expression]

@dataclass
class FunctionDeclaration(Statement):
    name: str
    params: List[str]
    body: List[Statement]

@dataclass
class IfStatement(Statement):
    condition: Expression
    then_branch: List[Statement]
    else_branch: Optional[List[Statement]] = None

@dataclass
class LoopStatement(Statement):
    condition: Expression
    body: List[Statement]

@dataclass
class ReturnStatement(Statement):
    value: Optional[Expression] = None

@dataclass
class BinaryExpression(Expression):
    left: Expression
    operator: str
    right: Expression

@dataclass
class CallExpression(Expression):
    callee: str
    arguments: List[Expression]

@dataclass
class Literal(Expression):
    value: Any

@dataclass
class Identifier(Expression):
    name: str

@dataclass
class UnaryExpression(Expression):
    operator: str
    right: Expression
