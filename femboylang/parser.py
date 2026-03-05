from .tokens import TokenType, Token
from .ast_nodes import *

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self, n=0):
        if self.pos + n >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.pos + n]

    def advance(self):
        token = self.peek()
        self.pos += 1
        return token

    def check(self, token_type):
        return self.peek().type == token_type

    def match(self, *token_types):
        for t in token_types:
            if self.check(t):
                self.advance()
                return True
        return False

    def consume(self, token_type, message):
        if self.check(token_type):
            return self.advance()
        raise SyntaxError(f"Parser Error: {message} at line {self.peek().line}, col {self.peek().column}")

    def parse(self):
        statements = []
        while not self.match(TokenType.EOF):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return Program(statements)

    def parse_statement(self):
        if self.match(TokenType.NEWLINE):
            return None
        
        if self.match(TokenType.UWU):
            return self.parse_variable_declaration()
        if self.match(TokenType.HAI):
            return self.parse_print_statement()
        if self.match(TokenType.NYA):
            return self.parse_function_declaration()
        if self.match(TokenType.BAKA):
            return self.parse_if_statement()
        if self.match(TokenType.LOOPIES):
            return self.parse_loop_statement()
        if self.match(TokenType.RETURNY):
            return self.parse_return_statement()
        
        return self.parse_expression_statement()

    def parse_variable_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name after 'uwu'").value
        self.consume(TokenType.ASSIGN, "Expect '=' after variable name")
        value = self.parse_expression()
        self.consume_statement_end()
        return VariableDeclaration(name, value)

    def parse_print_statement(self):
        expressions = []
        expressions.append(self.parse_expression())
        while self.match(TokenType.COMMA):
            expressions.append(self.parse_expression())
        self.consume_statement_end()
        return PrintStatement(expressions)

    def parse_function_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect function name").value
        self.consume(TokenType.LPAREN, "Expect '(' after function name")
        params = []
        if not self.check(TokenType.RPAREN):
            params.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name").value)
            while self.match(TokenType.COMMA):
                params.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name").value)
        self.consume(TokenType.RPAREN, "Expect ')' after parameters")
        self.consume(TokenType.COLON, "Expect ':' after function signature")
        body = self.parse_block()
        return FunctionDeclaration(name, params, body)

    def parse_if_statement(self):
        condition = self.parse_expression()
        self.consume(TokenType.COLON, "Expect ':' after condition")
        then_branch = self.parse_block()
        else_branch = None
        if self.match(TokenType.MOU):
            self.consume(TokenType.COLON, "Expect ':' after 'mou'")
            else_branch = self.parse_block()
        return IfStatement(condition, then_branch, else_branch)

    def parse_loop_statement(self):
        condition = self.parse_expression()
        self.consume(TokenType.COLON, "Expect ':' after condition")
        body = self.parse_block()
        return LoopStatement(condition, body)

    def parse_return_statement(self):
        value = None
        if not self.check(TokenType.NEWLINE) and not self.check(TokenType.EOF) and not self.check(TokenType.DEDENT):
            value = self.parse_expression()
        self.consume_statement_end()
        return ReturnStatement(value)

    def parse_block(self):
        self.consume(TokenType.NEWLINE, "Expect newline before block")
        self.consume(TokenType.INDENT, "Expect indentation")
        statements = []
        while not self.check(TokenType.DEDENT) and not self.check(TokenType.EOF):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        self.consume(TokenType.DEDENT, "Expect dedentation after block")
        return statements

    def parse_expression_statement(self):
        expr = self.parse_expression()
        self.consume_statement_end()
        return expr

    def consume_statement_end(self):
        if self.match(TokenType.NEWLINE, TokenType.EOF):
            return
        # If we are at dedent, it's also acceptable end of statement
        if self.check(TokenType.DEDENT):
            return
        raise SyntaxError(f"Expect end of statement/newline, got {self.peek().type} at line {self.peek().line}")

    def parse_expression(self):
        return self.equality()

    def equality(self):
        expr = self.comparison()
        while self.match(TokenType.EQ, TokenType.NEQ):
            operator = self.tokens[self.pos - 1].value
            right = self.comparison()
            expr = BinaryExpression(expr, operator, right)
        return expr

    def comparison(self):
        expr = self.term()
        while self.match(TokenType.LT, TokenType.GT, TokenType.LTE, TokenType.GTE):
            operator = self.tokens[self.pos - 1].value
            right = self.term()
            expr = BinaryExpression(expr, operator, right)
        return expr

    def term(self):
        expr = self.factor()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.tokens[self.pos - 1].value
            right = self.factor()
            expr = BinaryExpression(expr, operator, right)
        return expr

    def factor(self):
        expr = self.unary()
        while self.match(TokenType.MUL, TokenType.DIV):
            operator = self.tokens[self.pos - 1].value
            right = self.unary()
            expr = BinaryExpression(expr, operator, right)
        return expr

    def unary(self):
        if self.match(TokenType.MINUS):
            operator = self.tokens[self.pos - 1].value
            right = self.unary()
            return UnaryExpression(operator, right)
        return self.call()

    def call(self):
        expr = self.primary()
        if isinstance(expr, Identifier) and self.match(TokenType.LPAREN):
            args = []
            if not self.check(TokenType.RPAREN):
                args.append(self.parse_expression())
                while self.match(TokenType.COMMA):
                    args.append(self.parse_expression())
            self.consume(TokenType.RPAREN, "Expect ')' after arguments")
            return CallExpression(expr.name, args)
        return expr

    def primary(self):
        if self.match(TokenType.BOOLEAN, TokenType.NUMBER, TokenType.STRING):
            val = self.tokens[self.pos - 1].value
            if self.tokens[self.pos-1].type == TokenType.BOOLEAN:
                val = (val == 'True')
            return Literal(val)
        
        if self.match(TokenType.IDENTIFIER):
            return Identifier(self.tokens[self.pos - 1].value)
        
        if self.match(TokenType.LPAREN):
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN, "Expect ')' after expression")
            return expr
        
        raise SyntaxError(f"Unexpected token {self.peek().type} at line {self.peek().line}")
