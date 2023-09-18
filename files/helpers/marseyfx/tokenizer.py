from abc import abstractmethod
import re

class TokenizerError:
    index: int
    error: str

    def __init__(self, index: int, error: str):
        self.index = index
        self.error = error

class Tokenizer:
    str: str
    index: int
    errors: list[TokenizerError]

    def __init__(self, str: str):
        self.str = str
        self.index = 0
        self.errors = []

    def has_next(self):
        return self.index < len(self.str)

    def peek(self):
        return self.str[self.index]
    
    def eat(self):
        c = self.peek()
        self.index += 1
        return c
    
    def barf(self):
        self.index -= 1
    
    def error(self, error: str):
        self.errors.append(TokenizerError(self.index, error))

    def token_to_string(self, token):
        return self.str[token.span[0]:token.span[1]]

    def parse_next_tokens(self):
        print(self.str[self.index:])
        start = self.index
        tokens = []
        while self.has_next():
            if WordToken.can_parse(self):
                tokens.append(WordToken.parse(self))
            elif DotToken.can_parse(self):
                tokens.append(DotToken.parse(self))
            elif ArgsToken.can_parse(self):
                tokens.append(ArgsToken.parse(self))
            elif StringLiteralToken.can_parse(self):
                tokens.append(StringLiteralToken.parse(self))
            else:
                break

        if len(tokens) == 0:
            self.error('Expected a token')
            return None
        
        if len(tokens) == 1:
            return tokens[0]

        return GroupToken((start, self.index), tokens)

class Token:
    span: tuple[int, int]

    @staticmethod
    @abstractmethod
    def can_parse(tokenizer: Tokenizer) -> bool:
        pass

    @staticmethod
    @abstractmethod
    def parse(tokenizer: Tokenizer):
        pass

class WordToken(Token):
    value: str

    def __init__(self, span: tuple[int, int], value: str):
        self.value = value
        self.span = span

    @staticmethod
    def can_parse(tokenizer: Tokenizer):
        return re.fullmatch(r'[!#\w@]', tokenizer.peek())

    @staticmethod
    def parse(tokenizer: Tokenizer):
        start = tokenizer.index
        value = ''
        while tokenizer.has_next():
            if WordToken.can_parse(tokenizer):
                value += tokenizer.eat()
            else:
                break

        return WordToken((start, tokenizer.index), value)

class StringLiteralToken(Token):
    value: str

    def __init__(self, span: tuple[int, int], value: str):
        self.value = value
        self.span = span

    @staticmethod
    def can_parse(tokenizer: Tokenizer):
        return tokenizer.peek() == '"'
    
    # i was cuddling with my fwb while writing this ;3
    @staticmethod
    def parse(tokenizer: Tokenizer):
        start = tokenizer.index
        tokenizer.eat()
        value = ''
        next_escaped = False
        while tokenizer.has_next():
            if tokenizer.peek() == '"' and not next_escaped:
                tokenizer.eat()
                break
            elif tokenizer.peek() == '\\' and not next_escaped:
                next_escaped = True
                tokenizer.eat()
            else:
                value += tokenizer.eat()
                next_escaped = False

        return StringLiteralToken((start, tokenizer.index), value)
    
class NumberLiteralToken(Token):
    value: float

    def __init__(self, span: tuple[int, int], value: float):
        self.value = value
        self.span = span

    @staticmethod
    def can_parse(tokenizer: Tokenizer):
        return re.fullmatch(r'[-\d\.]', tokenizer.peek())

    @staticmethod
    def parse(tokenizer: Tokenizer):
        start = tokenizer.index
        value = ''
        while tokenizer.has_next():
            if NumberLiteralToken.can_parse(tokenizer):
                value += tokenizer.eat()
            else:
                break

        try:
            value = float(value)
        except ValueError:
            tokenizer.error('Invalid number literal')
            value = 0.0

        return NumberLiteralToken((start, tokenizer.index), value)
    
    def get_float(self):
        return float(self.value)

class DotToken(Token):
    def __init__(self, span: tuple[int, int]):
        self.span = span

    @staticmethod
    def can_parse(tokenizer: Tokenizer):
        return tokenizer.peek() == '.'

    @staticmethod
    def parse(tokenizer: Tokenizer):
        tokenizer.eat()
        return DotToken((tokenizer.index, tokenizer.index + 1))

class GroupToken(Token):
    children: list[Token]

    def __init__(self, span: tuple[int, int], children: list[Token]):
        self.children = children
        self.span = span

class ArgsToken(Token):
    children: list[GroupToken]
    def __init__(self, span: tuple[int, int], children: list[Token]):
        self.children = children
        self.span = span

    @staticmethod
    def can_parse(tokenizer: Tokenizer):
        return tokenizer.peek() == '('

    @staticmethod
    def parse(tokenizer: Tokenizer):
        start = tokenizer.index
        tokens = []
        while tokenizer.has_next():
            if tokenizer.peek() == ')':
                tokenizer.eat()
                break
            elif tokenizer.peek() == ',':
                tokenizer.eat()
            else:
                tokenizer.eat()
                tokens.append(tokenizer.parse_next_tokens())

        return ArgsToken((start, tokenizer.index), tokens)