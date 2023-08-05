# Python library imports.
import json

# Django imports.
from django.http import HttpResponse



class JsonResponse(HttpResponse):
	def __init__(self, content={}, status=None, content_type=None):
		if not content_type:
			content_type = 'application/json'
		super(JsonResponse, self).__init__(json.dumps(content), status=status, content_type=content_type)
