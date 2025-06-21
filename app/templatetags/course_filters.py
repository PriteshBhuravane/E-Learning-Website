from django import template
register = template.Library()


@register.filter
def get_course(courses, slug):
  return courses.get(slug=slug)