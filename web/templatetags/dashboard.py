from django.template import Library


register = Library()

@register.simple_tag()
def user_span(span):
    """转化用户空间单位"""
    span = int(span)
    if span < (1024 * 1024 *1024) and span > (1024 * 1024):
        return '%.2f GB' % (int(span) / (1024 * 1024 *1024))
    elif span < (1024 * 1024) and span > 1024:
        return '%.2f MB' % (int(span) / (1024 * 1024))
    else:
        return '%.2f kB' % (int(span))