from bs4 import BeautifulSoup, Tag
from files.helpers.config.const import SITE_FULL_IMAGES
from files.helpers.marseyfx.parser import Modifier
from files.helpers.marseyfx.tokenizer import StringLiteralToken

modifier_whitelist = []

def modifier(fn):
    modifier_whitelist.append(fn.__name__)

    def wrapper(*args, **kwargs):
        args[0].el['class'].append('marseyfx-modifier-' + fn.__name__)
        return fn(*args, **kwargs)
    return wrapper

class Modified:
    soup: BeautifulSoup
    el: Tag #BeautifulSoup element

    def __init__(self, el):
        self.soup = BeautifulSoup()
        self.el = el.wrap(self.soup.new_tag('div', class_='marseyfx-container'))

    def add_class(self, class_: str):
        self.el.attrs['class'].append(' ' + class_)

    def apply_modifiers(self, modifiers: list[Modifier]):
        for modifier in modifiers:
            if modifier.name in modifier_whitelist:
                getattr(self, modifier.name)(*modifier.args)

    # Using this instead of throwing everything in a string and then parsing it helps
    # mitigate the risk of XSS attacks
    def image(self, name: str):
        return self.soup.new_tag(
            'img', 
            loading='lazy', 
            class_=f'marseyfx-{name}',
            src=f'{SITE_FULL_IMAGES}/i/{name}.webp'
        ) 
    
    def underlay(self, underlay: Tag):
        self.el.insert(0, underlay)

    def overlay(self, overlay: Tag):
        self.el.append(overlay)

    @modifier
    def pat(self):
        self.overlay(self.el, self.image('pat'))

    @modifier
    def love(self):
        self.overlay(self.el, self.image('love-foreground'))
        self.underlay(self.el, self.image('love-background'))

    @modifier
    def talking(self):
        self.overlay(self.el, self.image('talking'))

    @modifier
    def genocide(self):
        pass

    @modifier
    def says(self, msg):
        if not isinstance(msg, StringLiteralToken):
            return
        
        self.overlay(self.el, self.image('says'))
        self.el.append(self.soup.new_tag(
            'span',
            class_='marseyfx-modifier-says-text',
            string=msg.value
        ))

    @modifier
    def fallover(self):
        self.el.wrap(self.soup.new_tag(
            'div',
            class_='marseyfx-modifier-fallover-container'
        ))

    @modifier
    def transform(self, transformstyle: str):
        if not transformstyle.fullmatch(r'[\w()\s%\.]*'):
            return
        
        if not 'style' in self.el.attrs:
            self.el.attrs['style'] = ''

        self.el.attrs['style'] += f'transform: {transformstyle};'
    
    @modifier
    def enraged(self):
        self.underlay(self.soup.new_tag(
            'div', 
            class_='marseyfx-enraged-underlay'
        ))

    @modifier
    def corrupted(self):
        pass

    @modifier
    def wavy(self):
        self.el.wrap(self.soup.new_tag('svg'))