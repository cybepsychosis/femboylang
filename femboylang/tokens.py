from enum import Enum, auto

class TokenType(Enum):
    # Keywords
    UWU = auto()      # variable declaration
    HAI = auto()      # print
    NYA = auto()      # function
    BAKA = auto()     # if
    MOU = auto()      # else
    LOOPIES = auto()  # loop
    RETURNY = auto()  # return

    # Literals
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    BOOLEAN = auto()

    # Operators
    ASSIGN = auto()   # =
    PLUS = auto()     # +
    MINUS = auto()    # -
    MUL = auto()      # *
    DIV = auto()      # /
    EQ = auto()       # ==
    NEQ = auto()      # !=
    LT = auto()       # <
    GT = auto()       # >
    LTE = auto()      # <=
    GTE = auto()      # >=

    # Punctuation
    LPAREN = auto()   # (
    RPAREN = auto()   # )
    COLON = auto()    # :
    COMMA = auto()    # ,
    INDENT = auto()
    DEDENT = auto()
    NEWLINE = auto()
    EOF = auto()

class Token:
    def __init__(self, type: TokenType, value: any, line: int, column: int):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, line={self.line}, col={self.column})"
