
from django.conf import settings


def base_template(request):
	"""
	Make the base template available everywhere for extending.
	"""
	if getattr(settings, 'BASE_TEMPLATE', None):
		base = settings.BASE_TEMPLATE
	else:
		base = 'avem/base.html'
	return {
		'BASE_TEMPLATE': base,
	}


