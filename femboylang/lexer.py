import re
from .tokens import TokenType, Token

class Lexer:
    KEYWORDS = {
        'uwu': TokenType.UWU,
        'hai': TokenType.HAI,
        'nya': TokenType.NYA,
        'baka': TokenType.BAKA,
        'mou': TokenType.MOU,
        'loopies': TokenType.LOOPIES,
        'returny': TokenType.RETURNY,
        'True': TokenType.BOOLEAN,
        'False': TokenType.BOOLEAN,
    }

    def __init__(self, source: str):
        self.source = source
        self.tokens = []
        self.pos = 0
        self.line = 1
        self.column = 1
        self.indent_stack = [0]

    def error(self, message):
        raise SyntaxError(f"Lexer Error: {message} at line {self.line}, column {self.column}")

    def peek(self, n=0):
        if self.pos + n >= len(self.source):
            return None
        return self.source[self.pos + n]

    def advance(self):
        char = self.peek()
        self.pos += 1
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    def tokenize(self):
        while self.pos < len(self.source):
            char = self.peek()

            # Handle Indentation at the start of a line
            if self.column == 1:
                indent_level = 0
                while self.peek() in (' ', '\t'):
                    c = self.advance()
                    indent_level += (4 if c == '\t' else 1)
                
                # Skip empty lines or comment-only lines
                next_chars = self.peek(0), self.peek(1), self.peek(2)
                if self.peek() == '\n' or self.peek() is None or (next_chars[0] == '>' and next_chars[1] == '/' and next_chars[2] == '/'):
                    if self.peek() == '\n':
                        self.advance()
                    elif self.peek() == '>':
                        while self.peek() and self.peek() != '\n':
                            self.advance()
                        if self.peek() == '\n':
                            self.advance()
                    continue

                if indent_level > self.indent_stack[-1]:
                    self.indent_stack.append(indent_level)
                    self.tokens.append(Token(TokenType.INDENT, indent_level, self.line, self.column))
                elif indent_level < self.indent_stack[-1]:
                    while indent_level < self.indent_stack[-1]:
                        self.indent_stack.pop()
                        self.tokens.append(Token(TokenType.DEDENT, indent_level, self.line, self.column))
                    if indent_level != self.indent_stack[-1]:
                        self.error("Inconsistent indentation")
                
                # Refresh char after advancing in the indentation block
                char = self.peek()

            if char is None: break

            if char.isspace() and char != '\n':
                self.advance()
            elif char == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, '\n', self.line, self.column))
                self.advance()
            elif char == '>' and self.peek(1) == '/' and self.peek(2) == '/':
                # Comment >//<
                while self.peek() and self.peek() != '\n':
                    self.advance()
            elif char.isdigit():
                self.tokens.append(self.read_number())
            elif char.isalpha() or char == '_':
                self.tokens.append(self.read_identifier())
            elif char == '"' or char == "'":
                self.tokens.append(self.read_string(char))
            elif char == '=':
                if self.peek(1) == '=':
                    self.advance(); self.advance()
                    self.tokens.append(Token(TokenType.EQ, '==', self.line, self.column - 2))
                else:
                    self.advance()
                    self.tokens.append(Token(TokenType.ASSIGN, '=', self.line, self.column - 1))
            elif char == '+':
                self.advance()
                self.tokens.append(Token(TokenType.PLUS, '+', self.line, self.column - 1))
            elif char == '-':
                self.advance()
                self.tokens.append(Token(TokenType.MINUS, '-', self.line, self.column - 1))
            elif char == '*':
                self.advance()
                self.tokens.append(Token(TokenType.MUL, '*', self.line, self.column - 1))
            elif char == '/':
                self.advance()
                self.tokens.append(Token(TokenType.DIV, '/', self.line, self.column - 1))
            elif char == '(':
                self.advance()
                self.tokens.append(Token(TokenType.LPAREN, '(', self.line, self.column - 1))
            elif char == ')':
                self.advance()
                self.tokens.append(Token(TokenType.RPAREN, ')', self.line, self.column - 1))
            elif char == ':':
                self.advance()
                self.tokens.append(Token(TokenType.COLON, ':', self.line, self.column - 1))
            elif char == ',':
                self.advance()
                self.tokens.append(Token(TokenType.COMMA, ',', self.line, self.column - 1))
            elif char == '<':
                if self.peek(1) == '=':
                    self.advance(); self.advance()
                    self.tokens.append(Token(TokenType.LTE, '<=', self.line, self.column - 2))
                else:
                    self.advance()
                    self.tokens.append(Token(TokenType.LT, '<', self.line, self.column - 1))
            elif char == '>':
                if self.peek(1) == '=':
                    self.advance(); self.advance()
                    self.tokens.append(Token(TokenType.GTE, '>=', self.line, self.column - 2))
                else:
                    self.advance()
                    self.tokens.append(Token(TokenType.GT, '>', self.line, self.column - 1))
            elif char == '!':
                if self.peek(1) == '=':
                    self.advance(); self.advance()
                    self.tokens.append(Token(TokenType.NEQ, '!=', self.line, self.column - 2))
                else:
                    self.error(f"Unexpected character '!' at line {self.line}")
            else:
                self.error(f"Unexpected character '{char}'")

        # Handle remaining dedents
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(Token(TokenType.DEDENT, None, self.line, self.column))

        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens

    def read_number(self):
        start_line = self.line
        start_col = self.column
        value = ""
        while self.peek() and (self.peek().isdigit() or self.peek() == '.'):
            value += self.advance()
        return Token(TokenType.NUMBER, float(value) if '.' in value else int(value), start_line, start_col)

    def read_identifier(self):
        start_line = self.line
        start_col = self.column
        value = ""
        while self.peek() and (self.peek().isalnum() or self.peek() == '_'):
            value += self.advance()
        
        token_type = self.KEYWORDS.get(value, TokenType.IDENTIFIER)
        return Token(token_type, value, start_line, start_col)

    def read_string(self, quote):
        start_line = self.line
        start_col = self.column
        self.advance() # Skip opening quote
        value = ""
        while self.peek() and self.peek() != quote:
            value += self.advance()
        if self.peek() == quote:
            self.advance() # Skip closing quote
        else:
            self.error("Unterminated string")
        return Token(TokenType.STRING, value, start_line, start_col)
