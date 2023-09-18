from tokenize import Token

from bs4 import BeautifulSoup
from files.helpers.config.const import SITE_FULL_IMAGES
from files.helpers.marseyfx.tokenizer import ArgsToken, DotToken, GroupToken, Tokenizer, WordToken
from modified import Modified

class Modifier:
    name: str
    args: list[Token]

    def __init__(self, name: str, args: list[Token]):
        self.name = name
        self.args = args

emoji_replacers = {
    '!': 'is_flipped',
    '#': 'is_big',
    '@': 'is_user'
}

class Emoji:
    name: str
    token: Token
    is_big = False
    is_flipped = False
    is_user = False
    modifiers: list[Modifier]

    def __init__(self, name: str, modifiers, token: Token):
        for symbol, value in emoji_replacers.items():
            name = name.replace(symbol, '')
            setattr(self, value, True)

        self.name = name
        self.modifiers = modifiers
        self.token = token
    def create_el(self):
        soup = BeautifulSoup()
        
        el = soup.new_tag(
            'img',
            loading='lazy',
            class_='marseyfx-emoji',
            src=f'{SITE_FULL_IMAGES}/e/{self.name}.webp'
        )

        if (self.is_big):
            el['class'].append(' marseyfx-big')

        if (self.is_flipped):
            el['class'].append(' marseyfx-flipped')

        mod = Modified(el)
        mod.apply_modifiers(self.modifiers)

        return mod.el

def parse_emoji(str: str):
    tokenizer = Tokenizer(str)
    token = tokenizer.parse_next_tokens()

    if len(tokenizer.errors) > 0:
        return False, None, token

    emoji = parse_from_token(tokenizer, token)

    if not emoji:
        return False, None, token

    return True, emoji, token

def parse_from_token(tokenizer: Tokenizer, token: GroupToken):
    if not isinstance(token, GroupToken):
        tokenizer.error('Malformed token -- Expected a group token')
        return

    emoji = token.tokens[0]

    if not isinstance(emoji, WordToken):
        tokenizer.error('Malformed token -- Expected an emoji (word token)')
        return
    
    modifiers = []

    i = 1
    while i + 1 < len(token.tokens):
        t = token.tokens[i]

        if not isinstance(t, DotToken):
            tokenizer.error('Malformed token -- Expected a dot')
            return

        modifier = token.tokens[i + 1]
        if not isinstance(modifier, WordToken):
            tokenizer.error('Malformed token -- Expected a modifier name (word token)')
            return
        
        if not i + 2 < len(token.tokens) or not isinstance(token.tokens[i + 2], ArgsToken):
            modifiers.append(Modifier(modifier.value, []))
            i += 2
        else:
            args = token.tokens[i + 2]
            modifiers.append(Modifier(modifier.value, args.tokens))
            i += 3

    return Emoji(emoji.value, modifiers, token)