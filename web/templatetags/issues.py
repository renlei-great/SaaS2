from django.template import Library


register = Library()


# 显示ｉｄ进行修改
@register.simple_tag()
def string_abjuct(id):
    """调整id"""
    return '#' + str(id).rjust(3, '0')