from tokenize import Token

from bs4 import BeautifulSoup
from files.helpers.config.const import SITE_FULL_IMAGES
from files.helpers.marseyfx.tokenizer import ArgsToken, DotToken, GroupToken, NumberLiteralToken, Tokenizer, WordToken
from files.helpers.marseyfx.modifiers import Modified, Modifier, modifier_whitelist

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
    is_primary = True

    def __init__(self, name: str, modifiers, token: Token, **args):
        for symbol, value in emoji_replacers.items():
            if symbol in name:
                name = name.replace(symbol, '')
                setattr(self, value, True)

        self.name = name
        self.modifiers = modifiers
        self.token = token
        self.is_primary = args.get('is_primary', True)

    def create_el(self, tokenizer: Tokenizer):
        soup = BeautifulSoup()
        
        el = soup.new_tag(
            'img',
            loading='lazy',
            src=f'{SITE_FULL_IMAGES}/e/{self.name}.webp',
            attrs={
                'class': f'marseyfx-emoji marseyfx-image',
            }
        )
        soup.append(el)
        el = el.wrap(
            soup.new_tag('div', attrs={
                'class': 'marseyfx-emoji-container'
            })
        )

        mod = Modified(el, tokenizer)
        mod.apply_modifiers(self.modifiers)


        container_attrs = {
            'class': 'marseyfx-container',
        }

        if self.is_primary:
            container_attrs |= {
                'data-bs-toggle': 'tooltip',
                'title': tokenizer.str
            }

        container = soup.new_tag('div', attrs=container_attrs)

        if (self.is_big):
            container['class'].append(' marseyfx-big')

        if (self.is_flipped):
            container['class'].append(' marseyfx-flipped')

        return mod.container.wrap(container)

def parse_emoji(tokenizer: Tokenizer):
    token = tokenizer.parse_next_tokens()

    if len(tokenizer.errors) > 0 or token is None:
        return False, None, token

    emoji = parse_from_token(tokenizer, token)
    print(f'Here! {emoji}')

    if not emoji:
        return False, None, token

    return True, emoji, token

def parse_from_token(tokenizer: Tokenizer, token: GroupToken):
    if not isinstance(token, GroupToken):
        tokenizer.error('Malformed token -- Expected a group token')
        return

    emoji = token.children[0]

    if not isinstance(emoji, WordToken) and not isinstance(emoji, NumberLiteralToken):
        tokenizer.error('Malformed token -- Expected an emoji (word token) or number literal token')
        return
    
    modifiers = []

    i = 1
    while i + 1 < len(token.children):
        t = token.children[i]

        if not isinstance(t, DotToken):
            tokenizer.error('Malformed token -- Expected a dot')
            return

        modifier = token.children[i + 1]
        if not isinstance(modifier, WordToken):
            tokenizer.error('Malformed token -- Expected a modifier name (word token)')
            return
        
        if not modifier.value in modifier_whitelist:
            tokenizer.error(f'Unknown modifier: {modifier.value}')
            return

        if not i + 2 < len(token.children) or not isinstance(token.children[i + 2], ArgsToken):
            modifiers.append(Modifier(modifier.value, []))
            i += 2
        else:
            args = token.children[i + 2]
            modifiers.append(Modifier(modifier.value, args.children))
            i += 3

    return Emoji(tokenizer.str[emoji.span[0]:emoji.span[1]], modifiers, token)