import re
from bs4 import BeautifulSoup, Tag
from files.helpers.config.const import SITE_FULL_IMAGES
from files.helpers.marseyfx.tokenizer import StringLiteralToken, Token

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
        slf.el = slf.el.wrap(slf.soup.new_tag('div', attrs={'class': f'marseyfx-modifier marseyfx-modifier-{fn.__name__}'}))
        return fn(*args, **kwargs)
    return wrapper

class Modified:
    soup: BeautifulSoup
    el: Tag #BeautifulSoup element

    def __init__(self, el):
        self.soup = BeautifulSoup()
        self.el = el

    def add_class(self, class_: str):
        self.el.attrs['class'].append(' ' + class_)

    def apply_modifiers(self, modifiers: list[Modifier]):
        for modifier in modifiers:
            if modifier.name in modifier_whitelist:
                getattr(self, modifier.name)(*modifier.args)

    # Using this instead of throwing everything in a string and then parsing it helps
    # mitigate the risk of XSS attacks
    def image(self, name: str):
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
        self.el.insert(0, underlay)

    def overlay(self, overlay: Tag):
        self.el.append(overlay)

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
        self.el.append(self.soup.new_tag(
            'span',
            string=msg.value,
            attrs={'class': 'marseyfx-modifier-says-text'}
        ))

    @modifier
    def fallover(self):
        self.el = self.el.wrap(self.soup.new_tag(
            'div',
            attrs={'class': 'marseyfx-modifier-fallover-container'}
        ))

    @modifier
    def transform(self, transformstyle: StringLiteralToken):
        if not re.fullmatch(r'[\w()\s%\.,]*', transformstyle.value):
            print(f'Evil transform detected: {transformstyle.value}')
            return
        
        self.el.attrs['style'] = f'transform: {transformstyle.value};'

    
    @modifier
    def enraged(self):
        self.underlay(self.soup.new_tag(
            'div', 
            attrs={'class': 'marseyfx-enraged-underlay'}
        ))

    @modifier
    def corrupted(self):
        pass

    @modifier
    def wavy(self):
        self.el.wrap(self.soup.new_tag('svg'))