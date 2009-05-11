"""
Html specific utility functions.
"""
from django.template import Context, loader
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse, HttpResponseRedirect

class Params(object):
    """
    Represents incoming parameters. Keyword arguments
    will be defaults.

    >>> p = Params(a=1, b=2, c=3, incoming=dict(c=4))
    >>> p.a, p.b, p.c
    (1, 2, 4)
    """
    def __init__(self, incoming={}, **kwds):
        self.__dict__.update(kwds)
        self.__dict__.update(incoming)

    def __repr__(self):
        return 'Params: %s' % self.__dict__

def render(name, **kwd):
    """Fills a template"""
    c = Context(kwd)
    t = loader.get_template(name)
    return t.render(c)

def response(data, **kwd):
    """Returns a http response"""
    return HttpResponse(data, **kwd)

def redirect(url):
    "Redirects to a url"
    return HttpResponseRedirect(url)

def template(request, name, mimetype=None, **kwd):
    """Renders a template and returns it as an http response"""
    messages = request.user.get_and_delete_messages()
    page = render(name, messages=messages, **kwd)
    return response(page, mimetype=mimetype)

def test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    test()