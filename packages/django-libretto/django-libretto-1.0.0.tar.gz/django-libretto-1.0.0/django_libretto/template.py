import django.template



def renderFile(path, context):
	t = django.template.loader.get_template(path)
	return t.render(django.template.Context(context))



def renderString(template, context):
	t = django.template.Template(template)
	return t.render(django.template.Context(context))
