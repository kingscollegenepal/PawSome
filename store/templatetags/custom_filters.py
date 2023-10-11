from django import template

register = template.Library()

@register.filter(name='k_format')
def k_format(value):
    try:
        value = int(value)
        if value < 1000:
            return str(value)
        elif value < 1000000:
            return str(round(value/1000, 1)) + 'k'
        # Add further formatting here if required
        else:
            return value
    except:
        return value
