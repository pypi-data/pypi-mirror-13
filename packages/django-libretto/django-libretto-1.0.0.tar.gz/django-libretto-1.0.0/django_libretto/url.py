from django.core import urlresolvers
import django.utils.http



def reverse(view, *args, **kwargs):
	'''
	User-friendly reverse. Pass arguments and keyword arguments to Django's `reverse`
	as `args` and `kwargs` arguments, respectively.

	The special optional keyword argument `query` is a dictionary of query (or GET) parameters
	that can be appended to the `reverse`d URL.

	Example:

		reverse('products:category', categoryId = 5, query = {'page': 2})

	is equivalent to

		django.core.urlresolvers.reverse('products:category', kwargs = {'categoryId': 5}) + '?page=2'

	'''
	if 'query' in kwargs:
		query = kwargs.pop('query')
	else:
		query = None
	base = urlresolvers.reverse(view, args = args, kwargs = kwargs)
	if query:
		return '{}?{}'.format(base, django.utils.http.urlencode(query))
	else:
		return base
