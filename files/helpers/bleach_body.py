import bleach
from bleach.css_sanitizer import CSSSanitizer
from bleach.linkifier import LinkifyFilter
import functools

from files.helpers.regex import sanitize_url_regex, excessive_css_scale_regex
from files.helpers.config.const import *

allowed_tags = ('a','alpha','audio','b','blink','blockquote','br','center','code','del','details','em','g','gl','h1','h2','h3','h4','h5','h6','hidden','hr','i','img','li','lite-youtube','marquee','ol','p','pre','rp','rt','ruby','small','span','spoiler','strike','strong','sub','summary','sup','table','tbody','td','th','thead','tr','u','ul','video')
allowed_tags_runtime = ('div', 'input', 'label', 'score', 'button', 'd')
allowed_css_properties = ('background-color', 'color', 'filter', 'font-weight', 'text-align', 'transform', 'font-variant-caps')

def allowed_attributes(tag, name, value):
	if name == 'style':
		value = value.lower()
		if 'transform' in value and 'scale' in value and excessive_css_scale_regex.search(value):
			return False
		return True

	if tag == 'marquee':
		if name in {'direction', 'behavior', 'scrollamount'}: return True
		if name in {'height', 'width'}:
			try: value = int(value.replace('px', ''))
			except: return False
			if 0 < value <= 250: return True

	if tag == 'a':
		if name == 'href' and '\\' not in value and 'xn--' not in value:
			return True
		if name == 'rel' and value == 'nofollow noopener': return True
		if name == 'target' and value == '_blank': return True

	if tag == 'img':
		if name in {'src','data-src'}: return is_safe_url(value)
		if name == 'loading' and value == 'lazy': return True
		if name == 'data-bs-toggle' and value == 'tooltip': return True
		if name in {'g','b','alpha','glow','party'} and not value: return True
		if name in {'alt','title'}: return True
		if name == 'class' and value == 'img': return True
		if name == 'data-user-submitted' and not value: return True

	if tag == 'lite-youtube':
		if name == 'params': return True
		if name == 'videoid': return True

	if tag == 'video':
		if name == 'controls' and value == '': return True
		if name == 'preload' and value == 'none': return True
		if name == 'src': return is_safe_url(value)
		if name == 'poster': return is_safe_url(value)

	if tag == 'audio':
		if name == 'src': return is_safe_url(value)
		if name == 'controls' and value == '': return True
		if name == 'preload' and value == 'none': return True

	if tag == 'p':
		if name == 'class' and value in {'mb-0','resizable','yt','text-center'}: return True

	if tag == 'span':
		if name == 'data-bs-toggle' and value == 'tooltip': return True
		if name == 'title': return True
		if name == 'alt': return True
		if name == 'cide' and not value: return True
		if name == 'bounce' and not value: return True

	if tag == 'table':
		if name == 'class' and value == 'table': return True

	if tag == 'blockquote':
		if name == 'class' and value == 'twitter-tweet': return True
		if name == 'data-dnt' and value == 'true': return True

	if tag in allowed_tags_runtime:
		return True

	return False


def bleach_body_html(body_html, runtime=False):
	css_sanitizer = CSSSanitizer(allowed_css_properties=allowed_css_properties)

	tags = allowed_tags
	if runtime:
		tags += allowed_tags_runtime

	body_html = bleach.Cleaner(
		tags=tags,
		attributes=allowed_attributes,
		protocols=['http', 'https'],
		css_sanitizer=css_sanitizer,
		filters=[
				functools.partial(
					LinkifyFilter,
					skip_tags=["pre","code"],
					parse_email=False, 
					url_re=sanitize_url_regex
				)
			]
	).clean(body_html)

	return body_html
