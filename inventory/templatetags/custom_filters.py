# custom_filters.py
from django import template


register = template.Library()

@register.filter
def custom_filter(value):
    # Burada filtre işlemlerini gerçekleştirin
    return value

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    """
    Check if the user belongs to the given group.

    Usage:
    {% if request.user|has_group:"admin" %}
        <!-- User is in the admin group -->
    {% endif %}
    """
    return user.groups.filter(name=group_name).exists()