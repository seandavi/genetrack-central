from django import template

from server.web import html

register = template.Library()

@register.inclusion_tag('admin-box.html', takes_context=True)
def admin_box(context):
    return {
        'user': context['user'],
    }

@register.inclusion_tag('account-box.html', takes_context=True)
def account_box(context, navloc):
    return {
        'user': context['user'],
        'navloc': navloc,
    }

@register.inclusion_tag('filter-box.html', takes_context=True)
def filter_box(context):
    return {
        'user': context['user'],
    }

def test():

    print admin_box()

if __name__ == '__main__':
    test()