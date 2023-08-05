from django import template
from django.core import urlresolvers



register = template.Library()



@register.simple_tag(takes_context = True)
def current(context, urlName, className = 'active', **kwargs):
	'''
	Return a class name (string) if the current URL matches the route name specified in ``className``.
	If any URL keyword arguments are provided, they must be matched as well.

	:param urlName: The route name that the current URL should match. Example: 'accounts:login'.
	:param className: The string that is returned if the current URL matches the specified one.
	:param kwargs: Any extra URL keyword arguments that must also be present in the current URL for it to match.
	:returns: ``className`` if the current URL matches, or an empty string otherwise.
	'''
	matches = pathMatches(context['request'].path, urlName, **kwargs)
	return className if matches else ''



def pathMatches(path, urlName, **kwargs):
	'''
	:param path: str
	:param urlName: str
	:returns: bool.
	'''
	resolved = urlresolvers.resolve(path)

	# Different URL name => the current URL cannot match.
	resolvedName = '{r.namespace}:{r.url_name}'.format(r = resolved) if resolved.namespace else resolved.url_name
	if urlName != resolvedName:
		return False

	# If any of the current keyword args is missing or different, the URL cannot match.
	for key, value in kwargs.items():
		currentArg = resolved.kwargs.get(key)
		if currentArg is None or str(value) != str(currentArg):
			return False

	return True
