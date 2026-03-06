import re
from typing import List, Optional
from .tokens import TokenType, Token

class Lexer:
    """The Lexical Analyzer (Lexer) converts source code into a stream of tokens."""

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
        self.tokens: List[Token] = []
        self.pos = 0
        self.line = 1
        self.column = 1
        self.indent_stack = [0]

    def error(self, message: str):
        raise SyntaxError(f"Lexer Error: {message} at line {self.line}, column {self.column}")

    def peek(self, n: int = 0) -> Optional[str]:
        if self.pos + n >= len(self.source):
            return None
        return self.source[self.pos + n]

    def advance(self) -> str:
        char = self.peek()
        self.pos += 1
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    def tokenize(self) -> List[Token]:
        """Scans the source and returns a list of tokens."""
        while self.pos < len(self.source):
            char = self.peek()

            # Handle Indentation
            if self.column == 1:
                indent_level = 0
                while self.peek() in (' ', '\t'):
                    c = self.advance()
                    indent_level += (4 if c == '\t' else 1)
                
                # Skip empty lines and comments
                next_chars = (self.peek(0), self.peek(1), self.peek(2))
                is_comment = next_chars[0] == '>' and next_chars[1] == '/' and next_chars[2] == '/'
                
                if self.peek() == '\n' or self.peek() is None or is_comment:
                    if self.peek() == '\n':
                        self.advance()
                    elif is_comment:
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
                
                char = self.peek()

            if char is None:
                break

            if char.isspace() and char != '\n':
                self.advance()
            elif char == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, '\n', self.line, self.column))
                self.advance()
            elif char == '>' and self.peek(1) == '/' and self.peek(2) == '/':
                # Handle single-line comment: >// comment here
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
                    self.error("Unexpected character '!' (did you mean '!='?)")
            else:
                self.error(f"Unexpected character: {char}")

        # EOF Indentation handling
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(Token(TokenType.DEDENT, None, self.line, self.column))

        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens

    def read_number(self) -> Token:
        start_line, start_col = self.line, self.column
        value = ""
        while self.peek() and (self.peek().isdigit() or self.peek() == '.'):
            value += self.advance()
        return Token(TokenType.NUMBER, float(value) if '.' in value else int(value), start_line, start_col)

    def read_identifier(self) -> Token:
        start_line, start_col = self.line, self.column
        value = ""
        while self.peek() and (self.peek().isalnum() or self.peek() == '_'):
            value += self.advance()
        
        token_type = self.KEYWORDS.get(value, TokenType.IDENTIFIER)
        return Token(token_type, value, start_line, start_col)

    def read_string(self, quote: str) -> Token:
        start_line, start_col = self.line, self.column
        self.advance() # Opening quote
        value = ""
        while self.peek() and self.peek() != quote:
            value += self.advance()
        if self.peek() == quote:
            self.advance() # Closing quote
        else:
            self.error("Unterminated string literal")
        return Token(TokenType.STRING, value, start_line, start_col)
