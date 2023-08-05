# Python library imports.
#

# Django imports.
from django.db import models



def extendManager(mixinClass):
	'''
	Use as a class decorator to add extra methods to your model manager.
	Example usage:

		class Article(django.db.models.Model):
			published = models.DateTimeField()
			...

			@extendManager
			class objects(object):
				def getPublished(self):
					return self.filter(published__lte = django.utils.timezone.now()).order_by('-published')

		...

		publishedArticles = Article.objects.getPublished()
	'''

	class MixinManager(models.Manager, mixinClass):
		class MixinQuerySet(models.query.QuerySet, mixinClass):
			pass
		def get_queryset(self):
			return self.MixinQuerySet(self.model, using = self._db)

	return MixinManager()
