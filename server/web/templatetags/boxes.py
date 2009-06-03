from django import template

from server.web import html

register = template.Library()

@register.simple_tag
def sep():
    "Default separator"
    return "&nbsp;&bull;&nbsp;"

@register.inclusion_tag('admin-box.html', takes_context=True)
def admin_box(context):
    return {
        'user': context['user'],
    }

@register.inclusion_tag('account-box.html', takes_context=True)
def account_box(context, navloc):
    return {
        'user': context['user'],
        'params': context.get('params'),
        'project': context.get('project'),
        'navloc': navloc,
    }

@register.inclusion_tag('filter-box.html', takes_context=True)
def filter_box(context):
    return {
        'user': context['user'],
    }

@register.inclusion_tag('project-actions-box.html', takes_context=True)
def project_actions_box(context):
    return {
        'user': context['user'],
        'project': context['project'],
    }

@register.inclusion_tag('upload-box.html', takes_context=True)
def upload_box(context):
    return {
        'user': context['user'],
    }

def test():

    print admin_box()

if __name__ == '__main__':
    test()