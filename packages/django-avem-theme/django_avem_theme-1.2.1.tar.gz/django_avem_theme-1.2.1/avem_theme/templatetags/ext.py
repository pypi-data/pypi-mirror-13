
from math import ceil
from django.contrib.staticfiles import finders
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.utils.html import mark_safe
from django import template
from django.utils.timesince import timesince
from os.path import getmtime
from random import random
from json import dumps
from avem_theme.functions.list_sample import list_sample
from avem_theme.functions.hashing import float_b64
from avem_theme.functions.sanitize import sanitize_html

register = template.Library()


@register.simple_tag(takes_context=True)
def if_url(context, url_name, output='active'):
	"""
	Return output if the url matches the reverse or url_name, else ''
	used to highlight currently active menu items.
	"""
	if 'request' in context:
		url = reverse(url_name)
		if context['request'].path == url:
			return output
	return ''


@register.filter
def sample(collection, limit=3):
	"""
	Given an ordered collection (list, tuple, ...), return a string representation
	of the first limit items (or fewer), e.g. "itemA, itemB, itemC and 7 more"
	rsample does the sample, but shuffles the first 50 items and picks from that.
	"""
	return list_sample(collection, limit)


@register.filter
def rsample(collection, limit=3):
	"""
	Like sample, but uses a random subset of the first 50 items.
	"""
	return list_sample(sorted(collection[:50], key=lambda x: random()), limit)


@register.filter
def head(text, places=50):
	"""
	Get the first part of a string, append '...' if it was truncated.
	"""
	if len(text) <= places:
		return text
	short = ' '.join(text[:places - 2].split(' ')[:-1])
	if len(short) < max(places * 0.8, places - 10):
		short = text[:places - 3]
	return short + '...'


@register.filter
def tail(text, places=50):
	"""
	Get the last part of a string, prepend '...' if it was truncated.
	"""
	if len(text) <= places:
		return text
	short = ' '.join(text[-places + 2:].split(' ')[1:])
	if len(short) < max(places * 0.8, places - 10):
		short = text[-places + 3:]
	return '...' + short


@register.filter
def noscr(text):
	"""
	Apply a whitelist filter, which allows a limited selection of
	secure HTML tags and attributes.
	"""
	return mark_safe(sanitize_html(text))


@register.filter
def json(obj, extra1=None, extra2=None, extra3=None, extra4=None, extra5=None):
	"""
	Combine (update, extend) one or several data structures and convert them to json
	note that this should only be used with trusted data (otherwise cross-site-script vulnerable)
	note also that *extra apparently does not work for template tags for some reason.
	"""
	for extra in [_f for _f in (extra1, extra2, extra3, extra4, extra5,) if _f]:
		try:
			obj.update(extra)
		except (TypeError, AttributeError):
			try:
				obj = obj + extra
			except TypeError:
				raise TypeError(
					'|json filter called with incompatible arguments that could not be combined: %s and %s' % (
					type(obj), type(extra)))
	try:
		js = dumps(obj, cls=DjangoJSONEncoder)
	except TypeError:
		raise TypeError('called |json filter on an object that is not serializable by DjangoJSONEncoder')
	return mark_safe(js)


@register.filter
def euro(amount, min=None, round=False):
	"""
	Euro amount.
	"""
	if min:
		amount = -amount
	if amount == '':
		raise ValueError('|euro filter applied to empty string (perhaps the variable was not found)')
	try:
		if round:
			return mark_safe('&euro; %d' % float(amount))
		return mark_safe('&euro; %.2f' % float(amount))
	except ValueError:
		raise ValueError('|euro filter should be applied to something that can be cast to a float (got %s)' % amount)


@register.filter
def ieuro(amount, min=None):
	"""
	Rounded (up) euro amount.
	"""
	return euro(ceil(amount), min=min, round=True)


@register.filter
def upto(text, delimiter=None):
	"""
	Get the text up to [delimiter] and throw away the rest.
	"""
	return str(text).split(delimiter)[0]


@register.filter
def since_short(text):
	"""
	Shorter version of |timesince. Makes sure there is only one unit. Also shortens 'minutes' and 'hours',
	so results are shorter in English but should still work in other language.
	"""
	return timesince(text).split(',')[0].strip().replace('minute', 'min').replace('hour', 'hr')


@register.simple_tag(takes_context=False)
def static_mtime_b64(*staticfile_paths):
	"""
	Return the b64 encoded most recent changed date among staticfile_paths, for cache invalidation.
	"""
	latest = None
	for path in staticfile_paths:
		found = finders.find(path)
		if found and (not latest or latest < getmtime(finders.find(path))):
			latest = getmtime(finders.find(path))
	if latest:
		return float_b64(latest)
	return None


