"""
Html specific utility functions.
"""
import string, mimetypes
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
    user = request.user        
    messages = user.get_and_delete_messages()
    page = render(name, messages=messages, user=user, **kwd)
    return response(page, mimetype=mimetype)


def valid_ascii(text):
    """
    Translates text into onto a valid filename on all platforms
    >>> valid_ascii("A@B#C%D(E)F G+H!I-J")
    'A-B-C-D-E-F-G-H-I-J'
    """
    valid = set(string.digits + string.ascii_letters + ".-=")
    def trans(letter):
        if letter in valid:
            return letter
        else:
            return '-'
    return ''.join(map(trans, text))

def download_data( data ):
    "Returns a file download"
    resp = download_stream( filename=data.path(), name=data.name, asfile=True)
    return resp

def download_stream( filename, name, mimetype=None, asfile=False ):
    "Returns a stream as a browser download"
    
    mimetype = mimetype or mimetypes.guess_type(name)[0] or 'application/octet-stream'
    stream = FileWrapper( open(filename, 'rb') )
    resp = HttpResponse( stream,  mimetype=mimetype )
    if asfile:
        name = valid_ascii(name)
        resp['Content-Disposition'] = 'attachment; filename=%s' % name
    return resp

def test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    test()