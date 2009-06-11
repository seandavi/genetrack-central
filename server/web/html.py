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

def download_response( data ):
    "Returns a file download"
    name = valid_ascii(data.name)
    mimetype = mimetypes.guess_type(name)[0] or 'application/octet-stream'
    stream = FileWrapper( open(data.path(), 'rb') )
    resp = HttpResponse( stream,  mimetype=mimetype )
    resp['Content-Disposition'] = 'attachment; filename=%s' % name
    return resp

def make_stream(fname):
    """
    Creates a django style chunked file stream from a file.
    This using the django upload functions on regular files
    (used mostly  during testing).

    >>> stream = make_stream(__file__)
    >>> for chunk in stream.chunks(size=10):
    ...     pass
    >>> 
    """
   
    class Chunks:
        def __init__(self,fname):
            self.fname = fname
        
        def chunks(self, size=2**10):
            "Returns chunks of data"
            fp = open(self.fname,'rb')
            while 1:
                data = fp.read(size)
                if not data:
                    raise StopIteration()
                yield data

    return Chunks(fname)

def test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    test()