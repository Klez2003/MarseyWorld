import copy
import re
from typing import Optional
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
		ctx = ModifierContextFrame(fn.__name__)
		slf.context_frames.insert(0, ctx)
		slf.child = slf.container
		slf.container = slf.child.wrap(slf.soup.new_tag('div', attrs={'class': f'marseyfx-modifier marseyfx-modifier-{ctx.name}'}))
		slf.add_child_class(f'marseyfx-modifier-{ctx.name}-self')
		res = fn(*args, **kwargs)
		slf.context_frames.pop(0)
		return res
	return wrapper

def heavy(fn):
	def wrapper(*args, **kwargs):
		slf = args[0]
		slf.heavy_count += 1
		return fn(*args, **kwargs)
	
	wrapper.heavy_count = 1

	return wrapper

class ModifierContextFrame:
	name: str
	wrap_depth: int = 0
	def __init__(self, name: str):
		self.name = name

class Modified:
	soup: BeautifulSoup
	container: Tag
	child: Tag
	tokenizer: Tokenizer
	heavy_count = 0
	context_frames: list[ModifierContextFrame]

	def __init__(self, el, tokenizer):
		self.soup = BeautifulSoup()
		self.container = el
		self.tokenizer = tokenizer
		self.context_frames = []

	def ctx(self):
		return self.context_frames[0] if len(self.context_frames) > 0 else None

	def add_class(self, class_: str):
		if not 'class' in self.container.attrs:
			self.container.attrs['class'] = [class_]
		else:
			self.container.attrs['class'].append(' ' + class_)

	def add_child_class(self, class_: str):
		if not 'class' in self.child.attrs:
			self.child.attrs['class'] = [class_]
		else:
			self.child.attrs['class'].append(' ' + class_)

	def apply_modifiers(self, modifiers: list[Modifier]):
		for modifier in modifiers:
			if modifier.name in modifier_whitelist:
				getattr(self, modifier.name)(*map(GroupToken.unwrap, modifier.args))

	# Using this instead of throwing everything in a string and then parsing it helps
	# mitigate the risk of XSS attacks
	def image(self, name: str):

		filename = name

		if not '.' in filename:
			filename += '.webp'

		image = self.soup.new_tag(
			'img', 
			loading='lazy', 
			src=f'{SITE_FULL_IMAGES}/i/{filename}',
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

	def meme_text(self, text: str, class_: Optional[str] = None):
		attrs = {}
		if class_ is not None:
			attrs = {'class': f'marseyfx-memetext-{class_}'}

		tag = self.soup.new_tag(
			'span',
			attrs=attrs
		)

		tag.string = text

		self.overlay(tag)

	def create_other(self, other: GroupToken = None):
		wrapper = self.soup.new_tag('div', attrs={'class': f'marseyfx-modifier-{self.ctx().name}-other'})

		if other is None:
			return wrapper
		
		other = other.wrap()
		other_emoji = parser.parse_from_token(self.tokenizer, other)

		if other_emoji is None:
			return wrapper
		
		other_emoji.is_primary = False

		return other_emoji.create_el(self.tokenizer).wrap(wrapper)
	
	def wrap_child(self, class_: str = ''):
		ctx = self.ctx()
		wrap_insert = ''
		if ctx.wrap_depth > 0:
			wrap_insert = f'-{ctx.wrap_depth + 1}'
		
		self.child = self.child.wrap(self.soup.new_tag('div', attrs={'class': f'marseyfx-modifier-{self.ctx().name}-wrapper{wrap_insert} {class_}'}))

		ctx.wrap_depth += 1

	@modifier
	def pat(self):
		self.overlay(self.image('hand'))

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
	def party(self):
		pass

	@modifier
	def says(self, msg):
		if not isinstance(msg, StringLiteralToken):
			return
		
		container = self.soup.new_tag(
			'div',
			attrs={'class': 'marseyfx-modifier-says-container'}
		)
		self.container.append(container)

		container.append(self.soup.new_tag(
			'div',
			attrs={'class': 'marseyfx-modifier-says-nub'}
		))

		tag = self.soup.new_tag(
			'span',
			attrs={'class': 'marseyfx-modifier-says-text'}
		)
		tag.string = msg.value
		container.append(tag)

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
	
	@modifier
	def enraged(self):
		self.underlay(self.soup.new_tag(
			'div', 
			attrs={'class': 'marseyfx-modifier-enraged-underlay'}
		))

	@modifier
	def meme(self, toptext: Optional[StringLiteralToken] = None, bottomtext: Optional[StringLiteralToken] = None):
		if isinstance(toptext, StringLiteralToken):
			self.meme_text(toptext.value, 'toptext')

		if isinstance(bottomtext, StringLiteralToken):
			self.meme_text(bottomtext.value, 'bottomtext')

	def bottomtext(self, text: StringLiteralToken):
		if not isinstance(text, StringLiteralToken):
			return

		tag = self.soup.new_tag(
			'span',
			attrs={'class': 'marseyfx-modifier-bottomtext-text'}
		)

		tag.string = text.value

		self.overlay(tag)

	@modifier
	def spin(self, speed=None):
		if not isinstance(speed, NumberLiteralToken):
			return

		self.add_style(f'animation-duration: {1/speed.value}s;')

	@modifier
	def triumphs(self, other: GroupToken):
		other = other.wrap()
		other_emoji = parser.parse_from_token(self.tokenizer, other)

		if other_emoji is None:
			return
		
		self.add_child_class('marseyfx-modifier-triumphs-self')

		other_emoji.is_primary = False

		other = other_emoji.create_el(self.tokenizer).wrap(
			self.soup.new_tag('div', attrs={'class': 'marseyfx-modifier-triumphs-other'})
		)
		self.underlay(other)

	@modifier
	def nested(self, inside: GroupToken):
		inside = inside.wrap()
		inside_emoji = parser.parse_from_token(self.tokenizer, inside)

		if inside_emoji is None:
			return
		
		inside_emoji.is_primary = False

		inside = inside_emoji.create_el(self.tokenizer).wrap(
			self.soup.new_tag('div', attrs={'class': 'marseyfx-modifier-nested-other'})
		)

		self.underlay(inside)

		self.add_child_class('marseyfx-modifier-nested-side')
		child = self.child
		self.child = child.wrap(self.soup.new_tag('div', attrs={'class': 'marseyfx-modifier-nested-outer-container'}))
		other_side = copy.copy(child)
		self.child.append(other_side)

	@modifier
	def morph(self, other: GroupToken):
		self.add_child_class('marseyfx-modifier-morph-self')

		other = other.wrap()
		other_emoji = parser.parse_from_token(self.tokenizer, other)

		if other_emoji is None:
			return
		
		other_emoji.is_primary = False
		other = other_emoji.create_el(self.tokenizer).wrap(
			self.soup.new_tag('div', attrs={'class': 'marseyfx-modifier-morph-other'})
		)

		self.container.append(other)

	""" Coming Soon (TM)
	@heavy
	@modifier
	def bulge(self, strength: NumberLiteralToken = None):
		self.child = self.child.wrap(self.soup.new_tag('svg', attrs={'class': 'marseyfx-modifier-bulge-container'}))
	"""

	@modifier
	def prohibition(self):
		self.overlay(self.image('prohibition.svg'))

	@modifier
	def scope(self):
		self.overlay(self.image('scope.svg'))
		self.add_child_class('marseyfx-modifier-scope-target')

	@modifier
	def fucks(self, other: GroupToken):
		other = self.create_other(other)
		self.container.append(other)

	@heavy
	@modifier
	def glow(self):
		pass

	@heavy
	@modifier
	def echo(self):
		for i in range(1, 4):
			tag = copy.copy(self.child)
			tag.attrs['class'] = tag.attrs['class'].copy()
			tag.attrs['class'].append(f'marseyfx-modifier-echo-clone marseyfx-modifier-echo-clone-{i}')
			self.container.append(tag)

	@modifier
	def rentfree(self):
		self.wrap_child()
		self.overlay(self.image('rentfree.png'))