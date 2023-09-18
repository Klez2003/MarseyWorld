import re
from bs4 import BeautifulSoup, Tag
from files.helpers.config.const import SITE_FULL_IMAGES
from files.helpers.marseyfx.tokenizer import GroupToken, NumberLiteralToken, StringLiteralToken, Token, Tokenizer
import files.helpers.marseyfx.parser as parser

modifier_whitelist = []

class Modifier:
    name: str
    args: list[Token]

    def __init__(self, name: str, args: list[Token]):
        self.name = name
        self.args = args

def modifier(fn):
    modifier_whitelist.append(fn.__name__)

    def wrapper(*args, **kwargs):
        slf = args[0]
        slf.child = slf.container
        slf.container = slf.child.wrap(slf.soup.new_tag('div', attrs={'class': f'marseyfx-modifier marseyfx-modifier-{fn.__name__}'}))
        return fn(*args, **kwargs)
    return wrapper

def heavy(fn):
    def wrapper(*args, **kwargs):
        slf = args[0]
        slf.heavy_count += 1
        return fn(*args, **kwargs)
    return wrapper

class Modified:
    soup: BeautifulSoup
    container: Tag
    child: Tag
    tokenizer: Tokenizer
    heavy_count = 0

    def __init__(self, el, tokenizer):
        self.soup = BeautifulSoup()
        self.container = el
        self.tokenizer = tokenizer

    def add_class(self, class_: str):
        if not 'class' in self.container.attrs:
            self.container.attrs['class'] = ''
        else:
            self.container.attrs['class'].append(' ' + class_)

    def add_child_class(self, class_: str):
        if not 'class' in self.child.attrs:
            self.child.attrs['class'] = ''
        else:
            self.child.attrs['class'].append(' ' + class_)

    def apply_modifiers(self, modifiers: list[Modifier]):
        for modifier in modifiers:
            if modifier.name in modifier_whitelist:
                getattr(self, modifier.name)(*modifier.args)

    # Using this instead of throwing everything in a string and then parsing it helps
    # mitigate the risk of XSS attacks
    def image_href(self, name: str):
        image = self.soup.new_tag(
            'img', 
            loading='lazy', 
            src=f'{SITE_FULL_IMAGES}/i/{name}.webp',
            attrs={'class': f'marseyfx-image marseyfx-image-{name}'}
        )

        container = self.soup.new_tag(
            'div',
            attrs={'class': f'marseyfx-image-container marseyfx-image-container-{name}'}
        )

        container.append(image)
        return container
    
    def underlay(self, underlay: Tag):
        self.container.insert(0, underlay)

    def overlay(self, overlay: Tag):
        self.container.append(overlay)

    def add_style(self, style: str):
        if 'style' in self.container.attrs:
            style = self.container.attrs['style'] + style

        self.container.attrs['style'] = style

    @modifier
    def pat(self):
        self.overlay(self.image('pat'))

    @modifier
    def love(self):
        self.overlay(self.image('love-foreground'))
        self.underlay(self.image('love-background'))

    @modifier
    def talking(self):
        self.overlay(self.image('talking'))

    @modifier
    def genocide(self):
        pass

    @modifier
    def says(self, msg):
        if not isinstance(msg, StringLiteralToken):
            return
        
        self.overlay(self.image('says'))
        self.container.append(self.soup.new_tag(
            'span',
            string=msg.value,
            attrs={'class': 'marseyfx-modifier-says-text'}
        ))

    @modifier
    def fallover(self):
        self.container = self.container.wrap(self.soup.new_tag(
            'div',
            attrs={'class': 'marseyfx-modifier-fallover-container'}
        ))

    @modifier
    def transform(self, transformstyle: StringLiteralToken):
        if not re.fullmatch(r'[\w()\s%\.,]*', transformstyle.value):
            print(f'Evil transform detected: {transformstyle.value}')
            return
        
        self.add_style(f'transform: {transformstyle.value};')
    
    @heavy
    @modifier
    def enraged(self):
        self.underlay(self.soup.new_tag(
            'div', 
            attrs={'class': 'marseyfx-enraged-underlay'}
        ))

    @heavy
    @modifier
    def corrupted(self):
        pass

    @heavy
    @modifier
    def wavy(self):
        self.container.wrap(self.soup.new_tag('svg'))

    @modifier
    def toptext(self, text: StringLiteralToken):
        if not isinstance(text, StringLiteralToken):
            return

        self.overlay(self.soup.new_tag(
            'span',
            string=text.value,
            attrs={'class': 'marseyfx-modifier-toptext-text'}
        ))

    @modifier
    def bottomtext(self, text: StringLiteralToken):
        if not isinstance(text, StringLiteralToken):
            return

        self.overlay(self.soup.new_tag(
            'span',
            string=text.value,
            attrs={'class': 'marseyfx-modifier-bottomtext-text'}
        ))

    @modifier
    def spin(self, speed: NumberLiteralToken):
        self.add_style('--marseyfx-spin-speed: ' + speed.value + ';')

    @modifier
    def triumphs(self, other: GroupToken):
        other_emoji = parser.parse_from_token(self.tokenizer, other)

        if other_emoji is None:
            return
        
        self.add_child_class('marseyfx-modifier-triumphs-self')

        other = other_emoji.create_el().wrap(
            self.soup.new_tag('div', attrs={'class': 'marseyfx-modifier-triumphs-other'})
        )
        self.underlay(other)

    